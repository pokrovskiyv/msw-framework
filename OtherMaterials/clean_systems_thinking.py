#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки файла Systems_thinking.md от артефактов конвертации PDF
"""

import re
from pathlib import Path

def is_page_number(line):
    """Проверяет, является ли строка номером страницы"""
    stripped = line.strip()
    # Номер страницы - это строка с 1-4 цифрами
    if stripped.isdigit() and 1 <= len(stripped) <= 4:
        return True
    return False

def is_list_item(line):
    """Проверяет, является ли строка элементом списка"""
    stripped = line.lstrip()
    # Маркированные списки
    if stripped.startswith(('•', '-', '▪', '○', '*')):
        return True
    # Нумерованные списки
    if re.match(r'^\d+\.', stripped):
        return True
    # Вложенные списки с буквой o
    if stripped.startswith('o '):
        return True
    return False

def is_table_row(line):
    """Проверяет, является ли строка частью таблицы"""
    return '|' in line

def should_merge_with_next(line, next_line):
    """Определяет, нужно ли объединить текущую строку со следующей"""
    if not line or not next_line:
        return False
    
    line_stripped = line.strip()
    next_stripped = next_line.strip()
    
    # Не объединять пустые строки
    if not line_stripped or not next_stripped:
        return False
    
    # Не объединять таблицы
    if is_table_row(line) or is_table_row(next_line):
        return False
    
    # Не объединять элементы списка
    if is_list_item(line) or is_list_item(next_line):
        return False
    
    # Не объединять если строка содержит только цифру (номер)
    if line_stripped.isdigit() or next_stripped.isdigit():
        return False
    
    # Не объединять заголовки (строки с ### в начале)
    if line_stripped.startswith('#') or next_stripped.startswith('#'):
        return False
    
    # Не объединять сноски (строки с числом в начале)
    if re.match(r'^\d+\s+http', next_stripped):
        return False
    
    # Не объединять если текущая строка очень короткая (меньше 20 символов) и заканчивается точкой
    if len(line_stripped) < 20 and line_stripped[-1] == '.':
        return False
    
    # Не объединять если следующая строка начинается с заглавной буквы и текущая заканчивается на точку
    if line_stripped[-1] in '.!?' and next_stripped[0].isupper():
        # Исключение: если это не конец предложения (например, "и т.д.")
        if not line_stripped.endswith(('т.д.', 'т.п.', 'и т.д.', 'и т.п.', 'и др.', 'г.', 'в.', 'т.е.')):
            return False
    
    # Не объединять если текущая строка заканчивается двоеточием
    if line_stripped.endswith(':'):
        return False
    
    # Объединять, если текущая строка заканчивается на запятую или тире
    if line_stripped[-1] in ',—–-':
        return True
    
    # Объединять, если текущая строка не заканчивается на знак препинания и следующая начинается с маленькой буквы
    if line_stripped[-1] not in '.!?:;,—–-' and next_stripped[0].islower():
        return True
    
    return False

def clean_markdown_file(input_file, output_file):
    """Очищает markdown файл от артефактов конвертации"""
    print(f"Читаю файл {input_file}...")
    
    # Попробуем разные кодировки
    encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'latin-1']
    lines = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            print(f"Успешно прочитано с кодировкой {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if lines is None:
        raise ValueError("Не удалось прочитать файл ни с одной из поддерживаемых кодировок")
    
    print(f"Прочитано {len(lines)} строк")
    
    # Шаг 1: Удаление номеров страниц
    print("Удаляю номера страниц...")
    cleaned_lines = []
    removed_pages = 0
    
    for line in lines:
        if is_page_number(line):
            removed_pages += 1
            continue
        cleaned_lines.append(line)
    
    print(f"Удалено {removed_pages} номеров страниц")
    
    # Шаг 2: Объединение разорванных абзацев
    print("Объединяю разорванные абзацы...")
    merged_lines = []
    i = 0
    merged_count = 0
    
    while i < len(cleaned_lines):
        current_line = cleaned_lines[i]
        
        # Если это пустая строка, просто добавляем
        if not current_line.strip():
            merged_lines.append(current_line)
            i += 1
            continue
        
        # Накапливаем строки для объединения
        accumulated = current_line.rstrip()
        i += 1
        
        while i < len(cleaned_lines):
            next_line = cleaned_lines[i]
            
            if should_merge_with_next(accumulated, next_line):
                # Добавляем пробел между строками
                accumulated += ' ' + next_line.lstrip()
                merged_count += 1
                i += 1
            else:
                break
        
        merged_lines.append(accumulated + '\n')
    
    print(f"Объединено {merged_count} разрывов абзацев")
    
    # Записываем результат
    print(f"Записываю результат в {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(merged_lines)
    
    print(f"Готово! Результат: {len(merged_lines)} строк")
    print(f"Сокращение: {len(lines)} -> {len(merged_lines)} ({len(lines) - len(merged_lines)} строк удалено)")

if __name__ == '__main__':
    # Определяем директорию скрипта
    script_dir = Path(__file__).parent
    input_file = script_dir / 'Systems_thinking.md.backup'
    output_file = script_dir / 'Systems_thinking.md'
    
    clean_markdown_file(input_file, output_file)
    print("\n✓ Обработка завершена успешно!")

