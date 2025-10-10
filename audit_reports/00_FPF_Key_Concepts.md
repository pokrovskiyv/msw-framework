# FPF Key Concepts — Краткая выжимка для аудита

**Версия:** 1.0  
**Дата:** 10 октября 2025  
**Назначение:** Быстрый референс ключевых концептов First Principles Framework для аудиторов

---

## Введение

Этот документ содержит выжимку ключевых концептов FPF, необходимых для понимания аудита. Для полной информации см. `OtherMaterials/First Principles Framework — Core Conceptual Specification (holonic).md`

---

## Part E: Constitution — Одиннадцать столпов (Eleven Pillars)

### P-1: Cognitive Elegance (Когнитивная элегантность)
- **Суть:** Минимальность и простота — Occam's Razor для концептов
- **Требование:** Каждый концепт должен быть необходим и достаточен
- **Проверка:** Нет дублирования, нет избыточных абстракций

### P-2: Didactic Primacy (Дидактический приоритет)
- **Суть:** Обучаемость важнее формальности
- **Требование:** Tell-Show-Show (объяснение → System пример → Episteme пример)
- **Проверка:** Каждый сложный концепт имеет практический пример

### P-10: Open-Ended Evolution (Открытая эволюция)
- **Суть:** Системы должны эволюционировать бесконечно
- **Требование:** Design-time → Run-time → Observe → Re-design (цикл)
- **Проверка:** Есть механизм обратной связи и версионирования

### P-7: Pragmatic Utility (Прагматическая полезность)
- **Суть:** Решения должны быть полезны, не только правильны
- **Требование:** Goodhart's Law awareness, MVE (Minimally Viable Examples)
- **Проверка:** "So What?" test — зачем это нужно?

---

## Part A: Kernel Architecture — Ядерные паттерны

### A.1: Holonic Foundation
**Суть:** Всё, что может быть составлено — это Holon (целое-часть)

**Таксономия:**
```
Entity → Holon → {System, Episteme}
```

**Ключевые концепты:**
- **System:** Физическая система (люди, машины, организации)
- **Episteme:** Знание (документы, теории, методы)
- **U.Boundary:** Граница holon (где заканчивается "внутри")

**Проверка:**
- ✅ Системы отделены от эпистем
- ❌ "Документ — это система" (нет, это Episteme)

---

### A.2: Role Taxonomy
**Суть:** Роль = контекстная способность, не сущность

**Формула:** `Holder#Role:Context [@Interval]`

**Ключевые различения:**
- **Role:** Способность (Holder#Role:Context)
- **RoleAssignment:** Назначение роли на холон
- **Должность:** Пакет ролей в организации (НЕ то же, что роль!)

**Инварианты:**
- Роль локальна к Context
- Роль ≠ part (не мереологическая часть)
- Только System может иметь behavioural roles
- Episteme может иметь только status roles (Evidence, Standard, etc.)

**Проверка:**
- ✅ "Разработчик API" — роль (способность)
- ❌ "Backend Developer" — должность (титул)
- ❌ "Роль включает написание кода" — это Work, не роль

---

### A.3: Transformer Quartet
**Суть:** Действие моделируется через четыре концепта

**Квартет:**
1. **System-in-Role:** Кто делает (System#TransformerRole:Context)
2. **Method:** Абстрактный способ действия (design-time)
3. **MethodDescription:** Документированный рецепт (U.Episteme)
4. **Work:** Фактическое выполнение (run-time, с ресурсами)

**Проверка:**
- ✅ Method описан в MethodDescription
- ✅ Work выполняется по Method
- ✅ Work имеет resource deltas
- ❌ Method содержит actuals (нет, это Work)

---

### A.4: Temporal Duality
**Суть:** Design-time ≠ Run-time (план ≠ реальность)

**Два времени:**
- **Design-time (Tᴰ):** Планирование, спецификация, намерения
- **Run-time (Tᴿ):** Исполнение, факты, evidence

**Инварианты:**
```
Tᴰ ∩ Tᴿ = ∅         (никогда не пересекаются)
```

**Типы по времени:**
- Design-time: Method, MethodDescription, WorkPlan
- Run-time: Work, Observation
- Timeless: Role, Capability, Service

**Проверка:**
- ✅ Plan отделён от Execution
- ❌ "Я планирую 5 статей" в разделе "достижения" (смешение)
- ✅ "План: 5 статей (WorkPlan) vs Факт: 3 статьи (Work)"

---

### A.7: Strict Distinction (Clarity Lattice)
**Суть:** Категориальные ошибки запрещены

**Ключевые различения:**
1. **Object ≠ Description**
   - Pump (System) ≠ Pump Manual (Episteme)
   
2. **Role ≠ Work**
   - SurgeonRole ≠ Surgery Work
   
3. **Method ≠ MethodDescription**
   - Способ действия ≠ Документ о способе
   
4. **System ≠ Episteme**
   - Физическая система ≠ Знание о системе
   
5. **Holder ≠ Role**
   - Dr. Kim ≠ SurgeonRole

**Проверка:**
- Найти смешения типов
- Использовать canonical rewrites
- Следовать lexical discipline (E.10)

---

### A.10: Evidence Anchoring
**Суть:** Каждое утверждение должно иметь якорь к доказательству

**Требования:**
- **SCR/RSCR:** Symbol Carrier Record (где хранится evidence)
- **No self-evidence:** Нельзя быть доказательством самому себе
- **Provenance:** Откуда взято, кто создал, когда

**Проверка:**
- ✅ "Владею X: Evidence = 3 артефакта"
- ❌ "Я хорошо владею X" (без evidence)

---

### A.12: External Transformer
**Суть:** Каждое изменение имеет внешнего агента

**Принцип:** No self-transformation без явного объяснения

**Формат:**
```
Agent (System#TransformerRole:Context) → Target (Holon)
```

**Проверка:**
- ✅ "Я (System#Strategist) обновляю контракт (Target)"
- ❌ "Контракт эволюционирует сам" (кто агент?)

---

### A.15: Role–Method–Work Alignment
**Суть:** Связывает роли, методы и работу

**Цепочка:**
```
RoleAssignment → binds → Method
Method → isDescribedBy → MethodDescription
Work → isExecutionOf → MethodDescription
Work → performedBy → System#Role:Context
```

**Инварианты:**
- Только Work имеет resource deltas
- Role никогда не имеет resource deltas
- Method существует только при Work

**Проверка:**
- Цепочка прослеживается
- Нет resource deltas на Role или Method

---

## Part B: Trans-disciplinary Reasoning

### B.1: Universal Algebra of Aggregation (Γ)
**Суть:** Правила композиции частей в целое

**Invariant Quintet:**
1. **IDEM:** Идемпотентность
2. **COMM:** Коммутативность (order doesn't matter for sets)
3. **LOC:** Локальность
4. **WLNK:** Weakest-Link (для trust, safety)
5. **MONO:** Монотонность

**Flavours:**
- **Γ_sys:** Агрегация систем (mass, energy — additive)
- **Γ_epist:** Агрегация знаний (trust — weakest-link)
- **Γ_method:** Агрегация методов (order-sensitive)
- **Γ_work:** Агрегация работ (resources — additive)
- **Γ_time:** Временная агрегация (union, convex hull)

**Проверка:**
- Агрегация следует правилам Γ
- Нет наивных averages для ordinals
- Trust использует weakest-link, не average

---

### B.3: Trust & Assurance Calculus (F-G-R)
**Суть:** Trust вычисляется, не утверждается

**Три характеристики:**
- **F (Formality):** Уровень формальности (F0-F9)
  - F0 = informal sketch
  - F9 = machine-verified proof
  
- **G (Scope / ClaimScope):** Где применимо
  - Operating conditions, populations, locales
  
- **R (Reliability):** Надёжность (на основе evidence)
  - L0 = Unsubstantiated
  - L1 = Typed (typed checks passed)
  - L2 = Validated (external validation)

**Congruence Level (CL):** Потери при трансляции между контекстами
- CL=3: minor losses
- CL=2: moderate losses
- CL=1: major losses
- CL=0: incompatible

**Проверка:**
- Утверждения имеют F-G-R scores
- CL указан для cross-context mappings
- Weakest-link используется для композиции

---

### B.5: Canonical Reasoning Cycle
**Суть:** Abduction → Deduction → Induction

**Цикл:**
```
Abduction (generate hypotheses)
   ↓
Deduction (derive consequences)
   ↓
Induction (test with evidence)
   ↓
Operate (run in reality)
   ↓
Observe (collect feedback)
   ↓
[back to Abduction]
```

**Стадии:**
1. **Explore:** Generate options (wide search)
2. **Shape:** Refine candidates
3. **Evidence:** Test and validate
4. **Operate:** Deploy and run

**Проверка:**
- Процесс генерации гипотез есть
- Тестирование предусмотрено
- Цикл замкнут (feedback loop)

---

## Part C: Architheories — Специализированные CALs

### C.17: Creativity-CHR
**Суть:** Измерение креативности через 4 характеристики

**Квадрет:**
1. **Novelty (N):** Насколько ново
2. **Use-Value (U):** Насколько полезно
3. **Surprise (S):** Насколько неожиданно
4. **Constraint-Fit (C):** Соответствие ограничениям

**Проверка:**
- Креативность измеряется, не утверждается
- Есть explicit descriptor map

---

### C.18: NQD-CAL (Novelty-Quality-Diversity)
**Суть:** Open-ended search calculus

**Компоненты:**
- Novelty (N)
- Quality (Q)
- Diversity (D)

**Использование:**
- Генерация вариантов
- Portfolio management
- Illumination maps

---

### C.19: E/E-LOG (Explore-Exploit Governor)
**Суть:** Баланс exploration vs exploitation

**Policy:**
- Explore: Wide search, generate options
- Exploit: Refine and optimize known good

**Проверка:**
- Policy явно указана
- Есть переключение explore ↔ exploit

---

## Part E: Lexical Discipline — Языковые правила

### E.10: LEX-BUNDLE
**Суть:** Строгие правила именования и употребления терминов

**Запрещённые термины в Core:**
- **"Process"** → заменить на Method/Work/WorkPlan
- **"Function"** → заменить на Capability/Method
- **"Validity"** → "ClaimScope (G)" или "WorkScope"
- **"Envelope"** → явно указать boundaries
- **"Context"** (без U.BoundedContext) → уточнить

**Registers:**
- **Tech:** Технический термин (formal)
- **Plain:** Повседневный язык (informal)
- **Colloquial:** Разговорный (не для нормативных текстов)

**Проверка:**
- Grep по запрещённым терминам
- Проверить использование в контексте
- Заменить на canonical forms

---

## Ключевые инварианты для аудита

### 1. Онтологические инварианты

```
✅ System ≠ Episteme
✅ Role ≠ Work
✅ Method ≠ MethodDescription ≠ Work
✅ Design-time ≠ Run-time
✅ Object ≠ Description
✅ Plan ≠ Reality
```

### 2. Мереологические инварианты

```
✅ Role NOT in partOf chain
✅ Method NOT in partOf chain
✅ Only substantial Holons can be parts
```

### 3. Temporal инварианты

```
✅ Tᴰ ∩ Tᴿ = ∅
✅ WorkPlan in Tᴰ
✅ Work in Tᴿ
✅ Only Work has resource deltas
```

### 4. Role инварианты

```
✅ Role is context-local
✅ Role = Holder#Role:Context
✅ Only System can have behavioral roles
✅ Episteme can have status roles only
```

### 5. Evidence инварианты

```
✅ Every claim has evidence anchor
✅ No self-evidence
✅ Provenance recorded
✅ Trust uses weakest-link
```

---

## Категориальные ошибки (запрещено)

### Type Errors

1. **Conflation:** Смешение типов
   - ❌ "Процесс — это роль"
   - ❌ "Документ — это система"
   
2. **Mereological error:** Роль как часть
   - ❌ "Роль — это компонент системы"
   
3. **Temporal error:** Смешение времён
   - ❌ "План содержит факты"
   - ❌ "Work в design-time"
   
4. **Behavioral error:** Episteme acts
   - ❌ "PDF enforced the rule" (Episteme не действует)

---

## Quick Reference Table

| Концепт | Тип FPF | Design/Run | Может быть part? | Имеет resources? |
|---------|---------|------------|------------------|------------------|
| System | U.System | both | yes | yes |
| Episteme | U.Episteme | both | no | no |
| Role | U.Role | design | no | no |
| Method | U.Method | design | no | no |
| MethodDescription | U.Episteme | design | no | no |
| Work | U.Work | run | no | yes |
| WorkPlan | U.WorkPlan | design | no | no |
| Capability | U.Capability | design | no | no |
| Service | U.Episteme | design | no | no |

---

## Использование в аудите

### Шаг 1: Классификация
Для каждого концепта определить:
- Тип по FPF
- Design-time или Run-time
- Может ли быть part
- Имеет ли resources

### Шаг 2: Проверка инвариантов
Проверить все инварианты из секций выше

### Шаг 3: Поиск category errors
Использовать список запрещённых смешений

### Шаг 4: Lexical discipline
Grep по запрещённым терминам

### Шаг 5: Evidence anchoring
Проверить наличие evidence для утверждений

---

## Литература

- **Full FPF Spec:** `OtherMaterials/First Principles Framework — Core Conceptual Specification (holonic).md`
- **FPF Lens Checklist:** `audit_reports/00_FPF_Lens_Checklist.md`

---

*Этот документ — живой reference, будет дополняться по мере аудита.*

