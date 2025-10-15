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

## Шаг 4: Скрипт автоматической синхронизации

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

## Шаг 5: Ручная синхронизация (альтернатива)

Если не хотите использовать скрипт, синхронизируйте вручную:

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

## Рабочий процесс

### Еженедельная синхронизация

1. Запустите скрипт синхронизации или выполните команды вручную
2. Проверьте что новые материалы подтянулись
3. Ваши личные данные остались без изменений
4. Продолжайте работу с обновленными материалами

### Работа с личными данными

В вашем приватном репозитории вы можете:

- Создавать и обновлять личные контракты в `personal_contracts/`
- Хранить рабочие продукты в `projects/`
- Вести систему личных знаний в `PKM/`
- Коммитить и пушить изменения как обычно

### Важно

⚠️ **Личные данные НЕ попадут в публичный репозиторий**

Благодаря `.gitattributes` с правилом `merge=ours`:
- При синхронизации ваши личные папки не изменяются
- Вы работаете только с приватным репозиторием
- Публичный репозиторий получает только разработку фреймворка

## Проверка настройки

После настройки проверьте:

```bash
# 1. Remotes настроены правильно
git remote -v

# 2. .gitattributes существует
cat .gitattributes

# 3. Пробная синхронизация
git fetch upstream
git merge upstream/main --no-edit

# 4. Личные данные на месте
ls personal_contracts/
ls projects/
```

## Troubleshooting

### Конфликт при merge

Если возникает конфликт при синхронизации:

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
- ✅ Получать обновления фреймворка автоматически
- ✅ Быть уверенными что личные данные защищены

