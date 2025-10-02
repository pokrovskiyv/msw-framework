"""
Класс Ontology для управления всей онтологией проекта.

Функции:
- Загрузка всех объектов из файлов
- Индексация по ID и name
- Построение графа связей
- Валидация связей (broken links)
- Добавление/удаление объектов
- Поиск по различным критериям
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

import networkx as nx
from rich.console import Console
from rich.table import Table

from ontology_toolkit.core.schema import (
    Concept as ConceptModel,
    Method,
    System,
    Problem,
    Artifact,
    BaseEntity,
    ConceptStatus,
    ConceptSchema,
)
from ontology_toolkit.core.concept import ConceptFile, ConceptFactory


class OntologyIndex:
    """Индекс для быстрого поиска объектов."""

    def __init__(self):
        """Инициализация индекса."""
        self.by_id: Dict[str, BaseEntity] = {}
        self.by_name: Dict[str, List[BaseEntity]] = defaultdict(list)
        self.by_prefix: Dict[str, List[BaseEntity]] = defaultdict(list)
        self.by_status: Dict[str, List[ConceptModel]] = defaultdict(list)

    def add(self, entity: BaseEntity) -> None:
        """Добавить объект в индекс."""
        self.by_id[entity.id] = entity
        
        # Нормализованное имя для поиска
        normalized_name = self._normalize_name(entity.name)
        self.by_name[normalized_name].append(entity)

        # По префиксу
        prefix, _ = ConceptSchema.parse_id(entity.id)
        self.by_prefix[prefix].append(entity)

        # По статусу (только для Concept)
        if isinstance(entity, ConceptModel):
            self.by_status[entity.status.value].append(entity)

    def remove(self, entity_id: str) -> Optional[BaseEntity]:
        """Удалить объект из индекса."""
        if entity_id not in self.by_id:
            return None

        entity = self.by_id.pop(entity_id)

        # Удаляем из других индексов
        normalized_name = self._normalize_name(entity.name)
        if normalized_name in self.by_name:
            self.by_name[normalized_name] = [
                e for e in self.by_name[normalized_name] if e.id != entity_id
            ]

        prefix, _ = ConceptSchema.parse_id(entity_id)
        self.by_prefix[prefix] = [e for e in self.by_prefix[prefix] if e.id != entity_id]

        if isinstance(entity, ConceptModel):
            self.by_status[entity.status.value] = [
                e for e in self.by_status[entity.status.value] if e.id != entity_id
            ]

        return entity

    def get(self, entity_id: str) -> Optional[BaseEntity]:
        """Получить объект по ID."""
        return self.by_id.get(entity_id)

    def find_by_name(self, name: str) -> List[BaseEntity]:
        """Найти объекты по имени (нормализованный поиск)."""
        normalized = self._normalize_name(name)
        return self.by_name.get(normalized, [])

    def get_next_id(self, prefix: str) -> str:
        """Получить следующий свободный ID для префикса."""
        entities = self.by_prefix.get(prefix, [])
        if not entities:
            return ConceptSchema.format_id(prefix, 1)

        # Находим максимальный номер
        max_num = 0
        for entity in entities:
            _, num = ConceptSchema.parse_id(entity.id)
            max_num = max(max_num, num)

        return ConceptSchema.format_id(prefix, max_num + 1)

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Нормализовать имя для поиска (lowercase, ё→е)."""
        return name.lower().replace("ё", "е").strip()


class Ontology:
    """Главный класс для работы с онтологией проекта."""

    def __init__(self, root_path: Path):
        """
        Инициализация онтологии.
        
        Args:
            root_path: Корневой путь к проекту онтологии (.ontology/)
        """
        self.root_path = Path(root_path)
        self.index = OntologyIndex()
        self.graph = nx.DiGraph()  # Направленный граф связей
        self.console = Console()

        # Пути к папкам
        self.concepts_dir = self.root_path / "concepts"
        self.methods_dir = self.root_path / "methods"
        self.systems_dir = self.root_path / "systems"
        self.problems_dir = self.root_path / "problems"
        self.artifacts_dir = self.root_path / "artifacts"

    def load_all(self) -> None:
        """Загрузить все объекты из файлов."""
        self.console.print("[bold blue]Загрузка онтологии...[/bold blue]")

        # Загружаем понятия
        if self.concepts_dir.exists():
            for file_path in self.concepts_dir.glob("*.md"):
                try:
                    concept_file = ConceptFile.from_file(file_path)
                    self.add_entity(concept_file.concept)
                except Exception as e:
                    self.console.print(f"[red]Ошибка загрузки {file_path}: {e}[/red]")

        # TODO: Загрузка methods, systems, problems, artifacts (аналогично)

        self.console.print(
            f"[green]Загружено объектов: {len(self.index.by_id)}[/green]"
        )

        # Строим граф
        self._build_graph()

    def add_entity(self, entity: BaseEntity) -> None:
        """
        Добавить объект в онтологию.
        
        Args:
            entity: Объект (Concept, Method, System, ...)
        """
        self.index.add(entity)

    def remove_entity(self, entity_id: str) -> Optional[BaseEntity]:
        """
        Удалить объект из онтологии.
        
        Args:
            entity_id: ID объекта
            
        Returns:
            Удалённый объект или None
        """
        entity = self.index.remove(entity_id)
        if entity:
            # Удаляем из графа
            if self.graph.has_node(entity_id):
                self.graph.remove_node(entity_id)
        return entity

    def add_concept(
        self, name: str, auto_assign_id: bool = True
    ) -> ConceptModel:
        """
        Добавить новое понятие (черновик).
        
        Args:
            name: Название понятия
            auto_assign_id: Автоматически присвоить ID
            
        Returns:
            Созданное понятие
        """
        # Проверка на дубликаты
        existing = self.index.find_by_name(name)
        if existing:
            raise ValueError(
                f"Понятие с именем '{name}' уже существует: {existing[0].id}"
            )

        # Создаём черновик
        concept_id = None
        if auto_assign_id:
            concept_id = self.index.get_next_id("C")

        concept = ConceptFactory.create_draft(name, concept_id)
        self.add_entity(concept)

        return concept

    def get_concept(self, concept_id: str) -> Optional[ConceptModel]:
        """Получить понятие по ID."""
        entity = self.index.get(concept_id)
        if isinstance(entity, ConceptModel):
            return entity
        return None

    def save_concept(self, concept: ConceptModel, overwrite: bool = True) -> Path:
        """
        Сохранить понятие в файл.
        
        Args:
            concept: Понятие для сохранения
            overwrite: Перезаписать если существует
            
        Returns:
            Путь к сохранённому файлу
        """
        concept_file = ConceptFile(concept)
        return concept_file.save(self.concepts_dir, overwrite=overwrite)

    def _build_graph(self) -> None:
        """Построить граф связей между объектами."""
        self.graph.clear()

        # Добавляем все узлы
        for entity_id in self.index.by_id:
            self.graph.add_node(entity_id)

        # Добавляем рёбра (связи)
        for entity_id, entity in self.index.by_id.items():
            for relation in entity.relations:
                if relation.target in self.index.by_id:
                    self.graph.add_edge(
                        entity_id,
                        relation.target,
                        type=relation.type.value,
                        description=relation.description,
                    )

    def validate_relations(self) -> List[Tuple[str, str, str]]:
        """
        Валидация связей (поиск broken links).
        
        Returns:
            Список (source_id, target_id, error) для broken links
        """
        errors = []

        for entity_id, entity in self.index.by_id.items():
            for relation in entity.relations:
                if relation.target not in self.index.by_id:
                    errors.append(
                        (
                            entity_id,
                            relation.target,
                            f"Целевой объект не найден: {relation.target}",
                        )
                    )

        return errors

    def fix_relations(self, dry_run: bool = True) -> int:
        """
        Исправить broken links (удалить связи на несуществующие объекты).
        
        Args:
            dry_run: Только показать, не исправлять
            
        Returns:
            Количество исправленных связей
        """
        errors = self.validate_relations()
        if not errors:
            return 0

        fixed = 0
        for source_id, target_id, _ in errors:
            entity = self.index.get(source_id)
            if entity:
                if not dry_run:
                    entity.remove_relation(target_id)
                fixed += 1

        if not dry_run:
            self._build_graph()

        return fixed

    def get_related(self, entity_id: str, depth: int = 1) -> Set[str]:
        """
        Получить связанные объекты на указанной глубине.
        
        Args:
            entity_id: ID объекта
            depth: Глубина поиска
            
        Returns:
            Множество ID связанных объектов
        """
        if entity_id not in self.graph:
            return set()

        related = set()
        for d in range(1, depth + 1):
            # Исходящие связи
            successors = list(self.graph.successors(entity_id))
            related.update(successors)

            # Входящие связи
            predecessors = list(self.graph.predecessors(entity_id))
            related.update(predecessors)

        return related

    def audit(self) -> Dict[str, Any]:
        """
        Провести аудит онтологии.
        
        Returns:
            Словарь с результатами аудита
        """
        audit_report = {
            "total_objects": len(self.index.by_id),
            "by_prefix": {
                prefix: len(entities)
                for prefix, entities in self.index.by_prefix.items()
            },
            "by_status": {
                status: len(entities)
                for status, entities in self.index.by_status.items()
            },
            "broken_links": len(self.validate_relations()),
            "isolated_nodes": len(list(nx.isolates(self.graph))),
        }

        return audit_report

    def print_audit(self) -> None:
        """Вывести результаты аудита в консоль."""
        audit = self.audit()

        table = Table(title="Аудит онтологии")
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", style="magenta")

        table.add_row("Всего объектов", str(audit["total_objects"]))
        
        for prefix, count in audit["by_prefix"].items():
            table.add_row(f"  - {prefix} (префикс)", str(count))

        table.add_row("", "")
        table.add_row("[bold]По статусам[/bold]", "")
        for status, count in audit["by_status"].items():
            table.add_row(f"  - {status}", str(count))

        table.add_row("", "")
        table.add_row("Broken links", str(audit["broken_links"]))
        table.add_row("Изолированные узлы", str(audit["isolated_nodes"]))

        self.console.print(table)

    def find_concepts_by_status(self, status: ConceptStatus) -> List[ConceptModel]:
        """Найти понятия по статусу."""
        return self.index.by_status.get(status.value, [])

    def get_next_id(self, prefix: str) -> str:
        """
        Получить следующий свободный ID для префикса.
        
        Args:
            prefix: Префикс (C, M, S, P, A)
            
        Returns:
            Следующий ID (например, C_5)
        """
        return self.index.get_next_id(prefix)

    def suggest_relations(self, entity_id: str, max_suggestions: int = 5) -> List[str]:
        """
        Предложить возможные связи для объекта на основе текстовой близости.
        
        Args:
            entity_id: ID объекта
            max_suggestions: Максимум предложений
            
        Returns:
            Список ID потенциально связанных объектов
        """
        # TODO: Реализовать анализ текстовой близости
        # Простая версия: предлагаем объекты из того же "кластера" в графе
        related = self.get_related(entity_id, depth=2)
        return list(related)[:max_suggestions]
