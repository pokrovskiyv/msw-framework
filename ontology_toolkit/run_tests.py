"""Скрипт для запуска тестов с правильными путями."""

import sys
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

# Теперь импортируем и запускаем тесты
from ontology_toolkit.tests.test_basic_flow import *

if __name__ == "__main__":
    import tempfile
    
    print("\n" + "="*50)
    print("Тестирование Ontology Toolkit")
    print("="*50 + "\n")
    
    test_concept_creation()
    test_concept_filling()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_concept_save_load(tmp_path)
        test_ontology_index(tmp_path)
        test_full_flow(tmp_path)
    
    print("\n" + "="*50)
    print("✅ Все тесты пройдены!")
    print("="*50 + "\n")
