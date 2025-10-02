"""
Тесты для AI модуля.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError
from ontology_toolkit.ai.factory import AIProviderFactory
from ontology_toolkit.ai.client import AIClient
from ontology_toolkit.ai.prompts import PromptLoader
from ontology_toolkit.core.schema import Concept, ConceptStatus


class MockProvider(AIProvider):
    """Mock провайдер для тестов."""
    
    def __init__(self, api_key: str, model: str = "mock-model", temperature: float = 0.3):
        super().__init__(api_key, model, temperature)
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Mock генерация."""
        return "| name | definition | purpose | meta_meta | examples |\n|------|-----------|---------|-----------|----------|\n| Тест | Тестовое определение | Тестовое назначение | характеристика | Пример 1; Пример 2 |"
    
    def is_available(self) -> bool:
        """Mock доступность."""
        return bool(self.api_key)
    
    @property
    def name(self) -> str:
        """Mock название."""
        return f"Mock Provider ({self.model})"


class TestAIProviderFactory:
    """Тесты фабрики провайдеров."""
    
    def test_list_providers(self):
        """Тест списка провайдеров."""
        providers = AIProviderFactory.list_providers()
        assert "anthropic" in providers
        assert "openai" in providers
        assert "gemini" in providers
        assert "grok" in providers
    
    def test_create_anthropic(self):
        """Тест создания Anthropic провайдера."""
        provider = AIProviderFactory.create("anthropic", "test-key", "claude-sonnet-4-20250514")
        assert provider.api_key == "test-key"
        assert provider.model == "claude-sonnet-4-20250514"
        assert "Anthropic" in provider.name
    
    def test_create_unknown_provider(self):
        """Тест создания неизвестного провайдера."""
        with pytest.raises(AIProviderError):
            AIProviderFactory.create("unknown", "test-key")
    
    def test_from_env_no_key(self):
        """Тест from_env без API ключа."""
        # Очищаем переменные окружения
        for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GROK_API_KEY"]:
            os.environ.pop(key, None)
        
        with pytest.raises(AIProviderError, match="API ключ не найден"):
            AIProviderFactory.from_env()
    
    def test_from_env_with_key(self):
        """Тест from_env с API ключом."""
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        try:
            provider = AIProviderFactory.from_env()
            assert provider.api_key == "test-key"
        finally:
            os.environ.pop("ANTHROPIC_API_KEY", None)
    
    def test_check_provider_available(self):
        """Тест проверки доступности провайдера."""
        # Без ключа
        available, message = AIProviderFactory.check_provider_available("anthropic")
        assert not available
        assert "API ключ не найден" in message


class TestAIClient:
    """Тесты AI клиента."""
    
    def test_client_initialization(self):
        """Тест инициализации клиента."""
        provider = MockProvider("test-key")
        client = AIClient(provider)
        assert client.provider == provider
        assert client.provider_name == "Mock Provider (mock-model)"
    
    def test_client_generate(self):
        """Тест генерации через клиент."""
        provider = MockProvider("test-key")
        client = AIClient(provider)
        response = client.generate("test prompt")
        assert "name" in response
        assert "definition" in response
    
    def test_client_unavailable(self):
        """Тест недоступного провайдера."""
        provider = MockProvider("")  # Пустой ключ
        client = AIClient(provider)
        with pytest.raises(AIProviderError, match="недоступен"):
            client.generate("test")


class TestPromptLoader:
    """Тесты загрузчика промптов."""
    
    def test_render_prompt(self):
        """Тест рендеринга промпта."""
        template = "Hello {name}, your {item}!"
        variables = {"name": "World", "item": "test"}
        result = PromptLoader.render_prompt(template, variables)
        assert result == "Hello World, your test!"
    
    def test_render_concept_fill(self, tmp_path):
        """Тест рендеринга промпта для заполнения понятия."""
        # Создаём временные промпты
        templates_dir = tmp_path / "prompts_templates"
        templates_dir.mkdir()
        
        concept_fill = templates_dir / "concept_fill.md"
        concept_fill.write_text("Concept: {concept_name}\nContext: {additional_context}", encoding="utf-8")
        
        loader = PromptLoader(templates_dir)
        result = loader.render_concept_fill("Агентность", "Тестовый контекст")
        
        assert "Агентность" in result
        assert "Тестовый контекст" in result


class TestConceptFiller:
    """Тесты автозаполнения понятий."""
    
    def test_parse_ai_response(self, tmp_path):
        """Тест парсинга ответа AI."""
        from ontology_toolkit.ai.filler import ConceptFiller
        from ontology_toolkit.core.ontology import Ontology
        
        # Создаём временную онтологию
        onto_path = tmp_path / ".ontology"
        onto_path.mkdir()
        (onto_path / "concepts").mkdir()
        
        ontology = Ontology(onto_path)
        provider = MockProvider("test-key")
        client = AIClient(provider)
        filler = ConceptFiller(client, ontology)
        
        # Тестовый ответ AI
        response = """
| name | definition | purpose | meta_meta | examples |
|------|-----------|---------|-----------|----------|
| Агентность | Способность действовать | Для развития | характеристика | Пример 1; Пример 2 |
"""
        
        parsed = filler._parse_ai_response(response)
        assert "definition" in parsed
        assert "purpose" in parsed
        assert parsed["definition"] == "Способность действовать"


class TestConceptExtractor:
    """Тесты извлечения понятий."""
    
    def test_extract_from_text(self, tmp_path):
        """Тест извлечения из текста."""
        from ontology_toolkit.ai.extractor import ConceptExtractor
        from ontology_toolkit.core.ontology import Ontology
        
        # Создаём временную онтологию
        onto_path = tmp_path / ".ontology"
        onto_path.mkdir()
        (onto_path / "concepts").mkdir()
        
        ontology = Ontology(onto_path)
        provider = MockProvider("test-key")
        client = AIClient(provider)
        extractor = ConceptExtractor(client, ontology)
        
        # Mock генерация
        with patch.object(provider, 'generate', return_value="""
| name | definition | purpose | meta_meta | examples |
|------|-----------|---------|-----------|----------|
| Понятие 1 | Определение 1 | Назначение 1 | характеристика | Пример 1 |
| Понятие 2 | Определение 2 | Назначение 2 | метод | Пример 2 |
"""):
            concepts = extractor.extract_from_text("Тестовый текст")
        
        assert len(concepts) == 2
        assert concepts[0].name == "Понятие 1"
        assert concepts[1].name == "Понятие 2"


@pytest.mark.skipif(
    os.getenv("ANTHROPIC_API_KEY") is None,
    reason="Требуется ANTHROPIC_API_KEY для интеграционных тестов"
)
class TestIntegrationAnthropic:
    """Интеграционные тесты с реальным Anthropic API."""
    
    def test_real_anthropic_generation(self):
        """Тест реальной генерации через Anthropic."""
        provider = AIProviderFactory.from_env()
        client = AIClient(provider)
        
        response = client.generate("Say 'test' and nothing else")
        assert response
        assert len(response) > 0

