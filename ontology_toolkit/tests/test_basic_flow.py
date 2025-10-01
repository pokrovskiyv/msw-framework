"""
Простой тест для проверки базового flow библиотеки.

Демонстрирует:
1. Создание понятия
2. Заполнение полей
3. Сохранение в MD
4. Загрузка из MD
5. Индексация
"""

from pathlib import Path
from datetime import datetime

from ontology_toolkit.core.schema import (
    Concept,
    ConceptStatus,
    MetaMetaType,
    RelationType,
)
from ontology_toolkit.core.concept import ConceptFile, ConceptFactory
from ontology_toolkit.core.ontology import Ontology


def test_concept_creation():
    """Тест создания понятия."""
    # Создаём черновик
    concept = ConceptFactory.create_draft("Агентность", "C_1")
    
    assert concept.id == "C_1"
    assert concept.name == "Агентность"
    assert concept.status == ConceptStatus.DRAFT
    print("✅ Создание черновика работает")


def test_concept_filling():
    """Тест заполнения понятия."""
    concept = ConceptFactory.create_filled(
        name="Стратегирование",
        definition="Непрерывный процесс работы с неудовлетворённостями",
        purpose="Переводить неудовлетворённости в проекты и гипотезы",
        meta_meta=MetaMetaType.METHOD,
        examples=[
            "Недельная сессия стратегирования",
            "Анализ неудовлетворённостей"
        ],
        concept_id="C_2"
    )
    
    assert concept.status == ConceptStatus.DRAFT_FILLED
    assert concept.meta_meta == MetaMetaType.METHOD
    assert len(concept.examples) == 2
    print("✅ Заполнение понятия работает")


def test_concept_save_load(tmp_path: Path):
    """Тест сохранения и загрузки MD файла."""
    # Создаём понятие
    concept = ConceptFactory.create_filled(
        name="Личный контракт",
        definition="Документ, который переводит личные смыслы в конкретные действия",
        purpose="Связывает долгосрочные цели с недельными задачами",
        meta_meta=MetaMetaType.ARTIFACT,
        examples=[
            "Контракт v1.0 с эпиками",
            "Недельный план со слотами"
        ],
        concept_id="C_3"
    )
    
    # Добавляем связи
    concept.add_relation("C_1", RelationType.REQUIRES)
    concept.add_relation("C_2", RelationType.ENABLES)
    
    # Сохраняем
    concept_file = ConceptFile(concept)
    file_path = concept_file.save(tmp_path, overwrite=True)
    
    assert file_path.exists()
    print(f"✅ Сохранение в файл: {file_path.name}")
    
    # Загружаем
    loaded_file = ConceptFile.from_file(file_path)
    loaded_concept = loaded_file.concept
    
    assert loaded_concept.id == concept.id
    assert loaded_concept.name == concept.name
    assert loaded_concept.definition == concept.definition
    assert len(loaded_concept.relations) == 2
    print("✅ Загрузка из файла работает")


def test_ontology_index(tmp_path: Path):
    """Тест индексации онтологии."""
    onto = Ontology(tmp_path / ".ontology")
    
    # Добавляем несколько понятий
    c1 = onto.add_concept("Агентность")
    c2 = onto.add_concept("Стратегирование")
    c3 = onto.add_concept("Личный контракт")
    
    assert c1.id == "C_1"
    assert c2.id == "C_2"
    assert c3.id == "C_3"
    
    # Проверяем индекс
    assert onto.index.get("C_1") == c1
    assert len(onto.index.by_prefix["C"]) == 3
    
    # Поиск по имени
    found = onto.index.find_by_name("Агентность")
    assert len(found) == 1
    assert found[0].id == "C_1"
    
    print("✅ Индексация работает")


def test_full_flow(tmp_path: Path):
    """Полный цикл: создание → сохранение → загрузка → аудит."""
    onto = Ontology(tmp_path / ".ontology")
    
    # 1. Создаём понятия
    c1 = onto.add_concept("Агентность")
    c1.definition = "Способность активно действовать"
    c1.purpose = "Брать ответственность за развитие"
    c1.meta_meta = MetaMetaType.CHARACTERISTIC
    c1.mark_filled()
    
    c2 = onto.add_concept("Личный контракт")
    c2.definition = "Документ со смыслами и планами"
    c2.purpose = "Связывать цели с действиями"
    c2.meta_meta = MetaMetaType.ARTIFACT
    c2.add_relation("C_1", RelationType.REQUIRES)
    c2.mark_filled()
    
    # 2. Сохраняем
    onto.save_concept(c1)
    onto.save_concept(c2)
    
    # 3. Загружаем заново
    onto2 = Ontology(tmp_path / ".ontology")
    onto2.load_all()
    
    # 4. Проверяем
    assert len(onto2.index.by_id) == 2
    
    loaded_c2 = onto2.get_concept("C_2")
    assert loaded_c2 is not None
    assert len(loaded_c2.relations) == 1
    
    # 5. Аудит
    audit = onto2.audit()
    assert audit["total_objects"] == 2
    assert audit["by_prefix"]["C"] == 2
    assert audit["by_status"]["draft+filled"] == 2
    assert audit["broken_links"] == 0
    
    print("✅ Полный цикл работает")
    onto2.print_audit()


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
