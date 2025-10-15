# Release Notes — v0.3.0 (AI Integration)

**Дата релиза:** 02.10.2025  
**Статус:** Beta

## 🎉 Основные изменения

### ✨ Новое: Универсальная AI Integration

**Поддержка 4 AI провайдеров:**
- ✅ **Anthropic Claude** (Sonnet, Opus, Haiku)
- ✅ **OpenAI ChatGPT** (GPT-4, GPT-4 Turbo, GPT-3.5)
- ✅ **Google Gemini** (Gemini Pro)
- ✅ **xAI Grok** (Grok-1, Grok-2)

### 🤖 Новые команды CLI

#### 1. `ontology config-ai`
Управление конфигурацией AI:
```bash
ontology config-ai --show              # Показать настройки
ontology config-ai --check             # Проверить доступность
ontology config-ai --list-providers    # Список провайдеров
```

#### 2. `ontology fill`
Автозаполнение понятий через AI:
```bash
ontology fill C_1                      # Заполнить все поля
ontology fill C_1 --fields definition,purpose  # Конкретные поля
ontology fill C_1 --provider openai    # Выбрать провайдер
ontology fill C_1 --context "..."      # Добавить контекст
```

**Что делает:**
- Анализирует название понятия
- Автоматически заполняет definition, purpose, meta_meta, examples
- Находит связи с существующими понятиями
- Меняет статус на `draft+filled`

#### 3. `ontology extract`
Извлечение понятий из текста:
```bash
ontology extract weeks/Week_01.md      # Из файла
ontology extract "Текст..."            # Из строки
ontology extract file.md --preview     # Только просмотр
ontology extract file.md --auto-add    # Сразу добавить
```

**Что делает:**
- Анализирует текст (MD, TXT файлы)
- Находит 3-7 ключевых понятий
- Автоматически заполняет все поля
- Показывает preview перед сохранением

### 🏗️ Архитектура AI модуля

```
ontology_toolkit/ai/
├── base_provider.py          # Базовый интерфейс AIProvider
├── factory.py                # Фабрика провайдеров
├── client.py                 # Унифицированный клиент
├── prompts.py                # Загрузка и рендеринг промптов
├── filler.py                 # Автозаполнение понятий
├── extractor.py              # Извлечение из текста
└── providers/
    ├── anthropic_provider.py
    ├── openai_provider.py
    ├── gemini_provider.py
    └── grok_provider.py
```

### 🔧 Конфигурация через ENV

```bash
# Выбор провайдера
ONTOLOGY_AI_PROVIDER=anthropic    # anthropic | openai | gemini | grok

# API ключи
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROK_API_KEY=xai-...

# Модель (опционально)
ONTOLOGY_AI_MODEL=claude-sonnet-4-20250514

# Температура (опционально)
ONTOLOGY_AI_TEMPERATURE=0.3
```

### 📦 Опциональные зависимости

```bash
# Только Anthropic (default)
pip install ontology-toolkit

# С OpenAI
pip install ontology-toolkit[ai-openai]

# С Gemini
pip install ontology-toolkit[ai-gemini]

# С Grok
pip install ontology-toolkit[ai-grok]

# Все провайдеры
pip install ontology-toolkit[ai-all]
```

## 🔄 Изменения в существующих модулях

### `pyproject.toml`
- Версия: `0.2.0` → `0.3.0`
- Статус: `Alpha` → `Beta`
- Добавлены optional dependencies для AI провайдеров
- Новые keywords: `ai`, `llm`

### `cli/main.py`
- Добавлены 3 новые команды: `config-ai`, `fill`, `extract`
- Интеграция с AI модулем

### `prompts_templates/`
- Используются существующие промпты: `concept_fill.md`, `context_extract.md`

## 📊 Статистика кода

| Модуль | Строк кода | Файлов | Новое |
|--------|-----------|--------|-------|
| AI providers | ~350 | 4 | ✅ |
| AI core | ~400 | 4 | ✅ |
| CLI commands | ~270 | - | ✅ |
| **Всего** | ~1020 | 8 | ✅ |

## 🚀 Примеры использования

### Пример 1: Быстрое заполнение понятия

```bash
# 1. Настройка (один раз)
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Добавить понятие
ontology add "Рефлексия"

# 3. Заполнить через AI
ontology fill C_1

# Результат:
# [OK] Понятие C_1 заполнено!
# Название: Рефлексия
# Определение: Процесс осмысления собственного опыта...
# Назначение: Извлечение уроков из прошлого опыта...
# Тип: характеристика
# Примеры: 3
# Статус: draft+filled
```

### Пример 2: Извлечение из материалов курса

```bash
# Извлечь понятия из недели 1
ontology extract weeks/Week_01_Foundation.md

# AI находит 5 понятий:
# - Стратегирование
# - Целеполагание
# - Рефлексия
# - Неделя
# - Личный контракт

# Подтверждаем и добавляем в онтологию
```

### Пример 3: Сравнение провайдеров

```bash
# Попробуйте разные провайдеры для одного понятия
ontology fill C_1 --provider anthropic
ontology fill C_1 --provider openai
ontology fill C_1 --provider gemini

# Выберите лучший результат
```

## 📚 Новая документация

- **AI_GUIDE.md** — полное руководство по AI Integration
- **WINDOWS_ENCODING.md** — решение проблем с кодировкой (v0.2.0)
- Обновлены: README.md, ROADMAP.md

## ⚠️ Breaking Changes

Нет breaking changes. Версия полностью обратно совместима с v0.2.0.

## 🐛 Исправленные баги

- Нет (новый функционал)

## 🔮 Что дальше (v0.4.0)

Планируемые фичи:
- Импорт из CSV/XLSX обратно в онтологию
- Поддержка Methods, Systems, Problems, Artifacts
- Расширенный граф с фильтрами
- `ontology fix-relations` — автоисправление связей
- Batch AI processing с progress bar
- AI-предложения для связей между понятиями

## 🙏 Благодарности

- Anthropic за Claude API
- OpenAI за GPT API
- Google за Gemini API
- xAI за Grok API

## 📄 Лицензия

MIT — используйте свободно в своих проектах

---

**Установка:**
```bash
pip install ontology-toolkit
```

**Быстрый старт:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
ontology init --project "My Project"
ontology add "Понятие 1"
ontology fill C_1
```

**Документация:**
- [README.md](./README.md) — общая информация
- [AI_GUIDE.md](./AI_GUIDE.md) — AI Integration guide
- [USER_GUIDE.md](./USER_GUIDE.md) — полное руководство

**Вопросы и поддержка:**  
MSW Framework Team

