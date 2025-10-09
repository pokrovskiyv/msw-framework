"""
Основной CLI модуль для курса «Системная карьера».

Команды:
- course start-week <N> — начать работу по неделе N
- course contract init — создать личный контракт
- course contract update — обновить контракт
- course progress — показать прогресс
- course template <name> — создать файл из шаблона
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
import shutil

# Настройка кодировки для Windows
if sys.platform == "win32":
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

app = typer.Typer(
    name="course",
    help="CLI для работы с курсом «Системная карьера»",
    add_completion=False
)

console = Console(
    force_terminal=True,
    legacy_windows=False,
    force_interactive=False
) if sys.platform == "win32" else Console()

# Путь к проекту (корень репозитория)
def get_project_root() -> Path:
    """Определить корень проекта."""
    # Начинаем поиск от директории, где находится этот файл
    current = Path(__file__).parent.parent.parent  # course_cli/course_cli/main.py -> корень
    
    # Проверяем, что мы в корне проекта
    if (current / "weeks").exists() and (current / "templates").exists():
        return current
    
    # Если не нашли от файла, ищем от текущей директории вверх
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "weeks").exists() and (parent / "templates").exists():
            return parent
    
    # В крайнем случае возвращаем текущую директорию
    return Path.cwd()

PROJECT_ROOT = get_project_root()
WEEKS_DIR = PROJECT_ROOT / "weeks"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
CONTRACTS_DIR = PROJECT_ROOT / "personal_contracts"


@app.command(name="start-week")
def start_week(
    week: int = typer.Argument(..., help="Номер недели (1-8)"),
    open_file: bool = typer.Option(True, "--open/--no-open", help="Открыть файл недели"),
    show_summary: bool = typer.Option(True, "--summary/--no-summary", help="Показать краткое описание"),
):
    """
    Начать работу по неделе N.
    
    Показывает:
    - Цели недели
    - Основной концепт
    - Практику
    - Рабочий продукт
    - Ссылки на материалы
    """
    if week < 1 or week > 8:
        console.print(f"[red]❌ Неделя должна быть от 1 до 8[/red]")
        raise typer.Exit(code=1)
    
    # Ищем файл недели
    week_files = list(WEEKS_DIR.glob(f"Week_0{week}_*.md"))
    
    if not week_files:
        console.print(f"[red]❌ Файл для недели {week} не найден в {WEEKS_DIR}[/red]")
        raise typer.Exit(code=1)
    
    week_file = week_files[0]
    
    console.print(f"\n[bold cyan]🎯 Неделя {week}: {week_file.stem.split('_', 2)[2]}[/bold cyan]\n")
    
    if show_summary:
        try:
            content = week_file.read_text(encoding="utf-8")
            
            # Извлекаем краткую информацию из файла
            lines = content.split('\n')
            
            # Находим основные секции
            summary = []
            in_goals = False
            in_concept = False
            
            for i, line in enumerate(lines[:100]):  # Первые 100 строк
                if line.startswith("## Цели недели") or line.startswith("## Learning Outcomes"):
                    in_goals = True
                    continue
                elif line.startswith("## Концепт недели") or line.startswith("## Основной концепт"):
                    in_concept = True
                    continue
                elif line.startswith("##") and (in_goals or in_concept):
                    break
                
                if in_goals or in_concept:
                    if line.strip() and not line.startswith("#"):
                        summary.append(line)
            
            if summary:
                summary_text = "\n".join(summary[:10])  # Первые 10 строк
                console.print(Panel(summary_text, title="📋 Краткое описание", border_style="cyan"))
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Не удалось прочитать файл: {e}[/yellow]")
    
    # Информация о файле
    console.print(f"\n[dim]📄 Файл: {week_file.relative_to(PROJECT_ROOT)}[/dim]")
    
    # Открываем файл
    if open_file:
        console.print(f"[green]✅ Открываем файл в редакторе по умолчанию...[/green]\n")
        try:
            if sys.platform == "win32":
                os.startfile(week_file)
            elif sys.platform == "darwin":
                os.system(f"open {week_file}")
            else:
                os.system(f"xdg-open {week_file}")
        except Exception as e:
            console.print(f"[yellow]⚠️  Не удалось открыть файл: {e}[/yellow]")
            console.print(f"[dim]Откройте вручную: {week_file}[/dim]")
    else:
        console.print(f"[dim]💡 Чтобы открыть файл: course start-week {week} --open[/dim]\n")


@app.command(name="contract")
def contract(
    action: str = typer.Argument(..., help="Действие: init, update, show"),
    week: Optional[int] = typer.Option(None, "--week", "-w", help="Номер недели (для init)"),
    open_file: bool = typer.Option(True, "--open/--no-open", help="Открыть файл"),
):
    """
    Управление личным контрактом.
    
    Actions:
    - init: создать новый контракт (по умолчанию для недели 1)
    - update: обновить существующий контракт
    - show: показать текущий контракт
    """
    # Создаём папку для контрактов, если её нет
    CONTRACTS_DIR.mkdir(exist_ok=True)
    
    if action == "init":
        # Определяем версию контракта по неделе
        week = week or 1
        
        if week == 1:
            template_name = "Personal_Contract_v1.0_Week1_Template.md"
            version = "v1.0"
        elif week <= 4:
            template_name = "Personal_Contract_v1.0_Week1_Template.md"  # Пока используем базовый
            version = f"v{min(week, 4)}.0"
        else:
            template_name = "Personal_Contract_v4.0_Template.md"
            version = "v4.0"
        
        template_path = TEMPLATES_DIR / template_name
        
        if not template_path.exists():
            console.print(f"[red]❌ Шаблон не найден: {template_name}[/red]")
            console.print(f"[yellow]💡 Доступные шаблоны в {TEMPLATES_DIR}[/yellow]")
            raise typer.Exit(code=1)
        
        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d")
        output_name = f"my_contract_week{week}_{timestamp}.md"
        output_path = CONTRACTS_DIR / output_name
        
        # Проверяем, существует ли уже контракт для этой недели
        existing = list(CONTRACTS_DIR.glob(f"my_contract_week{week}*.md"))
        if existing:
            console.print(f"[yellow]⚠️  Контракт для недели {week} уже существует:[/yellow]")
            for f in existing:
                console.print(f"   • {f.name}")
            
            overwrite = typer.confirm("Создать новый контракт?")
            if not overwrite:
                console.print("[dim]Отменено[/dim]")
                raise typer.Exit(code=0)
        
        # Копируем шаблон
        try:
            shutil.copy(template_path, output_path)
            console.print(f"\n[green]✅ Создан личный контракт {version}[/green]")
            console.print(f"[dim]📄 {output_path.relative_to(PROJECT_ROOT)}[/dim]\n")
            
            # Открываем файл
            if open_file:
                if sys.platform == "win32":
                    os.startfile(output_path)
                elif sys.platform == "darwin":
                    os.system(f"open {output_path}")
                else:
                    os.system(f"xdg-open {output_path}")
        
        except Exception as e:
            console.print(f"[red]❌ Ошибка создания контракта: {e}[/red]")
            raise typer.Exit(code=1)
    
    elif action == "show":
        # Показываем список всех контрактов
        contracts = sorted(CONTRACTS_DIR.glob("my_contract_*.md"))
        
        if not contracts:
            console.print("[yellow]❌ Личные контракты не найдены[/yellow]")
            console.print("[dim]💡 Создайте: course contract init[/dim]")
            raise typer.Exit(code=0)
        
        console.print(f"\n[bold cyan]📋 Ваши личные контракты ({len(contracts)}):[/bold cyan]\n")
        
        table = Table(show_header=True)
        table.add_column("Файл", style="cyan")
        table.add_column("Размер", justify="right")
        table.add_column("Изменён", style="dim")
        
        for contract in contracts:
            size = contract.stat().st_size
            size_kb = f"{size // 1024} КБ" if size > 1024 else f"{size} Б"
            mtime = datetime.fromtimestamp(contract.stat().st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(contract.name, size_kb, mtime_str)
        
        console.print(table)
        console.print()
        
    elif action == "update":
        console.print("[yellow]⚠️  Команда 'update' пока не реализована[/yellow]")
        console.print("[dim]💡 Откройте ваш контракт вручную и отредактируйте[/dim]")
    
    else:
        console.print(f"[red]❌ Неизвестное действие: {action}[/red]")
        console.print("[dim]Доступные: init, update, show[/dim]")
        raise typer.Exit(code=1)


@app.command(name="progress")
def progress(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Показать детальный прогресс"),
):
    """
    Показать ваш прогресс по курсу.
    
    Анализирует:
    - Какие контракты созданы
    - Какие недели пройдены
    - Статистику
    """
    console.print(f"\n[bold cyan]📊 Ваш прогресс по курсу[/bold cyan]\n")
    
    # Анализируем контракты
    contracts = list(CONTRACTS_DIR.glob("my_contract_*.md"))
    
    if not contracts:
        console.print("[yellow]⚠️  Контракты не найдены[/yellow]")
        console.print("[dim]💡 Начните с: course contract init --week 1[/dim]\n")
        return
    
    # Определяем недели с контрактами
    weeks_with_contracts = set()
    for contract in contracts:
        # Извлекаем номер недели из имени файла
        import re
        match = re.search(r'week(\d+)', contract.stem)
        if match:
            weeks_with_contracts.add(int(match.group(1)))
    
    # Таблица прогресса по неделям
    table = Table(title="Недели курса", show_header=True)
    table.add_column("Неделя", justify="center", style="cyan")
    table.add_column("Тема", style="white")
    table.add_column("Контракт", justify="center")
    table.add_column("Статус", justify="center")
    
    weeks = [
        (1, "Фундамент"),
        (2, "Направление"),
        (3, "Ценность"),
        (4, "Ритм"),
        (5, "Контекст"),
        (6, "Мастерство"),
        (7, "Коммуникация"),
        (8, "Устойчивость"),
    ]
    
    for week_num, week_name in weeks:
        has_contract = "✅" if week_num in weeks_with_contracts else "—"
        status = "[green]В процессе[/green]" if week_num in weeks_with_contracts else "[dim]Не начата[/dim]"
        
        table.add_row(str(week_num), week_name, has_contract, status)
    
    console.print(table)
    
    # Статистика
    completed_weeks = len(weeks_with_contracts)
    progress_pct = (completed_weeks / 8) * 100
    
    console.print(f"\n[bold]Статистика:[/bold]")
    console.print(f"  • Недель с контрактами: {completed_weeks}/8")
    console.print(f"  • Прогресс: {progress_pct:.0f}%")
    console.print(f"  • Контрактов создано: {len(contracts)}")
    console.print()
    
    if detailed:
        console.print(f"[bold]Файлы контрактов:[/bold]")
        for contract in sorted(contracts):
            size = contract.stat().st_size // 1024
            console.print(f"  • {contract.name} ({size} КБ)")
        console.print()


@app.command(name="template")
def template(
    name: Optional[str] = typer.Argument(None, help="Имя шаблона (или часть имени)"),
    list_all: bool = typer.Option(False, "--list", "-l", help="Показать список всех шаблонов"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Путь для сохранения"),
):
    """
    Создать файл из шаблона.
    
    Примеры:
    - course template Week_08_Energy  # создаст из шаблона энергобюджета
    - course template --list  # покажет все доступные шаблоны
    """
    if list_all:
        templates = sorted(TEMPLATES_DIR.glob("*.md"))
        
        if not templates:
            console.print(f"[yellow]⚠️  Шаблоны не найдены в {TEMPLATES_DIR}[/yellow]")
            return
        
        console.print(f"\n[bold cyan]📄 Доступные шаблоны ({len(templates)}):[/bold cyan]\n")
        
        for tmpl in templates:
            console.print(f"  • {tmpl.stem}")
        
        console.print()
        console.print("[dim]💡 Используйте: course template <имя>[/dim]")
        return
    
    if not name:
        console.print("[red]❌ Необходимо указать имя шаблона[/red]")
        console.print("[dim]💡 Посмотрите список: course template --list[/dim]")
        raise typer.Exit(code=1)
    
    # Ищем шаблон по имени
    templates = list(TEMPLATES_DIR.glob(f"*{name}*.md"))
    
    if not templates:
        console.print(f"[red]❌ Шаблон не найден: {name}[/red]")
        console.print(f"[dim]💡 Посмотрите список: course template --list[/dim]")
        raise typer.Exit(code=1)
    
    if len(templates) > 1:
        console.print(f"[yellow]⚠️  Найдено несколько шаблонов:[/yellow]")
        for tmpl in templates:
            console.print(f"   • {tmpl.stem}")
        console.print(f"[dim]💡 Уточните запрос[/dim]")
        raise typer.Exit(code=1)
    
    template_path = templates[0]
    
    # Определяем путь для сохранения
    if output:
        output_path = Path(output)
    else:
        # Создаём в personal_contracts с текущей датой
        CONTRACTS_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        output_path = CONTRACTS_DIR / f"{template_path.stem}_{timestamp}.md"
    
    # Копируем шаблон
    try:
        shutil.copy(template_path, output_path)
        console.print(f"\n[green]✅ Создан файл из шаблона[/green]")
        console.print(f"[dim]📄 {output_path}[/dim]\n")
        
        # Открываем файл
        if sys.platform == "win32":
            os.startfile(output_path)
        elif sys.platform == "darwin":
            os.system(f"open {output_path}")
        else:
            os.system(f"xdg-open {output_path}")
    
    except Exception as e:
        console.print(f"[red]❌ Ошибка: {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="docs")
def docs(
    action: str = typer.Argument(..., help="Действие: check, update"),
    strict: bool = typer.Option(False, "--strict", help="Строгий режим проверки"),
    days: int = typer.Option(7, "--days", help="Количество дней для анализа изменений"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Неинтерактивный режим"),
    auto_fix: bool = typer.Option(False, "--auto-fix", help="Автоматически исправлять проблемы с порядком версий"),
    auto_update: bool = typer.Option(False, "--auto-update", help="Автоматически обновлять дату в ASSESSMENT.md"),
):
    """
    Управление документацией проекта.
    
    Actions:
    - check: проверить синхронность документации
    - update: обновить документацию интерактивно
    """
    scripts_dir = PROJECT_ROOT / "scripts"
    
    if action == "check":
        console.print(f"\n[bold cyan]🔍 Проверка синхронности документации[/bold cyan]\n")
        
        # Формируем команду
        cmd = [sys.executable, str(scripts_dir / "check_docs_sync.py")]
        
        if strict:
            cmd.append("--strict")
        
        if days != 7:
            cmd.extend(["--days", str(days)])
        
        if auto_fix:
            cmd.append("--auto-fix")
        
        if auto_update:
            cmd.append("--auto-update")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=False,  # Показываем вывод в реальном времени
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"\n[green]✅ Документация синхронизирована[/green]")
            elif result.returncode == 1:
                console.print(f"\n[yellow]⚠️  Обнаружены предупреждения[/yellow]")
                console.print(f"[dim]💡 Рекомендуется: course docs update[/dim]")
            elif result.returncode == 2:
                console.print(f"\n[red]❌ Обнаружены критические проблемы[/red]")
                console.print(f"[dim]💡 Требуется: course docs update[/dim]")
            else:
                console.print(f"\n[red]❌ Ошибка проверки (exit code: {result.returncode})[/red]")
            
            return result.returncode
        
        except FileNotFoundError:
            console.print(f"[red]❌ Скрипт check_docs_sync.py не найден в {scripts_dir}[/red]")
            console.print(f"[dim]💡 Убедитесь, что вы находитесь в корне проекта[/dim]")
            raise typer.Exit(code=1)
        
        except Exception as e:
            console.print(f"[red]❌ Ошибка запуска проверки: {e}[/red]")
            raise typer.Exit(code=1)
    
    elif action == "update":
        console.print(f"\n[bold cyan]🔧 Обновление документации[/bold cyan]\n")
        
        # Формируем команду
        cmd = [sys.executable, str(scripts_dir / "update_docs.py")]
        
        if days != 7:
            cmd.extend(["--days", str(days)])
        
        if no_interactive:
            cmd.append("--no-interactive")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=False,  # Показываем вывод в реальном времени
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"\n[green]✅ Обновление документации завершено[/green]")
            else:
                console.print(f"\n[yellow]⚠️  Обновление завершено с предупреждениями[/yellow]")
            
            return result.returncode
        
        except FileNotFoundError:
            console.print(f"[red]❌ Скрипт update_docs.py не найден в {scripts_dir}[/red]")
            console.print(f"[dim]💡 Убедитесь, что вы находитесь в корне проекта[/dim]")
            raise typer.Exit(code=1)
        
        except Exception as e:
            console.print(f"[red]❌ Ошибка запуска обновления: {e}[/red]")
            raise typer.Exit(code=1)
    
    else:
        console.print(f"[red]❌ Неизвестное действие: {action}[/red]")
        console.print(f"[dim]Доступные: check, update[/dim]")
        raise typer.Exit(code=1)


@app.command(name="ai-guide")
def ai_guide(
    open_file: bool = typer.Option(True, "--open/--no-open", help="Открыть файл"),
):
    """
    Открыть руководство по работе с AI ассистентом.
    
    Показывает:
    - Структурированные промпты для AI
    - Правила работы с ассистентом
    - Примеры правильных диалогов
    - Troubleshooting проблем
    """
    ai_guide_path = PROJECT_ROOT / "docs/guides/AI_ASSISTANT_GUIDE.md"
    
    if not ai_guide_path.exists():
        console.print(f"[red]❌ Руководство по AI не найдено: {ai_guide_path}[/red]")
        console.print(f"[dim]💡 Убедитесь, что вы находитесь в корне проекта[/dim]")
        raise typer.Exit(code=1)
    
    console.print(f"\n[bold cyan]🤖 Руководство по работе с AI ассистентом[/bold cyan]\n")
    
    try:
        content = ai_guide_path.read_text(encoding="utf-8")
        
        # Извлекаем краткую информацию из файла
        lines = content.split('\n')
        
        # Находим основные секции
        summary = []
        in_problem = False
        in_solution = False
        
        for i, line in enumerate(lines[:50]):  # Первые 50 строк
            if line.startswith("## Проблема"):
                in_problem = True
                continue
            elif line.startswith("## Решение"):
                in_solution = True
                continue
            elif line.startswith("##") and (in_problem or in_solution):
                break
            
            if in_problem or in_solution:
                if line.strip() and not line.startswith("#"):
                    summary.append(line)
        
        if summary:
            summary_text = "\n".join(summary[:8])  # Первые 8 строк
            console.print(Panel(summary_text, title="📋 Краткое описание", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Не удалось прочитать файл: {e}[/yellow]")
    
    # Информация о файле
    console.print(f"\n[dim]📄 Файл: {ai_guide_path.relative_to(PROJECT_ROOT)}[/dim]")
    
    # Открываем файл
    if open_file:
        console.print(f"[green]✅ Открываем файл в редакторе по умолчанию...[/green]\n")
        try:
            if sys.platform == "win32":
                os.startfile(ai_guide_path)
            elif sys.platform == "darwin":
                os.system(f"open {ai_guide_path}")
            else:
                os.system(f"xdg-open {ai_guide_path}")
        except Exception as e:
            console.print(f"[yellow]⚠️  Не удалось открыть файл: {e}[/yellow]")
            console.print(f"[dim]Откройте вручную: {ai_guide_path}[/dim]")
    else:
        console.print(f"[dim]💡 Чтобы открыть файл: course ai-guide --open[/dim]\n")


@app.command(name="ai-chat")
def ai_chat(
    week: int = typer.Argument(1, help="Номер недели (1-8)"),
    contract_file: Optional[str] = typer.Option(None, "--file", "-f", help="Путь к файлу контракта"),
):
    """
    Автоматически отправить промпт в чат Cursor для заполнения контракта.
    
    Создает временный файл с промптом и открывает его в Cursor Chat.
    """
    # Определяем файл контракта
    if contract_file:
        contract_path = Path(contract_file)
    else:
        # Ищем существующий контракт или создаем новый
        contracts_dir = PROJECT_ROOT / "personal_contracts"
        if not contracts_dir.exists():
            contracts_dir.mkdir(exist_ok=True)
        
        # Ищем контракт для указанной недели
        existing_contracts = list(contracts_dir.glob(f"my_contract_week{week}_*.md"))
        if existing_contracts:
            contract_path = existing_contracts[0]  # Берем первый найденный
        else:
            # Создаем новый контракт
            date_str = datetime.now().strftime("%Y%m%d")
            contract_path = contracts_dir / f"my_contract_week{week}_{date_str}.md"
            
            # Копируем шаблон
            template_path = PROJECT_ROOT / f"templates/Personal_Contract_v{week}.0_Week{week}_Template.md"
            if not template_path.exists():
                template_path = PROJECT_ROOT / "Personal_Contract_v4.0_Template.md"
            
            if template_path.exists():
                shutil.copy2(template_path, contract_path)
                console.print(f"[green]✅ Создан новый контракт: {contract_path.name}[/green]")
            else:
                console.print(f"[red]❌ Шаблон не найден для недели {week}[/red]")
                raise typer.Exit(code=1)
    
    if not contract_path.exists():
        console.print(f"[red]❌ Файл контракта не найден: {contract_path}[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"\n[bold cyan]🤖 AI-чат для контракта недели {week}[/bold cyan]\n")
    console.print(f"[dim]📄 Файл: {contract_path.relative_to(PROJECT_ROOT)}[/dim]\n")
    
    # Генерируем промпт для AI
    prompt = generate_ai_prompt(week, contract_path)
    
    # Создаем временный файл с промптом
    temp_dir = PROJECT_ROOT / ".temp"
    temp_dir.mkdir(exist_ok=True)
    
    prompt_file = temp_dir / f"ai_prompt_week{week}_{datetime.now().strftime('%H%M%S')}.md"
    
    # Формируем содержимое файла
    content = f"""# AI Промпт для заполнения контракта недели {week}

## Инструкции
1. Скопируйте промпт ниже
2. Откройте Cursor Chat (Ctrl+L)
3. Вставьте промпт
4. Следуйте инструкциям AI
5. Заполняйте контракт: `{contract_path.relative_to(PROJECT_ROOT)}`

---

## Промпт для AI

```
{prompt}
```

---

## Файл контракта
Откройте для редактирования: `{contract_path.relative_to(PROJECT_ROOT)}`

## Troubleshooting
Если AI нарушает правила, используйте:
```
СТОП! Не добавляй информацию без моего запроса.
Работай только с моими данными.
Задавай вопросы, не предлагай готовые ответы.
```
"""
    
    # Записываем файл
    prompt_file.write_text(content, encoding="utf-8")
    
    console.print(f"[green]✅ Создан промпт-файл: {prompt_file.name}[/green]")
    console.print(f"[dim]📄 Путь: {prompt_file.relative_to(PROJECT_ROOT)}[/dim]\n")
    
    # Открываем файл в Cursor
    try:
        if sys.platform == "win32":
            os.startfile(prompt_file)
        elif sys.platform == "darwin":
            os.system(f"open {prompt_file}")
        else:
            os.system(f"xdg-open {prompt_file}")
        
        console.print(f"[green]✅ Файл открыт в Cursor[/green]")
        console.print(f"[yellow]💡 Теперь откройте Cursor Chat (Ctrl+L) и скопируйте промпт[/yellow]")
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Не удалось открыть файл: {e}[/yellow]")
        console.print(f"[dim]Откройте вручную: {prompt_file}[/dim]")
    
    # Показываем краткую инструкцию
    console.print(f"\n[bold green]📝 Быстрые шаги:[/bold green]")
    console.print(f"1. Файл с промптом уже открыт")
    console.print(f"2. Откройте Cursor Chat (Ctrl+L)")
    console.print(f"3. Скопируйте промпт из файла")
    console.print(f"4. Вставьте в чат и начните диалог")
    console.print(f"5. Откройте контракт: {contract_path.relative_to(PROJECT_ROOT)}")


def generate_ai_prompt(week: int, contract_path: Path) -> str:
    """Генерирует структурированный промпт для AI."""
    
    prompts = {
        1: """Ты помогаешь заполнить Личный контракт v1.0 (Неделя 1). 

ПРАВИЛА РАБОТЫ:
1. Задавай вопросы по одному разделу
2. НЕ добавляй информацию без моего подтверждения
3. Спрашивай: "Это соответствует вашей ситуации?"
4. Используй только мои ответы, не придумывай
5. Следуй структуре из файла Personal_Contract_v1.0_Week1_Template.md

РАЗДЕЛ: Аудит ролей
Заполним таблицу ролей. Для каждой роли нужно:
- Название роли (способность, не должность!)
- Контекст (надсистема)
- Рабочие продукты (артефакты)
- Уровень мастерства

Вопрос 1: Какие роли вы исполняете сейчас? Перечислите 5-7 ролей.""",

        2: """Ты помогаешь заполнить Личный контракт v2.0 (Неделя 2). 

ПРАВИЛА РАБОТЫ:
1. Задавай вопросы по одному разделу
2. НЕ добавляй информацию без моего подтверждения
3. Спрашивай: "Это соответствует вашей ситуации?"
4. Используй только мои ответы, не придумывай
5. Различаем: Проблема (объективный факт) ≠ Неудовлетворённость (состояние) ≠ Эмоция (реакция)

РАЗДЕЛ: Стратегии
Заполним таблицу стратегий. Для каждой стратегии нужно:
- Неудовлетворённость (состояние, потребность)
- Стратегия-гипотеза (метод решения)
- Целевая роль для роста
- Критерий проверки (3 месяца)

Вопрос 1: Что вас беспокоит в текущей работе/карьере? Перечислите 3-5 конкретных проблем.""",

        3: """Ты помогаешь заполнить Личный контракт v3.0 (Неделя 3). 

ПРАВИЛА РАБОТЫ:
1. Задавай вопросы по одному разделу
2. НЕ добавляй информацию без моего подтверждения
3. Спрашивай: "Это соответствует вашей ситуации?"
4. Используй только мои ответы, не придумывай

РАЗДЕЛ: Проекты
Заполним таблицу проектов. Для каждого проекта нужно:
- Название проекта
- Связь со стратегией
- Рабочие продукты (артефакты)
- Критерии приёмки
- Сроки

Вопрос 1: Какие проекты вы хотите запустить для реализации стратегий? Перечислите 2-3 проекта."""
    }
    
    if week in prompts:
        return prompts[week]
    else:
        return f"""Ты помогаешь заполнить Личный контракт v{week}.0 (Неделя {week}). 

ПРАВИЛА РАБОТЫ:
1. Задавай вопросы по одному разделу
2. НЕ добавляй информацию без моего подтверждения
3. Спрашивай: "Это соответствует вашей ситуации?"
4. Используй только мои ответы, не придумывай

РАЗДЕЛ: Основной раздел недели {week}
Заполним соответствующий раздел контракта.

Вопрос 1: Начнем с основного вопроса для этой недели."""


@app.command(name="info")
def info():
    """
    Показать информацию о курсе и доступных материалах.
    """
    console.print(f"\n[bold cyan]{'='*70}[/bold cyan]")
    console.print(f"[bold cyan]📚 Курс «Системная карьера»[/bold cyan]")
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")
    
    console.print(f"[bold]Структура курса:[/bold] 8 недель")
    console.print(f"[bold]Формат:[/bold] Концепт + Практика + Личный контракт\n")
    
    # Проверяем доступность материалов
    weeks_count = len(list(WEEKS_DIR.glob("Week_*.md")))
    templates_count = len(list(TEMPLATES_DIR.glob("*.md")))
    
    console.print(f"[bold]Доступные материалы:[/bold]")
    console.print(f"  • Недель: {weeks_count}/8")
    console.print(f"  • Шаблонов: {templates_count}")
    console.print(f"  • Примеров: {len(list((PROJECT_ROOT / 'examples').glob('*.md'))) if (PROJECT_ROOT / 'examples').exists() else 0}")
    
    console.print(f"\n[bold]Основные команды:[/bold]")
    console.print(f"  • [cyan]course start-week <N>[/cyan] — начать неделю")
    console.print(f"  • [cyan]course contract init[/cyan] — создать контракт")
    console.print(f"  • [cyan]course progress[/cyan] — показать прогресс")
    console.print(f"  • [cyan]course template <name>[/cyan] — использовать шаблон")
    console.print(f"  • [cyan]course docs check[/cyan] — проверить документацию")
    console.print(f"  • [cyan]course docs update[/cyan] — обновить документацию")
    console.print(f"  • [cyan]course ai-guide[/cyan] — руководство по работе с AI")
    console.print(f"  • [cyan]course ai-chat <N>[/cyan] — заполнить контракт с AI")
    
    console.print(f"\n[dim]💡 Справка по команде: course <команда> --help[/dim]\n")


if __name__ == "__main__":
    app()

