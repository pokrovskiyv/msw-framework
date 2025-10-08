#!/usr/bin/env python3
"""
Скрипт для экспорта страницы из Coda в Markdown формат.

Использование:
    python export_coda_page.py --api-key YOUR_API_KEY
    
    Или через переменную окружения:
    set CODA_API_KEY=YOUR_API_KEY
    python export_coda_page.py
"""

import argparse
import os
import sys
import time
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("⚠️  Модуль 'requests' не установлен.")
    print("Установите его командой: pip install requests")
    sys.exit(1)


# Константы
CODA_API_BASE = "https://coda.io/apis/v1"
DOC_ID = "TLUOWqMEYG"
PAGE_ID = "canvas-EeYMQYM-Km"
OUTPUT_DIR = "OtherMaterials"
MAX_WAIT_TIME = 300  # 5 минут
POLL_INTERVAL = 3  # проверять каждые 3 секунды

# Страницы для экспорта
PAGES_TO_EXPORT = [
    ("canvas-EeYMQYM-Km", "01_Краткое_описание.md"),
    # Промпты подсистем (самая ценная информация!)
    ("canvas-62TnMzLNLR", "Промпт_Методиста.md"),
    ("canvas-esKlGmECPU", "Промпт_Навигатора.md"),
    ("canvas-T-6C8aQTbX", "Промпт_Оценщика_качества.md"),
    ("canvas-Arii8C_CIr", "Промпт_Мотиватора.md"),
    # Полезные дополнительные страницы
    ("canvas-CtaZg5nPth", "Метамодель_Контекстной_подсистемы.md"),
    ("canvas-YDQ7uU-3Wv", "Сценарии_работы.md"),
]


def get_api_key():
    """Получить API ключ из аргументов командной строки или переменной окружения."""
    parser = argparse.ArgumentParser(
        description="Экспорт страницы из Coda в Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python export_coda_page.py --api-key YOUR_API_KEY
  
  С переменной окружения (Windows PowerShell):
  $env:CODA_API_KEY="YOUR_API_KEY"
  python export_coda_page.py
  
  С переменной окружения (Windows CMD):
  set CODA_API_KEY=YOUR_API_KEY
  python export_coda_page.py

Как получить API ключ:
  1. Перейдите на https://coda.io/account
  2. Найдите раздел "API Settings"
  3. Создайте новый API токен
  4. Скопируйте токен (он будет виден только один раз!)
        """
    )
    parser.add_argument(
        "--api-key",
        help="API ключ от Coda (или используйте переменную окружения CODA_API_KEY)"
    )
    
    args = parser.parse_args()
    
    # Проверяем аргумент командной строки
    if args.api_key:
        return args.api_key
    
    # Проверяем переменную окружения
    api_key = os.environ.get("CODA_API_KEY")
    if api_key:
        return api_key
    
    # Ключ не найден
    print("❌ API ключ не найден!")
    print()
    print("Укажите API ключ одним из способов:")
    print()
    print("1. Через аргумент командной строки:")
    print("   python export_coda_page.py --api-key YOUR_API_KEY")
    print()
    print("2. Через переменную окружения (Windows PowerShell):")
    print("   $env:CODA_API_KEY=\"YOUR_API_KEY\"")
    print("   python export_coda_page.py")
    print()
    print("3. Через переменную окружения (Windows CMD):")
    print("   set CODA_API_KEY=YOUR_API_KEY")
    print("   python export_coda_page.py")
    print()
    print("📖 Как получить API ключ:")
    print("   1. Перейдите на https://coda.io/account")
    print("   2. Найдите раздел 'API Settings'")
    print("   3. Создайте новый API токен")
    print("   4. Скопируйте токен (он будет виден только один раз!)")
    print()
    sys.exit(1)


def start_export(api_key, doc_id, page_id):
    """Начать экспорт страницы."""
    url = f"{CODA_API_BASE}/docs/{doc_id}/pages/{page_id}/export"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "outputFormat": "markdown"
    }
    
    print(f"🚀 Начинаю экспорт страницы {page_id}...")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        export_id = data.get("id")
        status_href = data.get("href")
        
        if not export_id or not status_href:
            raise ValueError(f"Неверный формат ответа от API: {data}")
        
        print(f"✅ Экспорт запущен! ID: {export_id}")
        return status_href
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise Exception("Ошибка авторизации: неверный API ключ")
        elif e.response.status_code == 403:
            raise Exception("Доступ запрещен: у вас нет прав на этот документ")
        elif e.response.status_code == 404:
            raise Exception(f"Страница не найдена: {page_id}")
        else:
            raise Exception(f"HTTP ошибка {e.response.status_code}: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка сети: {e}")


def poll_export_status(api_key, status_href):
    """Опрашивать статус экспорта до завершения."""
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    print("⏳ Ожидание завершения экспорта...")
    start_time = time.time()
    dots = 0
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > MAX_WAIT_TIME:
            raise Exception(f"Превышено время ожидания ({MAX_WAIT_TIME} секунд)")
        
        try:
            response = requests.get(status_href, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            
            if status == "complete":
                download_link = data.get("downloadLink")
                if not download_link:
                    raise Exception("Экспорт завершен, но ссылка на скачивание не найдена")
                print(f"\n✅ Экспорт завершен за {elapsed:.1f} секунд!")
                return download_link
            
            elif status == "failed":
                error = data.get("error", "Неизвестная ошибка")
                raise Exception(f"Экспорт завершился с ошибкой: {error}")
            
            elif status in ["inProgress", "queued"]:
                # Показываем прогресс
                dots = (dots + 1) % 4
                print(f"\r⏳ Экспорт в процессе{'.' * dots}{' ' * (3 - dots)} ({elapsed:.0f}с)", end="", flush=True)
                time.sleep(POLL_INTERVAL)
            
            else:
                print(f"\n⚠️  Неизвестный статус: {status}")
                time.sleep(POLL_INTERVAL)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при проверке статуса: {e}")


def download_file(api_key, download_link, output_path):
    """Скачать файл по ссылке и сохранить."""
    # Для S3 подписанного URL не нужен Authorization header
    print(f"📥 Скачивание файла...")
    
    try:
        response = requests.get(download_link)
        response.raise_for_status()
        
        # Создаем директорию если не существует
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем файл
        output_file.write_text(response.text, encoding="utf-8")
        
        file_size = len(response.text)
        print(f"✅ Файл сохранен: {output_path}")
        print(f"📊 Размер: {file_size:,} символов ({file_size / 1024:.1f} KB)")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при скачивании: {e}")
    except IOError as e:
        raise Exception(f"Ошибка при сохранении файла: {e}")


def main():
    """Основная функция."""
    print("=" * 80)
    print("🔧 Coda Pages Exporter")
    print("=" * 80)
    print()
    
    # Получаем API ключ
    api_key = get_api_key()
    
    print(f"📚 Экспорт {len(PAGES_TO_EXPORT)} страниц из документа {DOC_ID}")
    print()
    
    exported_files = []
    failed_exports = []
    
    for idx, (page_id, output_filename) in enumerate(PAGES_TO_EXPORT, 1):
        print(f"\n{'='*80}")
        print(f"📄 Страница {idx}/{len(PAGES_TO_EXPORT)}: {output_filename}")
        print(f"{'='*80}\n")
        
        output_path = f"{OUTPUT_DIR}/{output_filename}"
        
        try:
            # Шаг 1: Начинаем экспорт
            status_href = start_export(api_key, DOC_ID, page_id)
            
            # Шаг 2: Ожидаем завершения
            download_link = poll_export_status(api_key, status_href)
            
            # Шаг 3: Скачиваем файл
            download_file(api_key, download_link, output_path)
            
            exported_files.append(output_path)
            print(f"✅ Успешно экспортирована: {output_path}")
            
        except Exception as e:
            print(f"❌ Ошибка при экспорте: {e}")
            failed_exports.append((output_filename, str(e)))
        
        # Небольшая пауза между экспортами
        if idx < len(PAGES_TO_EXPORT):
            time.sleep(1)
    
    # Итоговая статистика
    print()
    print("=" * 80)
    print("📊 Итоги экспорта")
    print("=" * 80)
    print()
    print(f"✅ Успешно экспортировано: {len(exported_files)}/{len(PAGES_TO_EXPORT)}")
    
    if exported_files:
        print("\n📁 Экспортированные файлы:")
        for file_path in exported_files:
            print(f"   • {file_path}")
    
    if failed_exports:
        print(f"\n❌ Ошибки: {len(failed_exports)}")
        for filename, error in failed_exports:
            print(f"   • {filename}: {error}")
    
    print()
    print("=" * 80)
    if len(exported_files) == len(PAGES_TO_EXPORT):
        print("🎉 Все страницы успешно экспортированы!")
    elif exported_files:
        print("⚠️  Экспорт завершен с ошибками")
    else:
        print("❌ Не удалось экспортировать ни одной страницы")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

