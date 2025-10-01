# Онтология проекта: {project_name}

## Описание

{project_description}

## Метаданные

- **Версия:** {version}
- **Создано:** {created}
- **Язык:** {language}
- **Инструмент:** Ontology Toolkit v{toolkit_version}

## Статистика

- **Понятий (concepts):** {concepts_count}
- **Методов (methods):** {methods_count}
- **Систем (systems):** {systems_count}
- **Проблем (problems):** {problems_count}
- **Артефактов (artifacts):** {artifacts_count}

### По статусам

- **Утверждено (approved):** {approved_count}
- **Заполнено (draft+filled):** {draft_filled_count}
- **Черновик (draft):** {draft_count}

## Структура

```
.ontology/
├── README.md              # Этот файл
├── CHANGELOG.md           # История изменений
├── context/
│   └── project_context.yaml
├── prompts/
│   ├── concept_fill.md
│   └── context_extract.md
├── concepts/
│   └── C_*.md
├── methods/
│   └── M_*.md
├── systems/
│   └── S_*.md
├── problems/
│   └── P_*.md
└── artifacts/
    └── A_*.md
```

## Ключевые понятия

{key_concepts_list}

## Связи (граф)

Основные кластеры связей:

{relations_clusters}

## Использование

### Добавить понятие

```bash
ontology add "Название понятия" --auto-fill
```

### Аудит

```bash
ontology audit
```

### Экспорт

```bash
ontology export --format csv --output {project_name}_export.csv
```

## История изменений

См. [CHANGELOG.md](CHANGELOG.md)
