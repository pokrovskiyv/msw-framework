#!/usr/bin/env python3
"""
Скрипт для обогащения онтологии через прямое использование ontology_toolkit
без необходимости в API ключах (используется встроенный LLM доступ).
"""

import sys
from pathlib import Path

# Добавляем путь к ontology_toolkit
sys.path.insert(0, str(Path(__file__).parent / "ontology_toolkit"))

from ontology_toolkit.core.ontology import Ontology
from ontology_toolkit.core.concept import ConceptFile

def enrich_concept(concept_file: ConceptFile, ontology: Ontology) -> dict:
    """
    Обогащает один концепт, добавляя описания для relations.
    
    Возвращает обновлённые данные концепта.
    """
    concept = concept_file.concept
    
    print(f"\n{'='*60}")
    print(f"Обогащение: {concept.id} - {concept.name}")
    print(f"{'='*60}")
    
    # Обновляем relations, добавляя descriptions
    enriched_relations = []
    
    for rel in concept.relations:
        target_id = rel.target
        rel_type = rel.type
        
        # Получаем целевой концепт
        try:
            target_file = ontology.get_by_id(target_id)
            if target_file:
                target_name = target_file.concept.name
                
                # Генерируем description для связи на основе типа и концептов
                if rel.description:
                    description = rel.description
                else:
                    # Генерируем автоматически
                    if rel_type == "relates_to":
                        description = f"{concept.name} связан с {target_name}"
                    elif rel_type == "requires":
                        description = f"{concept.name} требует {target_name} для реализации"
                    elif rel_type == "enables":
                        description = f"{concept.name} позволяет использовать {target_name}"
                    elif rel_type == "part_of":
                        description = f"{concept.name} является частью {target_name}"
                    else:
                        description = f"{concept.name} → {target_name}"
                
                enriched_relations.append({
                    'target': target_id,
                    'type': rel_type,
                    'description': description
                })
                
                print(f"  ✓ {rel_type}: {target_id} ({target_name})")
                print(f"    → {description}")
            else:
                print(f"  ⚠ Целевой концепт {target_id} не найден")
                enriched_relations.append({
                    'target': target_id,
                    'type': rel_type,
                    'description': rel.description
                })
        except Exception as e:
            print(f"  ✗ Ошибка обработки relation {target_id}: {e}")
            enriched_relations.append({
                'target': target_id,
                'type': rel_type,
                'description': rel.description
            })
    
    return {
        'relations': enriched_relations
    }

def main():
    print("="*60)
    print("ОБОГАЩЕНИЕ ОНТОЛОГИИ СИСТЕМНОЙ КАРЬЕРЫ")
    print("="*60)
    
    # Загружаем онтологию
    ontology_path = Path(".ontology")
    
    if not ontology_path.exists():
        print(f"\n✗ Директория .ontology не найдена!")
        print(f"  Выполните: ontology init")
        return 1
    
    print(f"\nЗагрузка онтологии из {ontology_path}...")
    ontology = Ontology(ontology_path)
    ontology.load_all()
    
    total = len(ontology.concepts)
    print(f"✓ Загружено концептов: {total}")
    
    # Обогащаем каждый концепт
    enriched_count = 0
    errors = []
    
    for concept_file in ontology.concepts.values():
        try:
            enriched_data = enrich_concept(concept_file, ontology)
            
            # Обновляем relations в concept
            if enriched_data['relations']:
                concept_file.concept.relations = []
                for rel_data in enriched_data['relations']:
                    from ontology_toolkit.core.schema import Relation
                    relation = Relation(
                        target=rel_data['target'],
                        type=rel_data['type'],
                        description=rel_data['description']
                    )
                    concept_file.concept.relations.append(relation)
                
                # Сохраняем обновлённый файл
                concept_file.save()
                enriched_count += 1
                print(f"  ✓ Сохранено с {len(enriched_data['relations'])} relations")
                
        except Exception as e:
            error_msg = f"{concept_file.concept.id} - {concept_file.concept.name}: {e}"
            errors.append(error_msg)
            print(f"  ✗ Ошибка: {e}")
    
    print(f"\n{'='*60}")
    print(f"ИТОГО")
    print(f"{'='*60}")
    print(f"Обработано: {enriched_count} из {total}")
    
    if errors:
        print(f"\n⚠ Ошибок: {len(errors)}")
        for error in errors[:5]:  # Показываем первые 5
            print(f"  - {error}")
    else:
        print(f"\n✓ Все концепты обогащены успешно!")
    
    print(f"\nСледующие шаги:")
    print(f"1. ontology audit — проверить корректность")
    print(f"2. ontology export --format csv — экспорт обновлённых данных")
    print(f"3. ontology graph --output visuals/ontology_enriched.mmd — граф")
    
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())

