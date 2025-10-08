# Визуальная карта фреймворка «Системная карьера»

**Назначение:** Обзор структуры курса, взаимосвязей между элементами и пути участника от Недели 0 до Недели 8.

**Дата:** 08.10.2025  
**Версия:** 1.0

---

## 🗺️ Путь участника (8 недель)

```mermaid
flowchart TD
    Start([Старт курса]) --> W0[Week 0: Онбординг<br/>Подготовка инструментов]
    
    W0 --> W1[Week 1: Фундамент<br/>Аудит ролей + Неудовлетворённости]
    W1 --> Contract1[Контракт v1.0:<br/>Манифест, Принципы, Роли]
    
    W1 --> W2[Week 2: Направление<br/>Стратегия-гипотеза]
    W2 --> Contract2[Контракт v2.0:<br/>+ Стратегия + Красные зоны]
    
    W2 --> W3[Week 3: Ценность<br/>Проекты и рабочие продукты]
    W3 --> Contract25[Контракт v2.5:<br/>+ Проекты + Эпики]
    
    W3 --> W4[Week 4: Ритм<br/>Недельные спринты]
    W4 --> Rhythm{Ритм установлен?}
    
    Rhythm -->|Да| W5[Week 5: Контекст<br/>Окружение и связи]
    Rhythm -->|Нет| W4
    
    W5 --> W6[Week 6: Мастерство<br/>Развитие компетенций]
    W6 --> W7[Week 7: Коммуникация<br/>Публичность и репутация]
    W7 --> W8[Week 8: Устойчивость<br/>Энергобюджет и баланс]
    
    W8 --> Contract4[Контракт v4.0:<br/>Полная сборка]
    Contract4 --> End([Завершение курса<br/>Готовность к росту])
    
    style Start fill:#e1f5e1
    style W1 fill:#fff4e1
    style W2 fill:#ffe1e1
    style W3 fill:#e1f0ff
    style W4 fill:#f0e1ff
    style W8 fill:#e1ffe1
    style End fill:#ffe1f0
```

---

## 🧩 Структура Личного контракта (инкрементальная)

```mermaid
graph LR
    subgraph "v1.0 (Неделя 1)"
        V1_M[Манифест]
        V1_P[Принципы]
        V1_R[Роли 5+]
        V1_N[Неудовлетворённости 3+]
    end
    
    subgraph "v2.0 (Неделя 2)"
        V2_S[Стратегия-гипотеза]
        V2_Z[Красные зоны]
    end
    
    subgraph "v2.5 (Неделя 3)"
        V25_Pr[Проекты]
        V25_E[Эпики с воротами]
    end
    
    subgraph "v4.0 (Неделя 8)"
        V4_Sp[Недельные спринты]
        V4_O[Окружение]
        V4_En[Энергобюджет]
        V4_M[Метрики прогресса]
    end
    
    V1_M --> V2_S
    V1_R --> V2_S
    V1_N --> V2_S
    V2_S --> V25_Pr
    V25_Pr --> V4_Sp
```

---

## 🎯 Ключевые цепочки концептов

### Цепочка 1: От неудовлетворённости к артефакту

```mermaid
flowchart LR
    A[Неудовлетворённость<br/>Эмоция 7-10/10] --> B[Стратегирование<br/>5 вариантов]
    B --> C[Выбор метода<br/>Гипотеза]
    C --> D[Проект<br/>Реализация]
    D --> E[Эпики<br/>3-4 этапа]
    E --> F[Спринты<br/>Недельные]
    F --> G[Артефакты<br/>Публичные]
    G --> H[Репутация<br/>Офферы]
    
    style A fill:#ffcccc
    style D fill:#ccffcc
    style G fill:#ccccff
    style H fill:#ffffcc
```

---

### Цепочка 2: Недельный ритм

```mermaid
flowchart TD
    Sunday[Воскресенье<br/>Сессия стратегирования<br/>60 мин]
    
    Sunday --> Retro[Ретроспектива<br/>15 мин]
    Sunday --> Strategy[Проверка стратегии<br/>15 мин]
    Sunday --> Planning[Планирование недели<br/>15 мин]
    Sunday --> Update[Обновление контракта<br/>10 мин]
    
    Planning --> Mon[Понедельник<br/>Слот 1: 2 ч]
    Mon --> Wed[Среда<br/>Слот 2: 2 ч]
    Wed --> Sat[Суббота<br/>Слот 3: 2 ч<br/>+ Публикация]
    
    Sat --> NextSunday[Следующее<br/>воскресенье]
    NextSunday --> Sunday
    
    style Sunday fill:#ffe1e1
    style Mon fill:#e1f0ff
    style Wed fill:#e1f0ff
    style Sat fill:#e1ffe1
```

---

### Цепочка 3: Практики саморазвития

```mermaid
mindmap
  root((Практики<br/>саморазвития))
    Базовые
      Мышление письмом
        Исчезающие заметки
        Заготовки
        Публикации
      Планирование
        Проекты → Эпики
        Недельные спринты
        Защищённые слоты
      Учёт времени
        Трекинг часов
        Инвестиции vs траты
    Продвинутые
      Стратегирование
        Сессии 60 мин
        Проверка гипотез
        Адаптация
      Формирование окружения
        Менторы
        Peers
        Комьюнити
      Публичность
        Посты
        Статьи
        Доклады
    Поддерживающие
      Чтение
        Конспекты
        Применение
      Проговаривание
        1-on-1
        Доклады
      Восстановление
        Спорт
        Медитация
        Полные выходные
```

---

## 📚 Структура материалов курса

```mermaid
graph TB
    subgraph "Для участников"
        Weeks[8 недель курса<br/>weeks/]
        Contract[Личный контракт<br/>v1.0 → v4.0]
        Templates[Шаблоны<br/>templates/]
        Checklists[Чек-листы<br/>checklists/]
        Practices[Практики<br/>practices/]
        Examples[Примеры<br/>examples/]
        Cases[Кейсы-стади<br/>case_studies/]
    end
    
    subgraph "Для ведущих"
        Metrics[Система метрик<br/>Metrics_Framework]
        Feedback[Обратная связь<br/>Feedback_System]
        Pilot[Запуск пилота<br/>PILOT_LAUNCH_GUIDE]
    end
    
    subgraph "Справочные"
        FAQ[FAQ]
        Troubleshooting[Troubleshooting]
        Glossary[Глоссарий 68 терминов]
        Ontology[Онтология<br/>visuals/]
    end
    
    Weeks --> Contract
    Contract --> Templates
    Templates --> Practices
    Practices --> Examples
    Examples --> Cases
    
    Cases --> FAQ
    Cases --> Troubleshooting
```

---

## 🎓 Критические различения (визуально)

```mermaid
graph LR
    subgraph "Различение 1"
        Role[Роль<br/>Способность<br/>Аналитик причин багов]
        Person[Носитель<br/>Человек<br/>Анна Смирнова]
        Position[Должность<br/>Назначение<br/>QA Engineer]
        
        Person -->|исполняет| Role
        Role -.->|НЕ РАВНО| Position
        Role -->|может привести к| Position
    end
    
    subgraph "Различение 2"
        Method[Метод<br/>Способ<br/>Мышление письмом]
        Plan[План<br/>Документ<br/>Личный контракт]
        Work[Работа<br/>Процесс<br/>Карьера траектория]
        
        Method -.->|НЕ РАВНО| Plan
        Plan -.->|НЕ РАВНО| Work
        Method -->|используется в| Plan
        Plan -->|направляет| Work
    end
    
    subgraph "Различение 3"
        Problem[Проблема<br/>Объективный факт<br/>Нет обучения]
        Dissatisfaction[Неудовлетворённость<br/>Состояние<br/>В компетентности]
        Emotion[Эмоции<br/>Чувства<br/>Тревога 8/10]
        
        Problem -.->|порождает| Dissatisfaction
        Dissatisfaction -.->|проявляется как| Emotion
    end
    
    style Role fill:#ffffcc
    style Position fill:#ffeecc
    style Method fill:#eeccff
    style Plan fill:#cceeff
    style Work fill:#eeffcc
    style Problem fill:#ffcccc
    style Dissatisfaction fill:#ffdddd
    style Emotion fill:#ffeeee
```

---

## 📊 4 оси карьерного роста

```mermaid
graph TD
    Career[Карьерный рост]
    
    Career --> Axis1[Ось 1: Профессиональный рост<br/>Мастерство, сложность систем]
    Career --> Axis2[Ось 2: Должностной рост<br/>Ресурсность: люди, бюджет, влияние]
    Career --> Axis3[Ось 3: Калибр личности<br/>Масштаб создаваемых систем]
    Career --> Axis4[Ось 4: Траектория ролей<br/>Ученик → Мастер → Просветитель]
    
    Axis1 --> Ex1[Пример: Junior Dev → Senior Dev → Architect]
    Axis2 --> Ex2[Пример: Developer → Team Lead → EM]
    Axis3 --> Ex3[Пример: Личные проекты → Команда → Общество]
    Axis4 --> Ex4[Пример: Учусь → Делаю → Обучаю других]
    
    style Career fill:#e1f5e1
    style Axis1 fill:#fff4e1
    style Axis2 fill:#ffe1e1
    style Axis3 fill:#e1f0ff
    style Axis4 fill:#f0e1ff
```

---

## 🔗 Связанные материалы

- [Глоссарий](docs/development/Glossary.md) — 68 концептов с определениями
- [Онтология](visuals/ontology.mmd) — детальная диаграмма связей
- [Недели курса](weeks/) — детальные программы
- [Кейсы-стади](case_studies/INDEX.md) — реальные примеры путей

---

*Дата создания: 08.10.2025*  
*Версия: 1.0*

