"""
Загрузка и рендеринг промптов.
"""

from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """Загрузчик промптов из template файлов."""

    def __init__(self, templates_dir: Path | None = None):
        """
        Инициализация загрузчика.
        
        Args:
            templates_dir: Путь к директории с шаблонами промптов
        """
        if templates_dir is None:
            # По умолчанию используем prompts_templates в корне ontology_toolkit
            current_file = Path(__file__).resolve()
            self.templates_dir = current_file.parent.parent / "prompts_templates"
        else:
            self.templates_dir = Path(templates_dir)

    def load_concept_fill(self) -> str:
        """
        Загрузить промпт для заполнения понятия.
        
        Returns:
            Текст промпта
        """
        template_path = self.templates_dir / "concept_fill.md"
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")
        
        return template_path.read_text(encoding="utf-8")

    def load_context_extract(self) -> str:
        """
        Загрузить промпт для извлечения контекста.
        
        Returns:
            Текст промпта
        """
        template_path = self.templates_dir / "context_extract.md"
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")
        
        return template_path.read_text(encoding="utf-8")

    @staticmethod
    def render_prompt(template: str, variables: Dict[str, Any]) -> str:
        """
        Отрендерить промпт с подстановкой переменных.
        
        Args:
            template: Шаблон промпта с переменными в формате {variable_name}
            variables: Словарь переменных для подстановки
            
        Returns:
            Отрендеренный промпт
        """
        result = template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result

    def render_concept_fill(
        self,
        concept_name: str,
        additional_context: str = "",
        concepts_data: str = "",
        problems_data: str = "",
        methods_data: str = "",
        systems_data: str = "",
        artifacts_data: str = "",
        context_data: str = ""
    ) -> str:
        """
        Отрендерить промпт для заполнения понятия.
        
        Args:
            concept_name: Название понятия для заполнения
            additional_context: Дополнительный контекст
            concepts_data: Существующие понятия (CSV/табличный формат)
            problems_data: Существующие проблемы
            methods_data: Существующие методы
            systems_data: Существующие системы
            artifacts_data: Существующие артефакты
            context_data: Контекст проекта
            
        Returns:
            Готовый промпт для отправки в AI
        """
        template = self.load_concept_fill()
        
        variables = {
            "concept_name": concept_name,
            "additional_context": additional_context or "Нет",
            "concepts_data": concepts_data or "Пусто",
            "problems_data": problems_data or "Пусто",
            "methods_data": methods_data or "Пусто",
            "systems_data": systems_data or "Пусто",
            "artifacts_data": artifacts_data or "Пусто",
            "context_data": context_data or "Нет",
        }
        
        return self.render_prompt(template, variables)

