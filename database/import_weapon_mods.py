#!/usr/bin/env python3
"""
Import weapon mod data from CSV into MySQL database
"""

import csv
import os
import logging
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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


def get_lookup_tables(conn):
    """Load lookup tables for weapons, slots, and perks"""
    cursor = conn.cursor(dictionary=True)
    
    # Weapons by name
    cursor.execute("SELECT id, name FROM weapons")
    weapons = {row['name'].lower(): row['id'] for row in cursor.fetchall()}
    
    # Mod slots by name
    cursor.execute("SELECT id, name FROM weapon_mod_slots")
    slots = {row['name'].lower(): row['id'] for row in cursor.fetchall()}
    
    # Perks by name
    cursor.execute("SELECT id, name FROM perks")
    perks = {row['name'].lower(): row['id'] for row in cursor.fetchall()}
    
    logger.info(f"Loaded {len(weapons)} weapons, {len(slots)} slots, {len(perks)} perks")
    return weapons, slots, perks


def parse_bool(val):
    """Parse boolean from CSV value"""
    if not val:
        return False
    return val.strip() in ('1', 'true', 'True', 'yes', 'Yes')


def parse_decimal(val):
    """Parse decimal/float from CSV value"""
    if not val or val.strip() in ('', '-', '—'):
        return None
    try:
        # Handle percentage strings
        clean = val.replace('%', '').replace('+', '').strip()
        return float(clean)
    except ValueError:
        return None


def parse_int(val):
    """Parse int from CSV value"""
    if not val or val.strip() in ('', '-', '—'):
        return None
    try:
        clean = val.replace('%', '').replace('+', '').strip()
        return int(float(clean))
    except ValueError:
        return None


def import_weapon_mods(conn, csv_file: str):
    """Import weapon mods from CSV"""
    cursor = conn.cursor()
    weapons, slots, perks = get_lookup_tables(conn)
    
    imported = 0
    skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            weapon_name = row.get('weapon_name', '').strip()
            slot_name = row.get('slot', '').strip().lower()
            mod_name = row.get('mod_name', '').strip()
            
            # Look up weapon ID
            weapon_id = weapons.get(weapon_name.lower())
            if not weapon_id:
                logger.warning(f"Weapon not found: '{weapon_name}' - skipping mod '{mod_name}'")
                skipped += 1
                continue
            
            # Look up slot ID
            slot_id = slots.get(slot_name)
            if not slot_id:
                logger.warning(f"Slot not found: '{slot_name}' - skipping mod '{mod_name}'")
                skipped += 1
                continue
            
            try:
                # Insert mod
                sql = """
                INSERT INTO weapon_mods (
                    weapon_id, slot_id, name,
                    damage_change, damage_change_is_percent,
                    fire_rate_change, range_change, accuracy_change,
                    ap_cost_change, recoil_change, spread_change,
                    converts_to_auto, converts_to_semi,
                    crit_damage_bonus, hip_fire_accuracy_bonus, armor_penetration,
                    is_suppressed, is_scoped,
                    mag_size_change, reload_speed_change,
                    weight_change, value_change_percent,
                    form_id, source_url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    damage_change = VALUES(damage_change),
                    fire_rate_change = VALUES(fire_rate_change),
                    range_change = VALUES(range_change),
                    accuracy_change = VALUES(accuracy_change),
                    ap_cost_change = VALUES(ap_cost_change),
                    recoil_change = VALUES(recoil_change)
                """
                
                values = (
                    weapon_id,
                    slot_id,
                    mod_name,
                    parse_decimal(row.get('damage_change')),
                    parse_bool(row.get('damage_change_is_percent')),
                    parse_int(row.get('fire_rate_change')),
                    parse_int(row.get('range_change')),
                    parse_int(row.get('accuracy_change')),
                    parse_decimal(row.get('ap_cost_change')),
                    parse_int(row.get('recoil_change')),
                    parse_decimal(row.get('spread_change')),
                    parse_bool(row.get('converts_to_auto')),
                    parse_bool(row.get('converts_to_semi')),
                    parse_int(row.get('crit_damage_bonus')),
                    parse_int(row.get('hip_fire_accuracy_bonus')),
                    parse_int(row.get('armor_penetration')),
                    parse_bool(row.get('is_suppressed')),
                    parse_bool(row.get('is_scoped')),
                    parse_int(row.get('mag_size_change')),
                    parse_decimal(row.get('reload_speed_change')),
                    parse_decimal(row.get('weight_change')),
                    parse_int(row.get('value_change_percent')),
                    row.get('form_id', '').strip() or None,
                    row.get('source_url', '').strip() or None,
                )
                
                cursor.execute(sql, values)
                mod_id = cursor.lastrowid
                
                # Handle perk requirement
                perk_name = row.get('required_perk', '').strip()
                if perk_name:
                    perk_id = perks.get(perk_name.lower())
                    if perk_id:
                        perk_rank = parse_int(row.get('required_perk_rank')) or 1
                        cursor.execute("""
                            INSERT INTO weapon_mod_crafting (mod_id, perk_id, perk_rank)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE perk_rank = VALUES(perk_rank)
                        """, (mod_id, perk_id, perk_rank))
                
                imported += 1
                
            except Error as e:
                logger.error(f"Failed to import mod '{mod_name}' for '{weapon_name}': {e}")
                skipped += 1
                continue
    
    conn.commit()
    logger.info(f"Imported {imported} mods, skipped {skipped}")
    return imported, skipped


def main():
    """Main import process"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import weapon mods to database')
    parser.add_argument('-f', '--file', default='data/input/weapon_mods.csv',
                        help='CSV file to import')
    args = parser.parse_args()
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        imported, skipped = import_weapon_mods(conn, args.file)
        
        # Show counts
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weapon_mods")
        total_mods = cursor.fetchone()[0]
        
        print("\n" + "=" * 50)
        print("WEAPON MOD IMPORT COMPLETE")
        print("=" * 50)
        print(f"Imported this session: {imported}")
        print(f"Skipped:               {skipped}")
        print(f"Total mods in DB:      {total_mods}")
        print("=" * 50)
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()
