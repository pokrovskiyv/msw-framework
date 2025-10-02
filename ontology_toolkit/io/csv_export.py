"""
Экспорт онтологии в CSV формат.

Поддерживает фильтрацию по префиксу и статусу.
"""

import csv
from pathlib import Path
from typing import Optional, List

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import ConceptStatus


def export_concepts_to_csv(
    ontology: Ontology,
    output_path: Path,
    prefix: Optional[str] = None,
    status: Optional[ConceptStatus] = None
) -> int:
    """
    Экспортировать понятия в CSV файл.
    
    Args:
        ontology: Онтология для экспорта
        output_path: Путь к выходному CSV файлу
        prefix: Фильтр по префиксу (C, M, S, P, A) или None для всех
        status: Фильтр по статусу или None для всех
        
    Returns:
        Количество экспортированных объектов
    """
    # Получаем объекты для экспорта
    entities = []
    
    if prefix:
        entities = ontology.index.by_prefix.get(prefix, [])
    else:
        # Все объекты
        entities = list(ontology.index.by_id.values())
    
    # Фильтр по статусу (только для Concept)
    if status:
        entities = [e for e in entities if hasattr(e, 'status') and e.status == status]
    
    # Экспорт в CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        
        # Заголовки
        writer.writerow([
            "id", "name", "definition", "purpose", "status", "meta_meta",
            "examples", "relations", "created", "updated"
        ])
        
        # Данные
        for entity in entities:
            # Examples через точку с запятой
            examples_str = "; ".join(entity.examples) if entity.examples else ""
            
            # Relations через точку с запятой
            relations_str = "; ".join(
                [f"{r.type.value}:{r.target}" for r in entity.relations]
            ) if entity.relations else ""
            
            # Status и meta_meta только для Concept
            status_str = entity.status.value if hasattr(entity, 'status') else ""
            meta_meta_str = entity.meta_meta.value if hasattr(entity, 'meta_meta') and entity.meta_meta else ""
            
            writer.writerow([
                entity.id,
                entity.name,
                entity.definition,
                entity.purpose,
                status_str,
                meta_meta_str,
                examples_str,
                relations_str,
                entity.created.isoformat() if entity.created else "",
                entity.updated.isoformat() if entity.updated else ""
            ])
    
    return len(entities)


class CSVExporter:
    """Класс для экспорта в CSV (альтернативный интерфейс)."""
    
    def __init__(self, ontology: Ontology):
        """
        Инициализация экспортёра.
        
        Args:
            ontology: Онтология для экспорта
        """
        self.ontology = ontology
    
    def export(
        self,
        output_path: Path,
        prefix: Optional[str] = None,
        status: Optional[ConceptStatus] = None
    ) -> int:
        """
        Экспортировать в CSV.
        
        Args:
            output_path: Путь к выходному файлу
            prefix: Фильтр по префиксу
            status: Фильтр по статусу
            
        Returns:
            Количество экспортированных объектов
        """
        return export_concepts_to_csv(self.ontology, output_path, prefix, status)

