"""
Тесты для IO модулей (CSV и XLSX экспорт).
"""

import csv
from pathlib import Path

import pytest
import pandas as pd

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import MetaMetaType, RelationType, ConceptStatus
from ontology_toolkit.io.csv_export import export_concepts_to_csv
from ontology_toolkit.io.xlsx_export import export_to_xlsx


@pytest.fixture
def sample_ontology(tmp_path: Path):
    """Создать тестовую онтологию с несколькими понятиями."""
    onto = Ontology(tmp_path / ".ontology")
    
    # Добавляем понятия
    c1 = onto.add_concept("Агентность")
    c1.definition = "Характеристика личности"
    c1.purpose = "Брать ответственность"
    c1.meta_meta = MetaMetaType.CHARACTERISTIC
    c1.examples = ["Пример 1", "Пример 2"]
    c1.mark_filled()
    
    c2 = onto.add_concept("Стратегирование")
    c2.definition = "Непрерывный процесс"
    c2.purpose = "Переводить неудовлетворённости"
    c2.meta_meta = MetaMetaType.METHOD
    c2.examples = ["Недельная сессия"]
    c2.add_relation("C_1", RelationType.REQUIRES)
    c2.mark_filled()
    
    c3 = onto.add_concept("Личный контракт")
    c3.definition = "Документ со смыслами"
    c3.purpose = "Связывать цели"
    c3.meta_meta = MetaMetaType.ARTIFACT
    c3.add_relation("C_1", RelationType.REQUIRES)
    c3.add_relation("C_2", RelationType.ENABLES)
    c3.approve()
    
    # Сохраняем
    onto.save_concept(c1)
    onto.save_concept(c2)
    onto.save_concept(c3)
    
    return onto


def test_csv_export_basic(sample_ontology: Ontology, tmp_path: Path):
    """Тест базового экспорта в CSV."""
    output_path = tmp_path / "test_export.csv"
    
    count = export_concepts_to_csv(sample_ontology, output_path)
    
    assert count == 3
    assert output_path.exists()
    
    # Проверяем содержимое
    with open(output_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 3
    
    # Проверяем заголовки
    assert "id" in rows[0]
    assert "name" in rows[0]
    assert "definition" in rows[0]
    assert "status" in rows[0]
    
    # Проверяем первую строку
    assert rows[0]["id"] == "C_1"
    assert rows[0]["name"] == "Агентность"
    assert rows[0]["status"] == "draft+filled"


def test_csv_export_with_prefix_filter(sample_ontology: Ontology, tmp_path: Path):
    """Тест экспорта с фильтром по префиксу."""
    output_path = tmp_path / "test_export_filtered.csv"
    
    count = export_concepts_to_csv(sample_ontology, output_path, prefix="C")
    
    assert count == 3
    
    # Все должны быть с префиксом C
    with open(output_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    for row in rows:
        assert row["id"].startswith("C_")


def test_csv_export_with_status_filter(sample_ontology: Ontology, tmp_path: Path):
    """Тест экспорта с фильтром по статусу."""
    output_path = tmp_path / "test_export_approved.csv"
    
    count = export_concepts_to_csv(
        sample_ontology, 
        output_path, 
        status=ConceptStatus.APPROVED
    )
    
    assert count == 1  # Только C_3 approved
    
    with open(output_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 1
    assert rows[0]["status"] == "approved"


def test_csv_export_relations_format(sample_ontology: Ontology, tmp_path: Path):
    """Тест формата связей в CSV."""
    output_path = tmp_path / "test_export_relations.csv"
    
    export_concepts_to_csv(sample_ontology, output_path)
    
    with open(output_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # C_3 имеет 2 связи
    c3_row = [r for r in rows if r["id"] == "C_3"][0]
    relations = c3_row["relations"]
    
    assert "requires:C_1" in relations
    assert "enables:C_2" in relations
    assert ";" in relations  # Разделитель


def test_xlsx_export_basic(sample_ontology: Ontology, tmp_path: Path):
    """Тест базового экспорта в XLSX."""
    output_path = tmp_path / "test_export.xlsx"
    
    stats = export_to_xlsx(sample_ontology, output_path)
    
    assert output_path.exists()
    assert "Concepts" in stats
    assert stats["Concepts"] == 3
    
    # Проверяем содержимое
    df = pd.read_excel(output_path, sheet_name="Concepts")
    
    assert len(df) == 3
    assert "ID" in df.columns
    assert "Название" in df.columns
    assert "Определение" in df.columns
    
    # Проверяем данные
    assert df.iloc[0]["ID"] == "C_1"
    assert df.iloc[0]["Название"] == "Агентность"


def test_xlsx_export_multiple_sheets(sample_ontology: Ontology, tmp_path: Path):
    """Тест экспорта с несколькими вкладками."""
    output_path = tmp_path / "test_export_multi.xlsx"
    
    stats = export_to_xlsx(sample_ontology, output_path)
    
    # Должна быть только вкладка Concepts (у нас только понятия)
    assert len(stats) == 1
    assert "Concepts" in stats
    
    # Проверяем, что файл можно открыть
    xl_file = pd.ExcelFile(output_path)
    assert "Concepts" in xl_file.sheet_names


def test_xlsx_export_with_relations(sample_ontology: Ontology, tmp_path: Path):
    """Тест экспорта связей в XLSX."""
    output_path = tmp_path / "test_export_relations.xlsx"
    
    export_to_xlsx(sample_ontology, output_path)
    
    df = pd.read_excel(output_path, sheet_name="Concepts")
    
    # Проверяем C_3 со связями
    c3_row = df[df["ID"] == "C_3"].iloc[0]
    relations = c3_row["Связи"]
    
    assert isinstance(relations, str)
    assert "requires:C_1" in relations
    assert "enables:C_2" in relations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

