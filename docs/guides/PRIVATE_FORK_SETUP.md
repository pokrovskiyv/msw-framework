# Настройка приватного форка для личных данных

Если вы хотите хранить личные контракты и проекты в приватном репозитории, при этом получая обновления фреймворка, следуйте этой инструкции.

## Зачем это нужно

**Публичный репозиторий msw-framework:**
- Содержит фреймворк курса «Системная карьера»
- Регулярно обновляется с новыми материалами
- Доступен всем участникам курса

**Ваш приватный репозиторий:**
- Содержит ваши личные контракты и проекты
- Синхронизируется с обновлениями фреймворка
- Личные данные защищены и не попадают в публичный репозиторий

## Шаг 1: Создание приватного репозитория

### Вариант А: Fork на GitHub

1. Перейдите на https://github.com/pokrovskiyv/msw-framework
2. Нажмите кнопку "Fork" вверху справа
3. В настройках форка:
   - Выберите "Private" (приватный репозиторий)
   - Назовите репозиторий (например, `msw-personal`)
4. Клонируйте ваш приватный форк:

```bash
git clone https://github.com/ваш-username/msw-personal.git
cd msw-personal
```

### Вариант Б: Создание нового репозитория

1. Создайте новый приватный репозиторий на GitHub (например, `msw-personal`)
2. Клонируйте публичный фреймворк:

```bash
git clone https://github.com/pokrovskiyv/msw-framework.git msw-personal
cd msw-personal
```

3. Измените remote на ваш приватный:

```bash
git remote rename origin upstream
git remote add origin https://github.com/ваш-username/msw-personal.git
git push -u origin main
```

## Шаг 2: Настройка upstream для синхронизации

Если вы создали fork (Вариант А), добавьте upstream:

```bash
git remote add upstream https://github.com/pokrovskiyv/msw-framework.git
```

Проверьте настройки remotes:

```bash
git remote -v
```

Должно быть:
```
origin    https://github.com/ваш-username/msw-personal.git (fetch)
origin    https://github.com/ваш-username/msw-personal.git (push)
upstream  https://github.com/pokrovskiyv/msw-framework.git (fetch)
upstream  https://github.com/pokrovskiyv/msw-framework.git (push)
```

## Шаг 3: Защита личных данных

Создайте файл `.gitattributes` в корне репозитория:

```bash
# .gitattributes
# Личные данные - всегда использовать локальную версию при merge
projects/ merge=ours
personal_contracts/ merge=ours
PKM/ merge=ours

# Дополнительная защита для личных файлов
*.personal.md merge=ours
my_contract_*.md merge=ours
*_week*.md merge=ours
strategy_*.md merge=ours
ethical_filters.md merge=ours
Week_*_Energy_Budget_*.md merge=ours
```

Это гарантирует, что при синхронизации ваши личные файлы не будут перезаписаны.

**Важно:** Закоммитьте `.gitattributes` перед началом работы:

```bash
git add .gitattributes
git commit -m "chore: add .gitattributes to protect personal data"
git push origin main
```

## Шаг 4: Выбор способа синхронизации

Есть два способа получать обновления фреймворка. Выберите наиболее удобный для вас.

### ✅ Способ 1: Синхронизация через GitHub UI (рекомендуется)

**Подходит для:** большинства пользователей, кто создал приватный fork (Вариант А на Шаге 1)

**Преимущества:**
- Синхронизация в 2 клика через браузер
- Не требует локальных команд git
- GitHub автоматически уважает `.gitattributes`

**Как использовать:**

1. Перейдите в ваш приватный репозиторий на GitHub
2. Если доступны обновления, вы увидите сообщение:
   ```
   This branch is X commits behind pokrovskiyv:main
   ```
3. Нажмите кнопку **"Sync fork"** → **"Update branch"**
4. GitHub автоматически обновит фреймворк, сохранив ваши личные данные
5. Получите изменения локально:
   ```bash
   git pull origin main
   ```

**Защита данных:** `.gitattributes` с правилом `merge=ours` работает и при синхронизации через GitHub UI! Ваши личные папки (`projects/`, `personal_contracts/`, `PKM/`) не будут перезаписаны.

### 🛠️ Способ 2: Локальная синхронизация через скрипт (для продвинутых)

**Подходит для:** пользователей, кто хочет полный контроль над процессом синхронизации

**Преимущества:**
- Видите список изменений перед применением
- Контролируете каждый шаг
- Работает для любого типа настройки (fork или отдельный репозиторий)

**Скрипт автоматической синхронизации**

### Для Windows (PowerShell)

Создайте файл `sync-from-public.ps1`:

```powershell
Write-Host "🔄 Синхронизация с публичным репозиторием msw-framework..." -ForegroundColor Cyan

# Получить обновления из публичного репозитория
git fetch upstream

# Показать что изменилось
Write-Host "`n📋 Новые коммиты в upstream:" -ForegroundColor Yellow
git log --oneline HEAD..upstream/main --no-merges

# Спросить подтверждение
$response = Read-Host "`nПрименить обновления? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    # Применить обновления (личные папки защищены через .gitattributes)
    git merge upstream/main --no-edit
    
    Write-Host "`n✅ Синхронизация завершена" -ForegroundColor Green
    Write-Host "📊 Статус:" -ForegroundColor Yellow
    git status --short
    
    # Спросить про пуш в приватный репозиторий
    $pushResponse = Read-Host "`nЗапушить в приватный репозиторий? (y/n)"
    if ($pushResponse -eq "y" -or $pushResponse -eq "Y") {
        git push origin main
        Write-Host "🚀 Изменения отправлены в приватный репозиторий" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Синхронизация отменена" -ForegroundColor Red
}
```

Запуск:

```powershell
.\sync-from-public.ps1
```

### Для Linux/Mac (Bash)

Создайте файл `sync-from-public.sh`:

```bash
#!/bin/bash

echo "🔄 Синхронизация с публичным репозиторием msw-framework..."

# Получить обновления из публичного репозитория
git fetch upstream

# Показать что изменилось
echo ""
echo "📋 Новые коммиты в upstream:"
git log --oneline HEAD..upstream/main --no-merges

# Спросить подтверждение
read -p "Применить обновления? (y/n) " response
if [[ "$response" == "y" || "$response" == "Y" ]]; then
    # Применить обновления (личные папки защищены через .gitattributes)
    git merge upstream/main --no-edit
    
    echo ""
    echo "✅ Синхронизация завершена"
    echo "📊 Статус:"
    git status --short
    
    # Спросить про пуш в приватный репозиторий
    read -p "Запушить в приватный репозиторий? (y/n) " pushResponse
    if [[ "$pushResponse" == "y" || "$pushResponse" == "Y" ]]; then
        git push origin main
        echo "🚀 Изменения отправлены в приватный репозиторий"
    fi
else
    echo "❌ Синхронизация отменена"
fi
```

Сделайте скрипт исполняемым:

```bash
chmod +x sync-from-public.sh
```

Запуск:

```bash
./sync-from-public.sh
```

#### Ручная синхронизация (без скрипта)

Если не хотите использовать скрипт:

```bash
# 1. Получить обновления
git fetch upstream

# 2. Посмотреть что изменилось
git log --oneline HEAD..upstream/main --no-merges

# 3. Применить обновления (личные папки защищены)
git merge upstream/main --no-edit

# 4. Отправить в приватный репозиторий
git push origin main
```

## Шаг 5: Рабочий процесс

### Еженедельная синхронизация

**Если используете GitHub UI (Способ 1):**
1. Откройте ваш репозиторий на GitHub
2. Нажмите "Sync fork" → "Update branch"
3. Локально выполните `git pull origin main`
4. Ваши личные данные автоматически сохранены

**Если используете локальный скрипт (Способ 2):**
1. Запустите `.\sync-from-public.ps1` (Windows) или `./sync-from-public.sh` (Linux/Mac)
2. Просмотрите список изменений
3. Подтвердите применение обновлений
4. Ваши личные данные автоматически сохранены

### Работа с личными данными

В вашем приватном репозитории вы можете:

- Создавать и обновлять личные контракты в `personal_contracts/`
- Хранить рабочие продукты в `projects/`
- Вести систему личных знаний в `PKM/`
- Коммитить и пушить изменения как обычно

### Важно: Защита личных данных

⚠️ **Ваши личные данные защищены при ЛЮБОМ способе синхронизации**

Благодаря `.gitattributes` с правилом `merge=ours`:
- ✅ **Синхронизация через GitHub UI ("Sync fork")** - GitHub уважает `.gitattributes`, личные папки не изменяются
- ✅ **Локальная синхронизация (скрипт/вручную)** - git применяет правило `merge=ours`, личные папки не изменяются

**Что защищено:**
- `personal_contracts/` - ваши контракты
- `projects/` - ваши проекты и материалы
- `PKM/` - ваша система личных знаний

**Что обновляется:**
- Материалы недель (`weeks/`)
- Шаблоны (`templates/`)
- Документация (`docs/`)
- CLI инструмент (`course_cli/`)
- Примеры (`examples/`)
- И другие файлы фреймворка

## Шаг 6: Проверка настройки

### Базовая проверка

```bash
# 1. Проверьте что .gitattributes создан и закоммичен
cat .gitattributes

# 2. Проверьте remotes (для всех способов)
git remote -v
```

### Если используете GitHub UI (Способ 1):

1. Откройте ваш приватный репозиторий на GitHub
2. Найдите кнопку "Sync fork" (если есть обновления)
3. Нажмите "Update branch"
4. Локально выполните:
   ```bash
   git pull origin main
   ls personal_contracts/  # ваши файлы должны быть на месте
   ls projects/            # ваши файлы должны быть на месте
   ```

### Если используете локальный скрипт (Способ 2):

```bash
# 1. Пробная синхронизация
git fetch upstream
git merge upstream/main --no-edit

# 2. Проверьте что личные данные на месте
ls personal_contracts/
ls projects/
```

## Troubleshooting

### Кнопка "Sync fork" не появляется

Если вы создали приватный форк, но кнопки "Sync fork" нет:

1. Убедитесь что репозиторий действительно был создан через "Fork", а не как новый репозиторий
2. Проверьте что есть обновления в upstream (pokrovskiyv/msw-framework)
3. Если форк старый, GitHub может показывать его как "independent" - используйте локальный скрипт (Способ 2)

**Альтернатива:** Всегда можете использовать локальную синхронизацию через скрипт или вручную.

### Конфликт при merge

Если возникает конфликт при синхронизации (любой способ):

```bash
# Принять вашу версию для личных папок
git checkout --ours personal_contracts/ projects/ PKM/
git add .
git commit --no-edit
```

### Случайно запушили личные данные

Если случайно отправили личные данные в публичный репозиторий:

1. Удалите файлы из индекса (но не локально):

```bash
git rm --cached -r personal_contracts/ projects/ PKM/
git commit -m "chore: удалить личные данные"
git push origin main
```

2. Добавьте в `.gitignore` (если нужно дополнительно защитить):

```gitignore
# Личные данные (не отслеживать)
personal_contracts/
projects/
PKM/
```

## Поддержка

Если возникли проблемы с настройкой:

1. Проверьте раздел Troubleshooting выше
2. Обратитесь к `Troubleshooting.md` в корне проекта
3. Задайте вопрос в сообществе курса

## Готово! 🚀

Теперь вы можете:
- ✅ Работать с личными контрактами и проектами в приватном репозитории
- ✅ Получать обновления фреймворка удобным способом:
  - Через кнопку "Sync fork" в GitHub UI (Способ 1) - просто и быстро
  - Через локальный скрипт `sync-from-public.ps1` (Способ 2) - полный контроль
- ✅ Быть уверенными что личные данные защищены при любом способе синхронизации

### Рекомендуемый workflow:

**Для большинства пользователей (Способ 1):**
```
1. Работаете с контрактами локально
2. Коммитите и пушите: git push origin main
3. Раз в неделю: GitHub → "Sync fork" → "Update branch"
4. Локально: git pull origin main
```

**Для продвинутых пользователей (Способ 2):**
```
1. Работаете с контрактами локально
2. Коммитите и пушите: git push origin main
3. Раз в неделю: .\sync-from-public.ps1
4. Просматриваете изменения и подтверждаете
```

