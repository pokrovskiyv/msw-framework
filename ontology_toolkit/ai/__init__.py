"""
AI модуль для автоматизации работы с онтологией.

Предоставляет:
- Универсальный интерфейс для разных AI провайдеров (Anthropic, OpenAI, Gemini, Grok)
- Автозаполнение понятий через AI
- Извлечение понятий из текста
"""

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError
from ontology_toolkit.ai.client import AIClient
from ontology_toolkit.ai.factory import AIProviderFactory
from ontology_toolkit.ai.prompts import PromptLoader
from ontology_toolkit.ai.filler import ConceptFiller
from ontology_toolkit.ai.extractor import ConceptExtractor

__all__ = [
    "AIProvider",
    "AIProviderError",
    "AIClient",
    "AIProviderFactory",
    "PromptLoader",
    "ConceptFiller",
    "ConceptExtractor",
]
