#!/bin/bash
# Pre-commit hook для автоматической проверки документации
# Проект: Системная карьера

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Проверка документации перед коммитом...${NC}"

# Определяем корень проекта (переходим из .git/hooks в корень)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Проверяем, что скрипт существует
if [ ! -f "$SCRIPTS_DIR/check_docs_sync.py" ]; then
    echo -e "${RED}❌ Скрипт check_docs_sync.py не найден в $SCRIPTS_DIR${NC}"
    exit 1
fi

# Запускаем проверку документации
cd "$PROJECT_ROOT"
python "$SCRIPTS_DIR/check_docs_sync.py" --strict

# Получаем exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Документация синхронизирована. Коммит разрешён.${NC}"
    exit 0
elif [ $EXIT_CODE -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Обнаружены предупреждения в документации.${NC}"
    echo -e "${BLUE}💡 Рекомендуется обновить документацию:${NC}"
    echo -e "${BLUE}   python scripts/update_docs.py${NC}"
    echo ""
    read -p "Продолжить коммит несмотря на предупреждения? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⏭️  Коммит продолжен с предупреждениями.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⏸️  Коммит отменён. Обновите документацию и попробуйте снова.${NC}"
        exit 1
    fi
elif [ $EXIT_CODE -eq 2 ]; then
    echo -e "${RED}❌ Обнаружены критические проблемы в документации!${NC}"
    echo -e "${BLUE}💡 Требуется немедленное обновление документации:${NC}"
    echo -e "${BLUE}   python scripts/update_docs.py${NC}"
    echo ""
    read -p "Продолжить коммит несмотря на критические проблемы? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}⚠️  Коммит продолжен с критическими проблемами в документации!${NC}"
        exit 0
    else
        echo -e "${RED}🛑 Коммит отменён. Исправьте критические проблемы и попробуйте снова.${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Ошибка при проверке документации (exit code: $EXIT_CODE)${NC}"
    echo -e "${BLUE}💡 Попробуйте запустить проверку вручную:${NC}"
    echo -e "${BLUE}   python scripts/check_docs_sync.py${NC}"
    echo ""
    read -p "Продолжить коммит несмотря на ошибку? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⚠️  Коммит продолжен с ошибкой в проверке документации.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⏸️  Коммит отменён. Исправьте ошибку и попробуйте снова.${NC}"
        exit 1
    fi
fi
