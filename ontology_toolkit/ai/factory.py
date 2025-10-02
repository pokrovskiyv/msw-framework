"""
Фабрика для создания AI провайдеров.
"""

import os
from typing import Dict, Type

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError
from ontology_toolkit.ai.providers import (
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
    GrokProvider,
)


class AIProviderFactory:
    """Фабрика для создания AI провайдеров."""

    # Мапинг названий провайдеров на классы
    PROVIDERS: Dict[str, Type[AIProvider]] = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "grok": GrokProvider,
    }

    # Модели по умолчанию для каждого провайдера
    DEFAULT_MODELS = {
        "anthropic": "claude-sonnet-4-20250514",
        "openai": "gpt-4-turbo",
        "gemini": "gemini-pro",
        "grok": "grok-2-latest",
    }

    # Переменные окружения для API ключей
    ENV_KEY_MAPPING = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "grok": "GROK_API_KEY",
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        model: str | None = None,
        temperature: float = 0.3
    ) -> AIProvider:
        """
        Создать провайдер по имени.
        
        Args:
            provider_name: Название провайдера (anthropic, openai, gemini, grok)
            api_key: API ключ
            model: Модель (если None, используется default)
            temperature: Температура генерации
            
        Returns:
            Экземпляр провайдера
            
        Raises:
            AIProviderError: Если провайдер неизвестен
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls.PROVIDERS:
            available = ", ".join(cls.PROVIDERS.keys())
            raise AIProviderError(
                f"Неизвестный провайдер: {provider_name}. "
                f"Доступные: {available}"
            )
        
        provider_class = cls.PROVIDERS[provider_name]
        model = model or cls.DEFAULT_MODELS[provider_name]
        
        return provider_class(api_key=api_key, model=model, temperature=temperature)

    @classmethod
    def from_env(cls) -> AIProvider:
        """
        Создать провайдер из переменных окружения.
        
        Использует:
        - ONTOLOGY_AI_PROVIDER — название провайдера (default: anthropic)
        - {PROVIDER}_API_KEY — API ключ (напр., ANTHROPIC_API_KEY)
        - ONTOLOGY_AI_MODEL — модель (опционально)
        - ONTOLOGY_AI_TEMPERATURE — температура (default: 0.3)
        
        Returns:
            Экземпляр провайдера
            
        Raises:
            AIProviderError: Если API ключ не найден
        """
        provider_name = os.getenv("ONTOLOGY_AI_PROVIDER", "anthropic").lower()
        
        # Получаем API ключ
        env_key_name = cls.ENV_KEY_MAPPING.get(provider_name)
        if not env_key_name:
            raise AIProviderError(f"Неизвестный провайдер: {provider_name}")
        
        api_key = os.getenv(env_key_name)
        if not api_key:
            raise AIProviderError(
                f"API ключ не найден. Установите переменную окружения: {env_key_name}\n"
                f"Например: export {env_key_name}=sk-..."
            )
        
        # Получаем модель и температуру
        model = os.getenv("ONTOLOGY_AI_MODEL")
        temperature = float(os.getenv("ONTOLOGY_AI_TEMPERATURE", "0.3"))
        
        return cls.create(provider_name, api_key, model, temperature)

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """
        Получить список доступных провайдеров с моделями по умолчанию.
        
        Returns:
            Dict с названиями провайдеров и их default моделями
        """
        return {
            name: cls.DEFAULT_MODELS[name]
            for name in cls.PROVIDERS.keys()
        }

    @classmethod
    def check_provider_available(cls, provider_name: str) -> tuple[bool, str]:
        """
        Проверить, доступен ли провайдер.
        
        Args:
            provider_name: Название провайдера
            
        Returns:
            (доступен, сообщение)
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls.PROVIDERS:
            return False, f"Неизвестный провайдер: {provider_name}"
        
        # Проверяем наличие API ключа
        env_key_name = cls.ENV_KEY_MAPPING[provider_name]
        api_key = os.getenv(env_key_name)
        
        if not api_key:
            return False, f"API ключ не найден: {env_key_name}"
        
        # Пытаемся создать провайдер
        try:
            provider = cls.create(provider_name, api_key)
            if not provider.is_available():
                return False, "Библиотека провайдера не установлена"
            return True, "Доступен"
        except Exception as e:
            return False, str(e)

