#!/usr/bin/env python3
"""
Import script for Fallout 76 weapon and perk data into NORMALIZED MySQL database.

UPDATED FOR NORMALIZED SCHEMA - Use this instead of import_to_db.py

Usage:
    python import_to_db_normalized.py -u <username> -p <password> [-H <host>] [-d <database>]

    Or use environment variables:
    export MYSQL_USER=your_username
    export MYSQL_PASS=your_password
    python import_to_db_normalized.py
"""

import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Set, Tuple, Optional
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

        # Caches for lookup table IDs
        self.perk_id_cache: Dict[str, int] = {}
        self.legendary_perk_id_cache: Dict[str, int] = {}
        self.race_cache: Dict[str, int] = {}
        self.special_cache: Dict[str, int] = {}
        self.weapon_type_cache: Dict[str, int] = {}
        self.weapon_class_cache: Dict[str, int] = {}
        self.damage_type_cache: Dict[str, int] = {}

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

    def build_caches(self):
        """Build caches for lookup tables."""
        print("Building lookup caches...")

        # Races
        self.cursor.execute("SELECT id, name FROM races")
        self.race_cache = {name: race_id for race_id, name in self.cursor.fetchall()}

        # SPECIAL
        self.cursor.execute("SELECT id, code FROM special_attributes")
        self.special_cache = {code: special_id for special_id, code in self.cursor.fetchall()}

        # Damage types
        self.cursor.execute("SELECT id, name FROM damage_types")
        self.damage_type_cache = {name: dtype_id for dtype_id, name in self.cursor.fetchall()}

        # Weapon types
        self.cursor.execute("SELECT id, name FROM weapon_types")
        self.weapon_type_cache = {name: wtype_id for wtype_id, name in self.cursor.fetchall()}

        # Weapon classes
        self.cursor.execute("SELECT id, name FROM weapon_classes")
        self.weapon_class_cache = {name: wclass_id for wclass_id, name in self.cursor.fetchall()}

        print(f"  ✓ Cached {len(self.race_cache)} races")
        print(f"  ✓ Cached {len(self.special_cache)} SPECIAL attributes")
        print(f"  ✓ Cached {len(self.damage_type_cache)} damage types")

    def get_or_create_lookup(self, table: str, name: str, cache: Dict) -> Optional[int]:
        """Get or create lookup table entry."""
        if name in cache:
            return cache[name]

        try:
            self.cursor.execute(f"INSERT INTO {table} (name) VALUES (%s)", (name,))
            lookup_id = self.cursor.lastrowid
            cache[name] = lookup_id
            return lookup_id
        except Error:
            # Already exists, fetch it
            self.cursor.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
            result = self.cursor.fetchone()
            if result:
                cache[name] = result[0]
                return result[0]
            return None

    def parse_damage(self, damage_str: str) -> List[Dict]:
        """
        Parse damage string into components for weapon_damage_components table.

        Examples:
        - "51" -> [{'type': 'physical', 'min': 51, 'max': None, 'tier': None}]
        - "51 / 57 / 65 / 83" -> [{'type': 'physical', 'min': 51, 'tier': 1}, ...]
        - "30 + 10 energy" -> [{'type': 'physical', 'min': 30}, {'type': 'energy', 'min': 10}]
        """
        if not damage_str or damage_str.strip() == '':
            return []

        components = []

        # Check for multi-level damage (slashes)
        if ' / ' in damage_str:
            parts = damage_str.split(' / ')
            for tier, part in enumerate(parts, 1):
                val = self._parse_single_damage(part.strip())
                if val:
                    val['tier'] = tier
                    components.append(val)
        # Check for multi-type damage (plus signs)
        elif '+' in damage_str:
            parts = damage_str.split('+')
            for part in parts:
                val = self._parse_single_damage(part.strip())
                if val:
                    components.append(val)
        else:
            val = self._parse_single_damage(damage_str.strip())
            if val:
                components.append(val)

        return components

    def _parse_single_damage(self, damage_str: str) -> Optional[Dict]:
        """Parse single damage value."""
        # Match patterns like "51", "51-60", "30 energy", "10 radiation"
        match = re.match(r'(\d+\.?\d*)\s*-?\s*(\d+\.?\d*)?\s*(\w+)?', damage_str)
        if not match:
            return None

        min_val = float(match.group(1))
        max_val = float(match.group(2)) if match.group(2) else None
        dtype = match.group(3).lower() if match.group(3) else 'physical'

        # Normalize damage type names
        dtype_map = {
            'physical': 'physical',
            'energy': 'energy',
            'radiation': 'radiation',
            'rad': 'radiation',
            'fire': 'fire',
            'cryo': 'cryo',
            'poison': 'poison'
        }
        dtype = dtype_map.get(dtype, 'physical')

        return {
            'type': dtype,
            'min': min_val,
            'max': max_val,
            'tier': None
        }

    def parse_races(self, race_str: str) -> List[int]:
        """Parse race string into race IDs."""
        if not race_str or race_str.strip() == '':
            return []

        race_ids = []
        races = [r.strip() for r in race_str.split(',')]

        for race in races:
            if race in self.race_cache:
                race_ids.append(self.race_cache[race])

        return race_ids

    def import_perks(self, csv_file: str = "data/input/Perks.csv") -> int:
        """Import perks from CSV into normalized perks tables."""
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
                    special_code = row.get('special', '').strip() or None
                    special_id = self.special_cache.get(special_code) if special_code else None

                    perk_data[perk_name] = {
                        'special_id': special_id,
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
                    "INSERT INTO perks (name, special_id, min_level) VALUES (%s, %s, %s)",
                    (perk_name, data['special_id'], data['level'])
                )

                perk_id = self.cursor.lastrowid
                perks_inserted += 1

                # Insert race restrictions
                race_ids = self.parse_races(data['race'])
                for race_id in race_ids:
                    self.cursor.execute(
                        "INSERT IGNORE INTO perk_races (perk_id, race_id) VALUES (%s, %s)",
                        (perk_id, race_id)
                    )

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
        """Import legendary perks from CSV into normalized legendary_perks tables."""
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
                    "INSERT INTO legendary_perks (name, description) VALUES (%s, %s)",
                    (perk_name, base_description)
                )

                legendary_perk_id = self.cursor.lastrowid
                perks_inserted += 1

                # Insert race restrictions
                race_ids = self.parse_races(data['race'])
                for race_id in race_ids:
                    self.cursor.execute(
                        "INSERT IGNORE INTO legendary_perk_races (legendary_perk_id, race_id) VALUES (%s, %s)",
                        (legendary_perk_id, race_id)
                    )

                # Insert all ranks for this legendary perk
                for rank_data in data['ranks']:
                    self.cursor.execute(
                        """INSERT INTO legendary_perk_ranks
                           (legendary_perk_id, `rank`, description)
                           VALUES (%s, %s, %s)""",
                        (legendary_perk_id, rank_data['rank'], rank_data['description'])
                    )
                    rank_id = self.cursor.lastrowid
                    ranks_inserted += 1

                    # Insert effect data into legendary_perk_rank_effects if available
                    # Note: This is simplified - in production you'd want to parse effect_type
                    # and create proper effect_type entries
                    if rank_data['effect_value'] or rank_data['effect_type']:
                        # For now, skip effect normalization - can be added later
                        pass

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
        Parse the perks field into perk names with conditions.
        (Same as original - no changes needed)
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
                prefix, perk_list = section.split(':', 1)
                prefix_lower = prefix.strip().lower()
                if prefix_lower in ['pistol', 'rifle', 'heavy', 'melee', 'auto pistol', 'non-auto pistol']:
                    weapon_class_prefix = prefix_lower
                    section = perk_list.strip()

            perk_parts = self._smart_comma_split(section)

            for perk_part in perk_parts:
                if not perk_part:
                    continue

                perk_data = self._extract_perk_with_conditions(perk_part)

                for perk_name, conditions in perk_data:
                    if weapon_class_prefix:
                        conditions['weapon_class'] = weapon_class_prefix
                    perks.append((perk_name, conditions))

        # Remove duplicates while preserving order
        seen = set()
        unique_perks = []
        for perk_tuple in perks:
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
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        if current:
            parts.append(''.join(current).strip())

        return parts

    def _extract_perk_with_conditions(self, perk_str: str) -> List[Tuple[str, Dict]]:
        """Extract perk name(s) and conditions from a string."""
        conditions = {}

        # Extract conditions
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

        # Remove condition text
        clean_str = perk_str
        clean_str = re.sub(r'\s*\((?:scoped|sighted|unscoped|hip\s*fire|auto|semi|non-auto)(?:\s+only)?\)\s*', '', clean_str, flags=re.IGNORECASE)
        clean_str = re.sub(r'\s+only\s*$', '', clean_str, flags=re.IGNORECASE)
        clean_str = clean_str.strip()

        # Check for variants
        variant_match = re.search(r'^(.+?)\s*\(([^)]+)\)$', clean_str)

        if variant_match:
            base_name = variant_match.group(1).strip()
            variants_str = variant_match.group(2).strip()
            variants = [v.strip() for v in variants_str.split(',')]

            rank_variants = {'expert', 'master'}
            perk_names = []
            has_ranks = False

            for variant in variants:
                if variant.lower() in rank_variants:
                    perk_names.append((f"{base_name} {variant.title()}", conditions.copy()))
                    has_ranks = True

            if has_ranks:
                perk_names.insert(0, (base_name, conditions.copy()))
            else:
                perk_names = [(base_name, conditions.copy())]

            return perk_names
        else:
            return [(clean_str, conditions)]

    def import_weapons(self, csv_file: str = "data/input/human_corrected_weapons_clean.csv") -> int:
        """Import weapons from CSV into normalized weapons table."""
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

                # Get or create weapon type/class
                weapon_type_id = None
                if row.get('Type'):
                    weapon_type_id = self.get_or_create_lookup('weapon_types', row['Type'].strip(), self.weapon_type_cache)

                weapon_class_id = None
                if row.get('Class'):
                    weapon_class_id = self.get_or_create_lookup('weapon_classes', row['Class'].strip(), self.weapon_class_cache)

                # Parse level (convert to INT)
                min_level = None
                if row.get('Level'):
                    level_match = re.search(r'(\d+)', row['Level'])
                    if level_match:
                        min_level = int(level_match.group(1))

                try:
                    # Check if weapon exists
                    self.cursor.execute("SELECT id FROM weapons WHERE name = %s", (name,))
                    existing = self.cursor.fetchone()

                    if existing:
                        weapon_id = existing[0]
                        # Update existing weapon
                        self.cursor.execute("""
                            UPDATE weapons
                            SET weapon_type_id = %s, weapon_class_id = %s, min_level = %s, source_url = %s
                            WHERE id = %s
                        """, (weapon_type_id, weapon_class_id, min_level, row.get('Source URL'), weapon_id))
                        weapons_updated += 1
                    else:
                        # Insert new weapon
                        self.cursor.execute("""
                            INSERT INTO weapons (name, weapon_type_id, weapon_class_id, min_level, source_url)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (name, weapon_type_id, weapon_class_id, min_level, row.get('Source URL')))
                        weapon_id = self.cursor.lastrowid
                        weapons_inserted += 1

                    # Clear existing damage components
                    self.cursor.execute("DELETE FROM weapon_damage_components WHERE weapon_id = %s", (weapon_id,))

                    # Parse and insert damage components
                    damage_components = self.parse_damage(row.get('Damage', ''))
                    for comp in damage_components:
                        dtype_id = self.damage_type_cache.get(comp['type'])
                        if dtype_id:
                            self.cursor.execute("""
                                INSERT INTO weapon_damage_components
                                (weapon_id, damage_type_id, min_damage, max_damage, level_tier)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (weapon_id, dtype_id, comp['min'], comp['max'], comp['tier']))

                    # Parse and link perks
                    perks_raw = row.get('Perks', '')
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
        """Parse perks and create weapon_perks, weapon_legendary_perks, and weapon_perk_rules entries."""
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
        print("FALLOUT 76 DATABASE IMPORT (NORMALIZED SCHEMA)")
        print("=" * 60)

        # Build caches first
        self.build_caches()

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

        # Count weapon perk rules
        self.cursor.execute("SELECT COUNT(*) FROM weapon_perk_rules")
        rules_count = self.cursor.fetchone()[0]
        print(f"Weapon perk rules (conditional): {rules_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Import Fallout 76 weapon and perk data into normalized MySQL database'
    )
    parser.add_argument('-u', '--user',
                       default=os.getenv('MYSQL_USER'),
                       help='MySQL username (or set MYSQL_USER env var)')
    parser.add_argument('-p', '--password',
                       default=os.getenv('MYSQL_PASS'),
                       help='MySQL password (or set MYSQL_PASS env var)')
    parser.add_argument('-H', '--host',
                       default=os.getenv('MYSQL_HOST', 'localhost'),
                       help='MySQL host (default: localhost)')
    parser.add_argument('-d', '--database',
                       default=os.getenv('MYSQL_DB', 'f76'),
                       help='MySQL database name (default: f76)')
    parser.add_argument('--perks-csv',
                       default='data/input/Perks.csv',
                       help='Path to perks CSV file')
    parser.add_argument('--legendary-perks-csv',
                       default='data/input/LegendaryPerks.csv',
                       help='Path to legendary perks CSV file')
    parser.add_argument('--weapons-csv',
                       default='data/input/human_corrected_weapons_clean.csv',
                       help='Path to weapons CSV file')

    args = parser.parse_args()

    if not args.user or not args.password:
        print("✗ Error: MySQL username and password are required")
        print("  Either use -u/-p arguments or set MYSQL_USER/MYSQL_PASS environment variables")
        sys.exit(1)

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
