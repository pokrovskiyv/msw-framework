# AI Integration Guide — Ontology Toolkit v0.3.0

Руководство по использованию AI для автоматизации работы с онтологией.

## 🎯 Возможности AI

1. **Автозаполнение понятий** — AI анализирует название понятия и автоматически заполняет definition, purpose, meta_meta, examples
2. **Извлечение понятий из текста** — AI анализирует текст (файлы MD, TXT) и извлекает ключевые понятия
3. **Построение связей** — AI автоматически находит связи с существующими понятиями

## 🤖 Поддерживаемые провайдеры

| Провайдер | Модель по умолчанию | API Key | Установка |
|-----------|---------------------|---------|-----------|
| **Anthropic Claude** | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` | По умолчанию |
| **OpenAI ChatGPT** | `gpt-4-turbo` | `OPENAI_API_KEY` | `pip install ontology-toolkit[ai-openai]` |
| **Google Gemini** | `gemini-pro` | `GEMINI_API_KEY` | `pip install ontology-toolkit[ai-gemini]` |
| **xAI Grok** | `grok-2-latest` | `GROK_API_KEY` | `pip install ontology-toolkit[ai-grok]` |

## 📦 Установка

### Только Anthropic (default)
```bash
pip install ontology-toolkit
```

### С поддержкой всех провайдеров
```bash
pip install ontology-toolkit[ai-all]
```

### Конкретный провайдер
```bash
# OpenAI
pip install ontology-toolkit[ai-openai]

# Gemini
pip install ontology-toolkit[ai-gemini]

# Grok
pip install ontology-toolkit[ai-grok]
```

## 🔧 Настройка

### 1. Получить API ключ

#### Anthropic Claude
1. Зарегистрируйтесь на https://console.anthropic.com/
2. Создайте API ключ
3. Установите переменную окружения:
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...
```

#### OpenAI
1. Зарегистрируйтесь на https://platform.openai.com/
2. Создайте API ключ
3. Установите переменную:
```bash
export OPENAI_API_KEY=sk-...
```

#### Google Gemini
1. Получите ключ на https://makersuite.google.com/app/apikey
2. Установите:
```bash
export GEMINI_API_KEY=...
```

#### xAI Grok
1. Получите ключ на https://x.ai/
2. Установите:
```bash
export GROK_API_KEY=xai-...
```

### 2. Выбрать провайдер (опционально)

По умолчанию используется **Anthropic Claude**. Для переключения:

```bash
# Использовать OpenAI
export ONTOLOGY_AI_PROVIDER=openai

# Использовать Gemini
export ONTOLOGY_AI_PROVIDER=gemini

# Использовать Grok
export ONTOLOGY_AI_PROVIDER=grok
```

### 3. Настроить модель (опционально)

```bash
# Для Claude
export ONTOLOGY_AI_MODEL=claude-opus-4-20250514

# Для OpenAI
export ONTOLOGY_AI_MODEL=gpt-4

# Для Gemini
export ONTOLOGY_AI_MODEL=gemini-pro

# Для Grok
export ONTOLOGY_AI_MODEL=grok-1
```

### 4. Проверить конфигурацию

```bash
ontology config-ai --check
```

Вывод:
```
[OK] anthropic: Доступен
```

## 🚀 Использование

### Команда `ontology config-ai`

#### Показать текущую конфигурацию
```bash
ontology config-ai
# или
ontology config-ai --show
```

Вывод:
```
AI Configuration
Provider:    anthropic
Model:       claude-sonnet-4-20250514
Temperature: 0.3
Status:      ✓ Доступен
```

#### Проверить доступность
```bash
ontology config-ai --check
```

#### Список провайдеров
```bash
ontology config-ai --list-providers
```

Вывод:
```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Провайдер ┃ Модель по умолчанию       ┃ Переменная ENV    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ anthropic │ claude-sonnet-4-20250514  │ ANTHROPIC_API_KEY │
│ openai    │ gpt-4-turbo               │ OPENAI_API_KEY    │
│ gemini    │ gemini-pro                │ GEMINI_API_KEY    │
│ grok      │ grok-2-latest             │ GROK_API_KEY      │
└───────────┴───────────────────────────┴───────────────────┘
```

### Команда `ontology fill`

> ⚠️ **Принцип качества: 1 понятие = 1 запрос**
>
> Для обеспечения максимального качества заполнения, AI обрабатывает **только одно понятие за раз**.
> Это позволяет:
> - Полностью сфокусировать внимание AI на конкретном понятии
> - Глубоко проработать определение, примеры и связи
> - Избежать путаницы между понятиями
> - Легко контролировать и исправлять результат

#### Автозаполнить понятие
```bash
# Добавить draft-понятие
ontology add "Продуктивное состояние"

# Заполнить через AI (одно понятие!)
ontology fill C_4
```

Вывод:
```
Загрузка онтологии...
Загружено объектов: 3
Заполнение C_4 через Anthropic Claude (claude-sonnet-4-20250514)...

[OK] Понятие C_4 заполнено!
Название: Продуктивное состояние
Определение: Состояние, при котором человек работает с максимальной эффективностью, испытывая поток...
Назначение: Достижение максимальной производительности при сохранении качества и удовольствия от работы...
Тип: состояние
Примеры: 3
Статус: draft+filled
```

#### Заполнить только определённые поля
```bash
ontology fill C_4 --fields definition,purpose
```

#### Добавить дополнительный контекст
```bash
ontology fill C_4 --context "В контексте работы программиста"
```

#### Использовать другой провайдер
```bash
# Использовать OpenAI для этой команды
ontology fill C_4 --provider openai

# Использовать конкретную модель
ontology fill C_4 --provider openai --model gpt-4
```

#### Batch заполнение всех понятий

```bash
# Показать что будет заполнено (dry run)
ontology fill-all --dry-run

# Заполнить все пустые понятия (исключая approved и draft+filled)
ontology fill-all

# Настроить исключения
ontology fill-all --exclude-status "approved,draft+filled,review"

# Изменить паузу между запросами
ontology fill-all --delay 5
```

> ⚡ **Принцип качества сохраняется**: каждое понятие заполняется отдельным запросом!

### Команда `ontology extract`

#### Извлечь понятия из файла
```bash
ontology extract weeks/Week_01_Foundation.md
```

Вывод:
```
Загрузка онтологии...
Загружено объектов: 3
Извлечение понятий из Week_01_Foundation.md...

         Извлечено понятий: 5         
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ ID   ┃ Название           ┃ Определение     ┃ Тип            ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ C_4  │ Стратегирование    │ Процесс...      │ метод          │
│ C_5  │ Целеполагание      │ Определение...  │ метод          │
│ C_6  │ Рефлексия          │ Осмысление...   │ характеристика │
│ C_7  │ Неделя             │ Базовая...      │ артефакт       │
│ C_8  │ Личный контракт    │ Документ...     │ артефакт       │
└──────┴────────────────────┴─────────────────┴────────────────┘

Добавить эти понятия в онтологию? [y/N]: y

[OK] Добавлено 5 понятий!
```

#### Только предпросмотр (не сохранять)
```bash
ontology extract weeks/Week_01.md --preview
```

#### Автоматически добавить без подтверждения
```bash
ontology extract weeks/Week_01.md --auto-add
```

#### Извлечь из текста (не файла)
```bash
ontology extract "Агентность — способность инициировать изменения..."
```

## 💡 Полезные паттерны

### Batch-заполнение всех draft понятий

```bash
# Сначала добавьте draft-понятия
ontology add "Понятие 1"
ontology add "Понятие 2"
ontology add "Понятие 3"

# Заполните их последовательно
for id in C_1 C_2 C_3; do
    ontology fill $id
done
```

### Извлечение из всех файлов недели

```bash
for file in weeks/*.md; do
    ontology extract "$file" --auto-add
done
```

### Переключение между провайдерами

```bash
# Попробуйте разные провайдеры для сравнения
ontology fill C_1 --provider anthropic
ontology fill C_2 --provider openai
ontology fill C_3 --provider gemini
ontology fill C_4 --provider grok
```

## ⚙️ Продвинутые настройки

### Температура генерации

```bash
# Более детерминированные ответы (0.0-0.3)
export ONTOLOGY_AI_TEMPERATURE=0.1

# Более креативные ответы (0.5-1.0)
export ONTOLOGY_AI_TEMPERATURE=0.7
```

### Сохранение настроек в `.env`

Создайте файл `.env` в корне проекта:

```env
# Провайдер по умолчанию
ONTOLOGY_AI_PROVIDER=anthropic

# API ключи
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROK_API_KEY=xai-...

# Модель и температура
ONTOLOGY_AI_MODEL=claude-sonnet-4-20250514
ONTOLOGY_AI_TEMPERATURE=0.3
```

Затем используйте `python-dotenv`:
```bash
pip install python-dotenv
python-dotenv run ontology fill C_1
```

## 🐛 Troubleshooting

### Ошибка: "API ключ не найден"

```bash
# Проверьте переменные окружения
echo $ANTHROPIC_API_KEY

# Установите ключ
export ANTHROPIC_API_KEY=sk-ant-...

# Проверьте доступность
ontology config-ai --check
```

### Ошибка: "Библиотека провайдера не установлена"

```bash
# Для OpenAI
pip install ontology-toolkit[ai-openai]

# Для Gemini
pip install ontology-toolkit[ai-gemini]

# Для всех провайдеров
pip install ontology-toolkit[ai-all]
```

### AI генерирует некорректные данные

1. Попробуйте другой провайдер: `--provider openai`
2. Добавьте контекст: `--context "..."`
3. Уменьшите температуру: `export ONTOLOGY_AI_TEMPERATURE=0.1`
4. Отредактируйте файл понятия вручную после генерации

### Медленная генерация

- Claude Sonnet 4 — самый быстрый (2-5 сек)
- GPT-4 Turbo — средний (5-10 сек)
- Gemini Pro — быстрый (3-7 сек)
- Grok — средний (5-10 сек)

## 📊 Сравнение провайдеров

| Критерий | Anthropic | OpenAI | Gemini | Grok |
|----------|-----------|--------|--------|------|
| **Скорость** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Качество** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Цена** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Русский язык** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Рекомендация:** Используйте **Anthropic Claude Sonnet 4** — лучший баланс скорости, качества и цены.

## 💡 Best Practices

### Принцип качества: 1 понятие = 1 запрос

Для достижения максимального качества всегда обрабатывайте **одно понятие за раз**:

✅ **Правильно:**
```bash
ontology fill C_1  # Фокус на одном понятии
ontology fill C_2  # Следующее понятие отдельно
ontology fill C_3  # И так далее
```

❌ **Неправильно:**
```bash
# Batch-обработка снижает качество каждого понятия
ontology fill C_1 C_2 C_3  # НЕ поддерживается намеренно
```

**Почему это важно:**
- AI может посвятить больше "внимания" одному понятию
- Глубже анализирует контекст и связи
- Генерирует более качественные примеры
- Меньше риск путаницы между понятиями
- Легче контролировать и корректировать результат

### Итеративный подход

```bash
# 1. Добавляем понятие
ontology add "Агентность"

# 2. Заполняем через AI
ontology fill C_10

# 3. Проверяем результат
ontology list C_10 --verbose

# 4. Если нужно, корректируем вручную
# Редактируем .ontology/concepts/C_10_agentnost.md

# 5. Переходим к следующему
ontology add "Мастерство"
ontology fill C_11
```

### Используйте контекст проекта

Создайте `.ontology/context/project_context.yaml` для автоматического улучшения качества:

```yaml
project:
  name: "Systemic Career"
  domain: "Системная карьера"

key_concepts: "Агентность, Мастерство, Стратегирование"
guidelines: |
  - Использовать активный залог
  - Фокус на практическом применении
```

AI автоматически учтёт этот контекст при заполнении!

### Когда использовать --context

Параметр `--context` используйте для **дополнительного** контекста к конкретному понятию:

```bash
# Общий контекст уже загружен из project_context.yaml
# Добавляем специфичный контекст для этого понятия:
ontology fill C_15 --context "Относится к Week 6: Mastery"
```

## 🎓 Примеры использования

См. файлы в `examples/`:
- `ai_fill_example.sh` — пример автозаполнения
- `ai_extract_example.sh` — пример извлечения понятий
- `ai_batch_processing.sh` — массовая обработка

---

**Версия:** v0.3.0  
**Дата:** 02.10.2025  
**Автор:** System Career Team

