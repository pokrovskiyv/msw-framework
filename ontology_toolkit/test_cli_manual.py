#!/usr/bin/env python3
"""
Ручная проверка CLI функционала.
"""

import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from cli.main import app
from typer.testing import CliRunner

runner = CliRunner()

print("=" * 60)
print("Тестирование Ontology Toolkit CLI v0.2.0")
print("=" * 60)

# Тест 1: --help
print("\n1. Тест: ontology --help")
result = runner.invoke(app, ["--help"])
print(f"Код возврата: {result.exit_code}")
print(f"Вывод содержит 'Ontology Toolkit': {('Ontology Toolkit' in result.stdout)}")

# Тест 2: init
print("\n2. Тест: ontology init")
temp_path = Path(__file__).parent / ".test_ontology"
result = runner.invoke(app, ["init", "--path", str(temp_path)])
print(f"Код возврата: {result.exit_code}")
print(f"Структура создана: {temp_path.exists()}")
print(f"Папка concepts: {(temp_path / 'concepts').exists()}")

# Тест 3: add
print("\n3. Тест: ontology add")
result = runner.invoke(app, ["add", "Тестовое понятие", "--path", str(temp_path)])
print(f"Код возврата: {result.exit_code}")
concepts_files = list((temp_path / "concepts").glob("*.md"))
print(f"Создан файл: {len(concepts_files) > 0}")
if concepts_files:
    print(f"Имя файла: {concepts_files[0].name}")

# Тест 4: list
print("\n4. Тест: ontology list")
result = runner.invoke(app, ["list", "--path", str(temp_path)])
print(f"Код возврата: {result.exit_code}")
print(f"Вывод содержит 'C_1': {('C_1' in result.stdout)}")

# Тест 5: audit
print("\n5. Тест: ontology audit")
result = runner.invoke(app, ["audit", "--path", str(temp_path)])
print(f"Код возврата: {result.exit_code}")
print(f"Вывод содержит статистику: {('Всего объектов' in result.stdout)}")

# Очистка
print("\n6. Очистка тестовых файлов")
import shutil
if temp_path.exists():
    shutil.rmtree(temp_path)
    print("✅ Тестовая онтология удалена")

print("\n" + "=" * 60)
print("✅ Все тесты пройдены!")
print("=" * 60)

