#!/usr/bin/env python3
"""
Import script for weapon mechanics into the F76 normalized database.

This script detects and populates special weapon mechanics like charge-up,
chain lightning, spin-up, explosive AOE, etc.

Usage:
    python import_weapon_mechanics.py -u <username> -p <password> [-H <host>] [-d <database>]

    Or use environment variables:
    export MYSQL_USER=your_username
    export MYSQL_PASS=your_password
    python import_weapon_mechanics.py
"""

import argparse
import os
import sys
from typing import Dict, List, Tuple, Optional
import mysql.connector
from mysql.connector import Error


class WeaponMechanicsImporter:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

        # Cache for mechanic type IDs
        self.mechanic_type_cache: Dict[str, int] = {}

        # Define mechanic detection rules
        self.mechanic_rules = self._initialize_mechanic_rules()

    def _initialize_mechanic_rules(self) -> List[Dict]:
        """
        Define rules for detecting weapon mechanics based on weapon name and properties.

        Returns a list of rule dictionaries with:
        - mechanic_type: The type of mechanic
        - weapon_names: List of weapon names that have this mechanic
        - weapon_name_patterns: List of regex patterns to match weapon names
        - numeric_value: Optional numeric value for the mechanic
        - numeric_value_2: Optional second numeric value
        - string_value: Optional string value
        - unit: Unit of measurement
        - notes: Description/notes about the mechanic
        """
        return [
            # Charge mechanics - Gauss weapons (NOT Gauss minigun - it only has spin-up)
            {
                'mechanic_type': 'charge',
                'weapon_names': ['Gauss rifle', 'Gauss shotgun', 'Gauss pistol'],
                'weapon_name_patterns': [],  # Don't use pattern to avoid catching Gauss minigun
                'numeric_value': 0.50,
                'unit': 'multiplier',
                'notes': 'Uncharged damage is 50% of listed damage. Fully charged is 100%.'
            },

            # Explosive AOE - Gauss rifle
            {
                'mechanic_type': 'explosive_aoe',
                'weapon_names': ['Gauss rifle'],
                'weapon_name_patterns': [],
                'string_value': 'explosive',
                'notes': 'Fires explosive projectile that deals AOE damage to clustered enemies'
            },

            # Chain lightning - Tesla rifle
            {
                'mechanic_type': 'chain_lightning',
                'weapon_names': ['Tesla rifle'],
                'weapon_name_patterns': [r'^Tesla\s+rifle'],
                'numeric_value': 0.65,
                'numeric_value_2': 0.35,
                'unit': 'multiplier',
                'notes': 'First chain target takes 65% damage, each successive target takes 35% less (second chain: 42.25%)'
            },

            # Spin-up - Minigun, Gatling weapons, and Pepper Shaker
            {
                'mechanic_type': 'spin_up',
                'weapon_names': ['Minigun', 'Gauss minigun', 'Gatling gun', 'Gatling laser', 'Gatling plasma', 'Ultracite Gatling laser', 'Pepper Shaker'],
                'weapon_name_patterns': [r'^Gatling\s+\w+', r'minigun$'],
                'notes': 'Requires a moment to spin up before firing'
            },

            # Charge with self-damage - Salvaged Assaultron head
            {
                'mechanic_type': 'charge_self_damage',
                'weapon_names': ['Salvaged Assaultron head'],
                'weapon_name_patterns': [r'Assaultron\s+head'],
                'notes': 'Charged by reloading repeatedly. Higher charges deal more damage but irradiate the user.'
            },

            # Explosive AOE - Heavy explosive weapons
            {
                'mechanic_type': 'explosive_aoe',
                'weapon_names': [
                    'Fat Man', 'Missile launcher', 'Auto grenade launcher',
                    'M79 grenade launcher', 'Hellstorm missile launcher',
                    'Tesla cannon'
                ],
                'weapon_name_patterns': [
                    r'grenade launcher', r'missile launcher', r'^Fat\s+Man$'
                ],
                'string_value': 'explosive',
                'notes': 'Fires explosive projectiles with area-of-effect damage'
            },
        ]

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"✓ Connected to MySQL database '{self.database}' at {self.host}")
            return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Database connection closed")

    def populate_mechanic_types(self):
        """Populate the weapon_mechanic_types lookup table."""
        print("\n=== Populating Weapon Mechanic Types ===")

        mechanic_types = [
            ('charge', 'Weapon can be charged to increase damage. Uncharged shots deal reduced damage.'),
            ('charge_self_damage', 'Weapon charges by reloading repeatedly and irradiates the user.'),
            ('chain_lightning', 'Weapon damage chains to nearby enemies with reduced damage per hop.'),
            ('spin_up', 'Weapon requires time to spin up before firing at full rate.'),
            ('explosive_aoe', 'Weapon deals area-of-effect explosive damage.'),
            ('trap_creation', 'Weapon creates damage traps on impact.'),
            ('beam_weapon', 'Weapon fires a continuous beam rather than projectiles.')
        ]

        for name, description in mechanic_types:
            try:
                self.cursor.execute("""
                    INSERT INTO weapon_mechanic_types (name, description)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE description = VALUES(description)
                """, (name, description))

                # Cache the ID
                self.cursor.execute("SELECT id FROM weapon_mechanic_types WHERE name = %s", (name,))
                result = self.cursor.fetchone()
                if result:
                    self.mechanic_type_cache[name] = result['id']

            except Error as e:
                print(f"✗ Error inserting mechanic type '{name}': {e}")

        self.connection.commit()
        print(f"✓ Populated {len(mechanic_types)} mechanic types")

    def get_weapon_id(self, weapon_name: str) -> Optional[int]:
        """Get weapon ID by name."""
        try:
            self.cursor.execute("SELECT id FROM weapons WHERE name = %s", (weapon_name,))
            result = self.cursor.fetchone()
            return result['id'] if result else None
        except Error as e:
            print(f"✗ Error fetching weapon ID for '{weapon_name}': {e}")
            return None

    def import_mechanics(self):
        """Import weapon mechanics based on detection rules."""
        print("\n=== Importing Weapon Mechanics ===")

        mechanics_added = 0
        mechanics_skipped = 0

        for rule in self.mechanic_rules:
            mechanic_type = rule['mechanic_type']
            mechanic_type_id = self.mechanic_type_cache.get(mechanic_type)

            if not mechanic_type_id:
                print(f"⚠ Mechanic type '{mechanic_type}' not found in cache, skipping...")
                continue

            # Process each weapon in the rule
            for weapon_name in rule.get('weapon_names', []):
                weapon_id = self.get_weapon_id(weapon_name)

                if not weapon_id:
                    print(f"  ⚠ Weapon '{weapon_name}' not found in database, skipping...")
                    mechanics_skipped += 1
                    continue

                try:
                    # Check if mechanic already exists
                    self.cursor.execute("""
                        SELECT id FROM weapon_mechanics
                        WHERE weapon_id = %s AND mechanic_type_id = %s
                    """, (weapon_id, mechanic_type_id))

                    if self.cursor.fetchone():
                        print(f"  • '{weapon_name}' already has '{mechanic_type}' mechanic")
                        mechanics_skipped += 1
                        continue

                    # Insert the mechanic
                    self.cursor.execute("""
                        INSERT INTO weapon_mechanics
                        (weapon_id, mechanic_type_id, numeric_value, numeric_value_2,
                         string_value, unit, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        weapon_id,
                        mechanic_type_id,
                        rule.get('numeric_value'),
                        rule.get('numeric_value_2'),
                        rule.get('string_value'),
                        rule.get('unit'),
                        rule.get('notes')
                    ))

                    print(f"  ✓ Added '{mechanic_type}' to '{weapon_name}'")
                    mechanics_added += 1

                except Error as e:
                    print(f"  ✗ Error adding mechanic to '{weapon_name}': {e}")
                    mechanics_skipped += 1

        self.connection.commit()
        print(f"\n✓ Added {mechanics_added} weapon mechanics")
        if mechanics_skipped > 0:
            print(f"  Skipped {mechanics_skipped} (already exist or weapon not found)")

    def verify_import(self):
        """Verify the imported mechanics."""
        print("\n=== Verification ===")

        try:
            # Count mechanics by type
            self.cursor.execute("""
                SELECT wmt.name, COUNT(*) as count
                FROM weapon_mechanics wm
                JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
                GROUP BY wmt.name
                ORDER BY count DESC
            """)

            results = self.cursor.fetchall()
            print("\nMechanics by type:")
            for row in results:
                print(f"  {row['name']:20s}: {row['count']:3d} weapons")

            # Show some examples
            print("\nExample: Gauss weapons with charge mechanic:")
            self.cursor.execute("""
                SELECT w.name, wm.numeric_value, wm.unit, wm.notes
                FROM v_weapons_with_mechanics vwm
                JOIN weapons w ON vwm.id = w.id
                JOIN weapon_mechanics wm ON w.id = wm.weapon_id
                JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
                WHERE wmt.name = 'charge' AND w.name LIKE 'Gauss%'
            """)

            results = self.cursor.fetchall()
            for row in results:
                print(f"  • {row['name']}: {row['numeric_value']} {row['unit']} - {row['notes'][:60]}...")

        except Error as e:
            print(f"✗ Error during verification: {e}")

    def run(self):
        """Main execution flow."""
        print("=" * 70)
        print("Fallout 76 Weapon Mechanics Importer")
        print("=" * 70)

        if not self.connect():
            return False

        try:
            self.populate_mechanic_types()
            self.import_mechanics()
            self.verify_import()

            print("\n" + "=" * 70)
            print("✓ Import completed successfully!")
            print("=" * 70)
            return True

        except Exception as e:
            print(f"\n✗ Import failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            self.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description='Import weapon mechanics into Fallout 76 database'
    )
    parser.add_argument('-H', '--host', default='localhost',
                        help='MySQL host (default: localhost)')
    parser.add_argument('-u', '--user',
                        default=os.getenv('MYSQL_USER'),
                        help='MySQL username (or set MYSQL_USER env var)')
    parser.add_argument('-p', '--password',
                        default=os.getenv('MYSQL_PASS'),
                        help='MySQL password (or set MYSQL_PASS env var)')
    parser.add_argument('-d', '--database', default='f76',
                        help='Database name (default: f76)')

    args = parser.parse_args()

    # Validate required arguments
    if not args.user:
        print("Error: MySQL username required (use -u or MYSQL_USER env var)")
        sys.exit(1)
    if not args.password:
        print("Error: MySQL password required (use -p or MYSQL_PASS env var)")
        sys.exit(1)

    # Create importer and run
    importer = WeaponMechanicsImporter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    success = importer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
