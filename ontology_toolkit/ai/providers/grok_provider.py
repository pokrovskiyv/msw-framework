"""
xAI Grok провайдер.
"""

from typing import Optional

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError


class GrokProvider(AIProvider):
    """Провайдер для xAI Grok API."""

    def __init__(self, api_key: str, model: str = "grok-2-latest", temperature: float = 0.3):
        """
        Инициализация Grok провайдера.
        
        Args:
            api_key: xAI API ключ
            model: Модель Grok (по умолчанию grok-2-latest)
            temperature: Температура генерации
        """
        super().__init__(api_key, model, temperature)
        self._client: Optional[object] = None

    def _get_client(self):
        """Ленивая инициализация клиента."""
        if self._client is None:
            try:
                import openai
                # Grok использует OpenAI-совместимый API
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.x.ai/v1"
                )
            except ImportError:
                raise AIProviderError(
                    "OpenAI библиотека не установлена (нужна для Grok). "
                    "Установите: pip install ontology-toolkit[ai-grok]"
                )
        return self._client

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Генерация текста через Grok."""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise AIProviderError(f"Grok generation failed: {e}")

    def is_available(self) -> bool:
        """Проверка доступности."""
        if not self.api_key:
            return False
        try:
            import openai
            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        """Название провайдера."""
        return f"xAI Grok ({self.model})"

