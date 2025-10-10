# Проекты в submodules

Этот файл содержит список всех проектов, которые вынесены в отдельные Git submodules.

---

## Активные проекты

### 1. Making Systems Work (MSW)

**Путь:** `projects/msw/`  
**Репозиторий:** https://github.com/pokrovskiyv/msw-project  
**Статус:** Private (планируется Open Source)  
**Описание:** Методология "Making Systems Work" — эволюционный метод для управления жизнью и карьерой

**Содержимое:**
- Книга "Making Systems Work: An Evolutionary Method for Life and Career"
- Долгосрочное видение (vision.md)
- Roadmap развития (roadmap.md)
- Бизнес-модель Open Core (business_model.md)
- Журнал размышлений (reflections/)

**Документация:**
- [README проекта](projects/msw/README.md)
- [Видение MSW](projects/msw/vision.md)
- [Roadmap](projects/msw/roadmap.md)
- [Бизнес-модель](projects/msw/business_model.md)

**Начало:** Октябрь 2025

---

## Зачем submodules?

**Преимущества:**
1. **Изоляция** — каждый проект в отдельном репозитории
2. **Версионирование** — независимые коммиты
3. **Масштабируемость** — легко добавлять новые проекты
4. **Open Source готовность** — когда нужно, делаем репозиторий публичным
5. **Фокус** — курс остаётся курсом, проекты — проектами

---

## Как работать с submodules

### Клонирование репозитория с submodules

```bash
git clone --recurse-submodules https://github.com/pokrovskiyv/Course_System_Career.git
```

### Обновление submodules

```bash
git submodule update --remote --merge
```

### Работа внутри submodule

```bash
cd projects/msw
# Вносите изменения
git add .
git commit -m "Your commit message"
git push
```

### Коммит изменений в основном репозитории

```bash
cd ../..
git add projects/msw
git commit -m "Update MSW submodule"
git push
```

---

## Будущие проекты

В будущем могут быть добавлены другие проекты как submodules:
- Инструменты курса (отдельный репозиторий)
- Примеры применения (case studies)
- Исследовательские материалы

---

**Последнее обновление:** 10 октября 2025

