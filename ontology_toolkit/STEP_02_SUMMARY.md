# Шаг №2: Core модули (фундамент) ✅

## Выполнено

### 1. `core/schema.py` — Pydantic-схемы ✅

**Основные классы:**

#### Enums (перечисления):
- `ConceptStatus` — статусы понятий (draft, draft+filled, approved)
- `MetaMetaType` — типы из FPF (Характеристика, Роль, Метод, Артефакт, ...)
- `RelationType` — типы связей (requires, enables, relates_to, ...)

#### Models (модели данных):
- `Relation` — связь между объектами с типом и описанием
- `BaseEntity` — базовая сущность со всеми общими полями
  - `id`, `name`, `definition`, `purpose`
  - `examples`, `relations`
  - `created`, `updated`, `notes`
  - Методы: `add_relation()`, `remove_relation()`
  
- `Concept(BaseEntity)` — понятие с дополнительными полями:
  - `status: ConceptStatus`
  - `meta_meta: MetaMetaType`
  - Методы: `mark_filled()`, `approve()`

- `Method(BaseEntity)` — метод с полями `method_type`, `steps`
- `System(BaseEntity)` — система с полями `components`, `boundaries`
- `Problem(BaseEntity)` — проблема с полями `current_state`, `desired_state`, `metrics`
- `Artifact(BaseEntity)` — артефакт с полями `artifact_type`, `template_ref`

#### Утилиты:
- `ConceptSchema` — утилиты для работы со схемами
  - `get_entity_class(prefix)` — получить класс по префиксу
  - `parse_id(entity_id)` — распарсить ID на префикс и номер
  - `format_id(prefix, number)` — сформировать ID

**Валидация:**
- Автоматическая валидация полей через Pydantic
- Проверка на пустые значения
- Нормализация текста (trim, capitalize)

---

### 2. `core/concept.py` — Работа с MD + YAML ✅

**Основные классы:**

#### `ConceptFile`:
Управление файлами понятий в формате Markdown + YAML frontmatter.

**Методы:**
- `from_file(file_path)` — загрузить из MD файла
  - Парсинг YAML frontmatter
  - Извлечение секций (Definition, Purpose, Examples, Notes)
  - Конвертация в Pydantic-модель
  
- `to_markdown()` — конвертировать в MD + YAML
  - Формирование YAML frontmatter с метаданными
  - Генерация Markdown контента с секциями
  
- `save(directory, overwrite)` — сохранить в файл
  - Формирование имени файла: `C_1_agency.md`
  - Транслитерация русских названий
  - Создание директории если нужно

**Утилиты:**
- `_parse_content(content)` — парсинг MD на секции
- `_parse_list(text)` — парсинг маркированного списка
- `_parse_relations(data)` — парсинг связей из YAML
- `_sanitize_filename(name)` — транслитерация в безопасное имя файла

**Методы обновления:**
- `update_field(field_name, value)` — обновить поле
- `add_example(example)` — добавить пример
- `remove_example(example)` — удалить пример

#### `ConceptFactory`:
Фабрика для создания понятий.

**Методы:**
- `create_draft(name, id)` — создать черновик (только name)
- `create_filled(name, definition, ...)` — создать заполненное понятие

---

### 3. `core/ontology.py` — Граф и индексация ✅

**Основные классы:**

#### `OntologyIndex`:
Многоуровневый индекс для быстрого поиска.

**Индексы:**
- `by_id: Dict[str, BaseEntity]` — по ID
- `by_name: Dict[str, List[BaseEntity]]` — по нормализованному имени
- `by_prefix: Dict[str, List[BaseEntity]]` — по префиксу (C, M, S, P, A)
- `by_status: Dict[str, List[Concept]]` — по статусу (для concepts)

**Методы:**
- `add(entity)` — добавить в индекс
- `remove(entity_id)` — удалить из индекса
- `get(entity_id)` — получить по ID
- `find_by_name(name)` — найти по имени
- `get_next_id(prefix)` — получить следующий свободный ID

#### `Ontology`:
Главный класс для работы с онтологией.

**Атрибуты:**
- `root_path: Path` — корневой путь проекта
- `index: OntologyIndex` — индекс объектов
- `graph: nx.DiGraph` — направленный граф связей
- `console: Console` — для красивого вывода (rich)

**Методы загрузки:**
- `load_all()` — загрузить все объекты из файлов
- `add_entity(entity)` — добавить объект в онтологию
- `remove_entity(entity_id)` — удалить объект

**Методы работы с понятиями:**
- `add_concept(name)` — добавить новое понятие (черновик)
- `get_concept(concept_id)` — получить понятие по ID
- `save_concept(concept)` — сохранить понятие в файл
- `find_concepts_by_status(status)` — найти понятия по статусу

**Методы работы с графом:**
- `_build_graph()` — построить граф связей
- `validate_relations()` — найти broken links
- `fix_relations(dry_run)` — исправить broken links
- `get_related(entity_id, depth)` — получить связанные объекты

**Методы аудита:**
- `audit()` — провести аудит (статистика, broken links, изолированные узлы)
- `print_audit()` — вывести результаты аудита в консоль

---

## Архитектура

### Слои абстракции:

```
┌─────────────────────────────────────────┐
│     Ontology (высокий уровень)          │
│  - load_all(), audit(), save_concept()  │
│  - add_concept(), validate_relations()  │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│  OntologyIndex (индексация и поиск)     │
│  - by_id, by_name, by_prefix, by_status │
│  - add(), get(), find_by_name()         │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│  ConceptFile (MD + YAML)                │
│  - from_file(), to_markdown(), save()   │
│  - _parse_content(), _sanitize_filename │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│  Pydantic Models (schema.py)            │
│  - Concept, Method, System, Problem     │
│  - Relation, BaseEntity                 │
└─────────────────────────────────────────┘
```

### Поток работы:

1. **Загрузка:** MD файл → ConceptFile.from_file() → Pydantic Model → OntologyIndex.add()
2. **Поиск:** Ontology.get_concept() → OntologyIndex.by_id → Concept
3. **Сохранение:** Concept → ConceptFile.to_markdown() → MD файл
4. **Граф:** Ontology._build_graph() → nx.DiGraph (networkx)
5. **Валидация:** Ontology.validate_relations() → список broken links

---

## Примеры использования

### Создание и сохранение понятия:

```python
from pathlib import Path
from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import MetaMetaType

# Инициализация
onto = Ontology(Path(".ontology"))

# Создание черновика
concept = onto.add_concept("Агентность")
print(f"Создано: {concept.id} — {concept.name}")  # C_1 — Агентность

# Заполнение
concept.definition = "Характеристика личности, выражающаяся в желании..."
concept.purpose = "Позволяет человеку брать на себя ответственность..."
concept.meta_meta = MetaMetaType.CHARACTERISTIC
concept.examples = [
    "Самостоятельное планирование недели",
    "Инициирование проектов"
]
concept.mark_filled()  # Статус → draft+filled

# Сохранение
file_path = onto.save_concept(concept)
print(f"Сохранено: {file_path}")
```

### Загрузка и аудит:

```python
# Загрузить всю онтологию
onto.load_all()

# Аудит
onto.print_audit()

# Найти черновики
drafts = onto.find_concepts_by_status(ConceptStatus.DRAFT)
print(f"Черновиков: {len(drafts)}")

# Валидация связей
broken = onto.validate_relations()
if broken:
    print(f"Broken links: {len(broken)}")
    onto.fix_relations(dry_run=False)  # Исправить
```

---

## Критерии приёмки Шага №2 ✅

- [x] Созданы Pydantic-схемы для всех типов объектов
- [x] Реализован класс ConceptFile для работы с MD + YAML
- [x] Реализован класс Ontology с индексацией и графом
- [x] Загрузка понятий из файлов работает
- [x] Сохранение понятий в файлы работает
- [x] Индексация по ID, name, prefix, status работает
- [x] Граф связей строится корректно (networkx)
- [x] Валидация broken links реализована
- [x] Аудит онтологии работает (метрики и статистика)

---

## Assurance (F-G-R)

| Аспект | F (Формальность) | G (Область) | R (Надёжность) |
|--------|-----------------|-------------|---------------|
| **Схемы** | Pydantic валидация | Все типы объектов | ✅ Типобезопасность |
| **MD + YAML** | python-frontmatter | Чтение/запись concepts | ✅ Парсинг проверен |
| **Индексация** | Dict + нормализация | По ID, name, prefix, status | ✅ O(1) доступ |
| **Граф** | networkx DiGraph | Все связи между объектами | ✅ Стандартная библиотека |
| **Валидация** | Проверка существования ID | Все relations | ✅ Обнаружение broken links |

---

## Следующие шаги

### Шаг №3: IO модули
- [ ] `io/markdown.py` — универсальный MD reader/writer
- [ ] `io/csv_export.py` — экспорт в CSV (как у вас сейчас)
- [ ] `io/xlsx_export.py` — экспорт в XLSX с вкладками
- [ ] `io/validator.py` — расширенная валидация (дубликаты, пустые поля)

### Шаг №4: AI-интеграция
- [ ] `ai/prompts.py` — загрузка промптов из файлов
- [ ] `ai/filler.py` — заполнение через Claude API
- [ ] `ai/extractor.py` — извлечение понятий из текста

### Шаг №5: CLI
- [ ] `cli/main.py` — команды (init, add, fill, audit, export)
- [ ] Интеграция с Typer

### Шаг №6: MCP-сервер
- [ ] `mcp/server.py` — интеграция с Cursor

---

## Время выполнения

- **План:** 60-80 минут
- **Факт:** ~75 минут
- **Блокеры:** Нет

---

## Заметки

1. **Pydantic** обеспечивает надёжную валидацию и типобезопасность
2. **networkx** используется для графа → стандартная и мощная библиотека
3. **Транслитерация** русских названий в имена файлов работает корректно
4. **Многоуровневая индексация** позволяет быстрый поиск по разным критериям
5. **Граф связей** строится автоматически при загрузке онтологии
6. **Rich** используется для красивого вывода в консоль

---

**Статус:** ✅ Готово к переходу на Шаг №3 (IO модули)
