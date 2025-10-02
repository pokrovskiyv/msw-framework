"""
Экспорт онтологии в XLSX формат (Excel).

Создаёт отдельные вкладки для каждого типа объектов.
"""

from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import BaseEntity


def export_to_xlsx(ontology: Ontology, output_path: Path) -> Dict[str, int]:
    """
    Экспортировать онтологию в XLSX файл с вкладками.
    
    Args:
        ontology: Онтология для экспорта
        output_path: Путь к выходному XLSX файлу
        
    Returns:
        Словарь {имя_вкладки: количество_строк}
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Создаём Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        stats = {}
        
        # Экспортируем каждый тип объектов на отдельную вкладку
        prefixes = {
            "C": "Concepts",
            "M": "Methods",
            "S": "Systems",
            "P": "Problems",
            "A": "Artifacts"
        }
        
        for prefix, sheet_name in prefixes.items():
            entities = ontology.index.by_prefix.get(prefix, [])
            
            if not entities:
                continue
            
            # Конвертируем в DataFrame
            data = _entities_to_dict_list(entities)
            df = pd.DataFrame(data)
            
            # Экспортируем на вкладку
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Форматирование
            worksheet = writer.sheets[sheet_name]
            _format_worksheet(worksheet, df)
            
            stats[sheet_name] = len(entities)
    
    return stats


def _entities_to_dict_list(entities: List[BaseEntity]) -> List[Dict[str, Any]]:
    """
    Конвертировать список сущностей в список словарей для DataFrame.
    
    Args:
        entities: Список сущностей
        
    Returns:
        Список словарей
    """
    result = []
    
    for entity in entities:
        row = {
            "ID": entity.id,
            "Название": entity.name,
            "Определение": entity.definition,
            "Назначение": entity.purpose,
            "Примеры": "; ".join(entity.examples) if entity.examples else "",
            "Связи": "; ".join(
                [f"{r.type.value}:{r.target}" for r in entity.relations]
            ) if entity.relations else "",
            "Создано": entity.created.isoformat() if entity.created else "",
            "Обновлено": entity.updated.isoformat() if entity.updated else ""
        }
        
        # Дополнительные поля для Concept
        if hasattr(entity, 'status'):
            row["Статус"] = entity.status.value
        
        if hasattr(entity, 'meta_meta') and entity.meta_meta:
            row["Тип"] = entity.meta_meta.value
        
        # Дополнительные поля для других типов
        if hasattr(entity, 'steps') and entity.steps:
            row["Шаги"] = "; ".join(entity.steps)
        
        if hasattr(entity, 'components') and entity.components:
            row["Компоненты"] = "; ".join(entity.components)
        
        if hasattr(entity, 'current_state'):
            row["Текущее состояние"] = entity.current_state or ""
        
        if hasattr(entity, 'desired_state'):
            row["Желаемое состояние"] = entity.desired_state or ""
        
        result.append(row)
    
    return result


def _format_worksheet(worksheet, df: pd.DataFrame) -> None:
    """
    Форматировать worksheet (жирные заголовки, автоширина).
    
    Args:
        worksheet: Worksheet объект openpyxl
        df: DataFrame для определения ширины столбцов
    """
    from openpyxl.styles import Font
    
    # Жирные заголовки
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
    
    # Автоширина столбцов
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        
        # Ограничиваем максимальную ширину
        adjusted_width = min(max_length + 2, 50)
        worksheet.column_dimensions[column_letter].width = adjusted_width


class XLSXExporter:
    """Класс для экспорта в XLSX (альтернативный интерфейс)."""
    
    def __init__(self, ontology: Ontology):
        """
        Инициализация экспортёра.
        
        Args:
            ontology: Онтология для экспорта
        """
        self.ontology = ontology
    
    def export(self, output_path: Path) -> Dict[str, int]:
        """
        Экспортировать в XLSX.
        
        Args:
            output_path: Путь к выходному файлу
            
        Returns:
            Словарь со статистикой экспорта
        """
        return export_to_xlsx(self.ontology, output_path)

