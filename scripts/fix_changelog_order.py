#!/usr/bin/env python3
"""
Скрипт для исправления порядка версий в CHANGELOG.md.

Исправляет проблемы с порядком версий, когда более новые версии
идут после более старых (например, 1.0.0 после 1.1.0).

Использование:
  python scripts/fix_changelog_order.py
  python scripts/fix_changelog_order.py --dry-run
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple

def get_project_root() -> Path:
    """Определить корень проекта."""
    return Path(__file__).parent.parent

def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Парсинг версии в кортеж (major, minor, patch)."""
    parts = version_str.split('.')
    return (int(parts[0]), int(parts[1]), int(parts[2]))

def find_version_blocks(content: str) -> List[Tuple[str, int, int]]:
    """
    Найти все блоки версий в CHANGELOG.
    
    Returns:
        List of (version, start_line, end_line)
    """
    lines = content.split('\n')
    version_blocks = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'^## \[(\d+\.\d+\.\d+)\]', line)
        if match:
            version = match.group(1)
            start_line = i
            
            # Ищем конец блока (следующая версия или конец файла)
            end_line = len(lines)
            for j in range(i + 1, len(lines)):
                if re.match(r'^## \[(\d+\.\d+\.\d+)\]', lines[j]):
                    end_line = j
                    break
            
            version_blocks.append((version, start_line, end_line))
            i = end_line
        else:
            i += 1
    
    return version_blocks

def fix_changelog_order(changelog_path: Path, dry_run: bool = False) -> bool:
    """
    Исправить порядок версий в CHANGELOG.md.
    
    Args:
        changelog_path: путь к CHANGELOG.md
        dry_run: только показать, что будет исправлено
    
    Returns:
        True если были исправления
    """
    if not changelog_path.exists():
        print(f"❌ Файл {changelog_path} не найден")
        return False
    
    try:
        content = changelog_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return False
    
    # Находим блоки версий
    version_blocks = find_version_blocks(content)
    
    if len(version_blocks) < 2:
        print("✅ Менее 2 версий найдено, исправления не нужны")
        return False
    
    # Проверяем порядок версий
    needs_fix = False
    for i in range(len(version_blocks) - 1):
        current_version = version_blocks[i][0]
        next_version = version_blocks[i + 1][0]
        
        current_tuple = parse_version(current_version)
        next_tuple = parse_version(next_version)
        
        if current_tuple < next_tuple:
            print(f"⚠️  Найдена проблема: {current_version} < {next_version}")
            needs_fix = True
    
    if not needs_fix:
        print("✅ Порядок версий корректный")
        return False
    
    if dry_run:
        print("🔍 DRY RUN: исправления не применены")
        return True
    
    # Исправляем порядок
    lines = content.split('\n')
    new_lines = []
    
    # Копируем заголовок до первой версии
    first_version_start = version_blocks[0][1]
    new_lines.extend(lines[:first_version_start])
    
    # Сортируем блоки версий по убыванию
    sorted_blocks = sorted(version_blocks, key=lambda x: parse_version(x[0]), reverse=True)
    
    # Добавляем блоки в правильном порядке
    for i, (version, start_line, end_line) in enumerate(sorted_blocks):
        block_lines = lines[start_line:end_line]
        new_lines.extend(block_lines)
        
        # Добавляем разделитель между блоками (кроме последнего)
        if i < len(sorted_blocks) - 1:
            new_lines.append("")
    
    # Записываем исправленный файл
    try:
        new_content = '\n'.join(new_lines)
        changelog_path.write_text(new_content, encoding="utf-8")
        print("✅ CHANGELOG.md исправлен")
        return True
    except Exception as e:
        print(f"❌ Ошибка записи файла: {e}")
        return False

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Исправление порядка версий в CHANGELOG.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/fix_changelog_order.py
  python scripts/fix_changelog_order.py --dry-run
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Только показать, что будет исправлено, не применять изменения'
    )
    
    args = parser.parse_args()
    
    project_root = get_project_root()
    changelog_path = project_root / "CHANGELOG.md"
    
    print("🔧 Исправление порядка версий в CHANGELOG.md")
    print("=" * 50)
    
    fixed = fix_changelog_order(changelog_path, args.dry_run)
    
    if fixed and not args.dry_run:
        print("\n✅ Исправления применены успешно")
    elif fixed and args.dry_run:
        print("\n🔍 Для применения исправлений запустите без --dry-run")
    else:
        print("\n✅ Исправления не требуются")
    
    return 0

if __name__ == "__main__":
    exit(main())
