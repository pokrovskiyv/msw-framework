# Changelog

Все значимые изменения в проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Планируется (v0.4.0+)
- Batch AI processing с progress bar
- AI-предложения связей между понятиями
- Импорт из CSV/XLSX обратно в онтологию
- Поддержка Methods, Systems, Problems, Artifacts в CLI
- Расширенный граф с фильтрами и стилями
- `ontology fix-relations` — автоисправление связей

---

## [0.3.2] - 2025-10-02

### Added
- **Команда `fill-all`** — заполнение всех пустых понятий одной командой
  - `--exclude-status` — настраиваемые исключения (по умолчанию: approved, draft+filled)
  - `--dry-run` — предварительный просмотр без выполнения
  - `--delay` — настраиваемая пауза между запросами (по умолчанию: 2с)
  - Сохраняет принцип качества: каждое понятие заполняется отдельным запросом
  - Показывает прогресс выполнения и статистику результатов

### Changed
- Обновлена документация с примерами использования `fill-all`
- Добавлена секция "Batch заполнение" в README.md и AI_GUIDE.md

---

## [0.3.1] - 2025-10-02

### Added
- **Автозагрузка контекста проекта** — AI автоматически читает `.ontology/context/project_context.yaml`
  - Новый метод `ConceptFiller._load_project_context()` для чтения YAML и MD/TXT файлов
  - Обновлён `_prepare_context()` для использования контекста проекта
  - Template `project_context_template.yaml` создаётся при `ontology init`
  - Документация в README об использовании контекста

### Fixed
- Исправлен `RelationType.RELATED_TO` → `RelationType.RELATES_TO` в `filler.py`

### Changed
- Команда `ontology init` теперь создаёт папку `context/` и файл `project_context.yaml`
- Обновлён README с секцией "Контекст проекта для AI"
- **Документирован принцип "1 понятие = 1 запрос"** для обеспечения качества
- Добавлена секция "Best Practices" в AI_GUIDE.md

---

## [0.3.0.1] - 2025-10-02

### Fixed
- **Исправлен баг с `meta_meta.value`** — добавлены проверки `hasattr()` в CLI для безопасного отображения
- **Исправлено преобразование `meta_meta`** — AI ответ теперь корректно конвертируется из строки в enum `MetaMetaType`
- **Обновлен маппинг `MetaMetaType`** — используются только реальные значения из schema.py

### Changed
- Улучшена обработка `meta_meta` в `ConceptFiller._parse_ai_response()`
- Добавлены безопасные проверки в `cli/main.py` для команд `list`, `fill`, `extract`

---

## [0.3.0] - 2025-10-02

### Added
- **AI функции (полная реализация)** — работающие AI команды:
  - `config-ai` — управление конфигурацией AI провайдеров
  - `fill` — автозаполнение понятий через AI
  - `extract` — извлечение понятий из текста
- **Интеграция с реальными API**:
  - Anthropic Claude (готово к использованию)
  - OpenAI ChatGPT (опциональная зависимость)
  - Google Gemini (опциональная зависимость)
  - xAI Grok (опциональная зависимость)
- **ConceptFiller** — автозаполнение полей понятий (definition, purpose, examples, meta_meta)
- **ConceptExtractor** — извлечение понятий из текста/файлов
- **Улучшенный парсинг** — корректная обработка Markdown таблиц с гибким порядком колонок

### Changed
- Версия: `0.2.1` → `0.3.0`
- Улучшен парсинг ответов AI в `ConceptFiller._parse_ai_response()`
- Добавлен метод `Ontology.get_next_id()` для делегирования к индексу

### Fixed
- Исправлен парсинг Markdown таблиц — теперь определяется порядок колонок из заголовка
- Исправлена генерация ID в `ConceptExtractor` — корректная работа с `get_next_id()`
- Обновлены тесты CLI — заменены проверки эмодзи на текстовые метки `[OK]`/`[ERROR]`

---

## [0.2.1] - 2025-10-02

### Added
- **AI Integration (архитектура)** — подготовка инфраструктуры для 4 AI провайдеров:
  - Anthropic Claude (Sonnet, Opus, Haiku)
  - OpenAI ChatGPT (GPT-4, GPT-4 Turbo, GPT-3.5)
  - Google Gemini (Gemini Pro)
  - xAI Grok (Grok-1, Grok-2)
- **Планируемые команды** (интерфейсы готовы, реализация в процессе):
  - `config-ai` — управление конфигурацией AI
  - `fill` — автозаполнение понятий через AI
  - `extract` — извлечение понятий из текста
- **AI модуль** (`ai/`) — архитектура и интерфейсы:
  - `base_provider.py` — абстрактный базовый класс
  - `factory.py` — фабрика провайдеров с ENV конфигурацией
  - `client.py` — унифицированный клиент
  - `prompts.py` — загрузка и рендеринг промптов (заглушка)
  - `filler.py` — логика автозаполнения (заглушка)
  - `extractor.py` — логика извлечения понятий (заглушка)
  - `providers/` — интерфейсы для 4 провайдеров (заглушки)
- **Опциональные зависимости** в `pyproject.toml`:
  - `[ai-openai]` — для OpenAI
  - `[ai-gemini]` — для Gemini
  - `[ai-grok]` — для Grok
  - `[ai-all]` — все провайдеры сразу
- **Конфигурация через ENV**:
  - `ONTOLOGY_AI_PROVIDER` — выбор провайдера
  - `{PROVIDER}_API_KEY` — API ключи
  - `ONTOLOGY_AI_MODEL` — выбор модели
  - `ONTOLOGY_AI_TEMPERATURE` — температура генерации
- **Тесты** (`tests/test_ai.py`):
  - Mock провайдер для unit-тестов
  - Тесты фабрики, клиента, filler, extractor
  - Интеграционные тесты с реальным API (опционально)
- **Документация**:
  - `AI_GUIDE.md` — полное руководство по AI (388 строк)
  - `RELEASE_NOTES_v0.3.0.md` — детальные release notes
  - Обновлен `README.md` с разделом AI
  - Обновлен `ROADMAP.md`

### Changed
- Версия: `0.2.0` → `0.2.1`
- Keywords: добавлены `ai`, `llm` (подготовка к будущей реализации)

### Fixed
- **Windows кодировка UTF-8** — улучшена функция `fix_windows_encoding`:
  - Автоматическое определение правильной кириллицы
  - Исправление только "кракозябр" (latin-1 → utf-8)
  - Полная поддержка кириллицы в Windows Terminal с PowerShell Profile
- **Документация** — обновлен `WINDOWS_ENCODING.md` с проверенными решениями

---

## [0.2.0] - 2025-10-02

### Added
- **CLI MVP** — 6 основных команд:
  - `init` — инициализация онтологии
  - `add` — добавление понятий
  - `list` — просмотр списка с фильтрами
  - `audit` — проверка качества
  - `export` — экспорт в CSV/XLSX
  - `graph` — генерация Mermaid графа
- **IO модули**:
  - `io/csv_export.py` — экспорт в CSV с UTF-8-sig
  - `io/xlsx_export.py` — экспорт в XLSX с вкладками
  - Поддержка фильтров по префиксу и статусу
- **Тесты**:
  - `tests/test_io.py` — тесты экспорта (8 тестов)
  - `tests/test_cli.py` — тесты CLI (12 тестов)
  - Покрытие основных сценариев использования
- **Документация**:
  - `QUICK_START.md` — быстрый старт
  - `USER_GUIDE.md` — полное руководство
  - `.cursorrules` — интеграция с Cursor
  - `WINDOWS_ENCODING.md` — решение проблем кодировки
  - `RELEASE_NOTES_v0.2.0.md`
- **Rich console** — красивый вывод с таблицами и цветами

### Fixed
- Проблема с кодировкой UTF-8 в Windows консоли
- Конфликт имён в команде `list` (переименована в `list_entities`)
- Транслитерация имён файлов для безопасности в Windows
- Корректная работа с путями, содержащими пробелы

### Changed
- Улучшена структура `pyproject.toml` для setuptools
- Package discovery: явное указание пакетов и `package-dir`
- Установка: переход с `-e` (editable) на обычную для Windows

---

## [0.1.0] - 2025-10-01

### Added
- **Ядро (`core/`)**:
  - `schema.py` — Pydantic схемы для всех типов объектов:
    - `Concept` — понятия
    - `Method` — методы
    - `System` — системы
    - `Problem` — проблемы
    - `Artifact` — артефакты
  - `concept.py` — работа с понятиями (MD + YAML frontmatter):
    - `ConceptFile` — чтение/запись
    - `ConceptFactory` — создание draft и filled
  - `ontology.py` — управление онтологией:
    - `OntologyIndex` — индексация по ID, name, prefix, status
    - `Ontology` — загрузка, валидация, граф (networkx)
- **Схемы данных**:
  - Статусы: `draft`, `draft+filled`, `approved`
  - Типы связей: `relates_to`, `enables`, `requires`, etc.
  - MetaMetaType: 11 фундаментальных типов по FPF
- **Граф связей** — networkx для построения и валидации
- **Валидация**:
  - Проверка broken links
  - Поиск циклических зависимостей
  - Проверка корректности ID
- **Базовые тесты** (`tests/test_basic_flow.py`)
- **Промпты** (`prompts_templates/`):
  - `concept_fill.md` — для AI-заполнения
  - `context_extract.md` — для извлечения контекста
  - `meta_meta_rules.md` — правила FPF
- **Документация**:
  - `README.md` — основная документация
  - `ROADMAP.md` — план развития
  - `pyproject.toml` — конфигурация проекта
- **Зависимости**:
  - `pyyaml` — работа с YAML
  - `pydantic` — валидация данных
  - `networkx` — граф связей
  - `pandas`, `openpyxl` — экспорт данных
  - `python-frontmatter` — парсинг MD + YAML
  - `typer`, `rich` — CLI
  - `anthropic` — AI integration (подготовка)

### Technical
- Python 3.10+ поддержка
- MIT лицензия
- Git-friendly формат (MD + YAML)
- Type hints для всех публичных API

---

## Типы изменений

- `Added` — новые функции
- `Changed` — изменения в существующей функциональности
- `Deprecated` — функции, которые скоро будут удалены
- `Removed` — удалённые функции
- `Fixed` — исправления багов
- `Security` — исправления уязвимостей

---

[Unreleased]: https://github.com/system-career/ontology-toolkit/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/system-career/ontology-toolkit/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/system-career/ontology-toolkit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/system-career/ontology-toolkit/releases/tag/v0.1.0

