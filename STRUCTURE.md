# Структура проекта "Системная карьера"

**Назначение:** Этот документ объясняет структуру репозитория для разных ролей пользователей.

---

## 📚 Для участников курса

**Это материалы для прохождения 8-недельного курса:**

### Основные материалы
- **`weeks/`** — материалы 8 недель курса (Week_01 – Week_08)
- **`templates/`** — шаблоны для Личного контракта и других инструментов
- **`examples/`** — примеры заполненных контрактов (3 персоны)
- **`Personal_Contract_v4.0_Template.md`** — полный шаблон контракта

### Практики и инструменты
- **`practices/`** — 8 практик саморазвития (мышление письмом, стратегирование и др.)
- **`checklists/`** — чек-листы для еженедельных ритуалов
- **`case_studies/`** — кейсы-стади (аналитик, разработчик, лид)

### Руководства
- **`docs/guides/SELF_STUDY_GUIDE.md`** — руководство для самостоятельного прохождения
- **`docs/guides/How_to_fill_contract.md`** — как заполнять Личный контракт
- **`docs/guides/AI_ASSISTANT_GUIDE.md`** — работа с AI-консультантом

### CLI инструмент
- **`course_cli/`** — командная строка для навигации по курсу
  - `course start-week 1` — начать неделю
  - `course contract init` — создать контракт
  - `course progress` — показать прогресс

---

## 👨‍🏫 Для ведущих курса

**Материалы для проведения курса с группой участников:**

- **`docs/facilitators/PILOT_LAUNCH_GUIDE.md`** — полное руководство по запуску пилота
- **`docs/facilitators/PILOT_CHECKLIST.md`** — чек-лист для быстрого старта
- **`docs/facilitators/PLATFORM_COMPARISON.md`** — сравнение платформ (GitHub, Discord, Notion)
- **`docs/facilitators/Feedback_System.md`** — система обратной связи и peer review
- **`docs/facilitators/Metrics_Framework.md`** — система метрик для отслеживания прогресса
- **`docs/facilitators/templates/Weekly_Retro_Template.md`** — шаблон еженедельной ретроспективы
- **`docs/facilitators/templates/Progress_Dashboard_Template.md`** — dashboard прогресса участников

---

## 📚 Для исследователей

**Материалы для изучения методологии:**

- **`Systemic_Career_Framework_v2.md`** — полное описание фреймворка
- **`docs/factory/development/Glossary.md`** — глоссарий 68 концептов
- **`docs/navigation/`** — навигация по материалам
- **`Framework_Roadmap.md`** — визуальная карта фреймворка

---

## 🛠️ Для разработчиков курсов

**Инструменты для создания курсов (Course Factory):**

### Основные компоненты
- **`FACTORY_README.md`** — полное руководство по фабрике курсов
- **`ontology_toolkit/`** — граф понятий и AI-агенты для генерации контента
- **`scripts/`** — автоматизация и контроль качества
- **`docs/factory/`** — методология разработки курсов

### Система задач
- **`docs/factory/system/tasks.json`** — список задач разработки (15 задач)
- **`docs/factory/system/CHANGELOG.md`** — история изменений фабрики

### Документация
- **`FACTORY_CHANGELOG.md`** — история развития инструментов
- **`docs/factory/development/DEVELOPMENT_METHODOLOGY.md`** — методология создания курсов

---

## 🔒 Скрыто из публичного репозитория

**Эти папки/файлы НЕ попадают в публичный репозиторий (через `.gitignore`):**

- **`personal_contracts/`** — личные контракты участников
- **`private/`** — приватные заметки и черновики
- **`book_msw/`** — книга в разработке (личный проект автора)
- **`OtherMaterials/`** — архив исследований и материалов

**Почему скрыто:**
- Личные контракты содержат конфиденциальную информацию участников
- Приватные заметки — рабочие материалы, не готовые к публикации
- Книга в разработке — отдельный проект, не связанный с курсом
- Архив — хаотичные материалы, которые могут запутать участников

---

## 📂 Полная структура директорий

```
msw-framework/
├── weeks/                      # 8 недель курса
│   ├── Week_01_Foundation_v2.md
│   ├── Week_02_Direction.md
│   └── ... (Week_03 – Week_08)
│
├── templates/                  # Шаблоны контрактов и инструментов
│   ├── Personal_Contract_v1.0_Week1_Template.md
│   └── Week_*_*.md
│
├── examples/                   # Примеры заполнения
│   ├── persona_1_analyst_contract_v*.md
│   └── ...
│
├── practices/                  # 8 практик саморазвития
│   ├── Practice_01_Writing.md
│   └── ... (Practice_02 – Practice_08)
│
├── checklists/                 # Чек-листы
│   ├── Check_Public_Demo.md
│   └── Checklist_*.md
│
├── case_studies/               # Кейсы-стади
│   ├── Case_01_Analyst_Transition.md
│   └── ...
│
├── course_cli/                 # CLI инструмент
│   ├── README.md
│   └── course_cli/
│
├── ontology_toolkit/           # Граф понятий (для разработчиков)
├── scripts/                    # Автоматизация (для разработчиков)
├── docs/                       # Документация
│   ├── navigation/
│   └── factory/                # Фабрика курсов (для разработчиков)
│
├── visuals/                    # Диаграммы и визуализации
│
├── README.md                   # Главный файл (начните здесь!)
├── STRUCTURE.md                # Этот файл
├── SELF_STUDY_GUIDE.md         # Для участников
├── PILOT_LAUNCH_GUIDE.md       # Для ведущих
├── FACTORY_README.md           # Для разработчиков
├── Personal_Contract_v4.0_Template.md
└── ...
```

---

## 🚀 Быстрые ссылки

### Для новичков
1. Начните с **[README.md](README.md)** — выберите свою роль
2. Участники → **[SELF_STUDY_GUIDE.md](docs/guides/SELF_STUDY_GUIDE.md)**
3. Ведущие → **[PILOT_LAUNCH_GUIDE.md](docs/facilitators/PILOT_LAUNCH_GUIDE.md)**

### Навигация
- **[docs/navigation/INDEX.md](docs/navigation/INDEX.md)** — полный индекс материалов
- **[docs/navigation/NAVIGATION_GUIDE.md](docs/navigation/NAVIGATION_GUIDE.md)** — структурированная навигация
- **[docs/navigation/QUICK_START.md](docs/navigation/QUICK_START.md)** — быстрый старт

---

**Дата создания:** 9 октября 2025  
**Версия:** 1.0  
**Проект на:** 95% готовности к пилоту

