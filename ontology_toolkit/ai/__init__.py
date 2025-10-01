"""AI-модуль: заполнение полей, извлечение понятий, работа с промптами."""

from ontology_toolkit.ai.filler import ConceptFiller
from ontology_toolkit.ai.extractor import ConceptExtractor
from ontology_toolkit.ai.prompts import PromptManager

__all__ = ["ConceptFiller", "ConceptExtractor", "PromptManager"]
