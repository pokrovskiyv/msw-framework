"""
Автозаполнение полей понятий через AI.
"""

import re
from typing import List, Dict, Any, Optional

from ontology_toolkit.ai.client import AIClient
from ontology_toolkit.ai.prompts import PromptLoader
from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import Concept, ConceptStatus


class ConceptFiller:
    """Заполнение понятий через AI."""

    def __init__(self, client: AIClient, ontology: Ontology):
        """
        Инициализация filler'а.
        
        Args:
            client: AI клиент
            ontology: Онтология проекта
        """
        self.client = client
        self.ontology = ontology
        self.prompt_loader = PromptLoader()

    def fill_concept(
        self,
        concept_id: str,
        fields: Optional[List[str]] = None,
        additional_context: str = ""
    ) -> Concept:
        """
        Заполнить понятие через AI.
        
        Args:
            concept_id: ID понятия (напр., C_1)
            fields: Список полей для заполнения (если None, заполняются все)
            additional_context: Дополнительный контекст для AI
            
        Returns:
            Обновлённое понятие
            
        Raises:
            ValueError: Если понятие не найдено
        """
        # Получаем понятие
        concept = self.ontology.index.by_id.get(concept_id)
        if not concept:
            raise ValueError(f"Понятие {concept_id} не найдено")
        
        if not isinstance(concept, Concept):
            raise ValueError(f"{concept_id} не является понятием")
        
        # Подготавливаем контекст
        context = self._prepare_context()
        
        # Формируем промпт
        prompt = self.prompt_loader.render_concept_fill(
            concept_name=concept.name,
            additional_context=additional_context,
            concepts_data=context.get("concepts", ""),
            problems_data=context.get("problems", ""),
            methods_data=context.get("methods", ""),
            systems_data=context.get("systems", ""),
            artifacts_data=context.get("artifacts", ""),
            context_data=context.get("context", "")
        )
        
        # Генерируем ответ через AI
        response = self.client.generate(prompt, max_tokens=2000)
        
        # Парсим ответ
        parsed_data = self._parse_ai_response(response)
        
        # Обновляем поля понятия
        if not fields or "definition" in fields:
            concept.definition = parsed_data.get("definition", concept.definition)
        
        if not fields or "purpose" in fields:
            concept.purpose = parsed_data.get("purpose", concept.purpose)
        
        if not fields or "meta_meta" in fields:
            if parsed_data.get("meta_meta"):
                concept.meta_meta = parsed_data["meta_meta"]
        
        if not fields or "examples" in fields:
            if parsed_data.get("examples"):
                concept.examples = parsed_data["examples"]
        
        # Обновляем связи (если AI предложил)
        if (not fields or "relations" in fields) and parsed_data.get("relations"):
            concept.relations = parsed_data["relations"]
        
        # Меняем статус на draft+filled
        if concept.status == ConceptStatus.DRAFT:
            concept.status = ConceptStatus.DRAFT_FILLED
        
        # Обновляем время изменения
        from datetime import datetime
        concept.updated = datetime.now()
        
        return concept

    def _prepare_context(self) -> Dict[str, str]:
        """
        Подготовить контекст для AI (список существующих объектов).
        
        Returns:
            Словарь с данными по типам объектов
        """
        context = {}
        
        # Формируем список существующих понятий
        concepts = [
            f"{e.id}_{e.name}"
            for e in self.ontology.index.by_id.values()
            if hasattr(e, "prefix") and e.prefix == "C"
        ]
        if concepts:
            context["concepts"] = "; ".join(concepts[:50])  # Ограничиваем 50 для экономии токенов
        
        # Аналогично для других типов (пока пусто, т.к. поддерживаем только concepts)
        context["problems"] = ""
        context["methods"] = ""
        context["systems"] = ""
        context["artifacts"] = ""
        context["context"] = ""
        
        return context

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Распарсить ответ AI в структурированные данные.
        
        Args:
            response: Ответ AI (ожидается Markdown таблица)
            
        Returns:
            Словарь с полями понятия
        """
        result = {}
        
        # Ищем Markdown таблицу в ответе
        table_match = re.search(r'\|.*?\|.*?\|.*?\n\|[-:| ]+\|\n(\|.*?\|.*?\n)', response, re.MULTILINE | re.DOTALL)
        
        if table_match:
            # Извлекаем строку с данными
            data_row = table_match.group(1)
            # Разбиваем на ячейки
            cells = [cell.strip() for cell in data_row.split('|') if cell.strip()]
            
            # Ожидаемый порядок: id, name, definition, purpose, meta_meta, examples, relations
            if len(cells) >= 3:
                result["definition"] = cells[2] if len(cells) > 2 else ""
                result["purpose"] = cells[3] if len(cells) > 3 else ""
                result["meta_meta"] = cells[4] if len(cells) > 4 else None
                result["examples"] = cells[5].split("; ") if len(cells) > 5 and cells[5] else []
                
                # Парсим relations
                if len(cells) > 6 and cells[6]:
                    result["relations"] = self._parse_relations(cells[6])
        
        return result

    def _parse_relations(self, relations_str: str) -> List[Any]:
        """
        Распарсить строку со связями.
        
        Args:
            relations_str: Строка с ID связанных объектов (напр., "C_2_Name; P_1_Problem")
            
        Returns:
            Список Relation объектов
        """
        from ontology_toolkit.core.schema import Relation, RelationType
        
        relations = []
        if not relations_str or relations_str == "-":
            return relations
        
        # Разбиваем на отдельные связи
        parts = [p.strip() for p in relations_str.split(";") if p.strip()]
        
        for part in parts:
            # Извлекаем ID (формат: C_1_name или просто C_1)
            id_match = re.match(r'([CMPSA]_\d+)', part)
            if id_match:
                target_id = id_match.group(1)
                # Проверяем, существует ли такой объект
                if target_id in self.ontology.index.by_id:
                    relations.append(Relation(
                        type=RelationType.RELATED_TO,
                        target=target_id
                    ))
        
        return relations

