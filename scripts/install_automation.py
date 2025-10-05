#!/usr/bin/env python3
"""
Скрипт установки автоматизации для проекта «Системная карьера».

Устанавливает:
- Git pre-commit hook для проверки документации
- GitHub Actions workflow (опционально)
- Проверяет наличие CLI инструмента

Использование:
  python scripts/install_automation.py
  python scripts/install_automation.py --github-actions
  python scripts/install_automation.py --help
"""

import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

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

def check_git_repo(project_root: Path) -> bool:
    """Проверить, что мы в git репозитории."""
    git_dir = project_root / ".git"
    return git_dir.exists() and git_dir.is_dir()

def install_pre_commit_hook(project_root: Path) -> Tuple[bool, str]:
    """
    Установить pre-commit hook.
    
    Returns:
        (success, message)
    """
    hooks_dir = project_root / ".git" / "hooks"
    hook_template = project_root / "scripts" / "pre-commit.sh"
    hook_target = hooks_dir / "pre-commit"
    
    if not hooks_dir.exists():
        return False, "❌ Папка .git/hooks не найдена"
    
    if not hook_template.exists():
        return False, "❌ Шаблон pre-commit.sh не найден в scripts/"
    
    try:
        # Копируем шаблон
        shutil.copy2(hook_template, hook_target)
        
        # Делаем исполняемым
        os.chmod(hook_target, 0o755)
        
        return True, "✅ Pre-commit hook установлен"
    
    except Exception as e:
        return False, f"❌ Ошибка установки hook: {e}"

def check_cli_installation(project_root: Path) -> Tuple[bool, str]:
    """
    Проверить установку CLI инструмента.
    
    Returns:
        (is_installed, message)
    """
    try:
        result = subprocess.run(
            ['course', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return True, "✅ CLI инструмент установлен и работает"
        else:
            return False, "⚠️  CLI инструмент не установлен или не работает"
    
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "⚠️  CLI инструмент не установлен"

def install_cli(project_root: Path) -> Tuple[bool, str]:
    """
    Попытаться установить CLI инструмент.
    
    Returns:
        (success, message)
    """
    cli_dir = project_root / "course_cli"
    
    if not cli_dir.exists():
        return False, "❌ Папка course_cli/ не найдена"
    
    try:
        # Устанавливаем CLI
        result = subprocess.run(
            ['pip', 'install', '-e', '.'],
            cwd=cli_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return True, "✅ CLI инструмент установлен"
        else:
            return False, f"❌ Ошибка установки CLI: {result.stderr}"
    
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, f"❌ Ошибка установки CLI: {e}"

def create_github_actions(project_root: Path) -> Tuple[bool, str]:
    """
    Создать GitHub Actions workflow.
    
    Returns:
        (success, message)
    """
    workflows_dir = project_root / ".github" / "workflows"
    workflow_file = workflows_dir / "docs-check.yml"
    
    # Создаём папку .github/workflows если её нет
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Содержимое workflow
    workflow_content = """name: Documentation Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Check documentation sync
      run: |
        echo "🔍 Проверка синхронности документации..."
        python scripts/check_docs_sync.py --strict
        
    - name: Comment on PR if issues found
      if: failure() && github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '⚠️ **Проблемы с документацией обнаружены!**\\n\\n' +
                  'Пожалуйста, обновите документацию перед merge:\\n' +
                  '```bash\\n' +
                  'python scripts/update_docs.py\\n' +
                  '```\\n\\n' +
                  'Подробности см. в [логах CI]({{ github.server_url }}/{{ github.repository }}/actions/runs/{{ github.run_id }}).'
          })
"""
    
    try:
        workflow_file.write_text(workflow_content, encoding="utf-8")
        return True, "✅ GitHub Actions workflow создан"
    
    except Exception as e:
        return False, f"❌ Ошибка создания workflow: {e}"

def test_scripts(project_root: Path) -> Tuple[bool, str]:
    """
    Протестировать работу скриптов.
    
    Returns:
        (success, message)
    """
    try:
        # Тестируем check_docs_sync.py
        result = subprocess.run(
            [sys.executable, "scripts/check_docs_sync.py", "--help"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, "❌ Скрипт check_docs_sync.py не работает"
        
        # Тестируем update_docs.py
        result = subprocess.run(
            [sys.executable, "scripts/update_docs.py", "--help"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, "❌ Скрипт update_docs.py не работает"
        
        return True, "✅ Все скрипты работают корректно"
    
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, f"❌ Ошибка тестирования скриптов: {e}"

def print_instructions():
    """Вывести инструкции по использованию."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}📋 Инструкции по использованию{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    print(f"\n{Colors.OKCYAN}🔧 Основные команды:{Colors.ENDC}")
    print(f"  • {Colors.OKGREEN}python scripts/check_docs_sync.py{Colors.ENDC} — проверить документацию")
    print(f"  • {Colors.OKGREEN}python scripts/update_docs.py{Colors.ENDC} — обновить документацию")
    print(f"  • {Colors.OKGREEN}course docs check{Colors.ENDC} — проверить через CLI (если установлен)")
    print(f"  • {Colors.OKGREEN}course docs update{Colors.ENDC} — обновить через CLI (если установлен)")
    
    print(f"\n{Colors.OKCYAN}🚀 Workflow:{Colors.ENDC}")
    print(f"  1. Делаете изменения в weeks/, templates/, CLI и т.д.")
    print(f"  2. При {Colors.WARNING}git commit{Colors.ENDC} автоматически проверяется документация")
    print(f"  3. Если есть проблемы — обновляете документацию")
    print(f"  4. При push на GitHub — дополнительная проверка в CI/CD")
    
    print(f"\n{Colors.OKCYAN}⚙️  Настройки:{Colors.ENDC}")
    print(f"  • {Colors.WARNING}--strict{Colors.ENDC} — строгий режим проверки")
    print(f"  • {Colors.WARNING}--days N{Colors.ENDC} — анализировать изменения за N дней")
    print(f"  • {Colors.WARNING}--no-interactive{Colors.ENDC} — неинтерактивный режим")
    
    print(f"\n{Colors.OKCYAN}🆘 Troubleshooting:{Colors.ENDC}")
    print(f"  • Если hook не работает: {Colors.WARNING}chmod +x .git/hooks/pre-commit{Colors.ENDC}")
    print(f"  • Если CLI не работает: {Colors.WARNING}cd course_cli && pip install -e .{Colors.ENDC}")
    print(f"  • Если скрипты не работают: {Colors.WARNING}python scripts/check_docs_sync.py --help{Colors.ENDC}")

def main():
    """Основная функция установки."""
    parser = argparse.ArgumentParser(
        description="Установка автоматизации для проекта «Системная карьера»",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/install_automation.py
  python scripts/install_automation.py --github-actions
  python scripts/install_automation.py --install-cli
        """
    )
    
    parser.add_argument(
        '--github-actions',
        action='store_true',
        help='Создать GitHub Actions workflow'
    )
    
    parser.add_argument(
        '--install-cli',
        action='store_true',
        help='Попытаться установить CLI инструмент'
    )
    
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Только протестировать скрипты, не устанавливать'
    )
    
    args = parser.parse_args()
    
    project_root = get_project_root()
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 Установка автоматизации документации{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    # Проверяем, что мы в git репозитории
    if not check_git_repo(project_root):
        print(f"{Colors.FAIL}❌ Не найден git репозиторий в {project_root}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Запустите этот скрипт из корня git репозитория{Colors.ENDC}")
        return 1
    
    print(f"{Colors.OKGREEN}✅ Git репозиторий найден{Colors.ENDC}")
    
    # Тестируем скрипты
    print(f"\n{Colors.OKCYAN}🧪 Тестирование скриптов...{Colors.ENDC}")
    success, message = test_scripts(project_root)
    print(f"  {message}")
    
    if not success:
        print(f"{Colors.FAIL}❌ Не удалось протестировать скрипты{Colors.ENDC}")
        return 1
    
    if args.test_only:
        print(f"\n{Colors.OKGREEN}✅ Тестирование завершено успешно{Colors.ENDC}")
        return 0
    
    # Устанавливаем pre-commit hook
    print(f"\n{Colors.OKCYAN}🔧 Установка pre-commit hook...{Colors.ENDC}")
    success, message = install_pre_commit_hook(project_root)
    print(f"  {message}")
    
    if not success:
        print(f"{Colors.WARNING}⚠️  Не удалось установить pre-commit hook{Colors.ENDC}")
    
    # Проверяем/устанавливаем CLI
    print(f"\n{Colors.OKCYAN}🛠️  Проверка CLI инструмента...{Colors.ENDC}")
    cli_installed, cli_message = check_cli_installation(project_root)
    print(f"  {cli_message}")
    
    if not cli_installed and args.install_cli:
        print(f"\n{Colors.OKCYAN}📦 Установка CLI инструмента...{Colors.ENDC}")
        success, message = install_cli(project_root)
        print(f"  {message}")
        
        if success:
            # Проверяем ещё раз
            cli_installed, cli_message = check_cli_installation(project_root)
            print(f"  {cli_message}")
    
    # Создаём GitHub Actions (если запрошено)
    if args.github_actions:
        print(f"\n{Colors.OKCYAN}🔄 Создание GitHub Actions workflow...{Colors.ENDC}")
        success, message = create_github_actions(project_root)
        print(f"  {message}")
        
        if not success:
            print(f"{Colors.WARNING}⚠️  Не удалось создать GitHub Actions workflow{Colors.ENDC}")
    
    # Выводим итоги
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}✅ Установка завершена!{Colors.ENDC}")
    
    if cli_installed:
        print(f"\n{Colors.OKCYAN}🎯 Теперь доступны команды:{Colors.ENDC}")
        print(f"  • {Colors.OKGREEN}course docs check{Colors.ENDC}")
        print(f"  • {Colors.OKGREEN}course docs update{Colors.ENDC}")
    
    print_instructions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
