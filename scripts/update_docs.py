#!/usr/bin/env python3
"""
Помощник для обновления документации проекта Системная карьера.

Анализирует изменения в git и помогает обновить CHANGELOG, ASSESSMENT и README.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import subprocess
import re

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_project_root() -> Path:
    """Определить корень проекта."""
    return Path(__file__).parent.parent

def detect_major_changes(changes: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """
    Детектировать мажорные изменения в проекте.
    
    Returns:
        (has_major_changes, list_of_major_files)
    """
    # Паттерны мажорных изменений
    major_patterns = [
        'weeks/',
        'templates/',
        'course_cli/',
        'Personal_Contract_',
        'Systemic_Career_Framework_',
        '.cursorrules',
        'CURSOR_SETUP.md'
    ]
    
    major_files = []
    all_changed_files = changes['added'] + changes['modified'] + changes['deleted']
    
    for file_path in all_changed_files:
        for pattern in major_patterns:
            if pattern in file_path:
                major_files.append(file_path)
                break
    
    return len(major_files) > 0, major_files

def categorize_changes(changes: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Категоризировать изменения по типам для лучшей генерации CHANGELOG.
    
    Returns:
        {
            'weeks': [...],
            'templates': [...],
            'cli': [...],
            'contracts': [...],
            'framework': [...],
            'docs': [...],
            'other': [...]
        }
    """
    categorized = {
        'weeks': [],
        'templates': [],
        'cli': [],
        'contracts': [],
        'framework': [],
        'docs': [],
        'other': []
    }
    
    all_changed_files = changes['added'] + changes['modified'] + changes['deleted']
    
    for file_path in all_changed_files:
        if 'weeks/' in file_path:
            categorized['weeks'].append(file_path)
        elif 'templates/' in file_path:
            categorized['templates'].append(file_path)
        elif 'course_cli/' in file_path:
            categorized['cli'].append(file_path)
        elif 'Personal_Contract_' in file_path:
            categorized['contracts'].append(file_path)
        elif 'Systemic_Career_Framework_' in file_path:
            categorized['framework'].append(file_path)
        elif file_path.endswith('.md') and '/' not in file_path:
            categorized['docs'].append(file_path)
        else:
            categorized['other'].append(file_path)
    
    return categorized

def get_git_changes(project_root: Path, days: int = 7) -> Dict[str, List[str]]:
    """
    Получить список изменённых файлов из git за последние N дней.
    
    Returns:
        {
            'added': [...],
            'modified': [...],
            'deleted': [...]
        }
    """
    try:
        # Получаем изменения за последние N дней
        result = subprocess.run(
            ['git', 'log', f'--since={days}.days.ago', '--name-status', '--pretty=format:'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        changes = {'added': set(), 'modified': set(), 'deleted': set()}
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            
            status, file_path = parts[0], parts[1]
            
            if status == 'A':
                changes['added'].add(file_path)
            elif status == 'M':
                changes['modified'].add(file_path)
            elif status == 'D':
                changes['deleted'].add(file_path)
        
        # Конвертируем обратно в списки
        return {k: sorted(list(v)) for k, v in changes.items()}
    
    except Exception as e:
        print(f"{Colors.WARNING}⚠️  Не удалось получить git изменения: {e}{Colors.ENDC}")
        return {'added': [], 'modified': [], 'deleted': []}

def get_current_version(project_root: Path) -> str:
    """Получить текущую версию из CHANGELOG."""
    changelog_path = project_root / "CHANGELOG.md"
    
    if not changelog_path.exists():
        return "0.0.0"
    
    try:
        content = changelog_path.read_text(encoding="utf-8")
        # Ищем первую версию вида ## [X.Y.Z]
        match = re.search(r'## \[(\d+\.\d+\.\d+)\]', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    
    return "0.0.0"

def suggest_next_version(current: str, changes: Dict[str, List[str]]) -> str:
    """
    Предложить следующую версию на основе изменений.
    
    Правила семантического версионирования:
    - MAJOR (X.0.0): критические изменения, несовместимость
    - MINOR (x.Y.0): новая функциональность, обратная совместимость
    - PATCH (x.y.Z): исправления, мелкие улучшения
    """
    major, minor, patch = map(int, current.split('.'))
    
    # Детектируем мажорные изменения
    has_major, major_files = detect_major_changes(changes)
    
    if not has_major:
        # Если нет мажорных изменений, это patch
        return f"{major}.{minor}.{patch + 1}"
    
    # Анализируем типы мажорных изменений
    categorized = categorize_changes(changes)
    
    # Критические изменения (требуют MAJOR версии)
    critical_changes = (
        len(categorized['contracts']) > 0 or  # Изменения в контрактах
        len(categorized['framework']) > 0 or  # Изменения в фреймворке
        any('.cursorrules' in file for file in changes['modified'] + changes['deleted'])  # Изменения в .cursorrules
    )
    
    # Новая функциональность (требует MINOR версии)
    new_features = (
        len(categorized['weeks']) > 0 or      # Новые/изменённые недели
        len(categorized['templates']) > 0 or  # Новые шаблоны
        len(categorized['cli']) > 0 or        # Изменения в CLI
        len(changes['added']) > 2             # Много новых файлов
    )
    
    if critical_changes:
        return f"{major + 1}.0.0"
    elif new_features:
        return f"{major}.{minor + 1}.0"
    else:
        # Мажорные изменения, но не критические и не новые фичи
        return f"{major}.{minor}.{patch + 1}"

def generate_changelog_entry(
    version: str,
    changes: Dict[str, List[str]],
    project_root: Path
) -> str:
    """Сгенерировать заготовку записи в CHANGELOG."""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"## [{version}] - {date_str}\n\n"
    
    # Категоризируем изменения
    categorized = categorize_changes(changes)
    has_major, major_files = detect_major_changes(changes)
    
    # Добавляем информацию о мажорных изменениях
    if has_major:
        entry += f"**🚨 Мажорные изменения:** {len(major_files)} файлов\n\n"
    
    # Added
    if changes['added']:
        entry += "### Added (Добавлено)\n"
        
        # Недели
        if categorized['weeks']:
            for file in categorized['weeks']:
                week_name = Path(file).stem
                entry += f"- ✅ **{file}** — детальная программа {week_name}\n"
        
        # Шаблоны
        if categorized['templates']:
            for file in categorized['templates']:
                template_name = Path(file).stem
                entry += f"- ✅ **{file}** — шаблон {template_name}\n"
        
        # CLI изменения
        if categorized['cli']:
            for file in categorized['cli']:
                entry += f"- ✅ **{file}** — обновление CLI инструмента\n"
        
        # Контракты
        if categorized['contracts']:
            for file in categorized['contracts']:
                entry += f"- ✅ **{file}** — обновление шаблона контракта\n"
        
        # Фреймворк
        if categorized['framework']:
            for file in categorized['framework']:
                entry += f"- ✅ **{file}** — обновление концептуального фреймворка\n"
        
        # Документация
        if categorized['docs']:
            for file in categorized['docs']:
                entry += f"- ✅ **{file}** — обновление документации\n"
        
        # Остальные файлы
        if categorized['other']:
            for file in categorized['other'][:3]:  # Ограничиваем 3 файлами
                entry += f"- ✅ **{file}**\n"
        
        entry += "\n"
    
    # Changed
    if changes['modified']:
        entry += "### Changed (Изменено)\n"
        
        # Недели
        if categorized['weeks']:
            for file in categorized['weeks']:
                entry += f"- 🔄 **{file}** — обновление программы недели\n"
        
        # Шаблоны
        if categorized['templates']:
            for file in categorized['templates']:
                entry += f"- 🔄 **{file}** — обновление шаблона\n"
        
        # CLI изменения
        if categorized['cli']:
            for file in categorized['cli']:
                entry += f"- 🔄 **{file}** — улучшение CLI инструмента\n"
        
        # Контракты
        if categorized['contracts']:
            for file in categorized['contracts']:
                entry += f"- 🔄 **{file}** — доработка шаблона контракта\n"
        
        # Фреймворк
        if categorized['framework']:
            for file in categorized['framework']:
                entry += f"- 🔄 **{file}** — эволюция концептуального фреймворка\n"
        
        # Документация
        if categorized['docs']:
            for file in categorized['docs']:
                entry += f"- 🔄 **{file}** — обновление документации\n"
        
        # Остальные файлы
        if categorized['other']:
            for file in categorized['other'][:3]:  # Ограничиваем 3 файлами
                entry += f"- 🔄 **{file}**\n"
        
        entry += "\n"
    
    # Deleted
    if changes['deleted']:
        entry += "### Removed (Удалено)\n"
        for file in changes['deleted'][:5]:
            entry += f"- 🗑️ **{file}**\n"
        entry += "\n"
    
    # Impact - генерируем автоматически на основе типов изменений
    entry += "### Impact (Влияние)\n"
    
    impact_items = []
    if categorized['weeks']:
        impact_items.append("- Обновлены программы недель курса")
    if categorized['templates']:
        impact_items.append("- Добавлены/обновлены шаблоны для участников")
    if categorized['cli']:
        impact_items.append("- Улучшен CLI инструмент для работы с курсом")
    if categorized['contracts']:
        impact_items.append("- Эволюционировал шаблон личного контракта")
    if categorized['framework']:
        impact_items.append("- Развит концептуальный фреймворк курса")
    if categorized['docs']:
        impact_items.append("- Обновлена документация проекта")
    
    if impact_items:
        for item in impact_items:
            entry += f"{item}\n"
    else:
        entry += "- [Опишите влияние изменений на пользователей/участников курса]\n"
    
    entry += "\n---\n\n"
    
    return entry

def update_changelog_interactive(project_root: Path, changes: Dict[str, List[str]]):
    """Интерактивное обновление CHANGELOG."""
    changelog_path = project_root / "CHANGELOG.md"
    
    if not changelog_path.exists():
        print(f"{Colors.FAIL}❌ CHANGELOG.md не найден!{Colors.ENDC}")
        return
    
    current_version = get_current_version(project_root)
    suggested_version = suggest_next_version(current_version, changes)
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}📝 Обновление CHANGELOG{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Текущая версия: {current_version}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Предлагаемая версия: {suggested_version}{Colors.ENDC}\n")
    
    # Спрашиваем версию
    version_input = input(f"Введите версию (Enter для {suggested_version}): ").strip()
    version = version_input if version_input else suggested_version
    
    # Генерируем заготовку
    entry = generate_changelog_entry(version, changes, project_root)
    
    print(f"\n{Colors.OKCYAN}Сгенерированная заготовка:{Colors.ENDC}")
    print(f"{Colors.BOLD}{'─'*70}{Colors.ENDC}")
    print(entry)
    print(f"{Colors.BOLD}{'─'*70}{Colors.ENDC}\n")
    
    confirm = input(f"Добавить эту запись в CHANGELOG? (y/n): ").strip().lower()
    
    if confirm == 'y':
        try:
            # Читаем текущий CHANGELOG
            content = changelog_path.read_text(encoding="utf-8")
            
            # Находим позицию после [Unreleased] или в начале
            unreleased_pos = content.find("## [Unreleased]")
            
            if unreleased_pos != -1:
                # Находим конец секции [Unreleased]
                next_version_pos = content.find("\n## [", unreleased_pos + 1)
                if next_version_pos == -1:
                    next_version_pos = content.find("\n---", unreleased_pos)
                
                # Вставляем новую запись
                if next_version_pos != -1:
                    new_content = (
                        content[:next_version_pos] + 
                        "\n" + entry +
                        content[next_version_pos:]
                    )
                else:
                    new_content = content + "\n" + entry
            else:
                # Если нет секции Unreleased, ищем первую версию
                first_version_pos = content.find("## [")
                if first_version_pos != -1:
                    new_content = (
                        content[:first_version_pos] +
                        entry + "\n" +
                        content[first_version_pos:]
                    )
                else:
                    new_content = content + "\n" + entry
            
            # Сохраняем
            changelog_path.write_text(new_content, encoding="utf-8")
            print(f"{Colors.OKGREEN}✅ CHANGELOG обновлён!{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Ошибка обновления: {e}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⏸️  Обновление отменено{Colors.ENDC}")

def suggest_assessment_updates(project_root: Path, changes: Dict[str, List[str]]):
    """Предложить, какие блоки ASSESSMENT нужно обновить."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}📊 Рекомендации по ASSESSMENT.md{Colors.ENDC}\n")
    
    suggestions = []
    
    # Проверяем изменения в weeks/
    weeks_changes = [f for f in changes['added'] + changes['modified'] if 'weeks/' in f]
    if weeks_changes:
        suggestions.append("• Обновить блок '2. Структура курса (8 недель)'")
        suggestions.append(f"  Изменено файлов: {len(weeks_changes)}")
    
    # Проверяем изменения в Personal_Contract
    contract_changes = [f for f in changes['added'] + changes['modified'] 
                       if 'Personal_Contract' in f or 'contract' in f.lower()]
    if contract_changes:
        suggestions.append("• Обновить блок '3. Личный контракт'")
    
    # Проверяем изменения в templates/
    template_changes = [f for f in changes['added'] + changes['modified'] if 'templates/' in f]
    if template_changes:
        suggestions.append("• Обновить блок '6. Операционные инструменты'")
    
    # Проверяем изменения в examples/
    example_changes = [f for f in changes['added'] + changes['modified'] if 'examples/' in f]
    if example_changes:
        suggestions.append("• Обновить блок '7. Кейсы и примеры'")
    
    if suggestions:
        for s in suggestions:
            print(f"{Colors.OKCYAN}{s}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}💡 Не забудьте пересчитать проценты готовности!{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}✅ ASSESSMENT не требует обновления для текущих изменений{Colors.ENDC}")

def check_readme_needs_update(project_root: Path, changes: Dict[str, List[str]]):
    """Проверить, нужно ли обновить README."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}📖 Проверка README.md{Colors.ENDC}\n")
    
    needs_update = False
    categorized = categorize_changes(changes)
    
    # Новые недели → нужно добавить ссылки
    if categorized['weeks']:
        print(f"{Colors.WARNING}⚠️  Изменено недель: {len(categorized['weeks'])}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Проверьте, что в README есть ссылки на эти недели{Colors.ENDC}")
        needs_update = True
    
    # Новые шаблоны → нужно добавить упоминание
    if categorized['templates']:
        print(f"{Colors.WARNING}⚠️  Изменено шаблонов: {len(categorized['templates'])}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Проверьте раздел 'Шаблоны' в README{Colors.ENDC}")
        needs_update = True
    
    # CLI изменения → нужно обновить раздел CLI
    if categorized['cli']:
        print(f"{Colors.WARNING}⚠️  Изменён CLI: {len(categorized['cli'])} файлов{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Проверьте раздел 'Инструменты для работы с курсом' в README{Colors.ENDC}")
        needs_update = True
    
    if not needs_update:
        print(f"{Colors.OKGREEN}✅ README не требует обновления{Colors.ENDC}")

def check_cursor_setup_needs_update(project_root: Path, changes: Dict[str, List[str]]):
    """Проверить, нужно ли обновить CURSOR_SETUP.md."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}🎯 Проверка CURSOR_SETUP.md{Colors.ENDC}\n")
    
    needs_update = False
    
    # Изменения в .cursorrules
    cursorrules_changed = any('.cursorrules' in file for file in changes['modified'] + changes['deleted'])
    if cursorrules_changed:
        print(f"{Colors.WARNING}⚠️  Изменён .cursorrules{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Обновите CURSOR_SETUP.md с новыми правилами{Colors.ENDC}")
        needs_update = True
    
    # Изменения в CLI
    cli_changed = any('course_cli/' in file for file in changes['modified'] + changes['added'])
    if cli_changed:
        print(f"{Colors.WARNING}⚠️  Изменён CLI инструмент{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Проверьте инструкции по установке CLI в CURSOR_SETUP.md{Colors.ENDC}")
        needs_update = True
    
    if not needs_update:
        print(f"{Colors.OKGREEN}✅ CURSOR_SETUP.md не требует обновления{Colors.ENDC}")

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Помощник для обновления документации проекта Системная карьера",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/update_docs.py
  python scripts/update_docs.py --days 14
  python scripts/update_docs.py --no-interactive
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Количество дней для анализа изменений (по умолчанию: 7)'
    )
    
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Неинтерактивный режим (только анализ, без обновления CHANGELOG)'
    )
    
    args = parser.parse_args()
    
    project_root = get_project_root()
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}🔧 Помощник обновления документации{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    # Получаем изменения из git
    print(f"\n{Colors.OKCYAN}📊 Анализ изменений за последние {args.days} дней...{Colors.ENDC}\n")
    changes = get_git_changes(project_root, days=args.days)
    
    total = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])
    
    if total == 0:
        print(f"{Colors.WARNING}⚠️  Изменений не обнаружено (или git недоступен){Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Вы можете вручную обновить документацию{Colors.ENDC}\n")
        return 0
    
    print(f"{Colors.OKGREEN}Найдено изменений: {total}{Colors.ENDC}")
    print(f"  • Добавлено: {len(changes['added'])}")
    print(f"  • Изменено: {len(changes['modified'])}")
    print(f"  • Удалено: {len(changes['deleted'])}")
    
    # Проверяем мажорные изменения
    has_major, major_files = detect_major_changes(changes)
    if has_major:
        print(f"\n{Colors.WARNING}🚨 Обнаружены мажорные изменения: {len(major_files)} файлов{Colors.ENDC}")
        for file in major_files[:5]:  # Показываем первые 5
            print(f"  • {file}")
        if len(major_files) > 5:
            print(f"  • ... и ещё {len(major_files) - 5} файлов")
    
    # Обновление CHANGELOG (только в интерактивном режиме)
    if not args.no_interactive:
        update_changelog_interactive(project_root, changes)
    
    # Рекомендации по ASSESSMENT
    suggest_assessment_updates(project_root, changes)
    
    # Проверка README
    check_readme_needs_update(project_root, changes)
    
    # Проверка CURSOR_SETUP.md
    check_cursor_setup_needs_update(project_root, changes)
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Готово!{Colors.ENDC}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

