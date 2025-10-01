"""
Pydantic-схемы для валидации объектов онтологии.

Определяет структуру данных для:
- Concept (понятие)
- Method (метод)
- System (система)
- Problem (проблема)
- Artifact (артефакт)
- Relation (связь)
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class ConceptStatus(str, Enum):
    """Статус понятия в жизненном цикле."""

    DRAFT = "draft"  # Только name заполнен
    DRAFT_FILLED = "draft+filled"  # Все поля заполнены, не проверено
    APPROVED = "approved"  # Проверено и утверждено


class MetaMetaType(str, Enum):
    """Фундаментальные типы из FPF (человеко-понятные названия)."""

    CHARACTERISTIC = "Характеристика"
    INDICATOR = "Показатель"
    VALUE = "Значение"
    STATE = "Состояние"
    ROLE = "Роль"
    METHOD = "Метод"
    METHOD_DESCRIPTION = "Описание метода"
    WORK_PLAN = "План работ"
    EXECUTION = "Выполнение"
    ARTIFACT = "Артефакт"
    SYSTEM = "Система"
    PROBLEM = "Проблема"


class RelationType(str, Enum):
    """Типы связей между объектами."""

    REQUIRES = "requires"  # Требует (зависимость)
    ENABLES = "enables"  # Позволяет (результат)
    RELATES_TO = "relates_to"  # Связано с (общее)
    PART_OF = "part_of"  # Часть (композиция)
    INSTANCE_OF = "instance_of"  # Экземпляр (конкретизация)
    OPPOSITE_OF = "opposite_of"  # Противоположно
    SIMILAR_TO = "similar_to"  # Похоже на


class Relation(BaseModel):
    """Связь между объектами."""

    type: RelationType = Field(description="Тип связи")
    target: str = Field(description="ID целевого объекта (например, C_22)")
    description: Optional[str] = Field(None, description="Описание связи")

    def __str__(self) -> str:
        return f"{self.type.value} → {self.target}"


class BaseEntity(BaseModel):
    """Базовая сущность онтологии."""

    id: str = Field(description="Уникальный идентификатор (C_1, M_1, S_1, ...)")
    name: str = Field(description="Название (краткое, единственное число)")
    definition: str = Field(description="Определение (что это, из чего состоит)")
    purpose: str = Field(description="Назначение (зачем нужно, где применяется)")
    examples: List[str] = Field(
        default_factory=list, description="Примеры использования (2-5 штук)"
    )
    relations: List[Relation] = Field(
        default_factory=list, description="Связи с другими объектами"
    )
    created: datetime = Field(default_factory=datetime.now, description="Дата создания")
    updated: datetime = Field(default_factory=datetime.now, description="Дата обновления")
    notes: Optional[str] = Field(None, description="Дополнительные заметки")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация названия."""
        if not v or not v.strip():
            raise ValueError("Название не может быть пустым")
        # Первая буква заглавная
        return v.strip()

    @field_validator("definition", "purpose")
    @classmethod
    def validate_text_field(cls, v: str) -> str:
        """Валидация текстовых полей."""
        if not v or not v.strip():
            raise ValueError("Поле не может быть пустым")
        return v.strip()

    def add_relation(
        self, target: str, relation_type: RelationType, description: Optional[str] = None
    ) -> None:
        """Добавить связь с другим объектом."""
        # Проверка на дубликаты
        for rel in self.relations:
            if rel.target == target and rel.type == relation_type:
                return  # Связь уже существует

        self.relations.append(
            Relation(type=relation_type, target=target, description=description)
        )
        self.updated = datetime.now()

    def remove_relation(self, target: str, relation_type: Optional[RelationType] = None) -> bool:
        """Удалить связь с объектом. Возвращает True если удалено."""
        initial_len = len(self.relations)
        if relation_type:
            self.relations = [
                r for r in self.relations if not (r.target == target and r.type == relation_type)
            ]
        else:
            self.relations = [r for r in self.relations if r.target != target]

        if len(self.relations) < initial_len:
            self.updated = datetime.now()
            return True
        return False


class Concept(BaseEntity):
    """Понятие (мета-модель)."""

    status: ConceptStatus = Field(
        default=ConceptStatus.DRAFT, description="Статус понятия"
    )
    meta_meta: Optional[MetaMetaType] = Field(
        None, description="Фундаментальный тип из FPF"
    )

    @property
    def prefix(self) -> str:
        """Префикс ID для понятий."""
        return "C"

    def mark_filled(self) -> None:
        """Пометить как заполненное."""
        if self.status == ConceptStatus.DRAFT:
            self.status = ConceptStatus.DRAFT_FILLED
            self.updated = datetime.now()

    def approve(self) -> None:
        """Утвердить понятие."""
        self.status = ConceptStatus.APPROVED
        self.updated = datetime.now()


class Method(BaseEntity):
    """Метод (способ действия)."""

    method_type: Optional[str] = Field(
        None, description="Тип метода (абстрактный/описание/выполнение)"
    )
    steps: List[str] = Field(default_factory=list, description="Шаги выполнения метода")

    @property
    def prefix(self) -> str:
        """Префикс ID для методов."""
        return "M"


class System(BaseEntity):
    """Система (составная целостность)."""

    components: List[str] = Field(
        default_factory=list, description="Компоненты системы (ID других объектов)"
    )
    boundaries: Optional[str] = Field(None, description="Границы системы")

    @property
    def prefix(self) -> str:
        """Префикс ID для систем."""
        return "S"


class Problem(BaseEntity):
    """Проблема (разрыв между текущим и желаемым)."""

    current_state: Optional[str] = Field(None, description="Текущее состояние")
    desired_state: Optional[str] = Field(None, description="Желаемое состояние")
    metrics: List[str] = Field(
        default_factory=list, description="Метрики для измерения разрыва"
    )

    @property
    def prefix(self) -> str:
        """Префикс ID для проблем."""
        return "P"


class Artifact(BaseEntity):
    """Артефакт (знаниевый артефакт, рабочий продукт)."""

    artifact_type: Optional[str] = Field(
        None, description="Тип артефакта (документ/код/модель/...)"
    )
    template_ref: Optional[str] = Field(None, description="Ссылка на шаблон")

    @property
    def prefix(self) -> str:
        """Префикс ID для артефактов."""
        return "A"


class OntologyConfig(BaseModel):
    """Конфигурация онтологического проекта."""

    project_name: str = Field(description="Название проекта")
    project_description: str = Field(default="", description="Описание проекта")
    version: str = Field(default="0.1.0", description="Версия онтологии")
    language: str = Field(default="ru", description="Язык (ru/en)")
    created: datetime = Field(default_factory=datetime.now, description="Дата создания")

    # Префиксы ID
    prefixes: Dict[str, str] = Field(
        default_factory=lambda: {
            "concepts": "C",
            "methods": "M",
            "systems": "S",
            "problems": "P",
            "artifacts": "A",
        }
    )

    # Настройки AI
    ai_provider: str = Field(default="anthropic", description="Провайдер AI")
    ai_model: str = Field(default="claude-sonnet-4", description="Модель AI")
    ai_temperature: float = Field(default=0.3, description="Temperature для AI")


class ConceptSchema:
    """Утилиты для работы со схемами."""

    @staticmethod
    def get_entity_class(prefix: str) -> type[BaseEntity]:
        """Получить класс сущности по префиксу ID."""
        mapping = {
            "C": Concept,
            "M": Method,
            "S": System,
            "P": Problem,
            "A": Artifact,
        }
        return mapping.get(prefix, BaseEntity)

    @staticmethod
    def parse_id(entity_id: str) -> tuple[str, int]:
        """
        Распарсить ID на префикс и номер.
        
        Args:
            entity_id: ID в формате "C_123"
            
        Returns:
            (prefix, number): например ("C", 123)
        """
        parts = entity_id.split("_")
        if len(parts) != 2:
            raise ValueError(f"Неверный формат ID: {entity_id}")
        prefix = parts[0]
        try:
            number = int(parts[1])
        except ValueError:
            raise ValueError(f"Неверный номер в ID: {entity_id}")
        return prefix, number

    @staticmethod
    def format_id(prefix: str, number: int) -> str:
        """
        Сформировать ID из префикса и номера.
        
        Args:
            prefix: Префикс (C, M, S, P, A)
            number: Номер
            
        Returns:
            ID в формате "C_123"
        """
        return f"{prefix}_{number}"
