"""
CLI для Ontology Toolkit.

Основные команды:
- init: создать структуру онтологии
- add: добавить понятие
- list: показать список объектов
- audit: проверить онтологию
- export: экспортировать в CSV/XLSX
- graph: создать граф связей (Mermaid)
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Настройка кодировки для Windows
if sys.platform == "win32":
    # Устанавливаем UTF-8 для stdin/stdout/stderr
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Переменные окружения для Python
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Функция для исправления кодировки (если нужно)
    def fix_windows_encoding(text: str) -> str:
        """Исправить кодировку текста, переданного из Windows PowerShell.
        
        Если текст выглядит как "кракозябры" (латиница вместо кириллицы),
        пробуем перекодировать из cp1252 в utf-8.
        """
        # Проверяем, нужно ли исправление
        # Если в тексте есть кириллица, значит всё ОК
        if any('\u0400' <= c <= '\u04ff' for c in text):
            return text
        
        # Если текст содержит типичные "кракозябры" (неправильно декодированная кириллица)
        try:
            # Пробуем перекодировать: encode как latin-1, decode как utf-8
            fixed = text.encode('latin-1').decode('utf-8')
            # Проверяем, что результат содержит кириллицу
            if any('\u0400' <= c <= '\u04ff' for c in fixed):
                return fixed
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        
        # Если ничего не помогло, возвращаем как есть
        return text

import typer
from rich.console import Console
from rich.table import Table

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import ConceptStatus
from ontology_toolkit.io.csv_export import export_concepts_to_csv
from ontology_toolkit.io.xlsx_export import export_to_xlsx

app = typer.Typer(
    name="ontology",
    help="Ontology Toolkit v0.2.0 — управление онтологией проекта",
    add_completion=False
)

# Создаём консоль с принудительной UTF-8 кодировкой для Windows
console = Console(
    force_terminal=True,
    legacy_windows=False,
    force_interactive=False
) if sys.platform == "win32" else Console()

# Путь к онтологии по умолчанию
DEFAULT_ONTOLOGY_PATH = Path(".ontology")


@app.command()
def init(
    project: str = typer.Option("Ontology Project", "--project", "-p", help="Название проекта"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии")
):
    """
    Инициализировать структуру онтологии проекта.
    
    Создаёт папки для каждого типа объектов и README файл.
    """
    try:
        # Создаём структуру папок
        folders = ["concepts", "methods", "systems", "problems", "artifacts"]
        
        for folder in folders:
            folder_path = path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
        
        # Создаём README
        readme_path = path / "README.md"
        if not readme_path.exists():
            readme_content = f"""# {project}

Онтология проекта, управляемая через Ontology Toolkit.

## Структура

- `concepts/` — понятия (C_*)
- `methods/` — методы (M_*)
- `systems/` — системы (S_*)
- `problems/` — проблемы (P_*)
- `artifacts/` — артефакты (A_*)

## Использование

```bash
# Добавить понятие
ontology add "Название понятия"

# Посмотреть список
ontology list

# Проверить онтологию
ontology audit

# Экспортировать
ontology export --format csv
```

## Версия

Создано: {path.absolute()}
"""
            readme_path.write_text(readme_content, encoding="utf-8")
        
        console.print(f"[green][OK] Онтология инициализирована в {path.absolute()}[/green]")
        console.print(f"[dim]Создано папок: {len(folders)}[/dim]")
        
    except Exception as e:
        console.print(f"[red][ERROR] Ошибка инициализации: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def add(
    name: str = typer.Argument(..., help="Название объекта"),
    type: str = typer.Option("concept", "--type", "-t", help="Тип объекта (concept/method/system/problem/artifact)"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии")
):
    """
    Добавить новый объект (понятие, метод, систему и т.д.).
    
    Создаёт черновик и сохраняет в соответствующую папку.
    """
    try:
        # Исправляем кодировку имени для Windows
        original_name = name
        if sys.platform == "win32":
            name = fix_windows_encoding(name)
            # Отладка: показываем, если было исправление
            if name != original_name:
                console.print(f"[dim][DEBUG] Кодировка исправлена: {repr(original_name)} -> {repr(name)}[/dim]")
        
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Загружаем онтологию
        onto = Ontology(path)
        onto.load_all()
        
        # Добавляем понятие (пока только concepts поддерживается)
        if type == "concept":
            concept = onto.add_concept(name)
            file_path = onto.save_concept(concept)
            
            console.print(f"[green][OK] Создано: {concept.id} — {concept.name}[/green]")
            console.print(f"[dim][FILE] {file_path.name}[/dim]")
            console.print(f"[yellow][!] Статус: {concept.status.value} (нужно заполнить)[/yellow]")
        else:
            console.print(f"[red][ERROR] Тип '{type}' пока не поддерживается[/red]")
            console.print(f"[dim]Доступно: concept[/dim]")
            raise typer.Exit(code=1)
        
    except ValueError as e:
        console.print(f"[red][ERROR] Ошибка: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red][ERROR] Неожиданная ошибка: {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="list")
def list_entities(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Фильтр по статусу (draft/draft+filled/approved)"),
    prefix: Optional[str] = typer.Option(None, "--prefix", "-p", help="Фильтр по префиксу (C/M/S/P/A)"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии")
):
    """
    Показать список объектов онтологии.
    
    Можно фильтровать по статусу и префиксу.
    """
    try:
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Загружаем онтологию
        onto = Ontology(path)
        onto.load_all()
        
        # Получаем объекты
        entities = list(onto.index.by_id.values())
        
        # Фильтр по префиксу
        if prefix:
            entities = onto.index.by_prefix.get(prefix.upper(), [])
        
        # Фильтр по статусу
        if status:
            try:
                status_enum = ConceptStatus(status)
                entities = [e for e in entities if hasattr(e, 'status') and e.status == status_enum]
            except ValueError:
                console.print(f"[red][ERROR] Неверный статус: {status}[/red]")
                console.print(f"[dim]Доступные: draft, draft+filled, approved[/dim]")
                raise typer.Exit(code=1)
        
        # Вывод таблицы
        if not entities:
            console.print("[yellow]Объектов не найдено[/yellow]")
            return
        
        table = Table(title=f"Объекты онтологии ({len(entities)})")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Название", style="white")
        table.add_column("Статус", style="yellow")
        table.add_column("Тип", style="magenta")
        
        for entity in entities:
            status_str = entity.status.value if hasattr(entity, 'status') else "-"
            meta_meta_str = entity.meta_meta.value if hasattr(entity, 'meta_meta') and entity.meta_meta else "-"
            
            table.add_row(
                entity.id,
                entity.name[:50],  # Ограничиваем длину
                status_str,
                meta_meta_str
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red][ERROR] Ошибка: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def audit(
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии")
):
    """
    Проверить онтологию (статистика, broken links, изолированные узлы).
    """
    try:
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Загружаем онтологию
        onto = Ontology(path)
        onto.load_all()
        
        # Выводим аудит
        onto.print_audit()
        
        # Проверяем broken links
        broken = onto.validate_relations()
        if broken:
            console.print(f"\n[red][!] Найдено {len(broken)} битых ссылок:[/red]")
            for src, target, error in broken[:10]:  # Показываем первые 10
                console.print(f"[dim]  - {src} -> {target}: {error}[/dim]")
            
            if len(broken) > 10:
                console.print(f"[dim]  ... и ещё {len(broken) - 10}[/dim]")
            
            console.print(f"\n[yellow][TIP] Исправить: ontology fix-relations[/yellow]")
        else:
            console.print(f"\n[green][OK] Все связи корректны[/green]")
        
    except Exception as e:
        console.print(f"[red][ERROR] Ошибка: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def export(
    format: str = typer.Option("csv", "--format", "-f", help="Формат экспорта (csv/xlsx)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Путь к выходному файлу"),
    prefix: Optional[str] = typer.Option(None, "--prefix", "-p", help="Фильтр по префиксу"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Фильтр по статусу"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии")
):
    """
    Экспортировать онтологию в CSV или XLSX формат.
    """
    try:
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Загружаем онтологию
        onto = Ontology(path)
        onto.load_all()
        
        # Определяем выходной файл
        if not output:
            output = Path(f"ontology_export.{format}")
        
        # Экспорт
        if format == "csv":
            status_enum = ConceptStatus(status) if status else None
            count = export_concepts_to_csv(onto, output, prefix, status_enum)
            console.print(f"[green][OK] Экспортировано {count} объектов в {output.absolute()}[/green]")
            
        elif format == "xlsx":
            stats = export_to_xlsx(onto, output)
            console.print(f"[green][OK] Экспортировано в {output.absolute()}[/green]")
            for sheet, count in stats.items():
                console.print(f"[dim]  - {sheet}: {count} объектов[/dim]")
        else:
            console.print(f"[red][ERROR] Неподдерживаемый формат: {format}[/red]")
            console.print(f"[dim]Доступные: csv, xlsx[/dim]")
            raise typer.Exit(code=1)
        
    except Exception as e:
        console.print(f"[red][ERROR] Ошибка экспорта: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def graph(
    output: Path = typer.Option(Path("visuals/ontology.mmd"), "--output", "-o", help="Путь к выходному файлу"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии")
):
    """
    Создать граф связей в формате Mermaid (.mmd).
    
    Граф можно открыть в Obsidian или сконвертировать в PNG через mmdc.
    """
    try:
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Загружаем онтологию
        onto = Ontology(path)
        onto.load_all()
        
        # Создаём Mermaid граф
        mermaid_content = _generate_mermaid_graph(onto)
        
        # Сохраняем
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(mermaid_content, encoding="utf-8")
        
        console.print(f"[green][OK] Граф сохранён в {output.absolute()}[/green]")
        console.print(f"[dim]Узлов: {len(onto.index.by_id)}, рёбер: {onto.graph.number_of_edges()}[/dim]")
        console.print(f"\n[yellow][TIP] Конвертировать в PNG: mmdc -i {output} -o {output.with_suffix('.png')}[/yellow]")
        
    except Exception as e:
        console.print(f"[red][ERROR] Ошибка создания графа: {e}[/red]")
        raise typer.Exit(code=1)


def _generate_mermaid_graph(onto: Ontology) -> str:
    """
    Сгенерировать Mermaid граф из онтологии.
    
    Args:
        onto: Онтология
        
    Returns:
        Mermaid код
    """
    lines = ["graph TD"]
    
    # Добавляем узлы
    for entity_id, entity in onto.index.by_id.items():
        # Экранируем название для Mermaid
        safe_name = entity.name.replace('"', '\\"')
        lines.append(f'    {entity_id}["{safe_name}"]')
    
    # Добавляем рёбра
    for entity_id, entity in onto.index.by_id.items():
        for relation in entity.relations:
            if relation.target in onto.index.by_id:
                lines.append(f'    {entity_id} -->|{relation.type.value}| {relation.target}')
    
    return "\n".join(lines)


@app.command(name="config-ai")
def config_ai(
    show: bool = typer.Option(False, "--show", help="Показать текущую конфигурацию"),
    check: bool = typer.Option(False, "--check", help="Проверить доступность AI"),
    list_providers: bool = typer.Option(False, "--list-providers", help="Список провайдеров"),
):
    """
    Управление конфигурацией AI.
    
    Показывает настройки, проверяет доступность провайдеров.
    """
    from ontology_toolkit.ai.factory import AIProviderFactory
    from rich.table import Table
    
    try:
        if list_providers:
            # Показываем список провайдеров
            providers = AIProviderFactory.list_providers()
            
            table = Table(title="Поддерживаемые AI провайдеры")
            table.add_column("Провайдер", style="cyan")
            table.add_column("Модель по умолчанию", style="yellow")
            table.add_column("Переменная ENV", style="green")
            
            env_mapping = {
                "anthropic": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "gemini": "GEMINI_API_KEY",
                "grok": "GROK_API_KEY",
            }
            
            for provider, model in providers.items():
                table.add_row(provider, model, env_mapping[provider])
            
            console.print(table)
            console.print("\n[dim]Установите: export {PROVIDER}_API_KEY=your-key[/dim]")
            return
        
        if check:
            # Проверяем доступность
            provider_name = os.getenv("ONTOLOGY_AI_PROVIDER", "anthropic")
            available, message = AIProviderFactory.check_provider_available(provider_name)
            
            if available:
                console.print(f"[green][OK] {provider_name}: {message}[/green]")
            else:
                console.print(f"[red][ERROR] {provider_name}: {message}[/red]")
            return
        
        if show or (not list_providers and not check):
            # Показываем текущую конфигурацию
            provider_name = os.getenv("ONTOLOGY_AI_PROVIDER", "anthropic")
            model = os.getenv("ONTOLOGY_AI_MODEL", AIProviderFactory.DEFAULT_MODELS.get(provider_name, ""))
            temperature = os.getenv("ONTOLOGY_AI_TEMPERATURE", "0.3")
            
            available, status = AIProviderFactory.check_provider_available(provider_name)
            status_icon = "[green]✓[/green]" if available else "[red]✗[/red]"
            
            console.print("\n[bold cyan]AI Configuration[/bold cyan]")
            console.print(f"[dim]Provider:[/dim]    {provider_name}")
            console.print(f"[dim]Model:[/dim]       {model}")
            console.print(f"[dim]Temperature:[/dim] {temperature}")
            console.print(f"[dim]Status:[/dim]      {status_icon} {status}")
            
            if not available:
                console.print(f"\n[yellow][TIP] Установите API ключ:[/yellow]")
                console.print(f"[dim]export {AIProviderFactory.ENV_KEY_MAPPING[provider_name]}=your-key[/dim]")
    
    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="fill")
def fill(
    concept_id: str = typer.Argument(..., help="ID понятия (напр., C_1)"),
    fields: Optional[str] = typer.Option(None, "--fields", help="Поля для заполнения (через запятую)"),
    provider: Optional[str] = typer.Option(None, "--provider", help="AI провайдер (anthropic, openai, gemini, grok)"),
    model: Optional[str] = typer.Option(None, "--model", help="Модель AI"),
    context: Optional[str] = typer.Option(None, "--context", help="Дополнительный контекст"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии"),
):
    """
    Автозаполнить понятие через AI.
    
    Использует AI для заполнения полей понятия на основе его названия
    и контекста существующих понятий.
    """
    from ontology_toolkit.ai.factory import AIProviderFactory
    from ontology_toolkit.ai.client import AIClient
    from ontology_toolkit.ai.filler import ConceptFiller
    from ontology_toolkit.ai.base_provider import AIProviderError
    
    try:
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Создаём AI провайдер
        try:
            if provider:
                # Явно указанный провайдер
                env_key = AIProviderFactory.ENV_KEY_MAPPING.get(provider)
                api_key = os.getenv(env_key)
                if not api_key:
                    console.print(f"[red][ERROR] API ключ не найден: {env_key}[/red]")
                    raise typer.Exit(code=1)
                
                ai_provider = AIProviderFactory.create(provider, api_key, model)
            else:
                # Провайдер из ENV
                ai_provider = AIProviderFactory.from_env()
        
        except AIProviderError as e:
            console.print(f"[red][ERROR] {e}[/red]")
            console.print(f"\n[yellow][TIP] Проверьте конфигурацию:[/yellow]")
            console.print(f"[dim]ontology config-ai --check[/dim]")
            raise typer.Exit(code=1)
        
        client = AIClient(ai_provider)
        
        # Загружаем онтологию
        console.print(f"[blue]Загрузка онтологии...[/blue]")
        onto = Ontology(path)
        onto.load_all()
        
        # Создаём filler
        filler = ConceptFiller(client, onto)
        
        # Парсим список полей
        fields_list = None
        if fields:
            fields_list = [f.strip() for f in fields.split(",")]
        
        # Заполняем понятие
        console.print(f"[blue]Заполнение {concept_id} через {client.provider_name}...[/blue]")
        
        concept = filler.fill_concept(
            concept_id=concept_id,
            fields=fields_list,
            additional_context=context or ""
        )
        
        # Сохраняем
        onto.save_concept(concept)
        
        # Показываем результат
        console.print(f"\n[green][OK] Понятие {concept_id} заполнено![/green]")
        console.print(f"[dim]Название:[/dim] {concept.name}")
        console.print(f"[dim]Определение:[/dim] {concept.definition[:100]}...")
        console.print(f"[dim]Назначение:[/dim] {concept.purpose[:100]}...")
        console.print(f"[dim]Тип:[/dim] {concept.meta_meta.value if concept.meta_meta else '-'}")
        console.print(f"[dim]Примеры:[/dim] {len(concept.examples)}")
        console.print(f"[dim]Статус:[/dim] {concept.status.value}")
        
    except ValueError as e:
        console.print(f"[red][ERROR] {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red][ERROR] Неожиданная ошибка: {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="extract")
def extract(
    source: str = typer.Argument(..., help="Путь к файлу или текст"),
    provider: Optional[str] = typer.Option(None, "--provider", help="AI провайдер"),
    model: Optional[str] = typer.Option(None, "--model", help="Модель AI"),
    preview: bool = typer.Option(False, "--preview", help="Только показать, не сохранять"),
    auto_add: bool = typer.Option(False, "--auto-add", help="Сразу добавить в онтологию"),
    path: Path = typer.Option(DEFAULT_ONTOLOGY_PATH, "--path", help="Путь к онтологии"),
):
    """
    Извлечь понятия из текста через AI.
    
    Анализирует текст или файл и предлагает ключевые понятия для добавления в онтологию.
    """
    from ontology_toolkit.ai.factory import AIProviderFactory
    from ontology_toolkit.ai.client import AIClient
    from ontology_toolkit.ai.extractor import ConceptExtractor
    from ontology_toolkit.ai.base_provider import AIProviderError
    from rich.table import Table
    
    try:
        # Проверяем существование онтологии
        if not path.exists():
            console.print(f"[red][ERROR] Онтология не найдена: {path}[/red]")
            console.print(f"[yellow][TIP] Выполните: ontology init[/yellow]")
            raise typer.Exit(code=1)
        
        # Создаём AI провайдер
        try:
            if provider:
                env_key = AIProviderFactory.ENV_KEY_MAPPING.get(provider)
                api_key = os.getenv(env_key)
                if not api_key:
                    console.print(f"[red][ERROR] API ключ не найден: {env_key}[/red]")
                    raise typer.Exit(code=1)
                
                ai_provider = AIProviderFactory.create(provider, api_key, model)
            else:
                ai_provider = AIProviderFactory.from_env()
        
        except AIProviderError as e:
            console.print(f"[red][ERROR] {e}[/red]")
            console.print(f"\n[yellow][TIP] Проверьте конфигурацию:[/yellow]")
            console.print(f"[dim]ontology config-ai --check[/dim]")
            raise typer.Exit(code=1)
        
        client = AIClient(ai_provider)
        
        # Загружаем онтологию
        console.print(f"[blue]Загрузка онтологии...[/blue]")
        onto = Ontology(path)
        onto.load_all()
        
        # Создаём extractor
        extractor = ConceptExtractor(client, onto)
        
        # Определяем источник (файл или текст)
        source_path = Path(source)
        if source_path.exists() and source_path.is_file():
            console.print(f"[blue]Извлечение понятий из {source_path.name}...[/blue]")
            concepts = extractor.extract_from_file(source_path)
        else:
            console.print(f"[blue]Извлечение понятий из текста...[/blue]")
            concepts = extractor.extract_from_text(source)
        
        if not concepts:
            console.print(f"[yellow]Понятий не найдено[/yellow]")
            return
        
        # Показываем результат
        table = Table(title=f"Извлечено понятий: {len(concepts)}")
        table.add_column("ID", style="cyan")
        table.add_column("Название", style="white")
        table.add_column("Определение", style="dim")
        table.add_column("Тип", style="yellow")
        
        for concept in concepts:
            table.add_row(
                concept.id,
                concept.name,
                concept.definition[:50] + "..." if len(concept.definition) > 50 else concept.definition,
                concept.meta_meta.value if concept.meta_meta else "-"
            )
        
        console.print(table)
        
        # Сохраняем если нужно
        if not preview:
            if auto_add or typer.confirm("\nДобавить эти понятия в онтологию?"):
                for concept in concepts:
                    onto.add_entity(concept)
                    onto.save_concept(concept)
                
                console.print(f"\n[green][OK] Добавлено {len(concepts)} понятий![/green]")
            else:
                console.print(f"\n[dim]Понятия не добавлены (используйте --preview для предпросмотра)[/dim]")
        
    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="test-encoding", hidden=True)
def test_encoding(text: str = typer.Argument("Тест")):
    """Тестовая команда для проверки кодировки."""
    console.print(f"Получено: {text}")
    console.print(f"Байты (repr): {repr(text)}")
    console.print(f"Байты (utf-8): {text.encode('utf-8', errors='ignore')}")
    try:
        fixed = fix_windows_encoding(text) if sys.platform == "win32" else text
        console.print(f"После исправления: {fixed}")
    except Exception as e:
        console.print(f"Ошибка: {e}")


if __name__ == "__main__":
    app()

