#!/usr/bin/env python3
"""
Import collectibles (bobbleheads & magazines) into NORMALIZED MySQL database

Imports from:
- bobbleheads.csv
"""

import csv
import mysql.connector
import os
import re
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
BOBBLEHEADS_CSV = 'data/input/bobbleheads.csv'


def build_caches(conn):
    """Build caches for lookup tables"""
    cursor = conn.cursor(dictionary=True)
    caches = {}

    # Collectible types
    cursor.execute("SELECT id, name FROM collectible_types")
    caches['types'] = {row['name']: row['id'] for row in cursor.fetchall()}

    # Collectible series
    cursor.execute("SELECT id, name FROM collectible_series")
    caches['series'] = {row['name']: row['id'] for row in cursor.fetchall()}

    # SPECIAL attributes
    cursor.execute("SELECT id, code FROM special_attributes")
    caches['special'] = {row['code']: row['id'] for row in cursor.fetchall()}

    # Effect types
    cursor.execute("SELECT id, name FROM effect_types")
    caches['effect_types'] = {row['name']: row['id'] for row in cursor.fetchall()}

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


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    if not duration_str or duration_str.strip() == '':
        return None

    # Look for patterns like "1 hour(s)", "30 minute(s)"
    match = re.search(r'(\d+)\s*(hour|minute|second|min|sec|hr)', duration_str, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        unit = match.group(2).lower()

        if unit in ['hour', 'hr']:
            return value * 3600
        elif unit in ['minute', 'min']:
            return value * 60
        elif unit in ['second', 'sec']:
            return value

    return None


def parse_special_modifiers(modifiers_str: str, caches: dict):
    """
    Parse SPECIAL modifiers string into list of (special_id, modifier) tuples.
    """
    if not modifiers_str or modifiers_str.strip() == '':
        return []

    modifiers = []
    parts = modifiers_str.split(',')

    for part in parts:
        # Match patterns like "+2 STR", "-1 INT", "+3 S"
        match = re.search(r'([+-]?\d+)\s*([A-Z]{1,3})', part.strip(), re.IGNORECASE)
        if match:
            value = int(match.group(1))
            special_code = match.group(2).upper()

            # Map 3-letter codes to single letter
            code_map = {
                'STR': 'S', 'STRENGTH': 'S',
                'PER': 'P', 'PERCEPTION': 'P',
                'END': 'E', 'ENDURANCE': 'E',
                'CHA': 'C', 'CHARISMA': 'C',
                'INT': 'I', 'INTELLIGENCE': 'I',
                'AGI': 'A', 'AGILITY': 'A',
                'LCK': 'L', 'LUC': 'L', 'LUCK': 'L'
            }
            special_code = code_map.get(special_code, special_code)

            special_id = caches['special'].get(special_code)
            if special_id:
                modifiers.append((special_id, value))

    return modifiers


def import_collectibles(conn, caches):
    """Import collectibles from CSV"""
    cursor = conn.cursor()

    if not os.path.exists(BOBBLEHEADS_CSV):
        print(f"WARNING: {BOBBLEHEADS_CSV} not found")
        return 0

    # Read collectibles CSV
    with open(BOBBLEHEADS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        collectibles = list(reader)

    print(f"\nImporting {len(collectibles)} collectibles...")

    imported_count = 0
    for collectible in collectibles:
        try:
            # Get type ID
            type_name = collectible.get('collectible_type', 'bobblehead')
            type_id = caches['types'].get(type_name)
            if not type_id:
                print(f"ERROR: Unknown collectible type '{type_name}' for {collectible['name']}")
                continue

            # Get series ID (if applicable)
            series_id = None
            if collectible.get('series'):
                series_id = caches['series'].get(collectible['series'])

            # Parse duration
            duration_seconds = parse_duration(collectible.get('duration', ''))

            # Parse numeric fields
            weight = float(collectible['weight']) if collectible.get('weight') else None
            value = int(collectible['value']) if collectible.get('value') else None
            issue_number = int(collectible['issue_number']) if collectible.get('issue_number') else None

            # Insert collectible
            insert_sql = """
                INSERT INTO collectibles (
                    name, collectible_type_id, series_id, issue_number, duration_seconds,
                    stacking_behavior, weight, value, form_id, source_url, spawn_locations
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    collectible_type_id = VALUES(collectible_type_id),
                    series_id = VALUES(series_id),
                    issue_number = VALUES(issue_number),
                    duration_seconds = VALUES(duration_seconds),
                    stacking_behavior = VALUES(stacking_behavior),
                    weight = VALUES(weight),
                    value = VALUES(value),
                    form_id = VALUES(form_id),
                    source_url = VALUES(source_url),
                    spawn_locations = VALUES(spawn_locations)
            """

            cursor.execute(insert_sql, (
                collectible['name'],
                type_id,
                series_id,
                issue_number,
                duration_seconds,
                'duration_extends',  # Default stacking behavior
                weight,
                value,
                collectible.get('form_id') or None,
                collectible['source_url'],
                None  # spawn_locations not in CSV
            ))

            # Get collectible ID
            if cursor.lastrowid > 0:
                collectible_id = cursor.lastrowid
            else:
                # Updated existing, fetch ID
                cursor.execute("SELECT id FROM collectibles WHERE name = %s", (collectible['name'],))
                collectible_id = cursor.fetchone()[0]

            # Clear existing effects and modifiers
            cursor.execute("DELETE FROM collectible_effects WHERE collectible_id = %s", (collectible_id,))
            cursor.execute("DELETE FROM collectible_special_modifiers WHERE collectible_id = %s", (collectible_id,))

            # Insert effects
            if collectible.get('effects'):
                effect_type_id = get_or_create_effect_type(conn, 'collectible_effect', 'buff', caches)
                if effect_type_id:
                    cursor.execute("""
                        INSERT INTO collectible_effects (collectible_id, effect_type_id, description)
                        VALUES (%s, %s, %s)
                    """, (collectible_id, effect_type_id, collectible['effects']))

            # Parse and insert SPECIAL modifiers
            if collectible.get('special_modifiers'):
                modifiers = parse_special_modifiers(collectible['special_modifiers'], caches)
                for special_id, modifier_value in modifiers:
                    cursor.execute("""
                        INSERT INTO collectible_special_modifiers
                        (collectible_id, special_id, modifier)
                        VALUES (%s, %s, %s)
                    """, (collectible_id, special_id, modifier_value))

            imported_count += 1

        except Exception as e:
            print(f"ERROR importing {collectible['name']}: {e}")
            import traceback
            traceback.print_exc()

    conn.commit()
    cursor.close()

    print(f"✓ Successfully imported {imported_count}/{len(collectibles)} collectibles")
    return imported_count


def verify_import(conn):
    """Verify collectibles were imported correctly"""
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as count FROM collectibles")
    result = cursor.fetchone()
    total_count = result['count']

    cursor.execute("""
        SELECT ct.name, COUNT(*) as count
        FROM collectibles c
        JOIN collectible_types ct ON c.collectible_type_id = ct.id
        GROUP BY ct.name
    """)
    type_counts = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as count FROM collectible_special_modifiers")
    result = cursor.fetchone()
    modifier_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM collectible_effects")
    result = cursor.fetchone()
    effect_count = result['count']

    cursor.close()

    print(f"\nVerification:")
    print(f"  Total collectibles: {total_count}")
    for type_count in type_counts:
        print(f"  - {type_count['name'].capitalize()}: {type_count['count']}")
    print(f"  SPECIAL modifiers: {modifier_count}")
    print(f"  Effects: {effect_count}")

    return total_count


def main():
    print("="*60)
    print("COLLECTIBLES IMPORT SCRIPT (NORMALIZED SCHEMA)")
    print("="*60)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"✓ Connected to database '{DB_CONFIG['database']}'")

        # Build caches
        print("\nBuilding lookup caches...")
        caches = build_caches(conn)

        # Ensure bobblehead type exists
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO collectible_types (name)
            VALUES ('bobblehead')
            ON DUPLICATE KEY UPDATE name = name
        """)
        conn.commit()

        # Refresh type cache
        cursor.execute("SELECT id, name FROM collectible_types")
        caches['types'] = {row['name']: row['id'] for row in cursor.fetchall()}
        cursor.close()

        # Import collectibles
        imported = import_collectibles(conn, caches)

        # Verify
        total = verify_import(conn)

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Collectibles in database: {total}")
        print("="*60)

        conn.close()

    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
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
