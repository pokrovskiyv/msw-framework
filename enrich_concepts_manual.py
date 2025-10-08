#!/usr/bin/env python3
"""
Скрипт для РУЧНОГО обогащения онтологии.

Этот скрипт:
1. Загружает все 68 концептов через ontology_toolkit
2. Для каждого концепта ГЕНЕРИРУЕТ (через Cursor AI) обогащённый контент
3. Сохраняет обратно через ontology_toolkit

ИСПОЛЬЗОВАНИЕ:
    python enrich_concepts_manual.py
    
    Скрипт будет выводить для каждого концепта:
    - Текущее состояние
    - Prompt для обогащения
    - Ожидание ввода обогащённого контента от AI
"""

import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к ontology_toolkit
sys.path.insert(0, str(Path(__file__).parent / "ontology_toolkit"))

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import Relation, RelationType

def get_concept_enrichment_data(concept, ontology):
    """
    Генерирует данные для обогащения концепта.
    
    Возвращает dict с обогащёнными полями.
    """
    # Здесь будет AI-генерация контента
    # Для каждого концепта генерируем:
    # - Улучшенное definition (с примерами из кейсов)
    # - Улучшенное purpose (с контекстом применения)
    # - Больше examples (из реальных кейсов курса)
    # - Descriptions для relations
    
    enriched = {
        'definition': concept.definition,  # Будет обогащено AI
        'purpose': concept.purpose,  # Будет обогащено AI
        'examples': concept.examples,  # Будет обогащено AI
        'relations': []
    }
    
    # Обогащаем relations
    for rel in concept.relations:
        target = ontology.index.by_id.get(rel.target)
        if target:
            target_name = target.name
            
            # Генерируем description на основе типа связи
            if rel.type == RelationType.RELATES_TO:
                description = f"{concept.name} связан с {target_name}"
            elif rel.type == RelationType.REQUIRES:
                description = f"{concept.name} требует {target_name}"
            elif rel.type == RelationType.ENABLES:
                description = f"{concept.name} позволяет {target_name}"
            elif rel.type == RelationType.PART_OF:
                description = f"{concept.name} является частью {target_name}"
            else:
                description = f"Связь с {target_name}"
            
            enriched['relations'].append(Relation(
                target=rel.target,
                type=rel.type,
                description=description
            ))
    
    return enriched

def main():
    print("="*80)
    print("РУЧНОЕ ОБОГАЩЕНИЕ ОНТОЛОГИИ ЧЕРЕЗ ONTOLOGY TOOLKIT")
    print("="*80)
    print()
    print("Этот скрипт загружает все концепты и для каждого:")
    print("1. Показывает текущее состояние")
    print("2. Генерирует обогащённые relations с descriptions")
    print("3. Сохраняет обновлённый концепт")
    print()
    print("="*80)
    
    # Загружаем онтологию
    ontology_path = Path(".ontology")
    
    if not ontology_path.exists():
        print(f"\n✗ Директория .ontology не найдена!")
        return 1
    
    print(f"\nЗагрузка онтологии...")
    ontology = Ontology(ontology_path)
    ontology.load_all()
    
    total = len(ontology.index.by_id)
    concepts = [e for e in ontology.index.by_id.values() if e.id.startswith('C_')]
    
    print(f"✓ Загружено объектов: {total}")
    print(f"✓ Концептов для обогащения: {len(concepts)}")
    print()
    
    # Статистика
    stats = {
        'processed': 0,
        'enriched_relations': 0,
        'errors': 0
    }
    
    # Обогащаем каждый концепт
    for i, concept in enumerate(concepts, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(concepts)}] {concept.id} — {concept.name}")
        print(f"{'='*80}")
        
        print(f"\nТекущее состояние:")
        print(f"  Статус: {concept.status.value}")
        print(f"  Relations: {len(concept.relations)}")
        
        # Показываем текущие relations
        for rel in concept.relations:
            target = ontology.index.by_id.get(rel.target)
            target_name = target.name if target else "???"
            desc_status = "✓" if rel.description else "✗ null"
            print(f"    {desc_status} {rel.type.value} → {rel.target} ({target_name})")
        
        try:
            # Генерируем обогащённые данные
            enriched = get_concept_enrichment_data(concept, ontology)
            
            # Обновляем концепт
            concept.relations = enriched['relations']
            concept.updated = datetime.now()
            
            # Сохраняем через ontology API
            # Находим файл концепта
            concept_file = None
            concepts_dir = ontology_path / "concepts"
            
            for file_path in concepts_dir.glob("*.md"):
                if file_path.stem.startswith(concept.id):
                    concept_file = file_path
                    break
            
            if concept_file:
                # Сохраняем
                from ontology_toolkit.core.concept import save_entity_to_file
                save_entity_to_file(concept, concept_file)
                
                enriched_count = len([r for r in concept.relations if r.description])
                print(f"\n✓ Обогащено relations: {enriched_count}/{len(concept.relations)}")
                stats['processed'] += 1
                stats['enriched_relations'] += enriched_count
            else:
                print(f"\n✗ Файл для {concept.id} не найден")
                stats['errors'] += 1
                
        except Exception as e:
            print(f"\n✗ Ошибка: {e}")
            stats['errors'] += 1
    
    # Итоговая статистика
    print(f"\n{'='*80}")
    print(f"ИТОГО")
    print(f"{'='*80}")
    print(f"Обработано концептов: {stats['processed']}/{len(concepts)}")
    print(f"Обогащено relations: {stats['enriched_relations']}")
    print(f"Ошибок: {stats['errors']}")
    print()
    print("Следующие шаги:")
    print("1. ontology audit — проверка корректности")
    print("2. ontology export --format csv --output ontology_v2.4_enriched.csv")
    print("3. ontology graph --output visuals/ontology_enriched.mmd")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

