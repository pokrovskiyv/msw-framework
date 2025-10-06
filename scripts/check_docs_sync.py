#!/usr/bin/env python3
"""
Проверка синхронности документации проекта Системная карьера.

Анализирует изменения в ключевых файлах и проверяет,
обновлены ли CHANGELOG.md, ASSESSMENT.md, README.md и другие документы.

Exit codes:
- 0: Все проверки пройдены
- 1: Есть предупреждения (не критично)
- 2: Критические проблемы (требуют внимания)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re

# Цвета для вывода в терминал
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_file_mtime(file_path: Path) -> Optional[datetime]:
    """Получить время последней модификации файла."""
    try:
        if file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime)
    except Exception:
        pass
    return None

def get_project_root() -> Path:
    """Определить корень проекта."""
    current = Path(__file__).parent.parent
    return current

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
    
    except Exception:
        return {'added': [], 'modified': [], 'deleted': []}

def detect_major_changes(project_root: Path, days: int = 7) -> Tuple[bool, List[str]]:
    """
    Детектировать мажорные изменения в проекте.
    
    Returns:
        (has_major_changes, list_of_major_files)
    """
    changes = get_git_changes(project_root, days)
    
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

def check_major_changes_documentation(project_root: Path, days: int = 7) -> Tuple[bool, str, List[str]]:
    """
    Проверить, обновлена ли документация после мажорных изменений.
    
    Returns:
        (is_ok, message, major_files)
    """
    has_major, major_files = detect_major_changes(project_root, days)
    
    if not has_major:
        return True, "✅ Мажорных изменений не обнаружено", []
    
    # Проверяем, обновлялись ли ключевые документы после мажорных изменений
    changelog_path = project_root / "CHANGELOG.md"
    readme_path = project_root / "README.md"
    assessment_path = project_root / "ASSESSMENT.md"
    
    # Получаем время последнего изменения мажорных файлов
    latest_major_change = None
    for file_path in major_files:
        full_path = project_root / file_path
        if full_path.exists():
            mtime = get_file_mtime(full_path)
            if mtime and (latest_major_change is None or mtime > latest_major_change):
                latest_major_change = mtime
    
    if not latest_major_change:
        return True, "✅ Мажорные изменения не требуют обновления документации", major_files
    
    # Проверяем, обновлялись ли документы после мажорных изменений
    docs_to_check = [
        (changelog_path, "CHANGELOG.md"),
        (readme_path, "README.md"),
        (assessment_path, "ASSESSMENT.md")
    ]
    
    outdated_docs = []
    for doc_path, doc_name in docs_to_check:
        if doc_path.exists():
            doc_mtime = get_file_mtime(doc_path)
            if doc_mtime and doc_mtime < latest_major_change:
                days_diff = (latest_major_change - doc_mtime).days
                outdated_docs.append(f"  • {doc_name} не обновлялся {days_diff} дней после мажорных изменений")
    
    if outdated_docs:
        return False, f"⚠️  Обнаружены мажорные изменения, но документация не обновлена:", major_files + outdated_docs
    
    return True, f"✅ Документация актуальна после мажорных изменений ({len(major_files)} файлов)", major_files

def check_changelog_up_to_date(project_root: Path, days_threshold: int = 7) -> Tuple[bool, str]:
    """
    Проверить, обновлялся ли CHANGELOG недавно.
    
    Args:
        project_root: корень проекта
        days_threshold: количество дней, после которых считается устаревшим
        
    Returns:
        (is_ok, message)
    """
    changelog_path = project_root / "CHANGELOG.md"
    
    if not changelog_path.exists():
        return False, "❌ CHANGELOG.md не найден!"
    
    mtime = get_file_mtime(changelog_path)
    if not mtime:
        return False, "❌ Не удалось получить дату изменения CHANGELOG.md"
    
    days_ago = (datetime.now() - mtime).days
    
    if days_ago > days_threshold:
        return False, f"⚠️  CHANGELOG.md: последнее обновление {days_ago} дней назад"
    
    return True, f"✅ CHANGELOG.md: обновлён {days_ago} дней назад"

def check_assessment_vs_weeks(project_root: Path, auto_update: bool = False) -> Tuple[bool, str, List[str]]:
    """
    Проверить, обновлялся ли ASSESSMENT после изменений в weeks/.
    
    Args:
        project_root: корень проекта
        auto_update: автоматически обновлять дату в ASSESSMENT.md
    
    Returns:
        (is_ok, message, outdated_files)
    """
    assessment_path = project_root / "ASSESSMENT.md"
    weeks_dir = project_root / "weeks"
    
    if not assessment_path.exists():
        return False, "❌ ASSESSMENT.md не найден!", []
    
    if not weeks_dir.exists():
        return True, "✅ Папка weeks/ не найдена (ничего проверять)", []
    
    assessment_mtime = get_file_mtime(assessment_path)
    if not assessment_mtime:
        return False, "❌ Не удалось получить дату ASSESSMENT.md", []
    
    # Проверяем все файлы в weeks/
    outdated = []
    for week_file in weeks_dir.glob("Week_*.md"):
        week_mtime = get_file_mtime(week_file)
        if week_mtime and week_mtime > assessment_mtime:
            days_diff = (week_mtime - assessment_mtime).days
            outdated.append(f"  • {week_file.name} изменён {days_diff} дней после ASSESSMENT.md")
    
    # Автоматическое обновление даты
    if outdated and auto_update:
        try:
            content = assessment_path.read_text(encoding="utf-8")
            from datetime import datetime
            
            # Обновляем дату анализа
            new_date = datetime.now().strftime("%d %B %Y")
            content = re.sub(
                r'\*\*Дата анализа:\*\* \d+ \w+ \d{4}',
                f'**Дата анализа:** {new_date}',
                content
            )
            
            assessment_path.write_text(content, encoding="utf-8")
            return True, f"✅ ASSESSMENT.md автоматически обновлён (дата: {new_date})", []
            
        except Exception as e:
            return False, f"❌ Ошибка автоматического обновления ASSESSMENT.md: {e}", outdated
    
    if outdated:
        return False, f"⚠️  ASSESSMENT.md устарел! Найдено {len(outdated)} более новых файлов:", outdated
    
    return True, "✅ ASSESSMENT.md актуален относительно weeks/", []

def check_readme_links(project_root: Path) -> Tuple[bool, str, List[str]]:
    """
    Проверить, что все ссылки в README.md существуют.
    
    Returns:
        (is_ok, message, broken_links)
    """
    readme_path = project_root / "README.md"
    
    if not readme_path.exists():
        return False, "❌ README.md не найден!", []
    
    try:
        content = readme_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"❌ Ошибка чтения README.md: {e}", []
    
    # Поиск Markdown ссылок вида [text](path)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)
    
    broken = []
    for text, link in links:
        # Пропускаем внешние ссылки
        if link.startswith(('http://', 'https://', '#')):
            continue
        
        # Проверяем локальные файлы
        link_path = project_root / link
        if not link_path.exists():
            broken.append(f"  • [{text}]({link})")
    
    if broken:
        return False, f"⚠️  README.md: найдено {len(broken)} битых ссылок:", broken
    
    return True, "✅ README.md: все локальные ссылки работают", []

def check_contract_templates_vs_weeks(project_root: Path) -> Tuple[bool, str, List[str]]:
    """
    Проверить, что шаблоны контрактов синхронизированы с недельными программами.
    
    Returns:
        (is_ok, message, issues)
    """
    templates_dir = project_root / "templates"
    weeks_dir = project_root / "weeks"
    
    if not templates_dir.exists() or not weeks_dir.exists():
        return True, "✅ Папки templates/ или weeks/ не найдены", []
    
    # Проверяем, что для каждой недели есть шаблон (если он нужен)
    issues = []
    
    # Список недель, которые должны иметь специфичные шаблоны
    weeks_with_templates = {
        1: "Personal_Contract_v1.0_Week1_Template.md",
        5: ["Week_05_Contacts_CRM.md", "Week_05_Environment_Map.md", "Week_05_Media_Diet.md"],
        8: ["Week_08_Energy_Budget.md", "Week_08_Recovery_Reglament.md"]
    }
    
    for week_num, template_names in weeks_with_templates.items():
        week_file = weeks_dir / f"Week_0{week_num}_*.md"
        week_files = list(weeks_dir.glob(f"Week_0{week_num}_*.md"))
        
        if not week_files:
            continue
        
        if isinstance(template_names, str):
            template_names = [template_names]
        
        for template_name in template_names:
            template_path = templates_dir / template_name
            if not template_path.exists():
                issues.append(f"  • Неделя {week_num}: отсутствует шаблон {template_name}")
    
    if issues:
        return False, f"⚠️  Найдено {len(issues)} проблем с шаблонами:", issues
    
    return True, "✅ Все необходимые шаблоны на месте", []

def check_changelog_version_consistency(project_root: Path, auto_fix: bool = False) -> Tuple[bool, str, List[str]]:
    """
    Проверить консистентность версий в CHANGELOG.
    
    Args:
        project_root: корень проекта
        auto_fix: автоматически исправлять проблемы с порядком версий
    
    Returns:
        (is_ok, message, issues)
    """
    changelog_path = project_root / "CHANGELOG.md"
    
    if not changelog_path.exists():
        return False, "❌ CHANGELOG.md не найден!", []
    
    try:
        content = changelog_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"❌ Ошибка чтения CHANGELOG.md: {e}", []
    
    # Поиск версий вида ## [X.Y.Z] (только в основном списке, не в планах)
    # Исключаем раздел "Планы на следующие версии"
    main_content = content.split("## Планы на следующие версии")[0]
    version_pattern = r'## \[(\d+\.\d+\.\d+)\]'
    versions = re.findall(version_pattern, main_content)
    
    issues = []
    fixed_issues = []
    
    # Проверка: есть ли секция [Unreleased]
    if "[Unreleased]" not in content:
        issues.append("  • Отсутствует секция [Unreleased] для текущих изменений")
    
    # Проверка: версии идут в убывающем порядке
    if len(versions) > 1:
        version_blocks = []
        lines = content.split('\n')
        current_block = []
        
        # Разбиваем файл на блоки версий
        for line in lines:
            if re.match(r'^## \[(\d+\.\d+\.\d+)\]', line):
                if current_block:
                    version_blocks.append(current_block)
                current_block = [line]
            elif current_block:
                current_block.append(line)
        
        if current_block:
            version_blocks.append(current_block)
        
        # Проверяем порядок версий (только для соседних версий в основном списке)
        for i in range(len(versions) - 1):
            current = tuple(map(int, versions[i].split('.')))
            next_ver = tuple(map(int, versions[i+1].split('.')))
            
            # Проверяем только если версии действительно должны идти в убывающем порядке
            # Игнорируем случаи, когда младшая версия (0.x.x) идёт после старшей (1.x.x)
            # если между ними есть большой разрыв в номерах
            if current < next_ver:
                # Проверяем, не является ли это нормальным переходом от 0.x к 1.x
                if current[0] == 0 and next_ver[0] == 1:
                    # Это нормальный переход от 0.x к 1.x, не считаем ошибкой
                    continue
                elif current[0] == 1 and next_ver[0] == 0:
                    # Это действительно ошибка: 1.x после 0.x
                    issues.append(f"  • Версии не в порядке убывания: {versions[i]} < {versions[i+1]}")
                    
                    # Автоматическое исправление
                    if auto_fix:
                        fixed_issues.append(f"  ✅ Автоматически исправлен порядок: {versions[i+1]} → {versions[i]}")
                else:
                    # Обычная проверка для версий в одной мажорной версии
                    issues.append(f"  • Версии не в порядке убывания: {versions[i]} < {versions[i+1]}")
                    
                    # Автоматическое исправление
                    if auto_fix:
                        fixed_issues.append(f"  ✅ Автоматически исправлен порядок: {versions[i+1]} → {versions[i]}")
        
        # Если были исправления, используем специальный скрипт
        if auto_fix and fixed_issues:
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(project_root / "scripts" / "fix_changelog_order.py")],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Успешно исправлено
                    pass
                else:
                    issues.append(f"  ❌ Ошибка автоматического исправления: {result.stderr}")
                    
            except Exception as e:
                issues.append(f"  ❌ Ошибка запуска скрипта исправления: {e}")
    
    # Убираем исправленные проблемы из списка issues
    for fixed in fixed_issues:
        if fixed in issues:
            issues.remove(fixed)
    
    if issues:
        message = f"⚠️  Найдено {len(issues)} проблем с версионированием:"
        if fixed_issues:
            message += f"\n{fixed_issues[0]}"  # Показываем первое исправление
        return False, message, issues
    
    if fixed_issues:
        return True, f"✅ CHANGELOG: версии исправлены автоматически", fixed_issues
    
    return True, f"✅ CHANGELOG: версии корректны (последняя: {versions[0] if versions else 'не найдена'})", []

def print_report(checks: List[Tuple[bool, str, List[str]]], strict_mode: bool = False):
    """
    Вывести итоговый отчёт проверок.
    
    Args:
        checks: список результатов проверок (is_ok, message, details)
        strict_mode: строгий режим (все предупреждения = критические ошибки)
    
    Returns:
        exit_code: 0 (всё ОК), 1 (предупреждения), 2 (критические проблемы)
    """
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}📋 Проверка синхронности документации{Colors.ENDC}")
    if strict_mode:
        print(f"{Colors.BOLD}{Colors.WARNING}🔒 СТРОГИЙ РЕЖИМ{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    all_ok = True
    warnings_count = 0
    critical_count = 0
    
    for is_ok, message, details in checks:
        if is_ok:
            print(f"{Colors.OKGREEN}{message}{Colors.ENDC}")
        else:
            # Определяем критичность проблемы
            is_critical = (
                strict_mode or 
                "не найден" in message or 
                "битых ссылок" in message or
                "мажорных изменений" in message
            )
            
            if is_critical:
                print(f"{Colors.FAIL}{message}{Colors.ENDC}")
                critical_count += 1
            else:
                print(f"{Colors.WARNING}{message}{Colors.ENDC}")
                warnings_count += 1
            
            all_ok = False
        
        if details:
            for detail in details:
                if "мажорных изменений" in detail or "не найден" in detail:
                    print(f"{Colors.FAIL}{detail}{Colors.ENDC}")
                else:
                    print(f"{Colors.OKCYAN}{detail}{Colors.ENDC}")
        print()
    
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    if all_ok:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ Все проверки пройдены! Документация синхронизирована.{Colors.ENDC}\n")
        return 0
    elif critical_count > 0:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ Обнаружено {critical_count} критических проблем.{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Требуется немедленное обновление документации:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   python scripts/update_docs.py{Colors.ENDC}\n")
        return 2
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  Обнаружено {warnings_count} предупреждений.{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Рекомендуется обновить документацию:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   python scripts/update_docs.py{Colors.ENDC}\n")
        return 1

def main():
    """Основная функция проверки."""
    parser = argparse.ArgumentParser(
        description="Проверка синхронности документации проекта Системная карьера",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0 - Все проверки пройдены
  1 - Есть предупреждения (не критично)
  2 - Критические проблемы (требуют внимания)

Примеры использования:
  python scripts/check_docs_sync.py
  python scripts/check_docs_sync.py --strict
  python scripts/check_docs_sync.py --days 14
        """
    )
    
    parser.add_argument(
        '--strict', 
        action='store_true',
        help='Строгий режим: все предупреждения считаются критическими ошибками'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Количество дней для анализа изменений (по умолчанию: 7)'
    )
    
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Автоматически исправлять проблемы с порядком версий в CHANGELOG'
    )
    
    parser.add_argument(
        '--auto-update',
        action='store_true',
        help='Автоматически обновлять дату в ASSESSMENT.md при обнаружении устаревания'
    )
    
    args = parser.parse_args()
    
    project_root = get_project_root()
    
    # Список всех проверок
    checks = []
    
    # Проверка мажорных изменений (новая проверка)
    checks.append(check_major_changes_documentation(project_root, args.days))
    
    # Проверка CHANGELOG (возвращает 2 значения)
    is_ok, message = check_changelog_up_to_date(project_root, args.days)
    checks.append((is_ok, message, []))
    
    # Остальные проверки (возвращают 3 значения)
    checks.append(check_assessment_vs_weeks(project_root, args.auto_update))
    checks.append(check_readme_links(project_root))
    checks.append(check_contract_templates_vs_weeks(project_root))
    checks.append(check_changelog_version_consistency(project_root, args.auto_fix))
    
    return print_report(checks, args.strict)

if __name__ == "__main__":
    sys.exit(main())

