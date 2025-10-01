#!/usr/bin/env python3
"""
Простой пример добавления понятия "Карьерный концепт"
"""

from pathlib import Path
from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import MetaMetaType, RelationType

print("🚀 Добавляем понятие 'Карьерный концепт'\n")

# 1. Открываем онтологию
onto_path = Path(__file__).parent / ".ontology_demo"
onto = Ontology(onto_path)
onto.load_all()

print(f"📂 Онтология: {onto_path}")
print(f"   Текущих понятий: {len(onto.index.by_id)}\n")

# 2. Создаём понятие
concept = onto.add_concept("Карьерный концепт")

# 3. Заполняем поля
concept.definition = """Карьерный концепт — это мысленная модель желаемой карьерной траектории, \
включающая представление о целевых ролях, необходимом мастерстве, системных уровнях влияния \
и способах создания ценности. Это не жёсткий план, а визион и набор ориентиров, которые \
направляют стратегирование и выбор приоритетных проектов."""

concept.purpose = """Обеспечивает стратегическую ясность и направление для карьерного развития. \
Позволяет осознанно выбирать проекты, роли и возможности, которые приближают к желаемому \
состоянию. Служит критерием для оценки приоритетов."""

concept.meta_meta = MetaMetaType.CONCEPT

concept.examples = [
    "Концепт: 'Я — системный архитектор сложных продуктов в финтех-домене'",
    "Концепт: 'Я — методолог и образователь в области системного мышления'",
    "Визуализация карты ролей с целевыми позициями через 3-5-10 лет",
]

# 4. Добавляем связи (если есть C_2 и C_15)
if onto.index.get("C_2"):
    concept.add_relation("C_2", RelationType.REQUIRES, "Требует агентности")
    
# 5. Отмечаем как заполненное
concept.mark_filled()

# 6. Сохраняем
file_path = onto.save_concept(concept)

print(f"✅ Понятие создано!")
print(f"   ID: {concept.id}")
print(f"   Имя: {concept.name}")
print(f"   Статус: {concept.status.value}")
print(f"   Тип: {concept.meta_meta.value}")
print(f"   Файл: {file_path.name}\n")

# 7. Проверяем результат
onto.load_all()
print("📊 Статистика онтологии:")
onto.print_audit()

print("\n" + "="*60)
print("✨ Готово! Файл создан в:")
print(f"   {file_path}")
print("="*60)
