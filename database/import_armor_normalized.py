#!/usr/bin/env python3
"""
Import unified armor data (regular + power armor) from CSV into NORMALIZED MySQL database

UPDATED FOR NORMALIZED SCHEMA - Use this instead of import_armor.py
"""

import csv
import mysql.connector
from mysql.connector import Error
import logging
import re
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database connection config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'database': os.getenv('DB_NAME', 'f76')
}


def connect_db():
    """Establish database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("Connected to MySQL database")
        return conn
    except Error as e:
        logger.error(f"Database connection failed: {e}")
        return None


def build_caches(conn):
    """Build caches for lookup tables"""
    cursor = conn.cursor()

    caches = {}

    # Armor types
    cursor.execute("SELECT id, name FROM armor_types")
    caches['armor_types'] = {name: aid for aid, name in cursor.fetchall()}

    # Armor classes
    cursor.execute("SELECT id, name FROM armor_classes")
    caches['armor_classes'] = {name: cid for cid, name in cursor.fetchall()}

    # Armor slots
    cursor.execute("SELECT id, name FROM armor_slots")
    caches['armor_slots'] = {name: sid for sid, name in cursor.fetchall()}

    # Damage types (for resistances)
    cursor.execute("SELECT id, name FROM damage_types")
    caches['damage_types'] = {name: did for did, name in cursor.fetchall()}

    cursor.close()

    logger.info(f"Cached {len(caches['armor_types'])} armor types")
    logger.info(f"Cached {len(caches['armor_classes'])} armor classes")
    logger.info(f"Cached {len(caches['armor_slots'])} armor slots")
    logger.info(f"Cached {len(caches['damage_types'])} damage types")

    return caches


def get_or_create_lookup(conn, table: str, name: str, cache: dict) -> int:
    """Get or create lookup table entry"""
    if name in cache:
        return cache[name]

    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO {table} (name) VALUES (%s)", (name,))
        conn.commit()
        lookup_id = cursor.lastrowid
        cache[name] = lookup_id
        cursor.close()
        return lookup_id
    except Error:
        # Already exists, fetch it
        cursor.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            cache[name] = result[0]
            return result[0]
        raise


def parse_resistance(resistance_str: str) -> float:
    """Parse resistance value from string"""
    if not resistance_str or resistance_str.strip() == '':
        return None

    # Extract numeric value
    match = re.search(r'(\d+\.?\d*)', resistance_str)
    if match:
        return float(match.group(1))
    return None


def parse_level(level_str: str) -> int:
    """Parse level value from string"""
    if not level_str or level_str.strip() == '':
        return None

    match = re.search(r'(\d+)', level_str)
    if match:
        return int(match.group(1))
    return None


def import_unified_armor(conn, csv_file: str, caches: dict):
    """Import unified armor data (regular + power armor) from CSV"""
    cursor = conn.cursor()
    imported = 0
    regular_count = 0
    power_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # Get or create lookup IDs
                armor_type_id = None
                if row['Armor Type']:
                    armor_type_id = caches['armor_types'].get(row['Armor Type'])

                armor_class_id = None
                if row['Class']:
                    armor_class_id = get_or_create_lookup(conn, 'armor_classes', row['Class'], caches['armor_classes'])

                armor_slot_id = None
                if row['Slot']:
                    armor_slot_id = get_or_create_lookup(conn, 'armor_slots', row['Slot'], caches['armor_slots'])

                # Parse level
                min_level = parse_level(row['Level'])

                # Insert armor
                sql = """
                INSERT INTO armor (
                    name, armor_class_id, armor_slot_id, armor_type_id,
                    set_name, min_level, source_url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                """

                values = (
                    row['Name'],
                    armor_class_id,
                    armor_slot_id,
                    armor_type_id,
                    row['Set Name'] if row['Set Name'] else None,
                    min_level,
                    row['Source URL']
                )

                cursor.execute(sql, values)
                armor_id = cursor.lastrowid

                # Insert resistance values
                resistance_fields = [
                    ('Damage Resistance', 'physical'),
                    ('Energy Resistance', 'energy'),
                    ('Radiation Resistance', 'radiation'),
                    ('Cryo Resistance', 'cryo'),
                    ('Fire Resistance', 'fire'),
                    ('Poison Resistance', 'poison')
                ]

                for field, dtype in resistance_fields:
                    if row[field]:
                        res_value = parse_resistance(row[field])
                        if res_value is not None:
                            dtype_id = caches['damage_types'].get(dtype)
                            if dtype_id:
                                cursor.execute("""
                                    INSERT INTO armor_resistance_values
                                    (armor_id, damage_type_id, resistance_value)
                                    VALUES (%s, %s, %s)
                                """, (armor_id, dtype_id, res_value))

                imported += 1

                if row['Armor Type'] == 'regular':
                    regular_count += 1
                elif row['Armor Type'] == 'power':
                    power_count += 1

            except Error as e:
                logger.error(f"Failed to import '{row.get('Name', 'UNKNOWN')}': {e}")
                continue

    conn.commit()
    logger.info(f"Imported {imported} total armor pieces")
    logger.info(f"  - Regular armor: {regular_count}")
    logger.info(f"  - Power armor: {power_count}")
    cursor.close()
    return imported, regular_count, power_count


def get_table_counts(conn):
    """Get counts of all main tables"""
    cursor = conn.cursor()

    counts = {}
    tables = ['weapons', 'armor', 'perks', 'legendary_perks']

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except:
            counts[table] = 0

    cursor.close()
    return counts


def main():
    """Main import process"""
    conn = connect_db()
    if not conn:
        logger.error("Cannot proceed without database connection")
        return

    try:
        logger.info("Building lookup caches...")
        caches = build_caches(conn)

        logger.info("Starting unified armor import...")

        # Import all armor from unified CSV
        total, regular, power = import_unified_armor(conn, 'data/input/armor_unified.csv', caches)

        # Show final counts
        counts = get_table_counts(conn)

        print("\n" + "="*60)
        print("DATABASE IMPORT COMPLETE")
        print("="*60)
        print(f"Armor imported this session:")
        print(f"  - Regular armor:  {regular}")
        print(f"  - Power armor:    {power}")
        print(f"  - Total:          {total}")
        print("-"*60)
        print("TOTAL DATABASE RECORDS:")
        print(f"  Weapons:         {counts['weapons']}")
        print(f"  Armor (unified): {counts['armor']}")
        print(f"  Perks:           {counts['perks']}")
        print(f"  Legendary Perks: {counts['legendary_perks']}")
        print("="*60)

    except Exception as e:
        logger.error(f"Import failed: {e}")

    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


if __name__ == '__main__':
    main()
