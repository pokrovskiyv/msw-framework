"""
Ontology Toolkit — инструмент для управления онтологией проекта с опорой на FPF.

Основные компоненты:
- core: Базовые классы (Concept, Ontology, Schema)
- ai: AI-ассистирование (заполнение, извлечение)
- io: Чтение/запись файлов (MD, CSV, XLSX)
- cli: Командная строка
- mcp: Интеграция с Cursor через MCP
"""

__version__ = "0.1.0"
__author__ = "System Career Team"

from ontology_toolkit.core.concept import ConceptFile, ConceptFactory
from ontology_toolkit.core.ontology import Ontology, OntologyIndex
from ontology_toolkit.core.schema import (
    Concept,
    ConceptSchema,
    ConceptStatus,
    MetaMetaType,
    RelationType,
    Relation,
    BaseEntity,
    Method,
    System,
    Problem,
    Artifact,
)

__all__ = [
    # Core classes
    "Concept",
    "ConceptFile",
    "ConceptFactory",
    "Ontology",
    "OntologyIndex",
    "ConceptSchema",
    # Enums
    "ConceptStatus",
    "MetaMetaType",
    "RelationType",
    # Models
    "Relation",
    "BaseEntity",
    "Method",
    "System",
    "Problem",
    "Artifact",
]
