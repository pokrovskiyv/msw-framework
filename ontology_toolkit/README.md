# Ontology Toolkit

**Переиспользуемый инструмент для онтологической работы** с опорой на First Principles Framework (FPF).

## Назначение

Управление понятиями, их связями и контекстом проекта через:
- 📝 Markdown + YAML frontmatter (Git-friendly)
- 🤖 AI-ассистирование (автозаполнение полей)
- 🔗 Автоматическое построение связей между понятиями
- 📊 Экспорт в CSV/XLSX
- 💻 CLI + MCP интеграция с Cursor

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
pip install -e .
```

## Быстрый старт

### 1. Инициализация проекта

```bash
ontology init --project "Systemic_Career"
```

### 2. Добавление понятия

```bash
ontology add "Агентность" --auto-fill
```

### 3. Извлечение из текста

```bash
ontology extract --from week_01.md --output concepts/
```

### 4. Аудит понятий

```bash
ontology audit
```

### 5. Экспорт в CSV

```bash
ontology export --format csv --output systemic_career_v2.4.csv
```

## Команды CLI

| Команда | Описание |
|---------|----------|
| `init` | Создать структуру онтологии |
| `add` | Добавить понятие |
| `fill` | Заполнить поля понятия через AI |
| `extract` | Извлечь понятия из текста |
| `audit` | Проверить статусы и связи |
| `export` | Экспортировать в CSV/XLSX |
| `graph` | Построить граф связей |

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

## Интеграция с Cursor (MCP)

После установки доступны команды:
- `ontology.add_concept(name, source?)`
- `ontology.fill_concept(id, fields?)`
- `ontology.extract_from_selection()`
- `ontology.audit_concepts()`

## Лицензия

MIT

## Авторы

System Career Team
