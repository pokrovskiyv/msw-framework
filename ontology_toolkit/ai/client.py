"""
Унифицированный AI клиент.
"""

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError


class AIClient:
    """
    Унифицированный клиент для работы с AI провайдерами.
    
    Предоставляет единый интерфейс с обработкой ошибок.
    """

    def __init__(self, provider: AIProvider):
        """
        Инициализация клиента.
        
        Args:
            provider: AI провайдер
        """
        self.provider = provider

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Сгенерировать текст с обработкой ошибок.
        
        Args:
            prompt: Текст промпта
            max_tokens: Максимальное количество токенов
            
        Returns:
            Сгенерированный текст
            
        Raises:
            AIProviderError: При ошибке генерации
        """
        if not self.is_available():
            raise AIProviderError(
                f"Провайдер {self.provider.name} недоступен. "
                f"Проверьте API ключ и установку библиотеки."
            )
        
        try:
            return self.provider.generate(prompt, max_tokens)
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"Ошибка генерации: {e}")

    def is_available(self) -> bool:
        """
        Проверить доступность провайдера.
        
        Returns:
            True если провайдер доступен
        """
        return self.provider.is_available()

    @property
    def provider_name(self) -> str:
        """Название провайдера."""
        return self.provider.name

    @property
    def model(self) -> str:
        """Название модели."""
        return self.provider.model

    @property
    def temperature(self) -> float:
        """Температура генерации."""
        return self.provider.temperature

