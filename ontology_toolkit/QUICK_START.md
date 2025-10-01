# ⚡ Быстрый старт — Ontology Toolkit

**5 минут** от установки до первого понятия.

---

## 📦 Установка зависимостей

```bash
pip install python-frontmatter pyyaml pydantic networkx rich
```

---

## 🚀 Первый запуск (3 команды)

```python
from pathlib import Path
from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import MetaMetaType

# 1. Создать онтологию
onto = Ontology(Path(".ontology"))

# 2. Добавить понятие
concept = onto.add_concept("Агентность")
concept.definition = "Способность активно действовать для изменения мира"
concept.purpose = "Брать ответственность за собственное развитие"
concept.meta_meta = MetaMetaType.CHARACTERISTIC
concept.examples = ["Самостоятельное планирование", "Инициирование проектов"]
concept.mark_filled()

# 3. Сохранить
onto.save_concept(concept)
print(f"✅ Создано: {concept.id} — {concept.name}")
```

**Результат:** Файл `.ontology/concepts/C_1_agentnost.md` создан!

---

## 📖 Базовые операции (шпаргалка)

```python
# Импорты (1 раз)
from pathlib import Path
from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import MetaMetaType, RelationType, ConceptStatus

# Открыть онтологию
onto = Ontology(Path(".ontology"))
onto.load_all()

# ===== СОЗДАНИЕ =====

# Создать понятие
c = onto.add_concept("Название")
c.definition = "Что это..."
c.purpose = "Зачем нужно..."
c.meta_meta = MetaMetaType.CONCEPT  # или CHARACTERISTIC, METHOD, ARTIFACT...
c.examples = ["Пример 1", "Пример 2"]
c.mark_filled()
onto.save_concept(c)

# ===== ПОИСК =====

# По ID
c = onto.get_concept("C_2")

# По имени
concepts = onto.index.find_by_name("агентность")

# По статусу
drafts = onto.find_concepts_by_status(ConceptStatus.DRAFT)

# Все понятия
all_concepts = onto.index.by_prefix["C"]

# ===== ИЗМЕНЕНИЕ =====

# Получить → изменить → сохранить
c = onto.get_concept("C_2")
c.definition = "Новое определение"
c.add_example("Новый пример")
onto.save_concept(c)

# ===== СВЯЗИ =====

# Добавить связь
c.add_relation("C_22", RelationType.REQUIRES, "Требует...")
onto.save_concept(c)

# Удалить связь
c.remove_relation("C_22")
onto.save_concept(c)

# ===== СТАТУСЫ =====

# Изменить статус
c.mark_filled()  # draft → draft+filled
c.approve()      # draft+filled → approved
onto.save_concept(c)

# ===== ПРОВЕРКА =====

# Аудит (красивая таблица)
onto.print_audit()

# Найти битые ссылки
broken = onto.validate_relations()
if broken:
    print(f"⚠️ Проблем: {len(broken)}")
    onto.fix_relations(dry_run=False)  # Исправить

# Статистика
audit = onto.audit()
print(f"Всего: {audit['total_objects']}")
print(f"Черновиков: {audit['by_status'].get('draft', 0)}")
```

---

## 🎯 Типы из FPF (meta_meta)

```python
from ontology_toolkit.core.schema import MetaMetaType

# Основные типы:
MetaMetaType.CHARACTERISTIC   # Характеристика (Агентность, Ресурсность)
MetaMetaType.METHOD           # Метод (Стратегирование, Учёт времени)
MetaMetaType.ARTIFACT         # Артефакт (Личный контракт, Заготовка)
MetaMetaType.SYSTEM           # Система (Киберличность)
MetaMetaType.ROLE             # Роль (Заказчик, Создатель)
MetaMetaType.PROCESS          # Процесс (Карьерный рост)
MetaMetaType.PROBLEM          # Проблема
MetaMetaType.CONCEPT          # Понятие (общее)
```

---

## 🔗 Типы связей (relations)

```python
from ontology_toolkit.core.schema import RelationType

RelationType.REQUIRES      # Требует (A requires B = "A требует B")
RelationType.ENABLES       # Позволяет (A enables B = "A позволяет B")
RelationType.RELATES_TO    # Связано с (общая связь)
RelationType.PART_OF       # Часть целого
RelationType.INSTANCE_OF   # Экземпляр
RelationType.OPPOSITE_OF   # Противоположно
RelationType.SIMILAR_TO    # Похоже на
```

---

## 📊 Статусы понятий

```python
from ontology_toolkit.core.schema import ConceptStatus

ConceptStatus.DRAFT         # Черновик (только название)
ConceptStatus.DRAFT_FILLED  # Заполнено, не проверено
ConceptStatus.APPROVED      # Утверждено
```

---

## 🎨 Полный пример (копируй и запускай)

```python
#!/usr/bin/env python3
"""Пример добавления понятия"""

from pathlib import Path
from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import MetaMetaType, RelationType

# Открыть онтологию
onto = Ontology(Path(".ontology"))
onto.load_all()

# Создать понятие "Карьерный концепт"
concept = onto.add_concept("Карьерный концепт")
concept.definition = "Мысленная модель желаемой карьерной траектории"
concept.purpose = "Обеспечивает стратегическую ясность"
concept.meta_meta = MetaMetaType.CONCEPT
concept.examples = [
    "Концепт: 'Я — системный архитектор'",
    "Визуализация карты ролей",
]

# Добавить связи (если есть другие понятия)
if onto.index.get("C_2"):
    concept.add_relation("C_2", RelationType.REQUIRES, "Требует агентности")

# Сохранить
concept.mark_filled()
onto.save_concept(concept)

print(f"✅ {concept.id} — {concept.name}")

# Проверить
onto.load_all()
onto.print_audit()
```

**Сохрани как** `add_concept.py` → Запусти → Готово!

---

## 🛠️ Структура проекта

```
project/
├── .ontology/                  # Онтология (папка)
│   ├── concepts/               # Понятия (MD файлы)
│   │   ├── C_1_agentnost.md
│   │   └── C_2_strategirovanie.md
│   ├── methods/                # Методы
│   ├── systems/                # Системы
│   └── README.md               # Описание
└── add_concept.py              # Твой скрипт
```

---

## 📝 Формат файла (MD + YAML)

```markdown
---
id: C_2
name: Агентность
status: approved
meta_meta: Характеристика
relations:
  - type: enables
    target: C_22
    description: Позволяет создать личный контракт
created: 2025-09-15T10:00:00
updated: 2025-10-01T12:00:00
---

# Агентность

## Definition
Способность активно действовать...

## Purpose
Брать ответственность...

## Examples
- Самостоятельное планирование
- Инициирование проектов
```

**Можно редактировать вручную** в любом редакторе (VSCode, Obsidian, ...)

---

## ❓ Частые вопросы

### Как добавить несколько понятий сразу?

```python
names = ["Понятие 1", "Понятие 2", "Понятие 3"]
for name in names:
    c = onto.add_concept(name)
    c.definition = f"Определение для {name}"
    c.mark_filled()
    onto.save_concept(c)
    print(f"✅ {c.id}")
```

### Как найти все черновики?

```python
drafts = onto.find_concepts_by_status(ConceptStatus.DRAFT)
for d in drafts:
    print(f"{d.id} — {d.name}")
```

### Как проверить онтологию?

```python
onto.load_all()
onto.print_audit()

broken = onto.validate_relations()
if broken:
    print(f"⚠️ {len(broken)} проблем")
```

### Как экспортировать в CSV? (простой вариант)

```python
import csv

concepts = onto.index.by_prefix["C"]
with open("concepts.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "definition", "status"])
    for c in concepts:
        writer.writerow([c.id, c.name, c.definition, c.status.value])
```

---

## 📚 Полная документация

- [README.md](README.md) — общая информация
- [USER_GUIDE.md](USER_GUIDE.md) — подробное руководство
- [ROADMAP.md](ROADMAP.md) — план развития

---

**Версия:** 0.1.0  
**Дата:** 01.10.2025

Готов работать? Скопируй код выше и запусти! 🚀
