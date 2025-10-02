"""
Базовый интерфейс для AI провайдеров.

Определяет общий контракт, который должны реализовать все провайдеры.
"""

from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """Абстрактный базовый класс для всех AI провайдеров."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.3):
        """
        Инициализация провайдера.
        
        Args:
            api_key: API ключ
            model: Название модели
            temperature: Температура генерации (0.0-1.0)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Сгенерировать текст на основе промпта.
        
        Args:
            prompt: Текст промпта
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            Сгенерированный текст
            
        Raises:
            AIProviderError: При ошибке генерации
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Проверить доступность провайдера.
        
        Returns:
            True если провайдер доступен (есть API ключ и библиотека)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Человеко-читаемое название провайдера.
        
        Returns:
            Название в формате "Provider (model)"
        """
        pass


class AIProviderError(Exception):
    """Ошибка работы с AI провайдером."""
    pass

