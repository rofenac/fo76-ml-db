#!/usr/bin/env python3
"""
Import mutations from Mutations.csv into MySQL database

Usage:
    python import_mutations.py
"""

import csv
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.db_utils import get_db

# File paths
MUTATIONS_CSV = 'data/input/mutations.csv'


def parse_effects(effect_text):
    """Parse effect text into individual effect descriptions."""
    if not effect_text or effect_text.strip() == '':
        return []

    # Split by semicolons, commas, or newlines
    effects = []
    for separator in [';', ',', '\n']:
        if separator in effect_text:
            effects = [e.strip() for e in effect_text.split(separator) if e.strip()]
            break

    # If no separators found, treat the whole text as a single effect
    if not effects:
        effects = [effect_text.strip()]

    return effects


def import_mutations():
    """Import mutations from CSV"""
    db = get_db()

    # Read mutations CSV
    with open(MUTATIONS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mutations = list(reader)

    print(f"\nImporting {len(mutations)} mutations...")

    insert_sql = """
        INSERT INTO mutations (name, positive_effects, negative_effects, form_id, exclusive_with, source_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            positive_effects = VALUES(positive_effects),
            negative_effects = VALUES(negative_effects),
            form_id = VALUES(form_id),
            exclusive_with = VALUES(exclusive_with),
            source_url = VALUES(source_url)
    """

    imported_count = 0
    for mutation in mutations:
        try:
            db.execute_query(insert_sql, (
                mutation['name'],
                mutation['positive_effects'],
                mutation['negative_effects'],
                mutation['form_id'] or None,
                mutation['exclusive_with'] or None,
                mutation['source_url']
            ))
            imported_count += 1
        except Exception as e:
            print(f"ERROR importing {mutation['name']}: {e}")

    print(f"✓ Successfully imported {imported_count}/{len(mutations)} mutations")
    return imported_count


def populate_mutation_effects():
    """Populate mutation_effects table from mutations table TEXT fields."""
    db = get_db()

    print(f"\nPopulating mutation_effects table...")

    # Get all mutations
    mutations = db.execute_query(
        "SELECT id, name, positive_effects, negative_effects FROM mutations"
    )

    if not mutations:
        print("No mutations found in database")
        return 0

    # Clear existing mutation_effects
    db.execute_query("DELETE FROM mutation_effects")
    print(f"Cleared existing mutation_effects records")

    total_effects = 0
    for mutation in mutations:
        mutation_id = mutation['id']
        mutation_name = mutation['name']

        # Parse and insert positive effects
        positive = parse_effects(mutation['positive_effects'])
        for effect_desc in positive:
            try:
                db.execute_query(
                    "INSERT INTO mutation_effects (mutation_id, effect_type, description) VALUES (%s, %s, %s)",
                    (mutation_id, 'positive', effect_desc)
                )
                total_effects += 1
            except Exception as e:
                print(f"ERROR inserting positive effect for {mutation_name}: {e}")

        # Parse and insert negative effects
        negative = parse_effects(mutation['negative_effects'])
        for effect_desc in negative:
            try:
                db.execute_query(
                    "INSERT INTO mutation_effects (mutation_id, effect_type, description) VALUES (%s, %s, %s)",
                    (mutation_id, 'negative', effect_desc)
                )
                total_effects += 1
            except Exception as e:
                print(f"ERROR inserting negative effect for {mutation_name}: {e}")

    print(f"✓ Successfully populated {total_effects} mutation effects")
    return total_effects


def populate_foreign_keys():
    """
    Populate FK columns in mutations table by resolving VARCHAR names to IDs.
    This ensures proper 3NF compliance while maintaining backward-compatible VARCHAR fields.
    """
    db = get_db()

    print(f"\nPopulating foreign key relationships...")

    # Get all mutations
    mutations = db.execute_query("SELECT id, name, exclusive_with, suppression_perk, enhancement_perk FROM mutations")

    if not mutations:
        print("No mutations found in database")
        return 0

    updated_count = 0

    for mutation in mutations:
        mutation_id = mutation['id']
        mutation_name = mutation['name']
        updates_needed = False
        update_fields = []
        update_values = []

        # Resolve exclusive_with name to ID
        if mutation['exclusive_with']:
            exclusive = db.execute_query(
                "SELECT id FROM mutations WHERE name = %s",
                (mutation['exclusive_with'],)
            )
            if exclusive:
                update_fields.append("exclusive_with_id = %s")
                update_values.append(exclusive[0]['id'])
                updates_needed = True
            else:
                print(f"  ⚠ Warning: Could not find mutation '{mutation['exclusive_with']}' for {mutation_name}")

        # Resolve suppression_perk name to ID
        if mutation['suppression_perk']:
            suppression = db.execute_query(
                "SELECT id FROM perks WHERE name = %s",
                (mutation['suppression_perk'],)
            )
            if suppression:
                update_fields.append("suppression_perk_id = %s")
                update_values.append(suppression[0]['id'])
                updates_needed = True
            else:
                print(f"  ⚠ Warning: Could not find perk '{mutation['suppression_perk']}' for {mutation_name}")

        # Resolve enhancement_perk name to ID
        if mutation['enhancement_perk']:
            enhancement = db.execute_query(
                "SELECT id FROM perks WHERE name = %s",
                (mutation['enhancement_perk'],)
            )
            if enhancement:
                update_fields.append("enhancement_perk_id = %s")
                update_values.append(enhancement[0]['id'])
                updates_needed = True
            else:
                print(f"  ⚠ Warning: Could not find perk '{mutation['enhancement_perk']}' for {mutation_name}")

        # Execute update if any FKs need to be set
        if updates_needed:
            try:
                update_sql = f"UPDATE mutations SET {', '.join(update_fields)} WHERE id = %s"
                update_values.append(mutation_id)
                db.execute_query(update_sql, tuple(update_values))
                updated_count += 1
            except Exception as e:
                print(f"  ❌ ERROR updating FKs for {mutation_name}: {e}")

    print(f"✓ Successfully updated FK relationships for {updated_count} mutations")
    return updated_count


def verify_import():
    """Verify mutations were imported correctly"""
    db = get_db()

    result = db.execute_query("SELECT COUNT(*) as count FROM mutations")
    total_count = result[0]['count'] if result else 0

    result = db.execute_query("SELECT COUNT(*) as count FROM mutations WHERE exclusive_with != ''")
    exclusive_count = result[0]['count'] if result else 0

    exclusive_mutations = db.execute_query("SELECT name, exclusive_with FROM mutations WHERE exclusive_with != ''")

    result = db.execute_query("SELECT COUNT(*) as count FROM mutation_effects")
    effects_count = result[0]['count'] if result else 0

    result = db.execute_query("SELECT COUNT(*) as count FROM mutation_effects WHERE effect_type = 'positive'")
    positive_count = result[0]['count'] if result else 0

    result = db.execute_query("SELECT COUNT(*) as count FROM mutation_effects WHERE effect_type = 'negative'")
    negative_count = result[0]['count'] if result else 0

    # Check FK population
    result = db.execute_query("SELECT COUNT(*) as count FROM mutations WHERE exclusive_with IS NOT NULL AND exclusive_with_id IS NOT NULL")
    fk_exclusive_count = result[0]['count'] if result else 0

    result = db.execute_query("SELECT COUNT(*) as count FROM mutations WHERE suppression_perk IS NOT NULL AND suppression_perk_id IS NOT NULL")
    fk_suppression_count = result[0]['count'] if result else 0

    result = db.execute_query("SELECT COUNT(*) as count FROM mutations WHERE enhancement_perk IS NOT NULL AND enhancement_perk_id IS NOT NULL")
    fk_enhancement_count = result[0]['count'] if result else 0

    print(f"\nVerification:")
    print(f"  Total mutations: {total_count}")
    print(f"  Exclusive mutations: {exclusive_count}")
    if exclusive_mutations:
        print(f"  Exclusivity pairs:")
        for m in exclusive_mutations:
            print(f"    - {m['name']} <-> {m['exclusive_with']}")
    print(f"\n  Mutation effects: {effects_count} total ({positive_count} positive, {negative_count} negative)")
    print(f"\n  Foreign key relationships:")
    print(f"    - Exclusive pairs: {fk_exclusive_count} have FK populated")
    print(f"    - Suppression perks: {fk_suppression_count} have FK populated")
    print(f"    - Enhancement perks: {fk_enhancement_count} have FK populated")

    return total_count


def main():
    print("="*60)
    print("MUTATION IMPORT SCRIPT")
    print("="*60)

    try:
        # Import mutations
        imported = import_mutations()

        # Populate mutation_effects table
        effects = populate_mutation_effects()

        # Populate foreign key relationships for 3NF compliance
        fk_updates = populate_foreign_keys()

        # Verify
        total = verify_import()

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Mutations in database: {total}")
        print(f"Mutation effects: {effects}")
        print(f"FK relationships populated: {fk_updates}")
        print("="*60)

    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
        print(f"Make sure {MUTATIONS_CSV} exists")
        exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
