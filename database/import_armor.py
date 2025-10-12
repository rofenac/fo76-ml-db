#!/usr/bin/env python3
"""
Import unified armor data (regular + power armor) from CSV into MySQL database
"""

import csv
import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database connection config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'secret',
    'database': 'f76'
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


def import_unified_armor(conn, csv_file: str):
    """Import unified armor data (regular + power armor) from CSV"""
    cursor = conn.cursor()
    imported = 0
    regular_count = 0
    power_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                sql = """
                INSERT INTO armor (
                    name, class, slot, damage_resistance, energy_resistance,
                    radiation_resistance, cryo_resistance, fire_resistance,
                    poison_resistance, set_name, armor_type, level, source_url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    class = VALUES(class),
                    slot = VALUES(slot),
                    damage_resistance = VALUES(damage_resistance),
                    energy_resistance = VALUES(energy_resistance),
                    radiation_resistance = VALUES(radiation_resistance),
                    cryo_resistance = VALUES(cryo_resistance),
                    fire_resistance = VALUES(fire_resistance),
                    poison_resistance = VALUES(poison_resistance),
                    set_name = VALUES(set_name),
                    armor_type = VALUES(armor_type),
                    level = VALUES(level),
                    source_url = VALUES(source_url)
                """

                values = (
                    row['Name'],
                    row['Class'] if row['Class'] else None,
                    row['Slot'],
                    row['Damage Resistance'] if row['Damage Resistance'] else None,
                    row['Energy Resistance'] if row['Energy Resistance'] else None,
                    row['Radiation Resistance'] if row['Radiation Resistance'] else None,
                    row['Cryo Resistance'] if row['Cryo Resistance'] else None,
                    row['Fire Resistance'] if row['Fire Resistance'] else None,
                    row['Poison Resistance'] if row['Poison Resistance'] else None,
                    row['Set Name'],
                    row['Armor Type'],
                    row['Level'],
                    row['Source URL']
                )

                cursor.execute(sql, values)
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
    return imported, regular_count, power_count


def get_table_counts(conn):
    """Get counts of all main tables"""
    cursor = conn.cursor()

    counts = {}
    tables = ['weapons', 'armor', 'perks', 'legendary_perks']

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]

    return counts


def main():
    """Main import process"""
    conn = connect_db()
    if not conn:
        logger.error("Cannot proceed without database connection")
        return

    try:
        logger.info("Starting unified armor import...")

        # Import all armor from unified CSV
        total, regular, power = import_unified_armor(conn, 'data/input/armor_unified.csv')

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
