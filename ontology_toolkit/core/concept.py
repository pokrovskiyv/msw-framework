"""
Класс Concept для работы с понятиями в формате Markdown + YAML frontmatter.

Управляет жизненным циклом понятия:
- Создание из данных
- Сохранение в MD файл
- Загрузка из MD файла
- Обновление полей
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import frontmatter
import yaml

from ontology_toolkit.core.schema import (
    Concept as ConceptModel,
    BaseEntity,
    ConceptStatus,
    MetaMetaType,
    Relation,
    RelationType,
    ConceptSchema,
)


class ConceptFile:
    """Класс для работы с файлом понятия (MD + YAML frontmatter)."""

    def __init__(self, concept: ConceptModel):
        """
        Инициализация из Pydantic-модели.
        
        Args:
            concept: Модель понятия
        """
        self.concept = concept

    @classmethod
    def from_file(cls, file_path: Path) -> "ConceptFile":
        """
        Загрузить понятие из файла.
        
        Args:
            file_path: Путь к MD файлу
            
        Returns:
            ConceptFile экземпляр
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Парсим frontmatter
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        metadata = post.metadata
        content = post.content

        # Парсим контент на секции
        sections = cls._parse_content(content)

        # Создаём Pydantic модель
        concept = ConceptModel(
            id=metadata.get("id", ""),
            name=metadata.get("name", ""),
            status=ConceptStatus(metadata.get("status", "draft")),
            meta_meta=MetaMetaType(metadata["meta_meta"]) if metadata.get("meta_meta") else None,
            definition=sections.get("definition", ""),
            purpose=sections.get("purpose", ""),
            examples=cls._parse_list(sections.get("examples", "")),
            relations=cls._parse_relations(metadata.get("relations", [])),
            created=cls._parse_datetime(metadata.get("created")),
            updated=cls._parse_datetime(metadata.get("updated")),
            notes=sections.get("notes"),
        )

        return cls(concept)

    @staticmethod
    def _parse_content(content: str) -> Dict[str, str]:
        """
        Парсинг контента на секции (Definition, Purpose, Examples, Notes).
        
        Args:
            content: Markdown контент
            
        Returns:
            Словарь с секциями
        """
        sections = {}
        current_section = None
        current_text = []

        for line in content.split("\n"):
            # Проверяем заголовок секции
            if line.startswith("## "):
                # Сохраняем предыдущую секцию
                if current_section:
                    sections[current_section] = "\n".join(current_text).strip()
                # Новая секция
                current_section = line[3:].strip().lower()
                current_text = []
            elif current_section:
                current_text.append(line)

        # Сохраняем последнюю секцию
        if current_section:
            sections[current_section] = "\n".join(current_text).strip()

        return sections

    @staticmethod
    def _parse_list(text: str) -> List[str]:
        """
        Парсинг маркированного списка в список строк.
        
        Args:
            text: Текст со списком
            
        Returns:
            Список элементов
        """
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                items.append(line[2:].strip())
        return items

    @staticmethod
    def _parse_relations(relations_data: List[Dict[str, Any]]) -> List[Relation]:
        """
        Парсинг связей из YAML.
        
        Args:
            relations_data: Список словарей с relations
            
        Returns:
            Список Relation объектов
        """
        relations = []
        for rel_data in relations_data:
            try:
                rel = Relation(
                    type=RelationType(rel_data["type"]),
                    target=rel_data["target"],
                    description=rel_data.get("description"),
                )
                relations.append(rel)
            except (KeyError, ValueError) as e:
                # Логируем ошибку, но не падаем
                print(f"Warning: Не удалось распарсить связь: {rel_data}, ошибка: {e}")
        return relations

    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> datetime:
        """Парсинг datetime из строки."""
        if not dt_str:
            return datetime.now()
        if isinstance(dt_str, datetime):
            return dt_str
        try:
            return datetime.fromisoformat(str(dt_str))
        except:
            return datetime.now()

    def to_markdown(self) -> str:
        """
        Конвертировать в Markdown + YAML frontmatter.
        
        Returns:
            Строка с полным содержимым файла
        """
        # YAML frontmatter
        metadata = {
            "id": self.concept.id,
            "name": self.concept.name,
            "status": self.concept.status.value,
            "meta_meta": self.concept.meta_meta.value if self.concept.meta_meta else None,
            "relations": [
                {
                    "type": rel.type.value,
                    "target": rel.target,
                    "description": rel.description,
                }
                for rel in self.concept.relations
            ],
            "created": self.concept.created.isoformat(),
            "updated": self.concept.updated.isoformat(),
        }

        # Markdown контент
        content_parts = [
            f"# {self.concept.name}",
            "",
            "## Definition",
            self.concept.definition,
            "",
            "## Purpose",
            self.concept.purpose,
            "",
        ]

        if self.concept.examples:
            content_parts.extend([
                "## Examples",
                "",
            ])
            for example in self.concept.examples:
                content_parts.append(f"- {example}")
            content_parts.append("")

        if self.concept.notes:
            content_parts.extend([
                "## Notes",
                self.concept.notes,
                "",
            ])

        content = "\n".join(content_parts)

        # Собираем вместе
        post = frontmatter.Post(content, **metadata)
        return frontmatter.dumps(post)

    def save(self, directory: Path, overwrite: bool = False) -> Path:
        """
        Сохранить в файл.
        
        Args:
            directory: Директория для сохранения
            overwrite: Перезаписать если существует
            
        Returns:
            Путь к сохранённому файлу
        """
        # Формируем имя файла: C_1_agency.md
        safe_name = self._sanitize_filename(self.concept.name)
        filename = f"{self.concept.id}_{safe_name}.md"
        file_path = directory / filename

        if file_path.exists() and not overwrite:
            raise FileExistsError(f"Файл уже существует: {file_path}")

        # Создаём директорию если нужно
        directory.mkdir(parents=True, exist_ok=True)

        # Сохраняем
        markdown_content = self.to_markdown()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return file_path

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Преобразовать название в безопасное имя файла.
        
        Args:
            name: Название понятия
            
        Returns:
            Безопасное имя файла
        """
        # Транслитерация основных русских букв
        translit_map = {
            "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
            "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
            "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
            "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
            "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch",
            "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
            "э": "e", "ю": "yu", "я": "ya",
        }

        # Приводим к lowercase
        name = name.lower()

        # Транслитерация
        result = ""
        for char in name:
            if char in translit_map:
                result += translit_map[char]
            elif char.isalnum() or char in ("-", "_"):
                result += char
            elif char in (" ", "/", "\\"):
                result += "_"

        # Убираем множественные подчёркивания и ограничиваем длину
        result = re.sub(r"_+", "_", result)
        result = result.strip("_")
        return result[:50]  # Ограничение длины

    def update_field(self, field_name: str, value: Any) -> None:
        """
        Обновить поле понятия.
        
        Args:
            field_name: Название поля
            value: Новое значение
        """
        if hasattr(self.concept, field_name):
            setattr(self.concept, field_name, value)
            self.concept.updated = datetime.now()
        else:
            raise ValueError(f"Поле {field_name} не существует")

    def add_example(self, example: str) -> None:
        """Добавить пример."""
        if example not in self.concept.examples:
            self.concept.examples.append(example)
            self.concept.updated = datetime.now()

    def remove_example(self, example: str) -> bool:
        """Удалить пример. Возвращает True если удалён."""
        if example in self.concept.examples:
            self.concept.examples.remove(example)
            self.concept.updated = datetime.now()
            return True
        return False


class ConceptFactory:
    """Фабрика для создания понятий."""

    @staticmethod
    def create_draft(name: str, concept_id: Optional[str] = None) -> ConceptModel:
        """
        Создать черновик понятия (только с именем).
        
        Args:
            name: Название понятия
            concept_id: ID (если None, будет присвоен позже)
            
        Returns:
            Concept модель со статусом draft
        """
        return ConceptModel(
            id=concept_id or "C_TEMP",
            name=name,
            definition="[Заполнить]",
            purpose="[Заполнить]",
            status=ConceptStatus.DRAFT,
        )

    @staticmethod
    def create_filled(
        name: str,
        definition: str,
        purpose: str,
        meta_meta: MetaMetaType,
        examples: List[str],
        concept_id: Optional[str] = None,
    ) -> ConceptModel:
        """
        Создать заполненное понятие.
        
        Args:
            name: Название
            definition: Определение
            purpose: Назначение
            meta_meta: Тип из FPF
            examples: Примеры
            concept_id: ID (если None, будет присвоен позже)
            
        Returns:
            Concept модель со статусом draft+filled
        """
        return ConceptModel(
            id=concept_id or "C_TEMP",
            name=name,
            definition=definition,
            purpose=purpose,
            meta_meta=meta_meta,
            examples=examples,
            status=ConceptStatus.DRAFT_FILLED,
        )
