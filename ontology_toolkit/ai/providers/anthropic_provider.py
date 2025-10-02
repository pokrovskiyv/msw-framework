"""
Anthropic Claude провайдер.
"""

from typing import Optional

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError


class AnthropicProvider(AIProvider):
    """Провайдер для Anthropic Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", temperature: float = 0.3):
        """
        Инициализация Anthropic провайдера.
        
        Args:
            api_key: Anthropic API ключ
            model: Модель Claude (по умолчанию claude-sonnet-4)
            temperature: Температура генерации
        """
        super().__init__(api_key, model, temperature)
        self._client: Optional[object] = None

    def _get_client(self):
        """Ленивая инициализация клиента."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise AIProviderError(
                    "Anthropic библиотека не установлена. "
                    "Установите: pip install anthropic"
                )
        return self._client

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Генерация текста через Claude."""
        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise AIProviderError(f"Anthropic generation failed: {e}")

    def is_available(self) -> bool:
        """Проверка доступности."""
        if not self.api_key:
            return False
        try:
            import anthropic
            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        """Название провайдера."""
        return f"Anthropic Claude ({self.model})"

