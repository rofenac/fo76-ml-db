#!/usr/bin/env python3
"""
Import armor and power armor data from CSV files into MySQL database
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


def import_armor(conn, csv_file: str):
    """Import armor data from CSV"""
    cursor = conn.cursor()
    imported = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                sql = """
                INSERT INTO armor (
                    name, type, slot, armor_rating, energy_resistance,
                    radiation_resistance, set_name, level, weight, value,
                    form_id, editor_id, perks_raw, source_url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    type = VALUES(type),
                    slot = VALUES(slot),
                    armor_rating = VALUES(armor_rating),
                    energy_resistance = VALUES(energy_resistance),
                    radiation_resistance = VALUES(radiation_resistance),
                    set_name = VALUES(set_name),
                    level = VALUES(level),
                    weight = VALUES(weight),
                    value = VALUES(value),
                    form_id = VALUES(form_id),
                    editor_id = VALUES(editor_id),
                    perks_raw = VALUES(perks_raw),
                    source_url = VALUES(source_url)
                """

                values = (
                    row['Name'],
                    row['Type'],
                    row['Slot'],
                    row['Armor Rating'],
                    row['Energy Resistance'],
                    row['Radiation Resistance'],
                    row['Set Name'],
                    row['Level'],
                    row['Weight'],
                    row['Value'],
                    row['Form ID'] if row['Form ID'] else None,
                    row['Editor ID'],
                    row['Perks'],
                    row['Source URL']
                )

                cursor.execute(sql, values)
                imported += 1

            except Error as e:
                logger.error(f"Failed to import armor '{row.get('Name', 'UNKNOWN')}': {e}")
                continue

    conn.commit()
    logger.info(f"Imported {imported} armor pieces")
    return imported


def import_power_armor(conn, csv_file: str):
    """Import power armor data from CSV"""
    cursor = conn.cursor()
    imported = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                sql = """
                INSERT INTO power_armor (
                    name, type, set_name, armor_rating, energy_resistance,
                    radiation_resistance, level, weight, value, durability,
                    fusion_core_drain, form_id, editor_id, perks_raw, source_url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    type = VALUES(type),
                    set_name = VALUES(set_name),
                    armor_rating = VALUES(armor_rating),
                    energy_resistance = VALUES(energy_resistance),
                    radiation_resistance = VALUES(radiation_resistance),
                    level = VALUES(level),
                    weight = VALUES(weight),
                    value = VALUES(value),
                    durability = VALUES(durability),
                    fusion_core_drain = VALUES(fusion_core_drain),
                    form_id = VALUES(form_id),
                    editor_id = VALUES(editor_id),
                    perks_raw = VALUES(perks_raw),
                    source_url = VALUES(source_url)
                """

                values = (
                    row['Name'],
                    row['Type'],
                    row['Set Name'],
                    row['Armor Rating'],
                    row['Energy Resistance'],
                    row['Radiation Resistance'],
                    row['Level'],
                    row['Weight'],
                    row['Value'],
                    row['Durability'],
                    row['Fusion Core Drain'],
                    row['Form ID'] if row['Form ID'] else None,
                    row['Editor ID'],
                    row['Perks'],
                    row['Source URL']
                )

                cursor.execute(sql, values)
                imported += 1

            except Error as e:
                logger.error(f"Failed to import power armor '{row.get('Name', 'UNKNOWN')}': {e}")
                continue

    conn.commit()
    logger.info(f"Imported {imported} power armor pieces")
    return imported


def get_table_counts(conn):
    """Get counts of all main tables"""
    cursor = conn.cursor()

    counts = {}
    tables = ['weapons', 'armor', 'power_armor', 'perks', 'legendary_perks']

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
        logger.info("Starting armor and power armor import...")

        # Import armor
        armor_count = import_armor(conn, 'armor_scraped.csv')

        # Import power armor
        pa_count = import_power_armor(conn, 'power_armor_scraped.csv')

        # Show final counts
        counts = get_table_counts(conn)

        print("\n" + "="*60)
        print("DATABASE IMPORT COMPLETE")
        print("="*60)
        print(f"Armor imported this session:        {armor_count}")
        print(f"Power armor imported this session:  {pa_count}")
        print("-"*60)
        print("TOTAL DATABASE RECORDS:")
        print(f"  Weapons:        {counts['weapons']}")
        print(f"  Armor:          {counts['armor']}")
        print(f"  Power Armor:    {counts['power_armor']}")
        print(f"  Perks:          {counts['perks']}")
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
