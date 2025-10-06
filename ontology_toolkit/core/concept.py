"""
Инструменты чтения/записи сущностей FPF в формате Markdown + YAML frontmatter.

Содержит:
- универсальные функции для разбора и сериализации файлов;
- менеджер `ConceptFile`, сохраняющий обратную совместимость с текущим API;
- фабрику `ConceptFactory` для создания черновиков/заполненных концептов.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar

import frontmatter

from ontology_toolkit.core.schema import (
    Concept as ConceptModel,
    BaseEntity,
    ConceptStatus,
    MetaMetaType,
    Relation,
    RelationType,
)

__all__ = [
    "ConceptFile",
    "ConceptFactory",
    "entity_to_markdown",
    "load_entity_from_file",
    "save_entity_to_file",
]

TEntity = TypeVar("TEntity", bound=BaseEntity)


# ---------------------------------------------------------------------------
# Вспомогательные парсеры
# ---------------------------------------------------------------------------

def _parse_content_sections(content: str) -> Dict[str, str]:
    """Разбивает Markdown-содержимое на секции заголовков второго уровня."""
    sections: Dict[str, str] = {}
    current_section: Optional[str] = None
    buffer: List[str] = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = line[3:].strip().lower()
            buffer = []
        elif current_section is not None:
            buffer.append(line)

    if current_section:
        sections[current_section] = "\n".join(buffer).strip()

    return sections


def _parse_bullet_list(text: str) -> List[str]:
    """Выделяет элементы маркированного списка (- /*) в списке строк."""
    items: List[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            items.append(stripped[2:].strip())
    return items


def _parse_relations(relations_data: Sequence[Dict[str, Any]]) -> List[Relation]:
    """Конвертирует словари из frontmatter в объекты Relation."""
    relations: List[Relation] = []
    for raw in relations_data or []:
        try:
            relations.append(
                Relation(
                    type=RelationType(raw["type"]),
                    target=raw["target"],
                    description=raw.get("description"),
                )
            )
        except (KeyError, ValueError):
            # Некорректная запись — пропускаем, чтобы не прерывать загрузку.
            continue
    return relations


def _parse_datetime(value: Any) -> datetime:
    """Безопасно приводит значение к datetime."""
    if not value:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return datetime.now()


def _enum_to_value(value: Any) -> Any:
    """Возвращает `.value` для Enum-значений, и исходное значение в остальных случаях."""
    return getattr(value, "value", value)


def _sanitize_filename(name: str) -> str:
    """Формирует безопасное имя файла на основе названия сущности."""
    translit = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ь": "",
        "ы": "y",
        "ъ": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }

    normalized = []
    for char in name.lower():
        if char in translit:
            normalized.append(translit[char])
        elif char.isalnum() or char in ("-", "_"):
            normalized.append(char)
        elif char in (" ", "/", "\\"):
            normalized.append("_")
    safe = re.sub(r"_+", "_", "".join(normalized)).strip("_")
    return safe[:50]


# ---------------------------------------------------------------------------
# Универсальные функции загрузки/сохранения
# ---------------------------------------------------------------------------

def load_entity_from_file(file_path: Path, entity_cls: Type[TEntity]) -> TEntity:
    """Загружает сущность любого типа из Markdown-файла."""
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    with open(file_path, "r", encoding="utf-8") as handler:
        post = frontmatter.load(handler)

    metadata = dict(post.metadata)
    sections = _parse_content_sections(post.content)

    field_names = set(entity_cls.model_fields.keys())
    data: Dict[str, Any] = {}

    if "definition" in field_names:
        data["definition"] = sections.get("definition", "")
    if "purpose" in field_names:
        data["purpose"] = sections.get("purpose", "")
    if "examples" in field_names:
        data["examples"] = _parse_bullet_list(sections.get("examples", ""))
    if "notes" in field_names:
        data["notes"] = sections.get("notes")

    if "relations" in field_names:
        data["relations"] = _parse_relations(metadata.get("relations", []))
    if "created" in field_names:
        data["created"] = _parse_datetime(metadata.get("created"))
    if "updated" in field_names:
        data["updated"] = _parse_datetime(metadata.get("updated"))

    for key, value in metadata.items():
        if key in {"relations", "created", "updated"}:
            continue
        if key in field_names:
            data[key] = value

    return entity_cls(**data)  # type: ignore[arg-type]


def entity_to_markdown(entity: BaseEntity) -> str:
    """Формирует Markdown + YAML frontmatter для произвольной сущности."""
    payload = entity.model_dump(mode="python")

    metadata: Dict[str, Any] = {}
    definition = payload.pop("definition", "")
    purpose = payload.pop("purpose", "")
    examples = payload.pop("examples", [])
    notes = payload.pop("notes", None)
    relations = payload.pop("relations", [])
    created = payload.pop("created", datetime.now())
    updated = payload.pop("updated", datetime.now())

    for key, value in payload.items():
        metadata[key] = _enum_to_value(value)

    serialized_relations: List[Dict[str, Any]] = []
    for relation in relations:
        if isinstance(relation, Relation):
            serialized_relations.append(
                {
                    "type": relation.type.value,
                    "target": relation.target,
                    "description": relation.description,
                }
            )
        elif isinstance(relation, dict):
            serialized_relations.append(
                {
                    "type": _enum_to_value(relation.get("type")),
                    "target": relation.get("target"),
                    "description": relation.get("description"),
                }
            )
    metadata["relations"] = serialized_relations
    metadata["created"] = created.isoformat()
    metadata["updated"] = updated.isoformat()

    sections: List[Tuple[str, str]] = [
        ("Definition", definition or "[пусто]"),
        ("Purpose", purpose or "[пусто]"),
    ]

    lines: List[str] = [f"# {entity.name}", ""]
    for title, text in sections:
        lines.append(f"## {title}")
        lines.append(text)
        lines.append("")

    if examples:
        lines.append("## Examples")
        lines.append("")
        for example in examples:
            lines.append(f"- {example}")
        lines.append("")

    if notes:
        lines.append("## Notes")
        lines.append(notes)
        lines.append("")

    post = frontmatter.Post("\n".join(lines).strip() + "\n", **metadata)
    return frontmatter.dumps(post)


def save_entity_to_file(
    entity: BaseEntity,
    directory: Path,
    overwrite: bool = False,
) -> Path:
    """Сохраняет сущность в указанную директорию."""
    directory.mkdir(parents=True, exist_ok=True)

    filename = f"{entity.id}_{_sanitize_filename(entity.name or entity.id)}.md"
    file_path = directory / filename

    if file_path.exists() and not overwrite:
        raise FileExistsError(f"Файл уже существует: {file_path}")

    with open(file_path, "w", encoding="utf-8") as handler:
        handler.write(entity_to_markdown(entity))

    return file_path


# ---------------------------------------------------------------------------
# API для концептов (обратная совместимость)
# ---------------------------------------------------------------------------

class ConceptFile:
    """Обёртка над ConceptModel для обратной совместимости с текущим кодом."""

    def __init__(self, concept: ConceptModel):
        self.concept = concept

    @classmethod
    def from_file(cls, file_path: Path) -> "ConceptFile":
        return cls(load_entity_from_file(file_path, ConceptModel))

    def to_markdown(self) -> str:
        return entity_to_markdown(self.concept)

    def save(self, directory: Path, overwrite: bool = False) -> Path:
        return save_entity_to_file(self.concept, directory, overwrite=overwrite)

    def update_field(self, field_name: str, value: Any) -> None:
        if hasattr(self.concept, field_name):
            setattr(self.concept, field_name, value)
            self.concept.updated = datetime.now()
        else:
            raise ValueError(f"Поле {field_name} не найдено")

    def add_example(self, example: str) -> None:
        if example not in self.concept.examples:
            self.concept.examples.append(example)
            self.concept.updated = datetime.now()

    def remove_example(self, example: str) -> bool:
        if example in self.concept.examples:
            self.concept.examples.remove(example)
            self.concept.updated = datetime.now()
            return True
        return False


class ConceptFactory:
    """Фабрика для создания новых концептов."""

    @staticmethod
    def create_draft(name: str, concept_id: Optional[str] = None) -> ConceptModel:
        return ConceptModel(
            id=concept_id or "C_TEMP",
            name=name,
            definition="[пусто]",
            purpose="[пусто]",
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
        return ConceptModel(
            id=concept_id or "C_TEMP",
            name=name,
            definition=definition,
            purpose=purpose,
            meta_meta=meta_meta,
            examples=examples,
            status=ConceptStatus.DRAFT_FILLED,
        )
