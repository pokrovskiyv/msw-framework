#!/usr/bin/env python3
"""
Помощник для обновления документации проекта Системная карьера.

Анализирует изменения в git и помогает обновить CHANGELOG, ASSESSMENT и README.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
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
    
    # Анализируем масштаб изменений
    total_changes = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])
    
    # Проверяем критичные изменения (новые недели, изменения в контрактах)
    critical_files = ['Personal_Contract', 'Systemic_Career_Framework']
    has_critical_changes = any(
        any(cf in file for cf in critical_files)
        for file in changes['modified'] + changes['deleted']
    )
    
    # Проверяем новую функциональность (новые недели, новые шаблоны)
    new_weeks = any('Week_' in file for file in changes['added'])
    new_templates = any('templates/' in file for file in changes['added'])
    has_new_features = new_weeks or new_templates or len(changes['added']) > 3
    
    if has_critical_changes:
        return f"{major + 1}.0.0"
    elif has_new_features:
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"

def generate_changelog_entry(
    version: str,
    changes: Dict[str, List[str]],
    project_root: Path
) -> str:
    """Сгенерировать заготовку записи в CHANGELOG."""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"## [{version}] - {date_str}\n\n"
    
    # Группируем изменения по категориям
    weeks_added = [f for f in changes['added'] if 'weeks/Week_' in f]
    weeks_modified = [f for f in changes['modified'] if 'weeks/Week_' in f]
    templates_added = [f for f in changes['added'] if 'templates/' in f]
    templates_modified = [f for f in changes['modified'] if 'templates/' in f]
    docs_modified = [f for f in changes['modified'] if f.endswith('.md') and '/' not in f]
    
    # Added
    if changes['added']:
        entry += "### Added (Добавлено)\n"
        
        if weeks_added:
            for file in weeks_added:
                week_name = Path(file).stem
                entry += f"- ✅ **{file}** — детальная программа {week_name}\n"
        
        if templates_added:
            for file in templates_added:
                template_name = Path(file).stem
                entry += f"- ✅ **{file}** — шаблон {template_name}\n"
        
        # Остальные файлы
        other_added = [f for f in changes['added'] 
                      if f not in weeks_added and f not in templates_added]
        for file in other_added[:5]:  # Ограничиваем 5 файлами
            entry += f"- ✅ **{file}**\n"
        
        entry += "\n"
    
    # Changed
    if changes['modified']:
        entry += "### Changed (Изменено)\n"
        
        if weeks_modified:
            for file in weeks_modified:
                entry += f"- 🔄 **{file}** — обновление программы недели\n"
        
        if templates_modified:
            for file in templates_modified:
                entry += f"- 🔄 **{file}** — обновление шаблона\n"
        
        if docs_modified:
            for file in docs_modified:
                entry += f"- 🔄 **{file}** — обновление документации\n"
        
        entry += "\n"
    
    # Deleted
    if changes['deleted']:
        entry += "### Removed (Удалено)\n"
        for file in changes['deleted'][:5]:
            entry += f"- 🗑️ **{file}**\n"
        entry += "\n"
    
    entry += "### Impact (Влияние)\n"
    entry += "- [Опишите влияние изменений на пользователей/участников курса]\n\n"
    
    entry += "---\n\n"
    
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
    
    # Новые недели → нужно добавить ссылки
    new_weeks = [f for f in changes['added'] if 'weeks/Week_' in f]
    if new_weeks:
        print(f"{Colors.WARNING}⚠️  Добавлено недель: {len(new_weeks)}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Проверьте, что в README есть ссылки на эти недели{Colors.ENDC}")
        needs_update = True
    
    # Новые шаблоны → нужно добавить упоминание
    new_templates = [f for f in changes['added'] if 'templates/' in f]
    if new_templates:
        print(f"{Colors.WARNING}⚠️  Добавлено шаблонов: {len(new_templates)}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}   Проверьте раздел 'Шаблоны' в README{Colors.ENDC}")
        needs_update = True
    
    if not needs_update:
        print(f"{Colors.OKGREEN}✅ README не требует обновления{Colors.ENDC}")

def main():
    """Основная функция."""
    project_root = get_project_root()
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}🔧 Помощник обновления документации{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    # Получаем изменения из git
    print(f"\n{Colors.OKCYAN}📊 Анализ изменений за последние 7 дней...{Colors.ENDC}\n")
    changes = get_git_changes(project_root, days=7)
    
    total = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])
    
    if total == 0:
        print(f"{Colors.WARNING}⚠️  Изменений не обнаружено (или git недоступен){Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Вы можете вручную обновить документацию{Colors.ENDC}\n")
        return 0
    
    print(f"{Colors.OKGREEN}Найдено изменений: {total}{Colors.ENDC}")
    print(f"  • Добавлено: {len(changes['added'])}")
    print(f"  • Изменено: {len(changes['modified'])}")
    print(f"  • Удалено: {len(changes['deleted'])}")
    
    # Обновление CHANGELOG
    update_changelog_interactive(project_root, changes)
    
    # Рекомендации по ASSESSMENT
    suggest_assessment_updates(project_root, changes)
    
    # Проверка README
    check_readme_needs_update(project_root, changes)
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Готово!{Colors.ENDC}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

