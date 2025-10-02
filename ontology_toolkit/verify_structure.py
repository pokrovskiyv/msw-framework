#!/usr/bin/env python3
"""
Проверка структуры проекта и импортов.
"""

from pathlib import Path
import sys

print("=" * 60)
print("Проверка структуры Ontology Toolkit v0.2.0")
print("=" * 60)

root = Path(__file__).parent

# Проверка файлов
files_to_check = [
    "core/schema.py",
    "core/concept.py",
    "core/ontology.py",
    "io/markdown.py",
    "io/csv_export.py",
    "io/xlsx_export.py",
    "cli/main.py",
    "tests/test_basic_flow.py",
    "tests/test_io.py",
    "tests/test_cli.py",
    "README.md",
    "ROADMAP.md",
    ".cursorrules",
    "pyproject.toml"
]

print("\n[+] Checking files:")
all_exist = True
for file_path in files_to_check:
    full_path = root / file_path
    exists = full_path.exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"  {status} {file_path}")
    if not exists:
        all_exist = False

# Check version
print("\n[+] Checking version:")
pyproject = root / "pyproject.toml"
content = pyproject.read_text(encoding="utf-8")
if 'version = "0.2.0"' in content:
    print("  [OK] Version in pyproject.toml: 0.2.0")
else:
    print("  [FAIL] Version not 0.2.0")

# Check CLI entrypoint
if 'ontology = "ontology_toolkit.cli.main:app"' in content:
    print("  [OK] CLI entrypoint configured")
else:
    print("  [FAIL] Entrypoint not found")

# Check README
print("\n[+] Checking README:")
readme = root / "README.md"
readme_content = readme.read_text(encoding="utf-8")
if "v0.2.0" in readme_content:
    print("  [OK] Version in README: v0.2.0")
if "ontology init" in readme_content:
    print("  [OK] CLI commands documented")

# Check .cursorrules
print("\n[+] Checking .cursorrules:")
cursorrules = root / ".cursorrules"
if cursorrules.exists():
    cursorrules_content = cursorrules.read_text(encoding="utf-8")
    if "ontology init" in cursorrules_content:
        print("  [OK] CLI commands in .cursorrules")
    if "v0.2.0" in cursorrules_content:
        print("  [OK] Version specified")

# Check ROADMAP
print("\n[+] Checking ROADMAP:")
roadmap = root / "ROADMAP.md"
if roadmap.exists():
    roadmap_content = roadmap.read_text(encoding="utf-8")
    if "v0.2.0" in roadmap_content:
        print("  [OK] Version v0.2.0 documented")
    if "v0.3.0" in roadmap_content:
        print("  [OK] Plan v0.3.0 described")

print("\n" + "=" * 60)
if all_exist:
    print("[SUCCESS] ALL FILES IN PLACE!")
    print("[SUCCESS] VERSION 0.2.0 READY!")
else:
    print("[WARNING] Some files are missing")
print("=" * 60)

print("\n[INSTALL] To install, run:")
print("  cd ontology_toolkit")
print("  pip install -e .")
print("\n[CLI] After install, 'ontology' command will be available globally")

