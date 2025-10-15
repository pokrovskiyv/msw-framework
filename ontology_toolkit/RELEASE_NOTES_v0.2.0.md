# Release Notes — Ontology Toolkit v0.2.0

**Дата релиза:** 02 октября 2025  
**Тип релиза:** CLI MVP (Minimum Viable Product)

---

## 🎉 Что нового

### ✅ IO модули (экспорт данных)

**`io/csv_export.py`:**
- Экспорт онтологии в CSV формат
- Кодировка `utf-8-sig` для совместимости с Excel на Windows
- Фильтры по префиксу (C/M/S/P/A) и статусу (draft/draft+filled/approved)
- Функция `export_concepts_to_csv()` и класс `CSVExporter`

**`io/xlsx_export.py`:**
- Экспорт в Excel с отдельными вкладками для каждого типа объектов
- Автоматическое форматирование (жирные заголовки, автоширина столбцов)
- Библиотеки: `pandas` + `openpyxl`
- Функция `export_to_xlsx()` и класс `XLSXExporter`

**`io/markdown.py`:**
- Универсальный класс `MarkdownIO` для работы с MD файлами
- Методы `read_file()` и `write_file()`

### ✅ CLI (командная строка)

**6 команд для работы с онтологией:**

1. **`ontology init [--project NAME]`**
   - Создаёт структуру `.ontology/{concepts,methods,systems,problems,artifacts}`
   - Генерирует README файл

2. **`ontology add NAME [--type concept]`**
   - Добавляет новый объект (понятие)
   - Создаёт черновик в соответствующей папке
   - Автоматически присваивает ID (C_1, C_2, ...)

3. **`ontology list [--status] [--prefix]`**
   - Показывает список объектов в виде таблицы
   - Фильтры по статусу и префиксу
   - Красивый вывод через `rich.table`

4. **`ontology audit`**
   - Проверяет качество онтологии
   - Показывает статистику, broken links, изолированные узлы
   - Предлагает исправления

5. **`ontology export --format {csv,xlsx} [--output PATH]`**
   - Экспортирует онтологию в CSV или XLSX
   - Поддержка фильтров

6. **`ontology graph [--output PATH]`**
   - Создаёт граф связей в формате Mermaid (`.mmd`)
   - Можно открыть в Obsidian или сконвертировать в PNG

**Обработка ошибок:**
- Graceful сообщения при отсутствии `.ontology/`
- Коды возврата: 0 = успех, 1 = ошибка
- Понятные сообщения через `rich.console`

### ✅ Тесты

**`tests/test_io.py`:**
- 8 тестов для CSV/XLSX экспорта
- Проверка кодировки, фильтров, связей

**`tests/test_cli.py`:**
- 12 тестов для всех CLI команд
- Использование Typer `CliRunner`

**`tests/test_basic_flow.py`:**
- Базовые тесты ядра (уже были в v0.1.0)

### ✅ Документация

**README.md:**
- Обновлена секция "Быстрый старт" с CLI примерами
- Таблица команд с описаниями и примерами
- Секция "Интеграция с Cursor"

**ROADMAP.md (новый файл):**
- История версий (v0.1.0, v0.2.0)
- План развития (v0.3.0 — AI, v0.4.0 — расширенные фичи)
- Что НЕ будет реализовано (MCP, GUI, веб-интерфейс)

**.cursorrules (новый файл):**
- Правила для интеграции с Cursor
- Описание всех CLI команд и workflow
- Примеры использования

**pyproject.toml:**
- Версия обновлена до `0.2.0`
- Entrypoint для CLI: `ontology = "ontology_toolkit.cli.main:app"`

---

## 📦 Установка

```bash
cd ontology_toolkit
pip install -e .
```

После установки команда `ontology` доступна глобально.

---

## 🚀 Быстрый старт

```bash
# 1. Инициализация
ontology init --project "My Project"

# 2. Добавление понятий
ontology add "Агентность"
ontology add "Стратегирование"

# 3. Просмотр списка
ontology list

# 4. Проверка качества
ontology audit

# 5. Экспорт
ontology export --format csv --output concepts.csv
ontology export --format xlsx --output concepts.xlsx

# 6. Граф связей
ontology graph --output visuals/ontology.mmd
```

---

## 🔄 Миграция с v0.1.0

Если вы использовали v0.1.0 (только Python API):

1. Установите v0.2.0: `pip install -e .`
2. Теперь доступен CLI — можете использовать команды `ontology`
3. Python API остался без изменений — старые скрипты работают

---

## 🐛 Известные ограничения

1. **Только понятия (Concepts)**
   - CLI команда `add` пока работает только для понятий
   - Методы/системы/проблемы/артефакты можно добавлять через Python API
   - Будет исправлено в v0.3.0

2. **Нет AI-автозаполнения**
   - Функция `fill` из README пока не реализована
   - Запланирована на v0.3.0

3. **Нет извлечения из текста**
   - Функция `extract` пока не реализована
   - Запланирована на v0.3.0

4. **Windows кодировки**
   - При экспорте CSV используется `utf-8-sig` для Excel
   - Если возникают проблемы, используйте XLSX формат

---

## 🎯 Что дальше (v0.3.0)

**Планируется:**
- AI-автозаполнение полей: `ontology fill --id C_1`
- Извлечение понятий из текста: `ontology extract --from file.md`
- Поддержка всех типов объектов в CLI
- Тесты с mock Anthropic API

**Ожидаемый срок:** Q4 2025

См. [ROADMAP.md](ROADMAP.md) для деталей.

---

## 📝 Changelog

### Added
- IO модули: `csv_export.py`, `xlsx_export.py`, `markdown.py`
- CLI: 6 команд (init, add, list, audit, export, graph)
- Тесты: `test_io.py`, `test_cli.py`
- Документация: ROADMAP.md, .cursorrules
- Обновлён README с CLI примерами

### Changed
- Версия в `pyproject.toml`: 0.1.0 → 0.2.0
- README: добавлена секция CLI команд
- USER_GUIDE: примеры обновлены

### Fixed
- N/A (первый стабильный релиз CLI)

---

## 🙏 Благодарности

Спасибо MSW Framework Team за поддержку проекта!

---

**Версия:** 0.2.0  
**Лицензия:** MIT  
**Репозиторий:** (добавить ссылку)

