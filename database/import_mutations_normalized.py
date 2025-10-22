#!/usr/bin/env python3
"""
Import mutations from Mutations.csv into NORMALIZED MySQL database

UPDATED FOR NORMALIZED SCHEMA - Use this instead of import_mutations.py

Key changes:
- exclusive_with now uses foreign key to mutations table
- positive_effects and negative_effects stored in mutation_effects table
- suppression/enhancement perks stored in mutation_perk_interactions table
"""

import csv
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'database': os.getenv('DB_NAME', 'f76')
}

# File paths
MUTATIONS_CSV = 'data/input/Mutations.csv'


def build_caches(conn):
    """Build caches for lookup tables"""
    cursor = conn.cursor(dictionary=True)
    caches = {}

    # Effect types
    cursor.execute("SELECT id, name FROM effect_types")
    caches['effect_types'] = {row['name']: row['id'] for row in cursor.fetchall()}

    # Perks (for interactions)
    cursor.execute("SELECT id, name FROM perks")
    caches['perks'] = {row['name']: row['id'] for row in cursor.fetchall()}

    # Legendary perks (for interactions)
    cursor.execute("SELECT id, name FROM legendary_perks")
    caches['legendary_perks'] = {row['name']: row['id'] for row in cursor.fetchall()}

    cursor.close()
    return caches


def get_or_create_effect_type(conn, name: str, category: str, caches: dict) -> int:
    """Get or create effect type"""
    if name in caches['effect_types']:
        return caches['effect_types'][name]

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO effect_types (name, category) VALUES (%s, %s)", (name, category))
        conn.commit()
        effect_type_id = cursor.lastrowid
        caches['effect_types'][name] = effect_type_id
        cursor.close()
        return effect_type_id
    except:
        # Already exists, fetch it
        cursor.execute("SELECT id FROM effect_types WHERE name = %s", (name,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            caches['effect_types'][name] = result[0]
            return result[0]
        return None


def import_mutations(conn, caches):
    """Import mutations from CSV"""
    cursor = conn.cursor(dictionary=True)

    # Read mutations CSV
    with open(MUTATIONS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mutations = list(reader)

    print(f"\nImporting {len(mutations)} mutations...")

    # First pass: insert mutations (without exclusive_with FK)
    mutation_id_map = {}
    for mutation in mutations:
        try:
            cursor.execute("""
                INSERT INTO mutations (name, form_id, source_url)
                VALUES (%s, %s, %s)
            """, (
                mutation['name'],
                mutation['form_id'] or None,
                mutation['source_url']
            ))
            mutation_id_map[mutation['name']] = cursor.lastrowid
        except Exception as e:
            print(f"ERROR inserting mutation {mutation['name']}: {e}")

    conn.commit()

    # Second pass: update exclusive_with relationships
    for mutation in mutations:
        if mutation['exclusive_with']:
            exclusive_id = mutation_id_map.get(mutation['exclusive_with'])
            if exclusive_id:
                try:
                    cursor.execute("""
                        UPDATE mutations
                        SET exclusive_mutation_id = %s
                        WHERE name = %s
                    """, (exclusive_id, mutation['name']))
                except Exception as e:
                    print(f"ERROR updating exclusive_with for {mutation['name']}: {e}")

    conn.commit()

    # Third pass: insert effects
    imported_count = 0
    for mutation in mutations:
        mutation_id = mutation_id_map.get(mutation['name'])
        if not mutation_id:
            continue

        try:
            # Insert positive effects
            if mutation['positive_effects']:
                effect_type_id = get_or_create_effect_type(conn, 'positive_effect', 'buff', caches)
                if effect_type_id:
                    cursor.execute("""
                        INSERT INTO mutation_effects (mutation_id, effect_type_id, polarity, description)
                        VALUES (%s, %s, 'positive', %s)
                    """, (mutation_id, effect_type_id, mutation['positive_effects']))

            # Insert negative effects
            if mutation['negative_effects']:
                effect_type_id = get_or_create_effect_type(conn, 'negative_effect', 'debuff', caches)
                if effect_type_id:
                    cursor.execute("""
                        INSERT INTO mutation_effects (mutation_id, effect_type_id, polarity, description)
                        VALUES (%s, %s, 'negative', %s)
                    """, (mutation_id, effect_type_id, mutation['negative_effects']))

            # Insert perk interactions (if we have perk data)
            # Note: Most mutations reference "Class Freak" and "Strange in Numbers"
            # For now, we'll skip this as it requires perk data to be imported first
            # This can be added as a post-processing step

            imported_count += 1

        except Exception as e:
            print(f"ERROR importing effects for {mutation['name']}: {e}")

    conn.commit()
    cursor.close()

    print(f"✓ Successfully imported {imported_count}/{len(mutations)} mutations")
    return imported_count


def verify_import(conn):
    """Verify mutations were imported correctly"""
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as count FROM mutations")
    result = cursor.fetchone()
    total_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM mutations WHERE exclusive_mutation_id IS NOT NULL")
    result = cursor.fetchone()
    exclusive_count = result['count']

    cursor.execute("""
        SELECT m1.name, m2.name as exclusive_with
        FROM mutations m1
        JOIN mutations m2 ON m1.exclusive_mutation_id = m2.id
    """)
    exclusive_mutations = cursor.fetchall()

    cursor.close()

    print(f"\nVerification:")
    print(f"  Total mutations: {total_count}")
    print(f"  Mutations with exclusivity: {exclusive_count}")
    if exclusive_mutations:
        print(f"  Exclusivity pairs:")
        for m in exclusive_mutations:
            print(f"    - {m['name']} <-> {m['exclusive_with']}")

    return total_count


def main():
    print("="*60)
    print("MUTATION IMPORT SCRIPT (NORMALIZED SCHEMA)")
    print("="*60)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"✓ Connected to database '{DB_CONFIG['database']}'")

        # Build caches
        print("\nBuilding lookup caches...")
        caches = build_caches(conn)

        # Import mutations
        imported = import_mutations(conn, caches)

        # Verify
        total = verify_import(conn)

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Mutations in database: {total}")
        print("="*60)

        conn.close()

    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
        print(f"Make sure {MUTATIONS_CSV} exists")
        exit(1)
    except mysql.connector.Error as e:
        print(f"\nDATABASE ERROR: {e}")
        exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
