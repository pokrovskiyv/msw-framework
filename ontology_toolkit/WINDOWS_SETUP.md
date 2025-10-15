# Быстрая настройка для Windows

**⏱️ 5 минут** — и кириллица будет работать идеально!

## 1. Установите Windows Terminal

```powershell
winget install Microsoft.WindowsTerminal
```

Или через [Microsoft Store](https://aka.ms/terminal).

## 2. Настройте PowerShell Profile

Выполните в PowerShell:

```powershell
# Создайте профиль (если его нет)
New-Item -Path $PROFILE -ItemType File -Force

# Откройте в блокноте
notepad $PROFILE
```

**Добавьте эти строки:**

```powershell
# PowerShell Profile - UTF-8 Configuration
chcp 65001 | Out-Null
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$env:PYTHONIOENCODING = "utf-8"
Write-Host "[OK] UTF-8 encoding configured" -ForegroundColor Green
```

**Сохраните** (`Ctrl+S`) и **закройте** блокнот.

## 3. Перезапустите PowerShell

Откройте **новое окно** Windows Terminal — вы увидите:

```
[OK] UTF-8 encoding configured
```

## 4. Готово! 🎉

Теперь всё работает:

```powershell
# Перейдите в ваш проект
cd "C:\Projects\msw-framework"

# Добавьте понятие с кириллицей
ontology add "Агентность"

# Результат:
[OK] Создано: C_1 — Агентность  ← Правильная кириллица!
```

---

**❓ Проблемы?** См. полную инструкцию: [WINDOWS_ENCODING.md](./WINDOWS_ENCODING.md)

**💡 Важно:** Cursor не может передавать кириллицу корректно — используйте Windows Terminal напрямую для `ontology` команд.

