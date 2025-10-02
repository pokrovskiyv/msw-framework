"""
OpenAI ChatGPT провайдер.
"""

from typing import Optional

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError


class OpenAIProvider(AIProvider):
    """Провайдер для OpenAI API (ChatGPT)."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo", temperature: float = 0.3):
        """
        Инициализация OpenAI провайдера.
        
        Args:
            api_key: OpenAI API ключ
            model: Модель GPT (по умолчанию gpt-4-turbo)
            temperature: Температура генерации
        """
        super().__init__(api_key, model, temperature)
        self._client: Optional[object] = None

    def _get_client(self):
        """Ленивая инициализация клиента."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise AIProviderError(
                    "OpenAI библиотека не установлена. "
                    "Установите: pip install ontology-toolkit[ai-openai]"
                )
        return self._client

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Генерация текста через ChatGPT."""
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
            raise AIProviderError(f"OpenAI generation failed: {e}")

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
        return f"OpenAI ({self.model})"

