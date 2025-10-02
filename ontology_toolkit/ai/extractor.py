"""
Извлечение понятий из текста через AI.
"""

import re
from pathlib import Path
from typing import List

from ontology_toolkit.ai.client import AIClient
from ontology_toolkit.core.schema import Concept, ConceptStatus, MetaMetaType
from ontology_toolkit.core.ontology import Ontology


class ConceptExtractor:
    """Извлечение понятий из текста через AI."""

    def __init__(self, client: AIClient, ontology: Ontology):
        """
        Инициализация extractor'а.
        
        Args:
            client: AI клиент
            ontology: Онтология проекта
        """
        self.client = client
        self.ontology = ontology

    def extract_from_file(self, file_path: Path | str) -> List[Concept]:
        """
        Извлечь понятия из файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Список извлечённых понятий
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        text = file_path.read_text(encoding="utf-8")
        return self.extract_from_text(text, source=str(file_path))

    def extract_from_text(self, text: str, source: str = "") -> List[Concept]:
        """
        Извлечь понятия из текста.
        
        Args:
            text: Текст для анализа
            source: Источник текста (для справки)
            
        Returns:
            Список извлечённых понятий
        """
        # Формируем промпт
        prompt = self._build_extraction_prompt(text)
        
        # Генерируем ответ
        response = self.client.generate(prompt, max_tokens=3000)
        
        # Парсим ответ
        concepts = self._parse_extraction_response(response)
        
        return concepts

    def _build_extraction_prompt(self, text: str) -> str:
        """
        Построить промпт для извлечения понятий.
        
        Args:
            text: Текст для анализа
            
        Returns:
            Готовый промпт
        """
        # Получаем список существующих понятий
        existing_concepts = [
            f"{e.id}: {e.name}"
            for e in self.ontology.index.by_id.values()
            if hasattr(e, "prefix") and e.prefix == "C"
        ]
        existing_text = "\n".join(existing_concepts) if existing_concepts else "Нет"
        
        prompt = f"""# Задача: Извлечение понятий из текста

Проанализируй следующий текст и извлеки из него **ключевые понятия** (концепты), которые важны для понимания предметной области.

## Текст для анализа:

```
{text[:5000]}  # Ограничиваем длину для экономии токенов
```

## Существующие понятия в онтологии:

{existing_text}

## Инструкции:

1. Найди 3-7 ключевых понятий в тексте
2. Для каждого понятия укажи:
   - Название (кратко, 1-3 слова)
   - Определение (2-3 предложения)
   - Назначение (зачем это нужно)
   - Тип (характеристика, метод, состояние, роль, артефакт, система, проблема)
   - 2-3 примера использования

3. **Не дублируй** существующие понятия из списка выше
4. Фокусируйся на понятиях, которые **повторяются** или **центральны** для текста

## Формат ответа:

Верни результат в виде Markdown таблицы:

| name | definition | purpose | meta_meta | examples |
|------|-----------|---------|-----------|----------|
| Понятие 1 | Определение... | Назначение... | характеристика | Пример 1; Пример 2 |
| Понятие 2 | ... | ... | ... | ... |

Только таблица, без дополнительных комментариев.
"""
        return prompt

    def _parse_extraction_response(self, response: str) -> List[Concept]:
        """
        Распарсить ответ AI с извлечёнными понятиями.
        
        Args:
            response: Ответ AI
            
        Returns:
            Список понятий
        """
        concepts = []
        
        # Ищем Markdown таблицу
        table_pattern = r'\|.*?\|.*?\|.*?\n\|[-:| ]+\|\n((?:\|.*?\|\n)+)'
        table_match = re.search(table_pattern, response, re.MULTILINE)
        
        if not table_match:
            return concepts
        
        # Извлекаем строки с данными
        data_rows = table_match.group(1).strip().split('\n')
        
        # Получаем следующий ID (формат: C_5)
        next_id_str = self.ontology.get_next_id("C")
        # Извлекаем номер из ID
        from ontology_toolkit.core.schema import ConceptSchema
        _, next_num = ConceptSchema.parse_id(next_id_str)
        
        for i, row in enumerate(data_rows):
            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            
            if len(cells) >= 3:
                name = cells[0]
                definition = cells[1]
                purpose = cells[2] if len(cells) > 2 else "[Заполнить]"
                meta_meta_str = cells[3] if len(cells) > 3 else None
                examples_str = cells[4] if len(cells) > 4 else ""
                
                # Парсим meta_meta
                meta_meta = self._parse_meta_meta(meta_meta_str)
                
                # Парсим examples
                examples = [ex.strip() for ex in examples_str.split(";") if ex.strip()]
                
                # Создаём понятие с уникальным ID
                concept = Concept(
                    id=ConceptSchema.format_id("C", next_num + i),
                    name=name,
                    definition=definition,
                    purpose=purpose,
                    status=ConceptStatus.DRAFT_FILLED,
                    meta_meta=meta_meta,
                    examples=examples,
                    relations=[]
                )
                
                concepts.append(concept)
        
        return concepts

    def _parse_meta_meta(self, meta_meta_str: str | None) -> MetaMetaType | None:
        """
        Распарсить тип meta_meta из строки.
        
        Args:
            meta_meta_str: Строка с типом
            
        Returns:
            MetaMetaType или None
        """
        if not meta_meta_str:
            return None
        
        # Мапинг русских названий на enum
        type_mapping = {
            "характеристика": MetaMetaType.CHARACTERISTIC,
            "показатель": MetaMetaType.INDICATOR,
            "значение": MetaMetaType.VALUE,
            "состояние": MetaMetaType.STATE,
            "роль": MetaMetaType.ROLE,
            "метод": MetaMetaType.METHOD,
            "описание метода": MetaMetaType.METHOD_DESCRIPTION,
            "план работ": MetaMetaType.WORK_PLAN,
            "выполнение": MetaMetaType.EXECUTION,
            "артефакт": MetaMetaType.ARTIFACT,
            "система": MetaMetaType.SYSTEM,
            "проблема": MetaMetaType.PROBLEM,
        }
        
        normalized = meta_meta_str.lower().strip()
        return type_mapping.get(normalized)

