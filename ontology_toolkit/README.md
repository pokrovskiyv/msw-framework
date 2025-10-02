# Ontology Toolkit

**Переиспользуемый инструмент для онтологической работы** с опорой на First Principles Framework (FPF).

## Назначение

Управление понятиями, их связями и контекстом проекта через:
- 📝 Markdown + YAML frontmatter (Git-friendly)
- 🔄 **AI-ассистирование** — архитектура готова (v0.3.0), реализация в процессе
- 🔗 Автоматическое построение связей между понятиями
- 📊 Экспорт в CSV/XLSX
- 💻 CLI для работы из терминала и Cursor

## Ключевые различения (FPF)

- **Метод работы с понятиями** (промпты/правила) ↔ **Данные** (сами понятия) ↔ **Инструмент** (код)
- **Понятие** ↔ **Проблема** ↔ **Метод** ↔ **Система** ↔ **Артефакт**
- **Статусы**: `draft` → `draft+filled` → `approved`

## Структура проекта

```
.ontology/
├── README.md              # Описание онтологии проекта
├── CHANGELOG.md           # История изменений
├── context/
│   └── project_context.yaml
├── prompts/
│   ├── concept_fill.md
│   └── context_extract.md
├── concepts/
│   ├── C_1_gates.md
│   └── C_2_agency.md
├── methods/
│   └── M_1_weekly_strategizing.md
├── systems/
│   └── S_1_cyberpersonality.md
├── problems/
│   └── P_1_ontological_drift.md
└── artifacts/
    └── A_1_personal_contract.md
```

## Установка

```bash
cd ontology_toolkit
pip install .
```

> **⚠️ Windows пользователям**: Для корректной работы с кириллицей — 5 минут настройки:
> 
> 1. 🚀 **[Быстрая настройка](./WINDOWS_SETUP.md)** — 4 простых шага
> 2. 📖 **[Полная инструкция](./WINDOWS_ENCODING.md)** — если что-то пошло не так
> 
> **✅ Результат**: кириллица работает везде — в консоли, в файлах, в экспорте!

## Быстрый старт (CLI)

### 1. Инициализация проекта

```bash
ontology init --project "Systemic_Career"
```

Создаёт структуру `.ontology/{concepts,methods,systems,problems,artifacts}` + README.

### 2. Добавление понятия

```bash
ontology add "Агентность"
```

Создаёт черновик в `.ontology/concepts/C_1_agentnost.md`.

### 3. Просмотр списка

```bash
ontology list                    # Все объекты
ontology list --status draft     # Только черновики
ontology list --prefix C         # Только понятия
```

### 4. Проверка качества

```bash
ontology audit
```

Показывает статистику, broken links, изолированные узлы.

### 5. Экспорт

```bash
ontology export --format csv --output systemic_career_v2.4.csv
ontology export --format xlsx --output systemic_career_v2.4.xlsx
```

### 6. Граф связей

```bash
ontology graph --output visuals/ontology.mmd
```

Создаёт Mermaid диаграмму связей между понятиями.

## 🔄 AI Команды (v0.3.1)

> **Статус:** ✅ Полностью реализовано и готово к использованию!

**Доступные команды:**

- `ontology config-ai` — управление конфигурацией AI провайдеров
- `ontology fill <ID>` — автозаполнение полей понятия через AI (⚡ 1 понятие = 1 запрос для качества)
- `ontology extract <file>` — извлечение понятий из текста

📖 **Документация:** 
- [AI_GUIDE.md](./AI_GUIDE.md) — полное руководство по использованию AI функций
- [QUALITY_PRINCIPLES.md](./QUALITY_PRINCIPLES.md) — принципы качества и best practices

### ⚡ Принцип качества

**1 понятие = 1 запрос** — для максимального качества заполнения AI обрабатывает только одно понятие за раз. Это обеспечивает глубокую проработку определений, примеров и связей.

> 📖 Подробнее: [QUALITY_PRINCIPLES.md](./QUALITY_PRINCIPLES.md)

### Контекст проекта для AI

Для улучшения качества AI-заполнения создайте файл `.ontology/context/project_context.yaml`:

```yaml
project:
  name: "Systemic Career"
  domain: "Системная карьера"
  
purpose: |
  Систематизация знаний о карьерном развитии
  через фреймворк First Principles

key_concepts: |
  Агентность, Мастерство, Стратегирование, Ритмы
  
guidelines: |
  - Использовать активный залог
  - Фокус на практическом применении
  - Избегать абстрактных формулировок
```

**AI автоматически использует этот контекст при заполнении понятий!**

Этот файл создаётся автоматически при `ontology init`. Просто отредактируйте его под свой проект.

### 🚀 Batch заполнение

Для заполнения всех пустых понятий сразу используйте команду `fill-all`:

```bash
# Показать что будет заполнено (без выполнения)
ontology fill-all --dry-run

# Заполнить все понятия со статусом "draft" (исключая approved и draft+filled)
ontology fill-all

# Настроить исключения
ontology fill-all --exclude-status "approved,draft+filled,custom"

# Изменить паузу между запросами (по умолчанию 2 секунды)
ontology fill-all --delay 5
```

**Принцип качества сохраняется** - каждое понятие заполняется отдельным запросом для максимального качества!

## Команды CLI

| Команда | Описание | Пример |
|---------|----------|--------|
| **Базовые** |||
| `init` | Создать структуру онтологии | `ontology init --project "My Project"` |
| `add` | Добавить понятие | `ontology add "Агентность"` |
| `list` | Показать список объектов | `ontology list --status draft` |
| `audit` | Проверить статусы и связи | `ontology audit` |
| `export` | Экспортировать в CSV/XLSX | `ontology export --format csv` |
| `graph` | Построить граф связей (Mermaid) | `ontology graph` |
| **AI (v0.3.1)** ✅ |||
| `config-ai` | Управление AI конфигурацией | `ontology config-ai --check` |
| `fill` | Заполнить поля через AI | `ontology fill C_1` |
| `fill-all` | Заполнить все пустые понятия | `ontology fill-all --dry-run` |
| `extract` | Извлечь понятия из текста | `ontology extract file.md` |

## Формат понятия

```markdown
---
id: C_2
name: Агентность
status: approved
meta_meta: Характеристика
relations:
  - type: enables
    target: C_22_personal_contract
  - type: relates_to
    target: C_6_life_mastery
created: 2025-09-15
updated: 2025-10-01
---

# Агентность

## Definition
Характеристика личности, выражающаяся в сильном желании...

## Purpose
Позволяет человеку брать на себя ответственность...

## Examples
- Самостоятельное планирование карьерного пути
- Инициирование проектов вне должностных обязанностей
```

## Интеграция с Cursor

После установки Cursor может выполнять команды `ontology` через терминал:

```
Вы: "Добавь понятие Стратегирование в онтологию"
↓
Cursor выполняет: ontology add "Стратегирование"
```

См. `.cursorrules` для настройки интеграции.

## Лицензия

MIT

## Документация

- **[ROADMAP.md](ROADMAP.md)** — план развития проекта
- **[CHANGELOG.md](CHANGELOG.md)** — история изменений по версиям
- **[AI_GUIDE.md](AI_GUIDE.md)** — полное руководство по AI функциям
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** ⭐ — быстрая настройка для Windows (5 минут)
- **[WINDOWS_ENCODING.md](WINDOWS_ENCODING.md)** — полное решение проблем с кодировкой

## Версия

**v0.3.0** — CLI + AI интеграция (полностью работает!)

См. [CHANGELOG.md](CHANGELOG.md) для истории изменений.

## Авторы

System Career Team
