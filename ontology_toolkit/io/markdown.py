"""
Универсальный MD reader/writer для всех типов сущностей.

Содержит базовый класс для работы с Markdown + YAML frontmatter.
"""

from pathlib import Path
from typing import Optional


class MarkdownIO:
    """Универсальный MD reader/writer."""
    
    @staticmethod
    def read_file(file_path: Path) -> str:
        """
        Прочитать MD файл.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Содержимое файла
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    @staticmethod
    def write_file(file_path: Path, content: str, overwrite: bool = False) -> None:
        """
        Записать MD файл.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое
            overwrite: Перезаписать если существует
        """
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"Файл уже существует: {file_path}")
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

