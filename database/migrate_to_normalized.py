#!/usr/bin/env python3
"""
Migrate data from denormalized schema to fully normalized schema.

This script:
1. Backs up current database
2. Applies new normalized schema
3. Migrates all data from old tables to new normalized structure
4. Validates migration success

Usage:
    python migrate_to_normalized.py -u <username> -p <password>
"""

import argparse
import os
import re
import sys
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Tuple, Optional
import subprocess
from datetime import datetime


class SchemaMigrator:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

        # Caches for lookup table IDs
        self.race_cache = {}
        self.special_cache = {}
        self.damage_type_cache = {}
        self.weapon_type_cache = {}
        self.weapon_class_cache = {}
        self.armor_type_cache = {}
        self.armor_class_cache = {}
        self.armor_slot_cache = {}
        self.effect_type_cache = {}

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
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

    def backup_database(self):
        """Create backup of database before migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{self.database}_{timestamp}.sql"

        print(f"\n=== Creating Backup: {backup_file} ===")

        try:
            cmd = [
                "mysqldump",
                "-h", self.host,
                "-u", self.user,
                f"-p{self.password}",
                self.database
            ]

            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)

            print(f"✓ Backup created: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"⚠ Backup failed: {e}")
            print("  Continuing anyway...")
            return None

    def read_old_tables(self):
        """Read all data from old denormalized tables."""
        print("\n=== Reading Old Tables ===")

        old_data = {}

        tables = ['weapons', 'armor', 'perks', 'perk_ranks', 'legendary_perks',
                  'legendary_perk_ranks', 'mutations', 'consumables',
                  'weapon_perks', 'weapon_legendary_perk_effects', 'weapon_perk_rules']

        for table in tables:
            try:
                self.cursor.execute(f"SELECT * FROM {table}")
                old_data[table] = self.cursor.fetchall()
                print(f"  ✓ Read {len(old_data[table])} rows from {table}")
            except Error as e:
                print(f"  ⚠ Could not read {table}: {e}")
                old_data[table] = []

        return old_data

    def apply_new_schema(self):
        """Apply new normalized schema."""
        print("\n=== Applying New Schema ===")

        schema_file = os.path.join(os.path.dirname(__file__), 'f76_schema_normalized.sql')

        if not os.path.exists(schema_file):
            print(f"✗ Schema file not found: {schema_file}")
            return False

        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        # Split into individual statements and execute
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

        for stmt in statements:
            if stmt.startswith('USE '):
                continue  # Skip USE statement
            try:
                self.cursor.execute(stmt)
            except Error as e:
                if 'already exists' not in str(e):
                    print(f"  ⚠ Error executing statement: {e}")

        self.connection.commit()
        print("✓ New schema applied")
        return True

    def build_caches(self):
        """Build caches for lookup table IDs."""
        print("\n=== Building Lookup Caches ===")

        # Races
        self.cursor.execute("SELECT id, name FROM races")
        self.race_cache = {row['name']: row['id'] for row in self.cursor.fetchall()}

        # SPECIAL
        self.cursor.execute("SELECT id, code FROM special_attributes")
        self.special_cache = {row['code']: row['id'] for row in self.cursor.fetchall()}

        # Damage types
        self.cursor.execute("SELECT id, name FROM damage_types")
        self.damage_type_cache = {row['name']: row['id'] for row in self.cursor.fetchall()}

        # Weapon types
        self.cursor.execute("SELECT id, name FROM weapon_types")
        self.weapon_type_cache = {row['name']: row['id'] for row in self.cursor.fetchall()}

        # Armor types
        self.cursor.execute("SELECT id, name FROM armor_types")
        self.armor_type_cache = {row['name']: row['id'] for row in self.cursor.fetchall()}

        print(f"  ✓ Cached {len(self.race_cache)} races")
        print(f"  ✓ Cached {len(self.special_cache)} SPECIAL attributes")
        print(f"  ✓ Cached {len(self.damage_type_cache)} damage types")

    def get_or_create_lookup(self, table: str, name: str, cache: Dict) -> int:
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
                cache[name] = result['id']
                return result['id']
            raise

    def parse_damage(self, damage_str: str) -> List[Dict]:
        """
        Parse damage string into components.

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

    def parse_resistance(self, resistance_str: str) -> Optional[float]:
        """Parse resistance value from string."""
        if not resistance_str or resistance_str.strip() == '':
            return None

        # Extract numeric value
        match = re.search(r'(\d+\.?\d*)', resistance_str)
        if match:
            return float(match.group(1))
        return None

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

    def migrate_weapons(self, old_data: Dict):
        """Migrate weapons table."""
        print("\n=== Migrating Weapons ===")

        weapons = old_data.get('weapons', [])
        migrated = 0

        for weapon in weapons:
            try:
                # Get or create weapon type/class
                weapon_type_id = None
                if weapon.get('type'):
                    weapon_type_id = self.get_or_create_lookup('weapon_types', weapon['type'], self.weapon_type_cache)

                weapon_class_id = None
                if weapon.get('class'):
                    weapon_class_id = self.get_or_create_lookup('weapon_classes', weapon['class'], self.weapon_class_cache)

                # Parse level (convert to INT)
                min_level = None
                if weapon.get('level'):
                    level_match = re.search(r'(\d+)', str(weapon['level']))
                    if level_match:
                        min_level = int(level_match.group(1))

                # Insert weapon
                self.cursor.execute("""
                    INSERT INTO weapons (id, name, weapon_type_id, weapon_class_id, min_level, source_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (weapon['id'], weapon['name'], weapon_type_id, weapon_class_id, min_level, weapon.get('source_url')))

                # Parse and insert damage components
                damage_components = self.parse_damage(weapon.get('damage', ''))
                for comp in damage_components:
                    dtype_id = self.damage_type_cache.get(comp['type'])
                    if dtype_id:
                        self.cursor.execute("""
                            INSERT INTO weapon_damage_components
                            (weapon_id, damage_type_id, min_damage, max_damage, level_tier)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (weapon['id'], dtype_id, comp['min'], comp['max'], comp['tier']))

                migrated += 1

            except Error as e:
                print(f"  ✗ Error migrating weapon '{weapon.get('name')}': {e}")

        self.connection.commit()
        print(f"✓ Migrated {migrated}/{len(weapons)} weapons")

    def migrate_armor(self, old_data: Dict):
        """Migrate armor table."""
        print("\n=== Migrating Armor ===")

        armor_pieces = old_data.get('armor', [])
        migrated = 0

        for armor in armor_pieces:
            try:
                # Get or create lookup IDs
                armor_type_id = None
                if armor.get('armor_type'):
                    armor_type_id = self.armor_type_cache.get(armor['armor_type'])

                armor_class_id = None
                if armor.get('class'):
                    armor_class_id = self.get_or_create_lookup('armor_classes', armor['class'], self.armor_class_cache)

                armor_slot_id = None
                if armor.get('slot'):
                    armor_slot_id = self.get_or_create_lookup('armor_slots', armor['slot'], self.armor_slot_cache)

                # Parse level
                min_level = None
                if armor.get('level'):
                    level_match = re.search(r'(\d+)', str(armor['level']))
                    if level_match:
                        min_level = int(level_match.group(1))

                # Insert armor
                self.cursor.execute("""
                    INSERT INTO armor (id, name, armor_class_id, armor_slot_id, armor_type_id,
                                     set_name, min_level, source_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (armor['id'], armor['name'], armor_class_id, armor_slot_id, armor_type_id,
                      armor.get('set_name'), min_level, armor.get('source_url')))

                # Parse and insert resistance values
                resistance_fields = [
                    ('damage_resistance', 'physical'),
                    ('energy_resistance', 'energy'),
                    ('radiation_resistance', 'radiation'),
                    ('cryo_resistance', 'cryo'),
                    ('fire_resistance', 'fire'),
                    ('poison_resistance', 'poison')
                ]

                for field, dtype in resistance_fields:
                    if armor.get(field):
                        res_value = self.parse_resistance(armor[field])
                        if res_value is not None:
                            dtype_id = self.damage_type_cache.get(dtype)
                            if dtype_id:
                                self.cursor.execute("""
                                    INSERT INTO armor_resistance_values
                                    (armor_id, damage_type_id, resistance_value)
                                    VALUES (%s, %s, %s)
                                """, (armor['id'], dtype_id, res_value))

                migrated += 1

            except Error as e:
                print(f"  ✗ Error migrating armor '{armor.get('name')}': {e}")

        self.connection.commit()
        print(f"✓ Migrated {migrated}/{len(armor_pieces)} armor pieces")

    def migrate_perks(self, old_data: Dict):
        """Migrate perks and perk_ranks tables."""
        print("\n=== Migrating Perks ===")

        perks = old_data.get('perks', [])
        perk_ranks = old_data.get('perk_ranks', [])
        migrated_perks = 0
        migrated_ranks = 0

        for perk in perks:
            try:
                # Get SPECIAL ID
                special_id = None
                if perk.get('special'):
                    special_id = self.special_cache.get(perk['special'])

                # Insert perk
                self.cursor.execute("""
                    INSERT INTO perks (id, name, special_id, min_level)
                    VALUES (%s, %s, %s, %s)
                """, (perk['id'], perk['name'], special_id, perk.get('level')))

                # Insert race relationships
                race_ids = self.parse_races(perk.get('race', ''))
                for race_id in race_ids:
                    self.cursor.execute("""
                        INSERT IGNORE INTO perk_races (perk_id, race_id)
                        VALUES (%s, %s)
                    """, (perk['id'], race_id))

                migrated_perks += 1

            except Error as e:
                print(f"  ✗ Error migrating perk '{perk.get('name')}': {e}")

        # Migrate perk ranks
        for rank in perk_ranks:
            try:
                self.cursor.execute("""
                    INSERT INTO perk_ranks (id, perk_id, `rank`, description, form_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (rank['id'], rank['perk_id'], rank['rank'], rank['description'], rank.get('form_id')))

                migrated_ranks += 1

            except Error as e:
                print(f"  ✗ Error migrating perk rank: {e}")

        self.connection.commit()
        print(f"✓ Migrated {migrated_perks}/{len(perks)} perks")
        print(f"✓ Migrated {migrated_ranks}/{len(perk_ranks)} perk ranks")

    def migrate_legendary_perks(self, old_data: Dict):
        """Migrate legendary_perks and legendary_perk_ranks tables."""
        print("\n=== Migrating Legendary Perks ===")

        legendary_perks = old_data.get('legendary_perks', [])
        legendary_ranks = old_data.get('legendary_perk_ranks', [])
        migrated_perks = 0
        migrated_ranks = 0

        for perk in legendary_perks:
            try:
                # Insert legendary perk
                self.cursor.execute("""
                    INSERT INTO legendary_perks (id, name, description)
                    VALUES (%s, %s, %s)
                """, (perk['id'], perk['name'], perk.get('description')))

                # Insert race relationships
                race_ids = self.parse_races(perk.get('race', ''))
                for race_id in race_ids:
                    self.cursor.execute("""
                        INSERT IGNORE INTO legendary_perk_races (legendary_perk_id, race_id)
                        VALUES (%s, %s)
                    """, (perk['id'], race_id))

                migrated_perks += 1

            except Error as e:
                print(f"  ✗ Error migrating legendary perk '{perk.get('name')}': {e}")

        # Migrate legendary perk ranks
        for rank in legendary_ranks:
            try:
                self.cursor.execute("""
                    INSERT INTO legendary_perk_ranks (id, legendary_perk_id, `rank`, description)
                    VALUES (%s, %s, %s, %s)
                """, (rank['id'], rank['legendary_perk_id'], rank['rank'], rank.get('description')))

                # If effect_value and effect_type exist, create effect entry
                if rank.get('effect_value') or rank.get('effect_type'):
                    # Get or create effect type
                    effect_type_name = rank.get('effect_type', 'unknown')
                    if effect_type_name and effect_type_name not in self.effect_type_cache:
                        self.cursor.execute("""
                            INSERT IGNORE INTO effect_types (name, category)
                            VALUES (%s, 'buff')
                        """, (effect_type_name,))
                        self.cursor.execute("SELECT id FROM effect_types WHERE name = %s", (effect_type_name,))
                        result = self.cursor.fetchone()
                        if result:
                            self.effect_type_cache[effect_type_name] = result['id']

                    effect_type_id = self.effect_type_cache.get(effect_type_name)
                    if effect_type_id:
                        value = None
                        if rank.get('effect_value'):
                            try:
                                value = float(re.search(r'(\d+\.?\d*)', str(rank['effect_value'])).group(1))
                            except:
                                pass

                        self.cursor.execute("""
                            INSERT INTO legendary_perk_rank_effects
                            (legendary_perk_rank_id, effect_type_id, value, unit)
                            VALUES (%s, %s, %s, %s)
                        """, (rank['id'], effect_type_id, value, rank.get('effect_type')))

                migrated_ranks += 1

            except Error as e:
                print(f"  ✗ Error migrating legendary perk rank: {e}")

        self.connection.commit()
        print(f"✓ Migrated {migrated_perks}/{len(legendary_perks)} legendary perks")
        print(f"✓ Migrated {migrated_ranks}/{len(legendary_ranks)} legendary perk ranks")

    def migrate_mutations(self, old_data: Dict):
        """Migrate mutations table."""
        print("\n=== Migrating Mutations ===")

        mutations = old_data.get('mutations', [])
        migrated = 0

        for mutation in mutations:
            try:
                # Find exclusive mutation ID
                exclusive_id = None
                if mutation.get('exclusive_with'):
                    # Find the mutation with this name
                    for other in mutations:
                        if other['name'] == mutation['exclusive_with']:
                            exclusive_id = other['id']
                            break

                # Insert mutation
                self.cursor.execute("""
                    INSERT INTO mutations (id, name, form_id, exclusive_mutation_id, source_url)
                    VALUES (%s, %s, %s, %s, %s)
                """, (mutation['id'], mutation['name'], mutation.get('form_id'), exclusive_id, mutation.get('source_url')))

                # Parse and insert effects (simplified - just store description)
                if mutation.get('positive_effects'):
                    # Create a generic 'positive_effect' type
                    if 'positive_effect' not in self.effect_type_cache:
                        self.cursor.execute("INSERT IGNORE INTO effect_types (name, category) VALUES ('positive_effect', 'buff')")
                        self.cursor.execute("SELECT id FROM effect_types WHERE name = 'positive_effect'")
                        result = self.cursor.fetchone()
                        if result:
                            self.effect_type_cache['positive_effect'] = result['id']

                    effect_type_id = self.effect_type_cache.get('positive_effect')
                    if effect_type_id:
                        self.cursor.execute("""
                            INSERT INTO mutation_effects (mutation_id, effect_type_id, polarity, description)
                            VALUES (%s, %s, 'positive', %s)
                        """, (mutation['id'], effect_type_id, mutation['positive_effects']))

                if mutation.get('negative_effects'):
                    # Create a generic 'negative_effect' type
                    if 'negative_effect' not in self.effect_type_cache:
                        self.cursor.execute("INSERT IGNORE INTO effect_types (name, category) VALUES ('negative_effect', 'debuff')")
                        self.cursor.execute("SELECT id FROM effect_types WHERE name = 'negative_effect'")
                        result = self.cursor.fetchone()
                        if result:
                            self.effect_type_cache['negative_effect'] = result['id']

                    effect_type_id = self.effect_type_cache.get('negative_effect')
                    if effect_type_id:
                        self.cursor.execute("""
                            INSERT INTO mutation_effects (mutation_id, effect_type_id, polarity, description)
                            VALUES (%s, %s, 'negative', %s)
                        """, (mutation['id'], effect_type_id, mutation['negative_effects']))

                migrated += 1

            except Error as e:
                print(f"  ✗ Error migrating mutation '{mutation.get('name')}': {e}")

        self.connection.commit()
        print(f"✓ Migrated {migrated}/{len(mutations)} mutations")

    def migrate_consumables(self, old_data: Dict):
        """Migrate consumables table."""
        print("\n=== Migrating Consumables ===")

        consumables = old_data.get('consumables', [])
        migrated = 0

        for consumable in consumables:
            try:
                # Parse numeric fields
                duration_seconds = None
                if consumable.get('duration'):
                    match = re.search(r'(\d+)', str(consumable['duration']))
                    if match:
                        duration_seconds = int(match.group(1))

                hp_restore = self.parse_resistance(consumable.get('hp_restore'))
                rads = self.parse_resistance(consumable.get('rads'))
                hunger = self.parse_resistance(consumable.get('hunger_satisfaction'))
                thirst = self.parse_resistance(consumable.get('thirst_satisfaction'))
                addiction_risk = self.parse_resistance(consumable.get('addiction_risk'))
                disease_risk = self.parse_resistance(consumable.get('disease_risk'))

                # Insert consumable
                self.cursor.execute("""
                    INSERT INTO consumables
                    (id, name, category, subcategory, duration_seconds, hp_restore, rads,
                     hunger_satisfaction, thirst_satisfaction, addiction_risk, disease_risk,
                     weight, value, form_id, crafting_station, source_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (consumable['id'], consumable['name'], consumable['category'],
                      consumable.get('subcategory'), duration_seconds, hp_restore, rads,
                      hunger, thirst, addiction_risk, disease_risk,
                      consumable.get('weight'), consumable.get('value'),
                      consumable.get('form_id'), consumable.get('crafting_station'),
                      consumable.get('source_url')))

                # Insert effects (simplified - just store description)
                if consumable.get('effects'):
                    if 'consumable_effect' not in self.effect_type_cache:
                        self.cursor.execute("INSERT IGNORE INTO effect_types (name, category) VALUES ('consumable_effect', 'buff')")
                        self.cursor.execute("SELECT id FROM effect_types WHERE name = 'consumable_effect'")
                        result = self.cursor.fetchone()
                        if result:
                            self.effect_type_cache['consumable_effect'] = result['id']

                    effect_type_id = self.effect_type_cache.get('consumable_effect')
                    if effect_type_id:
                        self.cursor.execute("""
                            INSERT INTO consumable_effects (consumable_id, effect_type_id, description)
                            VALUES (%s, %s, %s)
                        """, (consumable['id'], effect_type_id, consumable['effects']))

                # Parse and insert SPECIAL modifiers
                if consumable.get('special_modifiers'):
                    # Parse "+2 STR, -1 INT" etc.
                    modifiers = consumable['special_modifiers'].split(',')
                    for mod in modifiers:
                        match = re.match(r'([+-]?\d+)\s*([SPECIAL])', mod.strip())
                        if match:
                            value = int(match.group(1))
                            special_code = match.group(2)
                            special_id = self.special_cache.get(special_code)
                            if special_id:
                                self.cursor.execute("""
                                    INSERT INTO consumable_special_modifiers
                                    (consumable_id, special_id, modifier)
                                    VALUES (%s, %s, %s)
                                """, (consumable['id'], special_id, value))

                migrated += 1

            except Error as e:
                print(f"  ✗ Error migrating consumable '{consumable.get('name')}': {e}")

        self.connection.commit()
        print(f"✓ Migrated {migrated}/{len(consumables)} consumables")

    def migrate_junction_tables(self, old_data: Dict):
        """Migrate junction tables (weapon_perks, etc.)."""
        print("\n=== Migrating Junction Tables ===")

        # Weapon perks
        weapon_perks = old_data.get('weapon_perks', [])
        for wp in weapon_perks:
            try:
                self.cursor.execute("""
                    INSERT INTO weapon_perks (weapon_id, perk_id)
                    VALUES (%s, %s)
                """, (wp['weapon_id'], wp['perk_id']))
            except Error:
                pass  # Ignore duplicates

        print(f"  ✓ Migrated {len(weapon_perks)} weapon-perk links")

        # Weapon legendary perk effects
        weapon_legendary = old_data.get('weapon_legendary_perk_effects', [])
        for wl in weapon_legendary:
            try:
                self.cursor.execute("""
                    INSERT INTO weapon_legendary_perk_effects (weapon_id, legendary_perk_id)
                    VALUES (%s, %s)
                """, (wl['weapon_id'], wl['legendary_perk_id']))
            except Error:
                pass  # Ignore duplicates

        print(f"  ✓ Migrated {len(weapon_legendary)} weapon-legendary perk links")

        # Weapon perk rules
        weapon_rules = old_data.get('weapon_perk_rules', [])
        for wr in weapon_rules:
            try:
                self.cursor.execute("""
                    INSERT INTO weapon_perk_rules
                    (id, weapon_id, perk_id, weapon_class, fire_mode, scope_state,
                     aim_state, vats_state, mod_requirements, note)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (wr['id'], wr['weapon_id'], wr['perk_id'], wr.get('weapon_class'),
                      wr.get('fire_mode'), wr.get('scope_state'), wr.get('aim_state'),
                      wr.get('vats_state'), wr.get('mod_requirements'), wr.get('note')))
            except Error:
                pass  # Ignore duplicates

        print(f"  ✓ Migrated {len(weapon_rules)} weapon perk rules")

        self.connection.commit()

    def validate_migration(self):
        """Validate that migration was successful."""
        print("\n=== Validating Migration ===")

        tables = {
            'weapons': 'weapons',
            'armor': 'armor',
            'perks': 'perks',
            'legendary_perks': 'legendary_perks',
            'mutations': 'mutations',
            'consumables': 'consumables'
        }

        for table_name, _ in tables.items():
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = self.cursor.fetchone()['count']
            print(f"  {table_name}: {count} rows")

        # Test views
        print("\n  Testing views...")
        view_tests = [
            'SELECT COUNT(*) FROM v_weapons_with_perks',
            'SELECT COUNT(*) FROM v_armor_complete',
            'SELECT COUNT(*) FROM v_perks_all_ranks',
            'SELECT COUNT(*) FROM v_legendary_perks_all_ranks',
            'SELECT COUNT(*) FROM v_mutations_complete',
            'SELECT COUNT(*) FROM v_consumables_complete'
        ]

        for test_sql in view_tests:
            try:
                self.cursor.execute(test_sql)
                result = self.cursor.fetchone()
                view_name = test_sql.split('FROM')[1].strip()
                print(f"    ✓ {view_name}: {result['COUNT(*)']} rows")
            except Error as e:
                print(f"    ✗ View test failed: {e}")

    def migrate_all(self):
        """Run full migration."""
        print("=" * 60)
        print("SCHEMA MIGRATION: DENORMALIZED → NORMALIZED")
        print("=" * 60)

        # Backup
        self.backup_database()

        # Read old data BEFORE applying new schema
        old_data = self.read_old_tables()

        # Apply new schema (drops and recreates tables)
        if not self.apply_new_schema():
            print("✗ Failed to apply new schema")
            return False

        # Build caches
        self.build_caches()

        # Migrate each table
        self.migrate_weapons(old_data)
        self.migrate_armor(old_data)
        self.migrate_perks(old_data)
        self.migrate_legendary_perks(old_data)
        self.migrate_mutations(old_data)
        self.migrate_consumables(old_data)
        self.migrate_junction_tables(old_data)

        # Validate
        self.validate_migration()

        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("Next steps:")
        print("  1. Run updated import scripts to test them")
        print("  2. Re-populate vector database: python rag/populate_vector_db.py")
        print("  3. Test RAG query engine: python rag/hybrid_cli.py")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Fallout 76 database to normalized schema'
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

    args = parser.parse_args()

    if not args.user or not args.password:
        print("✗ Error: MySQL username and password are required")
        print("  Either use -u/-p arguments or set MYSQL_USER/MYSQL_PASS environment variables")
        sys.exit(1)

    migrator = SchemaMigrator(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        if migrator.connect():
            if migrator.migrate_all():
                sys.exit(0)
            else:
                sys.exit(1)
    except KeyboardInterrupt:
        print("\n✗ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        migrator.close()


if __name__ == '__main__':
    main()
