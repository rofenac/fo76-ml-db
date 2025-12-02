#!/usr/bin/env python3
"""
Import script for Fallout 76 weapon and perk data into MySQL database.

Usage:
    python import_to_db.py -u <username> -p <password> [-H <host>] [-d <database>]

    Or use environment variables:
    export MYSQL_USER=your_username (or DB_USER)
    export MYSQL_PASS=your_password (or DB_PASSWORD)
    python import_to_db.py
"""

import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Set, Tuple
import mysql.connector
from mysql.connector import Error


class F76DatabaseImporter:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

        # Cache for perk name -> perk id mapping
        self.perk_id_cache: Dict[str, int] = {}
        self.legendary_perk_id_cache: Dict[str, int] = {}

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print(f"✓ Connected to MySQL database '{self.database}' at {self.host}")
            return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def import_perks(self, csv_file: str = "data/input/Perks.csv") -> int:
        """Import perks from CSV into perks and perk_ranks tables."""
        print(f"\n=== Importing Perks from {csv_file} ===")

        if not os.path.exists(csv_file):
            print(f"✗ File not found: {csv_file}")
            return 0

        # Read all rows and group by perk name
        perk_data = {}

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                perk_name = row['name'].strip()

                if not perk_name:
                    continue

                # Group all ranks for this perk
                if perk_name not in perk_data:
                    perk_data[perk_name] = {
                        'special': row.get('special', '').strip() or None,
                        'level': int(row.get('level', 0)) if row.get('level', '').strip() else None,
                        'race': row.get('race', '').strip() or None,
                        'ranks': []
                    }

                # Add this rank's data
                perk_data[perk_name]['ranks'].append({
                    'rank': int(row.get('rank', 1)),
                    'description': row.get('description', '').strip(),
                    'form_id': row.get('form_id', '').strip() or None
                })

        print(f"Found {len(perk_data)} unique perks with {sum(len(p['ranks']) for p in perk_data.values())} total ranks")

        perks_inserted = 0
        ranks_inserted = 0

        for perk_name, data in perk_data.items():
            try:
                # Insert base perk
                self.cursor.execute(
                    "INSERT INTO perks (name, special, level, race) VALUES (%s, %s, %s, %s)",
                    (perk_name, data['special'], data['level'], data['race'])
                )

                perk_id = self.cursor.lastrowid
                perks_inserted += 1

                # Insert all ranks for this perk
                for rank_data in data['ranks']:
                    self.cursor.execute(
                        "INSERT INTO perk_ranks (perk_id, `rank`, description, form_id) VALUES (%s, %s, %s, %s)",
                        (perk_id, rank_data['rank'], rank_data['description'], rank_data['form_id'])
                    )
                    ranks_inserted += 1

            except Error as e:
                print(f"✗ Error inserting perk '{perk_name}': {e}")

        self.connection.commit()
        print(f"✓ Inserted {perks_inserted} perks")
        print(f"✓ Inserted {ranks_inserted} perk ranks")

        # Build perk cache
        self._build_perk_cache()

        return perks_inserted

    def import_legendary_perks(self, csv_file: str = "data/input/LegendaryPerks.csv") -> int:
        """Import legendary perks from CSV into legendary_perks and legendary_perk_ranks tables."""
        print(f"\n=== Importing Legendary Perks from {csv_file} ===")

        if not os.path.exists(csv_file):
            print(f"⚠ File not found: {csv_file}, skipping legendary perks import")
            return 0

        # Read all rows and group by perk name
        perk_data = {}

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                perk_name = row['name'].strip()

                if not perk_name:
                    continue

                # Group all ranks for this perk
                if perk_name not in perk_data:
                    perk_data[perk_name] = {
                        'race': row.get('race', '').strip() or 'Human, Ghoul',
                        'ranks': []
                    }

                # Add this rank's data
                perk_data[perk_name]['ranks'].append({
                    'rank': int(row.get('rank', 1)),
                    'description': row.get('description', '').strip(),
                    'effect_value': row.get('effect_value', '').strip() or None,
                    'effect_type': row.get('effect_type', '').strip() or None,
                    'form_id': row.get('form_id', '').strip() or None
                })

        print(f"Found {len(perk_data)} unique legendary perks with {sum(len(p['ranks']) for p in perk_data.values())} total ranks")

        perks_inserted = 0
        ranks_inserted = 0

        for perk_name, data in perk_data.items():
            try:
                # Create a base description from rank 1
                base_description = data['ranks'][0]['description'] if data['ranks'] else None

                # Insert base legendary perk
                self.cursor.execute(
                    "INSERT INTO legendary_perks (name, description, race) VALUES (%s, %s, %s)",
                    (perk_name, base_description, data['race'])
                )

                legendary_perk_id = self.cursor.lastrowid
                perks_inserted += 1

                # Insert all ranks for this legendary perk
                for rank_data in data['ranks']:
                    self.cursor.execute(
                        """INSERT INTO legendary_perk_ranks
                           (legendary_perk_id, `rank`, description, effect_value, effect_type)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (legendary_perk_id, rank_data['rank'], rank_data['description'],
                         rank_data['effect_value'], rank_data['effect_type'])
                    )
                    ranks_inserted += 1

            except Error as e:
                print(f"✗ Error inserting legendary perk '{perk_name}': {e}")

        self.connection.commit()
        print(f"✓ Inserted {perks_inserted} legendary perks")
        print(f"✓ Inserted {ranks_inserted} legendary perk ranks")

        # Rebuild cache to include legendary perks
        self._build_perk_cache()

        return perks_inserted

    def _build_perk_cache(self):
        """Build cache of perk name -> perk id mapping."""
        self.cursor.execute("SELECT id, name FROM perks")
        self.perk_id_cache = {name: perk_id for perk_id, name in self.cursor.fetchall()}
        print(f"✓ Cached {len(self.perk_id_cache)} regular perk IDs")

        self.cursor.execute("SELECT id, name FROM legendary_perks")
        self.legendary_perk_id_cache = {name: perk_id for perk_id, name in self.cursor.fetchall()}
        print(f"✓ Cached {len(self.legendary_perk_id_cache)} legendary perk IDs")

    def parse_perks_field(self, perks_raw: str) -> List[Tuple[str, Dict]]:
        """
        Parse the perks_raw field into perk names with conditions.

        Handles cases like:
        - "Bloody Mess" -> ("Bloody Mess", {})
        - "Gunslinger (Expert, Master)" -> [("Gunslinger", {}), ("Gunslinger Expert", {}), ...]
        - "Sniper (scoped) only" -> ("Sniper", {'scope_state': 'scoped'})
        - "Pistol: Gun Runner" -> ("Gun Runner", {'weapon_class': 'pistol'})

        Returns list of tuples: (perk_name, conditions_dict)
        """
        if not perks_raw or perks_raw.strip() == '':
            return []

        # Fix common typos
        perks_raw = perks_raw.replace('Guerilla', 'Guerrilla')

        perks = []

        # Split by semicolon first (major delimiter)
        sections = [s.strip() for s in perks_raw.split(';')]

        for section in sections:
            if not section:
                continue

            # Check if section has a class prefix (e.g., "Pistol: perk1, perk2")
            weapon_class_prefix = None
            if ':' in section:
                # Split on colon and process the perk list part
                prefix, perk_list = section.split(':', 1)
                prefix_lower = prefix.strip().lower()
                if prefix_lower in ['pistol', 'rifle', 'heavy', 'melee', 'auto pistol', 'non-auto pistol']:
                    weapon_class_prefix = prefix_lower
                    section = perk_list.strip()

            # Now we need to split on commas, but NOT commas inside parentheses
            # Use a smarter split that respects parentheses
            perk_parts = self._smart_comma_split(section)

            for perk_part in perk_parts:
                if not perk_part:
                    continue

                # Extract base perk name, variants, and conditions
                perk_data = self._extract_perk_with_conditions(perk_part)

                # Apply weapon class prefix if present
                for perk_name, conditions in perk_data:
                    if weapon_class_prefix:
                        conditions['weapon_class'] = weapon_class_prefix
                    perks.append((perk_name, conditions))

        # Remove duplicates while preserving order
        seen = set()
        unique_perks = []
        for perk_tuple in perks:
            # Create a hashable key from perk name and sorted conditions
            perk_name, conditions = perk_tuple
            key = (perk_name, tuple(sorted(conditions.items())))
            if key not in seen:
                seen.add(key)
                unique_perks.append(perk_tuple)

        return unique_perks

    def _smart_comma_split(self, text: str) -> List[str]:
        """Split on commas, but not commas inside parentheses."""
        parts = []
        current = []
        paren_depth = 0

        for char in text:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                # This comma is not inside parentheses, so split here
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        # Don't forget the last part
        if current:
            parts.append(''.join(current).strip())

        return parts

    def _extract_perk_with_conditions(self, perk_str: str) -> List[Tuple[str, Dict]]:
        """
        Extract perk name(s) and conditions from a string like:
        - "Bloody Mess" -> [("Bloody Mess", {})]
        - "Gunslinger (Expert, Master)" -> [("Gunslinger", {}), ("Gunslinger Expert", {}), ...]
        - "Sniper (scoped) only" -> [("Sniper", {'scope_state': 'scoped'})]
        - "Crack Shot (sighted only)" -> [("Crack Shot", {'aim_state': 'ads'})]
        """
        conditions = {}

        # Extract conditions from the string
        # Look for: (scoped), (sighted), (unscoped), etc.
        condition_patterns = [
            (r'\bscoped\b', 'scope_state', 'scoped'),
            (r'\bunscoped\b', 'scope_state', 'unscoped'),
            (r'\bsighted\b', 'aim_state', 'ads'),
            (r'\bhip\s*fire\b', 'aim_state', 'hip_fire'),
            (r'\bauto\b', 'fire_mode', 'auto'),
            (r'\bsemi(?:-auto)?\b', 'fire_mode', 'semi'),
            (r'\bnon-auto\b', 'fire_mode', 'semi'),
        ]

        for pattern, key, value in condition_patterns:
            if re.search(pattern, perk_str, flags=re.IGNORECASE):
                conditions[key] = value

        # Remove condition text and "only" from perk string
        clean_str = perk_str
        clean_str = re.sub(r'\s*\((?:scoped|sighted|unscoped|hip\s*fire|auto|semi|non-auto)(?:\s+only)?\)\s*', '', clean_str, flags=re.IGNORECASE)
        clean_str = re.sub(r'\s+only\s*$', '', clean_str, flags=re.IGNORECASE)
        clean_str = clean_str.strip()

        # Check for variants in parentheses like "(Expert, Master)"
        variant_match = re.search(r'^(.+?)\s*\(([^)]+)\)$', clean_str)

        if variant_match:
            base_name = variant_match.group(1).strip()
            variants_str = variant_match.group(2).strip()

            # Check if these are rank variants (Expert, Master) or conditions
            variants = [v.strip() for v in variants_str.split(',')]

            # Known rank variants
            rank_variants = {'expert', 'master'}

            perk_names = []
            has_ranks = False

            for variant in variants:
                if variant.lower() in rank_variants:
                    # This is a rank variant
                    perk_names.append((f"{base_name} {variant.title()}", conditions.copy()))
                    has_ranks = True

            # If we found rank variants, also include the base perk
            if has_ranks:
                perk_names.insert(0, (base_name, conditions.copy()))
            else:
                # Not rank variants, just return the base name
                perk_names = [(base_name, conditions.copy())]

            return perk_names
        else:
            # No variants, just return the perk name with conditions
            return [(clean_str, conditions)]

    def import_weapons(self, csv_file: str = "data/input/human_corrected_weapons_clean.csv") -> int:
        """Import weapons from CSV into weapons table and populate weapon_perks."""
        print(f"\n=== Importing Weapons from {csv_file} ===")

        if not os.path.exists(csv_file):
            print(f"✗ File not found: {csv_file}")
            return 0

        weapons_inserted = 0
        weapons_updated = 0
        total_perk_links = 0

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row['Name'].strip()

                if not name:
                    continue

                # Prepare weapon data
                weapon_data = {
                    'name': name,
                    'type': row.get('Type', '').strip() or None,
                    'class': row.get('Class', '').strip() or None,
                    'level': row.get('Level', '').strip() or None,
                    'damage': row.get('Damage', '').strip() or None,
                    'perks_raw': row.get('Perks', '').strip() or None,
                    'source_url': row.get('Source URL', '').strip() or None,
                }

                try:
                    # Insert or update weapon
                    self.cursor.execute("""
                        INSERT INTO weapons (name, type, class, level, damage,
                                            perks_raw, source_url)
                        VALUES (%(name)s, %(type)s, %(class)s, %(level)s, %(damage)s,
                                %(perks_raw)s, %(source_url)s)
                        ON DUPLICATE KEY UPDATE
                            type = VALUES(type),
                            class = VALUES(class),
                            level = VALUES(level),
                            damage = VALUES(damage),
                            perks_raw = VALUES(perks_raw),
                            source_url = VALUES(source_url)
                    """, weapon_data)

                    if self.cursor.lastrowid > 0:
                        weapon_id = self.cursor.lastrowid
                        weapons_inserted += 1
                    else:
                        # Updated existing weapon, need to get its ID
                        self.cursor.execute("SELECT id FROM weapons WHERE name = %s", (name,))
                        weapon_id = self.cursor.fetchone()[0]
                        weapons_updated += 1

                    # Parse and link perks
                    perks_raw = weapon_data.get('perks_raw', '')
                    if perks_raw:
                        perk_count = self._link_weapon_perks(weapon_id, perks_raw, name)
                        total_perk_links += perk_count

                except Error as e:
                    print(f"✗ Error processing weapon '{name}': {e}")

        self.connection.commit()
        print(f"✓ Inserted {weapons_inserted} new weapons")
        if weapons_updated > 0:
            print(f"✓ Updated {weapons_updated} existing weapons")
        print(f"✓ Created {total_perk_links} weapon-perk links")

        return weapons_inserted + weapons_updated

    def _link_weapon_perks(self, weapon_id: int, perks_raw: str, weapon_name: str) -> int:
        """Parse perks_raw and create weapon_perks, weapon_legendary_perks, and weapon_perk_rules entries."""
        perk_data = self.parse_perks_field(perks_raw)

        if not perk_data:
            return 0

        # Clear existing links for this weapon
        self.cursor.execute("DELETE FROM weapon_perks WHERE weapon_id = %s", (weapon_id,))
        self.cursor.execute("DELETE FROM weapon_legendary_perk_effects WHERE weapon_id = %s", (weapon_id,))
        self.cursor.execute("DELETE FROM weapon_perk_rules WHERE weapon_id = %s", (weapon_id,))

        regular_links_created = 0
        legendary_links_created = 0
        rules_created = 0
        perks_not_found = []

        for perk_name, conditions in perk_data:
            # Try regular perks first
            perk_id = self.perk_id_cache.get(perk_name)

            if perk_id:
                try:
                    # Always create basic link in weapon_perks
                    self.cursor.execute(
                        "INSERT IGNORE INTO weapon_perks (weapon_id, perk_id) VALUES (%s, %s)",
                        (weapon_id, perk_id)
                    )
                    if self.cursor.rowcount > 0:
                        regular_links_created += 1

                    # If there are conditions, also create weapon_perk_rules entry
                    if conditions:
                        rules_created += self._create_perk_rule(weapon_id, perk_id, conditions, weapon_name)

                except Error as e:
                    print(f"  ✗ Error linking perk '{perk_name}' to weapon '{weapon_name}': {e}")
            else:
                # Try legendary perks
                legendary_perk_id = self.legendary_perk_id_cache.get(perk_name)

                if legendary_perk_id:
                    try:
                        self.cursor.execute(
                            "INSERT IGNORE INTO weapon_legendary_perk_effects (weapon_id, legendary_perk_id) VALUES (%s, %s)",
                            (weapon_id, legendary_perk_id)
                        )
                        if self.cursor.rowcount > 0:
                            legendary_links_created += 1
                    except Error as e:
                        print(f"  ✗ Error linking legendary perk '{perk_name}' to weapon '{weapon_name}': {e}")
                else:
                    perks_not_found.append(perk_name)

        if perks_not_found:
            print(f"  ⚠ Weapon '{weapon_name}': {len(perks_not_found)} perk(s) not found in any perk table:")
            for perk in perks_not_found:
                print(f"    - '{perk}'")

        if rules_created > 0:
            print(f"  ✓ Created {rules_created} conditional perk rules")

        return regular_links_created + legendary_links_created

    def _create_perk_rule(self, weapon_id: int, perk_id: int, conditions: Dict, weapon_name: str) -> int:
        """Create a weapon_perk_rules entry for conditional perk application."""
        # Map condition keys to database columns
        weapon_class = conditions.get('weapon_class', 'any')
        fire_mode = conditions.get('fire_mode', 'any')
        scope_state = conditions.get('scope_state', 'any')
        aim_state = conditions.get('aim_state', 'any')
        vats_state = conditions.get('vats_state', 'any')

        # Normalize weapon_class values
        if weapon_class in ['auto pistol', 'non-auto pistol']:
            weapon_class = 'pistol'

        # Create human-readable note
        note_parts = []
        for key, value in conditions.items():
            if key == 'weapon_class':
                note_parts.append(f"{value} mode")
            elif key == 'fire_mode':
                note_parts.append(f"{value} fire")
            elif key == 'scope_state':
                note_parts.append(value)
            elif key == 'aim_state':
                if value == 'ads':
                    note_parts.append("when aiming down sights")
                else:
                    note_parts.append(f"{value}")

        note = ", ".join(note_parts) if note_parts else None

        try:
            self.cursor.execute("""
                INSERT INTO weapon_perk_rules
                (weapon_id, perk_id, weapon_class, fire_mode, scope_state, aim_state, vats_state, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (weapon_id, perk_id, weapon_class, fire_mode, scope_state, aim_state, vats_state, note))

            return 1 if self.cursor.rowcount > 0 else 0

        except Error as e:
            print(f"  ✗ Error creating perk rule for weapon '{weapon_name}', perk_id {perk_id}: {e}")
            return 0

    def import_all(self, perks_csv: str = "data/input/Perks.csv",
                   legendary_perks_csv: str = "data/input/LegendaryPerks.csv",
                   weapons_csv: str = "data/input/human_corrected_weapons_clean.csv"):
        """Import all data: perks first, then weapons."""
        print("=" * 60)
        print("FALLOUT 76 DATABASE IMPORT")
        print("=" * 60)

        # Import regular perks first
        perks_count = self.import_perks(perks_csv)

        # Import legendary perks
        legendary_perks_count = self.import_legendary_perks(legendary_perks_csv)

        # Import weapons and link perks
        weapons_count = self.import_weapons(weapons_csv)

        print("\n" + "=" * 60)
        print("IMPORT COMPLETE")
        print("=" * 60)
        print(f"Total regular perks imported: {perks_count}")
        print(f"Total legendary perks imported: {legendary_perks_count}")
        print(f"Total weapons imported: {weapons_count}")

        # Show summary statistics
        self._show_summary()

    def _show_summary(self):
        """Display summary statistics."""
        print("\n=== Database Summary ===")

        # Count weapons
        self.cursor.execute("SELECT COUNT(*) FROM weapons")
        weapon_count = self.cursor.fetchone()[0]
        print(f"Weapons in database: {weapon_count}")

        # Count regular perks
        self.cursor.execute("SELECT COUNT(*) FROM perks")
        perk_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM perk_ranks")
        perk_rank_count = self.cursor.fetchone()[0]
        print(f"Regular perks in database: {perk_count} ({perk_rank_count} total ranks)")

        # Count legendary perks
        self.cursor.execute("SELECT COUNT(*) FROM legendary_perks")
        legendary_perk_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM legendary_perk_ranks")
        legendary_rank_count = self.cursor.fetchone()[0]
        print(f"Legendary perks in database: {legendary_perk_count} ({legendary_rank_count} total ranks)")

        # Count weapon-perk links
        self.cursor.execute("SELECT COUNT(*) FROM weapon_perks")
        link_count = self.cursor.fetchone()[0]
        print(f"Weapon → regular perk links: {link_count}")

        # Count weapon-legendary perk links
        self.cursor.execute("SELECT COUNT(*) FROM weapon_legendary_perk_effects")
        legendary_link_count = self.cursor.fetchone()[0]
        print(f"Weapon → legendary perk effects: {legendary_link_count}")

        # Count weapon perk rules (conditional)
        self.cursor.execute("SELECT COUNT(*) FROM weapon_perk_rules")
        rules_count = self.cursor.fetchone()[0]
        print(f"Weapon perk rules (conditional): {rules_count}")

        # Show weapons with no perks at all
        self.cursor.execute("""
            SELECT w.name
            FROM weapons w
            LEFT JOIN weapon_perks wp ON w.id = wp.weapon_id
            LEFT JOIN weapon_legendary_perk_effects wlpe ON w.id = wlpe.weapon_id
            WHERE wp.weapon_id IS NULL AND wlpe.weapon_id IS NULL
        """)
        weapons_no_perks = self.cursor.fetchall()
        if weapons_no_perks:
            print(f"\nWeapons with no perks (regular or legendary): {len(weapons_no_perks)}")
            for (weapon_name,) in weapons_no_perks:
                print(f"  - {weapon_name}")


def main():
    parser = argparse.ArgumentParser(
        description='Import Fallout 76 weapon and perk data into MySQL database'
    )
    parser.add_argument('-u', '--user',
                       default=os.getenv('MYSQL_USER') or os.getenv('DB_USER'),
                       help='MySQL username (or set MYSQL_USER/DB_USER env var)')
    parser.add_argument('-p', '--password',
                       default=os.getenv('MYSQL_PASS') or os.getenv('DB_PASSWORD'),
                       help='MySQL password (or set MYSQL_PASS/DB_PASSWORD env var)')
    parser.add_argument('-H', '--host',
                       default=os.getenv('MYSQL_HOST') or os.getenv('DB_HOST', 'localhost'),
                       help='MySQL host (default: localhost)')
    parser.add_argument('-d', '--database',
                       default=os.getenv('MYSQL_DB') or os.getenv('DB_NAME', 'f76'),
                       help='MySQL database name (default: f76)')
    parser.add_argument('--perks-csv',
                       default='data/input/perks.csv',
                       help='Path to perks CSV file (default: data/input/perks.csv)')
    parser.add_argument('--legendary-perks-csv',
                       default='data/input/legendary_perks.csv',
                       help='Path to legendary perks CSV file (default: data/input/legendary_perks.csv)')
    parser.add_argument('--weapons-csv',
                       default='data/input/weapons.csv',
                       help='Path to weapons CSV file (default: data/input/weapons.csv)')

    args = parser.parse_args()

    # Validate required arguments
    if not args.user or not args.password:
        print("✗ Error: MySQL username and password are required")
        print("  Either use -u/-p arguments or set MYSQL_USER/MYSQL_PASS (or DB_USER/DB_PASSWORD) environment variables")
        sys.exit(1)

    # Create importer and run
    importer = F76DatabaseImporter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        if importer.connect():
            importer.import_all(args.perks_csv, args.legendary_perks_csv, args.weapons_csv)
    except KeyboardInterrupt:
        print("\n✗ Import cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
