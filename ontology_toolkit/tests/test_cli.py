"""
Тесты для CLI команд.
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ontology_toolkit.cli.main import app

runner = CliRunner()


def test_cli_help():
    """Тест команды --help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Ontology Toolkit" in result.stdout


def test_init_command(tmp_path: Path):
    """Тест команды init."""
    ontology_path = tmp_path / ".ontology"
    
    result = runner.invoke(app, [
        "init",
        "--project", "Test Project",
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 0
    assert "OK" in result.stdout
    
    # Проверяем структуру
    assert ontology_path.exists()
    assert (ontology_path / "concepts").exists()
    assert (ontology_path / "methods").exists()
    assert (ontology_path / "systems").exists()
    assert (ontology_path / "problems").exists()
    assert (ontology_path / "artifacts").exists()
    assert (ontology_path / "README.md").exists()


def test_add_command(tmp_path: Path):
    """Тест команды add."""
    ontology_path = tmp_path / ".ontology"
    
    # Сначала инициализируем
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    
    # Добавляем понятие
    result = runner.invoke(app, [
        "add",
        "Тестовое понятие",
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 0
    assert "C_1" in result.stdout
    assert "draft" in result.stdout.lower()
    
    # Проверяем, что файл создан
    concepts_dir = ontology_path / "concepts"
    files = list(concepts_dir.glob("*.md"))
    assert len(files) == 1


def test_add_command_method(tmp_path: Path):
    """Проверяем команду add для типа method."""
    ontology_path = tmp_path / ".ontology"

    runner.invoke(app, ["init", "--path", str(ontology_path)])

    result = runner.invoke(
        app,
        [
            "add",
            "Test Method",
            "--type",
            "method",
            "--path",
            str(ontology_path),
        ],
    )

    assert result.exit_code == 0
    assert "M_1" in result.stdout
    assert "Test Method" in result.stdout

    methods_dir = ontology_path / "methods"
    files = list(methods_dir.glob("*.md"))
    assert len(files) == 1


def test_add_command_without_init(tmp_path: Path):
    """Тест команды add без инициализации (должен вернуть ошибку)."""
    ontology_path = tmp_path / ".ontology"
    
    result = runner.invoke(app, [
        "add",
        "Тестовое понятие",
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 1
    assert "ERROR" in result.stdout


def test_list_command_empty(tmp_path: Path):
    """Тест команды list на пустой онтологии."""
    ontology_path = tmp_path / ".ontology"
    
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    
    result = runner.invoke(app, ["list", "--path", str(ontology_path)])
    
    assert result.exit_code == 0
    assert "не найдено" in result.stdout.lower()


def test_list_command_with_concepts(tmp_path: Path):
    """Тест команды list с понятиями."""
    ontology_path = tmp_path / ".ontology"
    
    # Инициализируем и добавляем понятия
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 1", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 2", "--path", str(ontology_path)])
    
    result = runner.invoke(app, ["list", "--path", str(ontology_path)])
    
    assert result.exit_code == 0
    assert "C_1" in result.stdout
    assert "C_2" in result.stdout
    assert "Понятие 1" in result.stdout
    assert "Понятие 2" in result.stdout
    assert "concept" in result.stdout.lower()


def test_list_command_with_status_filter(tmp_path: Path):
    """Тест команды list с фильтром по статусу."""
    ontology_path = tmp_path / ".ontology"
    
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 1", "--path", str(ontology_path)])
    
    result = runner.invoke(app, [
        "list",
        "--status", "draft",
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 0
    assert "C_1" in result.stdout




def test_list_command_with_type_filter(tmp_path: Path):
    """????????? ?????????? ?????? ?? ???? ????????."""
    ontology_path = tmp_path / ".ontology"

    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Concept One", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Method One", "--type", "method", "--path", str(ontology_path)])

    result = runner.invoke(app, ["list", "--prefix", "method", "--path", str(ontology_path)])

    assert result.exit_code == 0
    assert "M_1" in result.stdout
    assert "C_1" not in result.stdout


def test_audit_command(tmp_path: Path):
    """Тест команды audit."""
    ontology_path = tmp_path / ".ontology"
    
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 1", "--path", str(ontology_path)])
    
    result = runner.invoke(app, ["audit", "--path", str(ontology_path)])
    
    assert result.exit_code == 0
    assert "Всего объектов" in result.stdout
    assert "1" in result.stdout


def test_export_csv_command(tmp_path: Path):
    """Тест команды export в CSV."""
    ontology_path = tmp_path / ".ontology"
    output_file = tmp_path / "export.csv"
    
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 1", "--path", str(ontology_path)])
    
    result = runner.invoke(app, [
        "export",
        "--format", "csv",
        "--output", str(output_file),
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 0
    assert "OK" in result.stdout
    assert output_file.exists()


def test_export_xlsx_command(tmp_path: Path):
    """Тест команды export в XLSX."""
    ontology_path = tmp_path / ".ontology"
    output_file = tmp_path / "export.xlsx"
    
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 1", "--path", str(ontology_path)])
    
    result = runner.invoke(app, [
        "export",
        "--format", "xlsx",
        "--output", str(output_file),
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 0
    assert "OK" in result.stdout
    assert output_file.exists()


def test_graph_command(tmp_path: Path):
    """Тест команды graph."""
    ontology_path = tmp_path / ".ontology"
    output_file = tmp_path / "graph.mmd"
    
    runner.invoke(app, ["init", "--path", str(ontology_path)])
    runner.invoke(app, ["add", "Понятие 1", "--path", str(ontology_path)])
    
    result = runner.invoke(app, [
        "graph",
        "--output", str(output_file),
        "--path", str(ontology_path)
    ])
    
    assert result.exit_code == 0
    assert "OK" in result.stdout
    assert output_file.exists()
    
    # Проверяем содержимое
    content = output_file.read_text(encoding="utf-8")
    assert "graph TD" in content
    assert "C_1" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

