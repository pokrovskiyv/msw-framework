# Документация проекта

**Версия:** 2.0  
**Дата:** 8 октября 2025  

Документация разделена на три части в соответствии с двумя продуктами репозитория:

---

## 📚 [course/](course/) — Документация курса "Системная карьера"

**Для участников, ведущих, кураторов**

### Гайды для участников:
- [AI_CONTRACT_CONSULTANT_GUIDE.md](course/AI_CONTRACT_CONSULTANT_GUIDE.md) — AI-консультант для контракта
  - Пошаговое ведение по разделам
  - Проверка онтологической чистоты
  - Автоматическая активация в Cursor

**Целевая аудитория:** Участники курса, ведущие, кураторы

---

## 🏭 [factory/](factory/) — Документация фабрики курсов

**Для создателей курсов и разработчиков инструментов**

### 🛠️ [development/](factory/development/) — Методология создания
- [DEVELOPMENT_METHODOLOGY.md](factory/development/DEVELOPMENT_METHODOLOGY.md) — полный пайплайн создания курсов (1098 строк)
  - Стадия 1: Исследование и валидация (7 шагов)
  - Стадия 2: Разработка курса (итерационная)
- [Glossary.md](factory/development/Glossary.md) — глоссарий системных терминов
- [CURSOR_SETUP.md](factory/development/CURSOR_SETUP.md) — настройка среды разработки

### 🤖 [automation/](factory/automation/) — Автоматизация
- [AUTOMATION_SUMMARY.md](factory/automation/AUTOMATION_SUMMARY.md) — обзор автоматизации
- [AUTOMATION_IMPLEMENTATION.md](factory/automation/AUTOMATION_IMPLEMENTATION.md) — детали реализации
- [QUICK_START_CLI.md](factory/automation/QUICK_START_CLI.md) — быстрый старт CLI

### 🔧 [system/](factory/system/) — Системная документация
- [ASSESSMENT.md](factory/system/ASSESSMENT.md) — оценка готовности компонентов
- [CHANGELOG.md](factory/system/CHANGELOG.md) — старая история изменений
- [CLEANUP_REPORT.md](factory/system/CLEANUP_REPORT.md) — отчёт об очистке
- [REPOSITORY_ANALYSIS.md](factory/system/REPOSITORY_ANALYSIS.md) — анализ структуры
- [tasks.json](factory/system/tasks.json) — задачи разработки

**Целевая аудитория:** Разработчики, создатели курсов, контрибьюторы

---

## 🧭 [navigation/](navigation/) — Общая навигация

**Для всех пользователей**

- [NAVIGATION_GUIDE.md](navigation/NAVIGATION_GUIDE.md) — структурированная навигация по ролям
- [INDEX.md](navigation/INDEX.md) — полный индекс материалов
- [QUICK_START.md](navigation/QUICK_START.md) — быстрый старт

---

## 🎯 Для кого эта документация

### 👤 Участник курса
Основные материалы находятся в корне репозитория:
- `weeks/` — материалы 8 недель курса
- `templates/` — шаблоны для участников
- `Personal_Contract_v4.0_Template.md` — шаблон контракта

### 👨‍🏫 Ведущий курса
Материалы для проведения курса:
- `PILOT_LAUNCH_GUIDE.md` — руководство по запуску
- `PILOT_CHECKLIST.md` — чек-лист для быстрого старта
- `PLATFORM_COMPARISON.md` — сравнение платформ

### 🛠️ Разработчик
Системная документация:
- `docs/development/` — методология и глоссарий
- `docs/system/` — оценка и задачи
- `docs/automation/` — автоматизация

### 📚 Исследователь
Теоретические материалы:
- `Systemic_Career_Framework_v2.md` — основной фреймворк
- `docs/development/Glossary.md` — глоссарий понятий
- `OtherMaterials/` — архивные материалы

---

## 🔍 Быстрый поиск

### По типам контента
- **Системные файлы:** `docs/system/`
- **Разработка:** `docs/development/`
- **Автоматизация:** `docs/automation/`
- **Навигация:** `docs/navigation/`

### По ролям
- **Участник:** корневой каталог + `weeks/`, `templates/`
- **Ведущий:** корневой каталог + `docs/navigation/`
- **Разработчик:** `docs/development/`, `docs/system/`, `docs/automation/`
- **Исследователь:** корневой каталог + `docs/development/`

---

## 📖 Связанные документы

### Основные
- **[README.md](../README.md)** — главная страница проекта
- **[Systemic_Career_Framework_v2.md](../Systemic_Career_Framework_v2.md)** — основной фреймворк

### Навигация
- **[QUICK_START.md](navigation/QUICK_START.md)** — быстрый старт
- **[NAVIGATION_GUIDE.md](navigation/NAVIGATION_GUIDE.md)** — полная навигация
- **[INDEX.md](navigation/INDEX.md)** — индекс материалов

---

## 🎯 Принципы организации

### Логическая группировка
- Системные файлы отделены от пользовательских
- Документация разработки сгруппирована
- Навигация вынесена в отдельную папку

### Удобство использования
- Корневой каталог содержит только основные материалы
- Системная документация не мешает пользователям
- Чёткая структура для разных ролей

### Поддержка
- Легче находить нужные документы
- Проще обновлять системную документацию
- Лучшая организация проекта

---

## 🔗 Быстрые ссылки

### Для участников курса:
- [← Вернуться к курсу](../README.md)
- [Начать неделю 1](../weeks/Week_01_Foundation_v2.md)
- [Создать контракт](../templates/Personal_Contract_v1.0_Week1_Template.md)
- [История курса](../COURSE_CHANGELOG.md)

### Для создателей курсов:
- [← Перейти к фабрике](../FACTORY_README.md)
- [Методология создания](factory/development/DEVELOPMENT_METHODOLOGY.md)
- [Ontology toolkit](../ontology_toolkit/README.md)
- [Скрипты автоматизации](../scripts/README.md)
- [История фабрики](../FACTORY_CHANGELOG.md)

---

*Создано: 6 октября 2025*  
*Обновлено: 8 октября 2025*  
*Версия документа: 2.0*  
*Документация разделена на course/ и factory/*
