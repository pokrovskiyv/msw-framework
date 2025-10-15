#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки и конвертации кодировки .md файлов в UTF-8 без BOM.

Использование:
    python scripts/check_encoding.py                    # Проверка и конвертация всех файлов
    python scripts/check_encoding.py --dry-run          # Только проверка без конвертации
    python scripts/check_encoding.py --backup-dir ./bak # Указать директорию для backup
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

try:
    import chardet
except ImportError:
    print("ОШИБКА: Необходимо установить модуль 'chardet'")
    print("Установите: pip install chardet")
    sys.exit(1)


class EncodingChecker:
    """Класс для проверки и конвертации кодировки файлов."""
    
    def __init__(self, backup_dir: str = "encoding_backups", dry_run: bool = False, root_dir: Path = None):
        self.backup_dir = Path(backup_dir)
        self.dry_run = dry_run
        self.root_dir = root_dir if root_dir else Path.cwd()
        self.report = {
            'checked': [],
            'converted': [],
            'errors': [],
            'already_utf8': []
        }
        
    def detect_encoding(self, file_path: Path) -> Tuple[str, float]:
        """
        Определяет кодировку файла.
        
        Returns:
            Tuple[str, float]: (encoding, confidence)
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    
    def is_utf8_bom(self, file_path: Path) -> bool:
        """Проверяет наличие BOM в UTF-8 файле."""
        with open(file_path, 'rb') as f:
            bom = f.read(3)
            return bom == b'\xef\xbb\xbf'
    
    def convert_to_utf8(self, file_path: Path, source_encoding: str) -> bool:
        """
        Конвертирует файл в UTF-8 без BOM.
        
        Args:
            file_path: Путь к файлу
            source_encoding: Исходная кодировка
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            # Читаем с исходной кодировкой
            with open(file_path, 'r', encoding=source_encoding, errors='ignore') as f:
                content = f.read()
            
            # Создаём backup
            if not self.dry_run:
                self._create_backup(file_path)
            
            # Записываем в UTF-8 без BOM
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            self.report['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False
    
    def remove_bom(self, file_path: Path) -> bool:
        """Удаляет BOM из UTF-8 файла."""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if not self.dry_run:
                self._create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            self.report['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False
    
    def _create_backup(self, file_path: Path):
        """Создаёт backup файла."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        # Создаём структуру директорий для backup
        try:
            relative_path = file_path.relative_to(self.root_dir)
        except ValueError:
            # Если файл вне root_dir, используем абсолютный путь
            relative_path = Path(file_path.name)
        
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Копируем файл
        shutil.copy2(file_path, backup_path)
    
    def check_file(self, file_path: Path) -> Dict:
        """
        Проверяет и при необходимости конвертирует файл.
        
        Returns:
            Dict с информацией о проверке
        """
        try:
            encoding, confidence = self.detect_encoding(file_path)
            
            result = {
                'file': str(file_path),
                'encoding': encoding,
                'confidence': confidence
            }
            
            self.report['checked'].append(result)
            
            # Проверяем, нужна ли конвертация
            if encoding and encoding.lower() == 'ascii':
                # ASCII - подмножество UTF-8, всё в порядке
                self.report['already_utf8'].append(result)
                return result
            
            elif encoding and 'utf-8' in encoding.lower():
                # Проверяем наличие BOM
                if self.is_utf8_bom(file_path):
                    print(f"  ⚠️  UTF-8 с BOM: {file_path}")
                    if self.remove_bom(file_path):
                        result['action'] = 'removed_bom'
                        self.report['converted'].append(result)
                    return result
                else:
                    # UTF-8 без BOM - идеально
                    self.report['already_utf8'].append(result)
                    return result
            
            else:
                # Нужна конвертация
                print(f"  🔄 Конвертирую из {encoding} в UTF-8: {file_path}")
                
                # Пробуем разные кодировки для Windows
                encodings_to_try = [encoding, 'cp1251', 'cp866', 'windows-1252', 'iso-8859-1']
                
                for enc in encodings_to_try:
                    if enc is None:
                        continue
                    try:
                        if self.convert_to_utf8(file_path, enc):
                            result['action'] = 'converted'
                            result['from_encoding'] = enc
                            self.report['converted'].append(result)
                            break
                    except:
                        continue
                
                return result
                
        except Exception as e:
            error = {
                'file': str(file_path),
                'error': str(e)
            }
            self.report['errors'].append(error)
            return error
    
    def scan_directory(self, root_dir: Path = Path('.')) -> List[Path]:
        """
        Сканирует директорию на наличие .md файлов.
        
        Args:
            root_dir: Корневая директория для сканирования
            
        Returns:
            List[Path]: Список найденных .md файлов
        """
        md_files = []
        
        # Директории для игнорирования
        ignore_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'encoding_backups', '.cursor', '.vscode', 'build', 'dist'
        }
        
        for path in root_dir.rglob('*.md'):
            # Пропускаем файлы в игнорируемых директориях
            if any(part in ignore_dirs for part in path.parts):
                continue
            md_files.append(path)
        
        return sorted(md_files)
    
    def generate_report(self) -> str:
        """Генерирует текстовый отчёт о проверке."""
        report_lines = [
            "=" * 80,
            "ОТЧЁТ О ПРОВЕРКЕ КОДИРОВКИ .md ФАЙЛОВ",
            "=" * 80,
            f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Режим: {'Только проверка (dry-run)' if self.dry_run else 'Проверка и конвертация'}",
            "",
            f"📊 СТАТИСТИКА:",
            f"  Всего проверено файлов: {len(self.report['checked'])}",
            f"  Уже в UTF-8: {len(self.report['already_utf8'])}",
            f"  Конвертировано: {len(self.report['converted'])}",
            f"  Ошибок: {len(self.report['errors'])}",
            ""
        ]
        
        if self.report['converted']:
            report_lines.append("✅ КОНВЕРТИРОВАННЫЕ ФАЙЛЫ:")
            for item in self.report['converted']:
                from_enc = item.get('from_encoding', 'unknown')
                action = item.get('action', 'converted')
                if action == 'removed_bom':
                    report_lines.append(f"  - {item['file']} (удалён BOM)")
                else:
                    report_lines.append(f"  - {item['file']} (из {from_enc})")
            report_lines.append("")
        
        if self.report['errors']:
            report_lines.append("❌ ОШИБКИ:")
            for item in self.report['errors']:
                report_lines.append(f"  - {item['file']}: {item['error']}")
            report_lines.append("")
        
        if not self.report['converted'] and not self.report['errors']:
            report_lines.append("✅ Все файлы уже в UTF-8 без BOM. Конвертация не требуется.")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: str = "encoding_report.txt"):
        """Сохраняет отчёт в файл."""
        report_content = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📄 Отчёт сохранён в: {filename}")


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description='Проверка и конвертация кодировки .md файлов в UTF-8 без BOM'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Только проверка без конвертации'
    )
    parser.add_argument(
        '--backup-dir',
        default='encoding_backups',
        help='Директория для backup файлов (по умолчанию: encoding_backups)'
    )
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Не сохранять отчёт в файл'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ПРОВЕРКА КОДИРОВКИ .md ФАЙЛОВ")
    print("=" * 80)
    
    if args.dry_run:
        print("⚠️  Режим: ТОЛЬКО ПРОВЕРКА (файлы не будут изменены)")
    else:
        print("🔧 Режим: ПРОВЕРКА И АВТОМАТИЧЕСКАЯ КОНВЕРТАЦИЯ")
        print(f"💾 Backup будут сохранены в: {args.backup_dir}/")
    
    print()
    
    root_dir = Path.cwd()
    checker = EncodingChecker(backup_dir=args.backup_dir, dry_run=args.dry_run, root_dir=root_dir)
    
    print("🔍 Сканирую директорию на наличие .md файлов...")
    md_files = checker.scan_directory(root_dir)
    
    print(f"📝 Найдено {len(md_files)} .md файлов")
    print()
    
    print("🔄 Проверяю файлы...")
    for md_file in md_files:
        checker.check_file(md_file)
    
    print()
    report_text = checker.generate_report()
    print(report_text)
    
    if not args.no_report:
        checker.save_report()
    
    # Возвращаем код ошибки если были ошибки
    return 1 if checker.report['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())

