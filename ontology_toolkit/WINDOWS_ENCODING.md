# Проблема кодировки в Windows

## Проблема

При использовании `ontology_toolkit` в Windows PowerShell вы можете столкнуться с отображением "кракозябр" (неправильных символов) при работе с кириллицей:

```powershell
ontology add "Агентность"
# Вывод: [OK] Создано: C_1 — РђРіРµРЅС‚РЅРѕСЃС‚СЊ
```

## Причина

Это связано с тем, что:
1. Windows PowerShell использует кодировку CP1251/CP866 по умолчанию
2. Python получает аргументы командной строки уже в неправильной кодировке
3. Rich консоль не может правильно отобразить символы в старом Windows Terminal

**Важно для пользователей Cursor:** Cursor запускает команды через временные PowerShell скрипты, которые могут не учитывать настройки кодировки. Для корректной работы рекомендуется запускать `ontology` команды напрямую из Windows Terminal.

## ✅ Что работает правильно

**Важно:** Несмотря на "кракозябры" в консоли:
- ✅ **Файлы сохраняются корректно** (в UTF-8)
- ✅ **Содержимое файлов правильное** (кириллица читается)
- ✅ **Экспорт в CSV/XLSX работает** (данные экспортируются правильно)
- ✅ **Имена файлов транслитерированы** (безопасны для Windows)

Пример:
```
Файл: C_1_agentnost.md        ← транслитерация (латиница)
Содержимое:
---
name: Агентность               ← правильная кириллица
---
# Агентность                   ← правильная кириллица
```

## 🛠️ Решения

### Вариант 1: Windows Terminal + PowerShell Profile (рекомендуется)

**Шаг 1:** Установите [Windows Terminal](https://aka.ms/terminal):

```powershell
# Установка через winget
winget install Microsoft.WindowsTerminal

# Или через Microsoft Store
# Поиск: "Windows Terminal"
```

**Шаг 2:** Создайте PowerShell профиль с автоматической настройкой UTF-8:

```powershell
# Откройте PowerShell и выполните:
New-Item -Path $PROFILE -ItemType File -Force
notepad $PROFILE
```

**Шаг 3:** Добавьте в открывшийся файл:

```powershell
# PowerShell Profile - UTF-8 Configuration
chcp 65001 | Out-Null
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$env:PYTHONIOENCODING = "utf-8"
Write-Host "[OK] UTF-8 encoding configured" -ForegroundColor Green
```

**Шаг 4:** Сохраните файл и перезапустите PowerShell/Windows Terminal.

Теперь кириллица будет работать автоматически во всех новых сессиях!

После установки запустите PowerShell через Windows Terminal — кириллица будет отображаться правильно!

### Вариант 2: Настройка PowerShell

Добавьте в ваш профиль PowerShell (`$PROFILE`):

```powershell
# Открыть профиль
notepad $PROFILE

# Добавить строки:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
chcp 65001 | Out-Null
```

Перезапустите PowerShell.

### Вариант 3: Использовать CMD

В классическом `cmd.exe` кодировка иногда работает лучше:

```cmd
chcp 65001
ontology add Агентность
```

### Вариант 4: Batch Import (для больших объёмов)

Создайте файл `concepts.txt`:
```
Агентность
Целеполагание
Системное мышление
Рефлексия
```

Затем импортируйте:
```powershell
Get-Content concepts.txt -Encoding UTF8 | ForEach-Object { ontology add $_ }
```

## 📊 Проверка

Чтобы убедиться, что данные сохранены правильно:

```powershell
# Экспортируйте в CSV
ontology export --format csv

# Откройте в Excel / LibreOffice
# Данные будут отображаться правильно!
```

Или проверьте файлы напрямую:

```powershell
# Прочитайте файл с UTF-8
Get-Content .ontology\concepts\C_1_agentnost.md -Encoding UTF8
```

## 🎯 Итог

После настройки **Windows Terminal + PowerShell Profile** (Вариант 1), всё работает идеально:

### ✅ Протестировано и работает:

```powershell
# Добавление понятий с кириллицей
PS C:\Projects\...\Course_System_Career> ontology add "Рефлексия"
[OK] Создано: C_7 — Рефлексия          ← Правильная кириллица в консоли!
[FILE] C_7_refleksiya.md                ← Транслитерация в имени файла

# Просмотр списка
PS C:\Projects\...\Course_System_Career> ontology list
┏━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━┓
┃ ID  ┃ Название      ┃ Статус ┃ Тип ┃
┡━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━┩
│ C_3 │ Агентность    │ draft  │ -   │  ← Правильная кириллица!
│ C_6 │ Целеполагание │ draft  │ -   │
│ C_7 │ Рефлексия     │ draft  │ -   │
└─────┴───────────────┴────────┴─────┘

# Проверка содержимого файла
PS C:\Projects\...\Course_System_Career> Get-Content .ontology/concepts/C_7_refleksiya.md -Encoding UTF8 | Select-String "^name:"
name: Рефлексия                        ← Правильная кириллица в файле!
```

### 📋 Что нужно помнить:

1. ✅ **Имена файлов транслитерируются** — это фича, не баг!
   - `C_7_refleksiya.md` ← безопасно для Windows/Git
   - `name: Рефлексия` ← правильная кириллица внутри

2. ⚠️ **Cursor ограничения:**
   - Cursor создаёт временные PowerShell скрипты с ошибками кодировки
   - **Решение:** запускайте `ontology` команды напрямую в Windows Terminal

3. ✅ **После настройки профиля:**
   - Все новые сессии PowerShell автоматически используют UTF-8
   - Кириллица работает везде: консоль, файлы, экспорт

### 🚀 Рекомендация

**Используйте Windows Terminal для работы с `ontology_toolkit`** — это современный терминал от Microsoft с полной поддержкой UTF-8, который решает все проблемы с кодировкой раз и навсегда.

