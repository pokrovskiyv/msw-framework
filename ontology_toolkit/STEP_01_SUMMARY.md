# Шаг №1: Структура проекта и базовая настройка ✅

## Выполнено

### 1. Создана структура папок библиотеки

```
ontology_toolkit/
├── __init__.py
├── pyproject.toml
├── README.md
├── .gitignore
├── core/
│   └── __init__.py
├── ai/
│   └── __init__.py
├── io/
│   └── __init__.py
├── mcp/
│   └── __init__.py
├── cli/
│   └── __init__.py
├── tests/
└── prompts_templates/
    ├── concept_fill.md
    ├── context_extract.md
    ├── meta_meta_rules.md
    ├── ontology_project_template.yaml
    ├── ontology_README_template.md
    └── CHANGELOG_template.md
```

### 2. Настроен pyproject.toml

**Основные зависимости:**
- `pyyaml` — работа с YAML
- `typer` + `rich` — CLI с красивым выводом
- `anthropic` — интеграция с Claude API
- `pydantic` — валидация данных
- `networkx` — граф связей
- `pandas` + `openpyxl` — экспорт в CSV/XLSX
- `python-frontmatter` — парсинг MD + YAML

**Dev-зависимости:**
- `pytest` — тестирование
- `black` + `ruff` — форматирование и линтинг
- `mypy` — проверка типов

### 3. Созданы шаблоны промптов

#### `context_extract.md`
Промпт для извлечения LLM-контекста проекта по FPF:
- Bounded Context
- Roles, Capabilities, Services
- Work Plan, Work Log
- Assurance (F-G-R)
- Measures

#### `concept_fill.md`
Промпт для заполнения понятий:
- Определение фундаментального типа (meta_meta)
- Заполнение definition, purpose, examples
- Построение relations с существующими объектами
- Валидация по FPF (различение метод/план/работа)

#### `meta_meta_rules.md`
Справочник типов:
- Характеристика, Показатель, Значение
- Роль, Метод, План работ, Выполнение
- Артефакт, Система, Проблема
- Примеры и алгоритм определения типа

### 4. Создан шаблон конфигурации

`ontology_project_template.yaml` включает:
- Метаданные проекта (name, version, language)
- Структуру папок
- Префиксы ID (C, M, S, P, A)
- Статусы (draft → draft+filled → approved)
- Типы связей (requires, enables, relates_to, ...)
- Настройки AI (provider, model, prompts)
- Правила валидации

### 5. Созданы шаблоны для онтологии

- `ontology_README_template.md` — README для проекта онтологии
- `CHANGELOG_template.md` — шаблон истории изменений

## Архитектура (утверждена)

### Формат хранения: ✅ Markdown + YAML frontmatter

**Обоснование:**
- ✅ Git-friendly (построчный diff)
- ✅ Человекочитаемость
- ✅ Прямые ссылки между файлами
- ✅ AI-friendly для редактирования
- ✅ Переиспользование между проектами

### Вкладки (типы объектов): ✅

1. **README** — описание онтологии
2. **context** — LLM-контекст проекта (YAML)
3. **tables** — сводные таблицы
4. **concepts** — понятия (C_*)
5. **methods** — методы (M_*)
6. **systems** — системы (S_*)
7. **problems** — проблемы (P_*)
8. **artifacts** — артефакты (A_*)
9. **CHANGELOG** — история изменений

### Ключевые различения (FPF): ✅

- **Метод** ↔ **Описание метода** ↔ **Выполнение**
- **План** ↔ **Факт работы**
- **Роль** ↔ **Носитель роли**
- **Характеристика** ↔ **Показатель** ↔ **Значение**

## Следующие шаги

### Шаг №2: Core модули (фундамент)
- [ ] `core/schema.py` — Pydantic-схемы для Concept, Method, System
- [ ] `core/concept.py` — класс Concept с YAML frontmatter
- [ ] `core/ontology.py` — граф связей, индексация

### Шаг №3: IO модули
- [ ] `io/markdown.py` — парсинг MD + YAML
- [ ] `io/validator.py` — проверка связей, broken links
- [ ] `io/csv_export.py` — экспорт в CSV

### Шаг №4: AI-интеграция
- [ ] `ai/prompts.py` — загрузка промптов из файлов
- [ ] `ai/filler.py` — заполнение через Claude API
- [ ] `ai/extractor.py` — извлечение понятий из текста

### Шаг №5: CLI
- [ ] `cli/main.py` — команды (init, add, fill, audit, export)

### Шаг №6: MCP-сервер
- [ ] `mcp/server.py` — интеграция с Cursor

## Критерии приёмки Шага №1 ✅

- [x] Создана структура папок библиотеки
- [x] Настроен `pyproject.toml` с зависимостями
- [x] Созданы шаблоны промптов (concept_fill, context_extract, meta_meta_rules)
- [x] Создан шаблон конфигурации проекта (YAML)
- [x] Созданы README и CHANGELOG шаблоны
- [x] Все __init__.py файлы на месте
- [x] .gitignore настроен

## Assurance (F-G-R)

| Аспект | F (Формальность) | G (Область) | R (Надёжность) |
|--------|-----------------|-------------|---------------|
| **Структура** | Папки и файлы по стандарту | Вся библиотека | Создано и проверено |
| **Зависимости** | pyproject.toml (Poetry/pip) | Все модули | Установка будет протестирована в Шаге №2 |
| **Промпты** | Markdown-файлы с placeholder | concept_fill, context_extract | Готовы к использованию AI |
| **Шаблоны** | YAML + MD шаблоны | Онтология проектов | Готовы к init команде |

## Время выполнения

- **План:** 30-40 минут
- **Факт:** ~35 минут
- **Блокеры:** Нет

## Заметки

1. Выбран формат **MD + YAML frontmatter** как оптимальный для Git и AI
2. Промпты сохранены как отдельные файлы → легко поддерживать и версионировать
3. Конфигурация вынесена в YAML → гибкость для разных проектов
4. Префиксы ID стандартизированы: C (concept), M (method), S (system), P (problem), A (artifact)

---

**Статус:** ✅ Готово к переходу на Шаг №2
