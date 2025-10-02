"""
Google Gemini провайдер.
"""

from typing import Optional

from ontology_toolkit.ai.base_provider import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    """Провайдер для Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-pro", temperature: float = 0.3):
        """
        Инициализация Gemini провайдера.
        
        Args:
            api_key: Google API ключ
            model: Модель Gemini (по умолчанию gemini-pro)
            temperature: Температура генерации
        """
        super().__init__(api_key, model, temperature)
        self._model: Optional[object] = None
        self._model_name = model

    def _get_model(self):
        """Ленивая инициализация модели."""
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self._model_name)
            except ImportError:
                raise AIProviderError(
                    "Google Generative AI библиотека не установлена. "
                    "Установите: pip install ontology-toolkit[ai-gemini]"
                )
        return self._model

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Генерация текста через Gemini."""
        try:
            model = self._get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": self.temperature
                }
            )
            return response.text
        except Exception as e:
            raise AIProviderError(f"Gemini generation failed: {e}")

    def is_available(self) -> bool:
        """Проверка доступности."""
        if not self.api_key:
            return False
        try:
            import google.generativeai
            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        """Название провайдера."""
        return f"Google Gemini ({self._model_name})"

