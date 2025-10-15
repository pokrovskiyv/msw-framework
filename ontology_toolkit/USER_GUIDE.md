# Руководство пользователя — Ontology Toolkit

**Версия:** 0.1.0  
**Для кого:** Методологов, авторов курсов, работающих с понятиями

---

## 🎯 Что это такое?

**Ontology Toolkit** — это инструмент для управления понятиями проекта (курса, документации, базы знаний).

### Зачем нужен?

- ✅ **Вместо одного большого CSV** — отдельные файлы для каждого понятия
- ✅ **Git-friendly** — видно кто, когда, что изменил (как в коде)
- ✅ **Граф связей** — автоматически строится, можно валидировать
- 🔄 **AI-помощник** — архитектура готова, реализация в процессе (v0.3.0+)
- ✅ **Командная работа** — можно редактировать параллельно без конфликтов

---

## 📚 Основные понятия

### Понятие (Concept)
Основная единица онтологии. Каждое понятие — это отдельный `.md` файл.

**Поля:**
- `id` — уникальный номер (C_1, C_2, ...)
- `name` — название (краткое, в единственном числе)
- `definition` — что это такое
- `purpose` — зачем нужно
- `meta_meta` — тип из FPF (Характеристика, Метод, Артефакт...)
- `examples` — примеры использования (2-5 штук)
- `relations` — связи с другими понятиями
- `status` — статус (draft → draft+filled → approved)

### Статусы

| Статус | Что значит | Действие |
|--------|------------|----------|
| `draft` | Черновик, только название | Нужно заполнить |
| `draft+filled` | Заполнено, но не проверено | Нужно проверить |
| `approved` | Проверено и утверждено | Готово |

### Типы связей

| Тип | Описание | Пример |
|-----|----------|--------|
| `requires` | Требует (зависимость) | "Личный контракт" requires "Агентность" |
| `enables` | Позволяет (результат) | "Агентность" enables "Личный контракт" |
| `relates_to` | Связано с | "Агентность" relates_to "Жизненное мастерство" |
| `part_of` | Часть целого | "Слот" part_of "Недельный распорядок" |

---

## 🚀 Как начать работу

### Вариант 1: Создать новую онтологию

```python
from pathlib import Path
from ontology_toolkit.core.ontology import Ontology

# Создать онтологию
onto = Ontology(Path(".ontology"))
print("✅ Онтология создана")
```

Будет создана структура:
```
.ontology/
├── concepts/     # Понятия
├── methods/      # Методы
├── systems/      # Системы
├── problems/     # Проблемы
└── artifacts/    # Артефакты
```

### Вариант 2: Загрузить существующую

```python
onto = Ontology(Path(".ontology"))
onto.load_all()  # Загрузить все файлы

print(f"Загружено понятий: {len(onto.index.by_id)}")
```

---

## ✍️ Базовые операции

### 1. Добавить понятие

```python
# Создать черновик
concept = onto.add_concept("Карьерный концепт")

# Заполнить поля
concept.definition = "Мысленная модель желаемой карьерной траектории..."
concept.purpose = "Обеспечивает стратегическую ясность..."
concept.meta_meta = MetaMetaType.CONCEPT
concept.examples = [
    "Концепт: 'Я — системный архитектор'",
    "Визуализация карты ролей",
]

# Отметить как заполненное
concept.mark_filled()

# Сохранить
onto.save_concept(concept)
print(f"✅ Создано: {concept.id} — {concept.name}")
```

### 2. Найти понятие

```python
# По ID
concept = onto.get_concept("C_2")

# По имени
concepts = onto.index.find_by_name("агентность")

# По статусу
drafts = onto.find_concepts_by_status(ConceptStatus.DRAFT)
```

### 3. Изменить понятие

```python
# Получить
concept = onto.get_concept("C_2")

# Изменить
concept.definition = "Новое определение..."
concept.add_example("Новый пример")

# Сохранить
onto.save_concept(concept)
```

### 4. Добавить связи

```python
concept = onto.get_concept("C_22")

# Добавить связь
concept.add_relation(
    target="C_2",
    rel_type=RelationType.REQUIRES,
    description="Требует агентности для создания"
)

onto.save_concept(concept)
```

### 5. Утвердить понятие

```python
concept = onto.get_concept("C_2")

# Изменить статус
concept.approve()

onto.save_concept(concept)
```

---

## 🔍 Проверка и аудит

### Проверить связи

```python
# Найти битые ссылки
broken = onto.validate_relations()

if broken:
    print(f"⚠️ Найдено {len(broken)} проблем:")
    for src, target, error in broken:
        print(f"  {src} → {target}: {error}")
```

### Исправить проблемы

```python
# Удалить битые ссылки
onto.fix_relations(dry_run=False)
print("✅ Проблемы исправлены")
```

### Получить статистику

```python
# Аудит с красивым выводом
onto.print_audit()

# Или получить данные
audit_data = onto.audit()
print(f"Всего объектов: {audit_data['total_objects']}")
print(f"Broken links: {audit_data['broken_links']}")
```

---

## 📊 Работа с графом

### Найти связанные понятия

```python
# Получить все связанные понятия (глубина 2)
related = onto.get_related("C_2", depth=2)
print(f"Связанные понятия: {related}")
```

---

## 🎨 Типичные сценарии

### Сценарий 1: Массовое добавление понятий

```python
concepts_to_add = [
    ("Агентность", "Способность активно действовать..."),
    ("Стратегирование", "Практика еженедельного планирования..."),
    ("Личный контракт", "Документ со смыслами и планами..."),
]

for name, definition in concepts_to_add:
    c = onto.add_concept(name)
    c.definition = definition
    c.mark_filled()
    onto.save_concept(c)
    print(f"✅ {c.id} — {c.name}")
```

### Сценарий 2: Найти все черновики и заполнить

```python
drafts = onto.find_concepts_by_status(ConceptStatus.DRAFT)
print(f"Найдено черновиков: {len(drafts)}")

for draft in drafts:
    print(f"\n📝 {draft.id} — {draft.name}")
    # Здесь можно вручную заполнить или использовать AI
```

### Сценарий 3: Экспорт списка понятий

```python
import csv

with open("concepts_list.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Название", "Статус", "Тип"])
    
    for concept in onto.index.by_prefix["C"]:
        writer.writerow([
            concept.id,
            concept.name,
            concept.status.value,
            concept.meta_meta.value if concept.meta_meta else ""
        ])

print("✅ Экспортировано в concepts_list.csv")
```

---

## 🛠️ Расширенные возможности

### Работа с файлами напрямую

Если нужно отредактировать файл вручную:

```python
from ontology_toolkit.core.concept import ConceptFile

# Загрузить из файла
file_path = Path(".ontology/concepts/C_2_agentnost.md")
concept_file = ConceptFile.from_file(file_path)

# Изменить
concept_file.concept.definition = "Новое определение"

# Сохранить
concept_file.save(Path(".ontology/concepts"), overwrite=True)
```

### Создать понятие с нуля

```python
from ontology_toolkit.core.concept import ConceptFactory

# Только название
draft = ConceptFactory.create_draft("Новое понятие")

# Полностью заполненное
filled = ConceptFactory.create_filled(
    name="Новое понятие",
    definition="Определение...",
    purpose="Назначение...",
    meta_meta=MetaMetaType.CONCEPT,
    examples=["Пример 1", "Пример 2"]
)
```

---

## 📖 Примеры из реальной практики

### Пример 1: Добавить понятие из курса

```python
# Загрузить онтологию
onto = Ontology(Path(".ontology"))
onto.load_all()

# Создать понятие "Карьерный концепт"
concept = onto.add_concept("Карьерный концепт")
concept.definition = """Мысленная модель желаемой карьерной траектории..."""
concept.purpose = """Обеспечивает стратегическую ясность..."""
concept.meta_meta = MetaMetaType.CONCEPT
concept.examples = [
    "Концепт: 'Я — системный архитектор'",
    "Визуализация карты ролей",
]

# Добавить связи
concept.add_relation("C_2", RelationType.REQUIRES, "Требует агентности")
concept.add_relation("C_15", RelationType.RELATES_TO, "Направляет рост")

# Сохранить
concept.mark_filled()
onto.save_concept(concept)

print(f"✅ {concept.id} — {concept.name} создано")
```

### Пример 2: Проверить онтологию перед релизом

```python
onto = Ontology(Path(".ontology"))
onto.load_all()

print("📊 Проверка онтологии...\n")

# 1. Статистика
audit = onto.audit()
print(f"Всего понятий: {audit['total_objects']}")
print(f"Утверждённых: {audit['by_status'].get('approved', 0)}")
print(f"Черновиков: {audit['by_status'].get('draft', 0)}")

# 2. Проверка связей
broken = onto.validate_relations()
if broken:
    print(f"\n⚠️ Найдено {len(broken)} битых ссылок!")
else:
    print("\n✅ Все связи корректны")

# 3. Поиск понятий без связей
orphans = audit.get('orphan_concepts', [])
if orphans:
    print(f"\n⚠️ Понятий без связей: {len(orphans)}")
    for orphan_id in orphans:
        concept = onto.get_concept(orphan_id)
        print(f"   - {orphan_id}: {concept.name}")

# 4. Красивый отчёт
print("\n" + "="*60)
onto.print_audit()
```

---

## ❓ FAQ

### Как импортировать из существующего CSV?

**Ответ:** Функция импорта будет в Шаге №3.3. Пока можно создать скрипт:

```python
import csv

with open("concepts.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        c = onto.add_concept(row["name"])
        c.definition = row["definition"]
        c.purpose = row["purpose"]
        # ... остальные поля
        c.mark_filled()
        onto.save_concept(c)
```

### Как экспортировать обратно в CSV?

**Ответ:** Функция экспорта будет в Шаге №3.1. Можно использовать временное решение:

```python
import csv

concepts = onto.index.by_prefix["C"]
with open("export.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "definition", "purpose", "status"])
    for c in concepts:
        writer.writerow([c.id, c.name, c.definition, c.purpose, c.status.value])
```

### Можно ли редактировать файлы вручную?

**Ответ:** Да! Файлы — это обычный Markdown с YAML frontmatter. Можно открыть в Obsidian, VSCode, любом редакторе.

После ручного редактирования просто загрузи заново:
```python
onto.load_all()
```

### Как работать в команде?

**Ответ:** 
1. Папка `.ontology` в Git
2. Каждый работает над своими понятиями
3. Периодически делаете `git pull` / `git push`
4. При конфликтах Git покажет, что изменилось (как с кодом)

---

## 🚧 Что будет дальше?

### Шаг №3: Импорт/Экспорт (в разработке)
- Импорт из CSV/XLSX
- Экспорт в CSV/XLSX с сохранением формата

### Шаг №4: AI-интеграция (в разработке)
- Автозаполнение полей через Claude API
- Извлечение понятий из текста
- Предложение связей

### Шаг №5: CLI (в разработке)
```bash
ontology init --project "My_Project"
ontology add "Понятие" --auto-fill
ontology audit
ontology export --format csv
```

### Шаг №6: MCP для Cursor (в разработке)
Работа прямо из редактора кода.

---

## 📞 Поддержка

**Вопросы?** См. [README.md](README.md) и [ROADMAP.md](ROADMAP.md)

**Проблемы?** Проверь [STEP_02_SUMMARY.md](STEP_02_SUMMARY.md) для деталей реализации

---

**Версия:** 0.1.0  
**Дата:** 01.10.2025  
**Автор:** MSW Framework Team
