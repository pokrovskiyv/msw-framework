#!/usr/bin/env python3
"""
Проверка синхронности документации проекта Системная карьера.

Анализирует изменения в ключевых файлах и проверяет,
обновлены ли CHANGELOG.md, ASSESSMENT.md, README.md и другие документы.
"""

import os
import sys
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

def check_assessment_vs_weeks(project_root: Path) -> Tuple[bool, str, List[str]]:
    """
    Проверить, обновлялся ли ASSESSMENT после изменений в weeks/.
    
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

def check_changelog_version_consistency(project_root: Path) -> Tuple[bool, str, List[str]]:
    """
    Проверить консистентность версий в CHANGELOG.
    
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
    
    # Поиск версий вида ## [X.Y.Z]
    version_pattern = r'## \[(\d+\.\d+\.\d+)\]'
    versions = re.findall(version_pattern, content)
    
    issues = []
    
    # Проверка: есть ли секция [Unreleased]
    if "[Unreleased]" not in content:
        issues.append("  • Отсутствует секция [Unreleased] для текущих изменений")
    
    # Проверка: версии идут в убывающем порядке
    if len(versions) > 1:
        for i in range(len(versions) - 1):
            current = tuple(map(int, versions[i].split('.')))
            next_ver = tuple(map(int, versions[i+1].split('.')))
            if current < next_ver:
                issues.append(f"  • Версии не в порядке убывания: {versions[i]} < {versions[i+1]}")
    
    if issues:
        return False, f"⚠️  Найдено {len(issues)} проблем с версионированием:", issues
    
    return True, f"✅ CHANGELOG: версии корректны (последняя: {versions[0] if versions else 'не найдена'})", []

def print_report(checks: List[Tuple[bool, str, List[str]]]):
    """
    Вывести итоговый отчёт проверок.
    
    Args:
        checks: список результатов проверок (is_ok, message, details)
    """
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}📋 Проверка синхронности документации{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    all_ok = True
    warnings_count = 0
    
    for is_ok, message, details in checks:
        if is_ok:
            print(f"{Colors.OKGREEN}{message}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}{message}{Colors.ENDC}")
            all_ok = False
            warnings_count += 1
        
        if details:
            for detail in details:
                print(f"{Colors.OKCYAN}{detail}{Colors.ENDC}")
        print()
    
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    if all_ok:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ Все проверки пройдены! Документация синхронизирована.{Colors.ENDC}\n")
        return 0
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  Обнаружено {warnings_count} предупреждений.{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Рекомендуется обновить документацию:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   python scripts/update_docs.py{Colors.ENDC}\n")
        return 1

def main():
    """Основная функция проверки."""
    project_root = get_project_root()
    
    # Список всех проверок (оборачиваем результаты с 2 значениями в tuple с пустым списком)
    checks = []
    
    # Проверка CHANGELOG (возвращает 2 значения)
    is_ok, message = check_changelog_up_to_date(project_root)
    checks.append((is_ok, message, []))
    
    # Остальные проверки (возвращают 3 значения)
    checks.append(check_assessment_vs_weeks(project_root))
    checks.append(check_readme_links(project_root))
    checks.append(check_contract_templates_vs_weeks(project_root))
    checks.append(check_changelog_version_consistency(project_root))
    
    return print_report(checks)

if __name__ == "__main__":
    sys.exit(main())

