#!/usr/bin/env python3
"""
Интерактивное обогащение relations в онтологии.

Скрипт загружает все концепты через ontology_toolkit и для каждого
показывает текущие relations, чтобы Cursor AI мог сгенерировать
осмысленные descriptions.

ИСПОЛЬЗОВАНИЕ в Agent Mode в Cursor:
    1. Запустить: python enrich_relations_interactive.py --prepare
    2. Скрипт создаст файл enrichment_data.json со всеми концептами
    3. Cursor AI обработает файл и добавит descriptions для relations
    4. Запустить: python enrich_relations_interactive.py --apply
    5. Скрипт применит обогащённые данные
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Добавляем путь к ontology_toolkit
sys.path.insert(0, str(Path(__file__).parent / "ontology_toolkit"))

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.schema import Relation, RelationType

def prepare_enrichment_data(ontology: Ontology) -> dict:
    """
    Подготавливает данные для обогащения.
    
    Возвращает dict с информацией о всех концептах и их relations.
    """
    data = {
        'concepts': [],
        'total': 0
    }
    
    concepts = [e for e in ontology.index.by_id.values() if e.id.startswith('C_')]
    data['total'] = len(concepts)
    
    for concept in concepts:
        concept_data = {
            'id': concept.id,
            'name': concept.name,
            'definition': concept.definition,
            'meta_meta': concept.meta_meta,
            'relations': []
        }
        
        for rel in concept.relations:
            target = ontology.index.by_id.get(rel.target)
            target_name = target.name if target else "???"
            target_meta = target.meta_meta if target else "???"
            
            relation_data = {
                'type': rel.type.value,
                'target_id': rel.target,
                'target_name': target_name,
                'target_meta': target_meta,
                'current_description': rel.description,
                'suggested_description': None  # Будет заполнено AI
            }
            
            concept_data['relations'].append(relation_data)
        
        data['concepts'].append(concept_data)
    
    return data

def apply_enrichment(ontology: Ontology, enrichment_file: Path):
    """
    Применяет обогащённые данные к концептам.
    """
    with open(enrichment_file, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)
    
    stats = {
        'processed': 0,
        'enriched_relations': 0,
        'errors': 0
    }
    
    for concept_data in enriched_data['concepts']:
        concept_id = concept_data['id']
        concept = ontology.index.by_id.get(concept_id)
        
        if not concept:
            print(f"✗ Концепт {concept_id} не найден")
            stats['errors'] += 1
            continue
        
        # Обновляем relations с новыми descriptions
        new_relations = []
        for rel_data in concept_data['relations']:
            description = rel_data.get('suggested_description') or rel_data.get('current_description')
            
            new_relations.append(Relation(
                type=RelationType(rel_data['type']),
                target=rel_data['target_id'],
                description=description
            ))
        
        concept.relations = new_relations
        concept.updated = datetime.now()
        
        # Сохраняем
        from ontology_toolkit.core.concept import save_entity_to_file
        
        # Находим файл
        concepts_dir = Path(".ontology") / "concepts"
        concept_file = None
        
        for file_path in concepts_dir.glob(f"{concept_id}_*.md"):
            concept_file = file_path
            break
        
        if concept_file:
            save_entity_to_file(concept, concept_file)
            enriched_count = len([r for r in new_relations if r.description])
            stats['enriched_relations'] += enriched_count
            stats['processed'] += 1
            print(f"✓ {concept_id} — {concept.name}: {enriched_count} relations enriched")
        else:
            print(f"✗ Файл для {concept_id} не найден")
            stats['errors'] += 1
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Обогащение relations в онтологии")
    parser.add_argument('--prepare', action='store_true', help="Подготовить данные для обогащения")
    parser.add_argument('--apply', action='store_true', help="Применить обогащённые данные")
    parser.add_argument('--output', default='enrichment_data.json', help="Файл для данных")
    
    args = parser.parse_args()
    
    # Загружаем онтологию
    ontology_path = Path(".ontology")
    if not ontology_path.exists():
        print("✗ Директория .ontology не найдена!")
        return 1
    
    print("Загрузка онтологии...")
    ontology = Ontology(ontology_path)
    ontology.load_all()
    print(f"✓ Загружено объектов: {len(ontology.index.by_id)}")
    
    if args.prepare:
        print("\n📝 Подготовка данных для обогащения...")
        data = prepare_enrichment_data(ontology)
        
        output_file = Path(args.output)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Данные сохранены в {output_file}")
        print(f"  Концептов: {data['total']}")
        print(f"  Relations для обогащения: {sum(len(c['relations']) for c in data['concepts'])}")
        print()
        print("Следующий шаг:")
        print("  1. Откройте enrichment_data.json")
        print("  2. Попросите Cursor AI заполнить 'suggested_description' для каждой relation")
        print("  3. Запустите: python enrich_relations_interactive.py --apply")
        
    elif args.apply:
        print("\n📝 Применение обогащённых данных...")
        enrichment_file = Path(args.output)
        
        if not enrichment_file.exists():
            print(f"✗ Файл {enrichment_file} не найден!")
            print("  Сначала запустите с --prepare")
            return 1
        
        stats = apply_enrichment(ontology, enrichment_file)
        
        print(f"\n{'='*60}")
        print(f"ИТОГО")
        print(f"{'='*60}")
        print(f"Обработано концептов: {stats['processed']}")
        print(f"Обогащено relations: {stats['enriched_relations']}")
        print(f"Ошибок: {stats['errors']}")
        print()
        print("Следующие шаги:")
        print("  1. ontology audit")
        print("  2. ontology export --format csv --output ontology_v2.4_enriched.csv")
        print("  3. ontology graph --output visuals/ontology_enriched.mmd")
        
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

