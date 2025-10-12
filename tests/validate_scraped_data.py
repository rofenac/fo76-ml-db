#!/usr/bin/env python3
"""
Validate scraped weapon data for quality and completeness
"""

import csv
import sys
from typing import List, Dict, Set
import pandas as pd


class DataValidator:
    """Validates scraped weapon data"""

    def __init__(self, perks_csv: str = "Perks.csv"):
        self.canonical_perks = self._load_canonical_perks(perks_csv)
        self.errors = []
        self.warnings = []

    def _load_canonical_perks(self, perks_csv: str) -> Set[str]:
        """Load canonical perk names"""
        try:
            df = pd.read_csv(perks_csv)
            return set(df['name'].str.strip())
        except Exception as e:
            print(f"Warning: Could not load perks CSV: {e}")
            return set()

    def validate_csv(self, csv_file: str) -> bool:
        """
        Validate a scraped weapons CSV file

        Returns True if validation passes, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Validating: {csv_file}")
        print(f"{'='*60}\n")

        self.errors = []
        self.warnings = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                weapons = list(reader)
        except Exception as e:
            print(f"❌ ERROR: Could not read CSV file: {e}")
            return False

        if not weapons:
            print("❌ ERROR: No weapons found in CSV")
            return False

        print(f"Found {len(weapons)} weapons\n")

        # Run validation checks
        for i, weapon in enumerate(weapons, 1):
            self._validate_weapon(weapon, i)

        # Print results
        self._print_results(weapons)

        return len(self.errors) == 0

    def _validate_weapon(self, weapon: Dict[str, str], index: int):
        """Validate a single weapon entry"""
        name = weapon.get('Name', f'Weapon #{index}')

        # Check required fields
        required_fields = ['Name', 'Form ID', 'Editor ID', 'Source URL']
        for field in required_fields:
            if not weapon.get(field):
                self.errors.append(f"{name}: Missing required field '{field}'")

        # Check Form ID format (8-digit hex)
        form_id = weapon.get('Form ID', '')
        if form_id and not self._is_valid_form_id(form_id):
            self.errors.append(f"{name}: Invalid Form ID format '{form_id}' (expected 8-digit hex)")

        # Check if perks field is populated
        perks = weapon.get('Perks', '')
        if not perks:
            self.warnings.append(f"{name}: No perks extracted")
        else:
            # Validate individual perks
            self._validate_perks(name, perks)

        # Check if level is populated
        if not weapon.get('Level'):
            self.warnings.append(f"{name}: Missing level information")

        # Check if type is populated
        if not weapon.get('Type'):
            self.warnings.append(f"{name}: Missing weapon type")

    def _is_valid_form_id(self, form_id: str) -> bool:
        """Check if Form ID is valid 8-digit hex"""
        if len(form_id) != 8:
            return False
        try:
            int(form_id, 16)
            return True
        except ValueError:
            return False

    def _validate_perks(self, weapon_name: str, perks_str: str):
        """Validate perks string"""
        if not self.canonical_perks:
            return  # Can't validate without canonical list

        # Split by semicolon and parse
        perk_parts = [p.strip() for p in perks_str.split(';') if p.strip()]

        for part in perk_parts:
            # Handle conditional perks (e.g., "scoped only: Sniper")
            if ':' in part:
                condition, perk_list = part.split(':', 1)
                perks_to_check = [p.strip() for p in perk_list.split(',')]
            else:
                perks_to_check = [part]

            for perk in perks_to_check:
                # Remove parenthetical conditions
                perk_clean = perk.split('(')[0].strip()

                if perk_clean and perk_clean not in self.canonical_perks:
                    # Check if it's a known variant
                    if not self._is_known_variant(perk_clean):
                        self.warnings.append(
                            f"{weapon_name}: Unknown perk '{perk_clean}'"
                        )

    def _is_known_variant(self, perk: str) -> bool:
        """Check if perk is a known variant (Expert, Master, etc.)"""
        known_variants = ['Expert', 'Master', 'Expert, Master']
        return perk in known_variants

    def _print_results(self, weapons: List[Dict[str, str]]):
        """Print validation results"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60 + "\n")

        # Count completeness
        complete_weapons = 0
        partial_weapons = 0

        for weapon in weapons:
            name = weapon.get('Name', 'Unknown')
            missing_count = sum(1 for field in ['Type', 'Level', 'Damage', 'Perks', 'Form ID', 'Editor ID']
                               if not weapon.get(field))

            if missing_count == 0:
                complete_weapons += 1
            elif missing_count < 4:
                partial_weapons += 1

        print(f"Total weapons: {len(weapons)}")
        print(f"Complete data: {complete_weapons} ({complete_weapons/len(weapons)*100:.1f}%)")
        print(f"Partial data:  {partial_weapons} ({partial_weapons/len(weapons)*100:.1f}%)")
        print(f"Incomplete:    {len(weapons) - complete_weapons - partial_weapons}")

        # Print errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n✅ No errors found")

        # Print warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:20]:  # Limit to first 20
                print(f"  - {warning}")
            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more")
        else:
            print("\n✅ No warnings")

        print("\n" + "="*60)

        # Final verdict
        if not self.errors:
            print("✅ VALIDATION PASSED")
            if self.warnings:
                print(f"   ({len(self.warnings)} warnings - review recommended)")
        else:
            print("❌ VALIDATION FAILED")
            print(f"   Fix {len(self.errors)} errors before importing")

        print("="*60 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Validate scraped weapon data')
    parser.add_argument('csv_file', help='CSV file to validate')
    parser.add_argument('--perks', default='Perks.csv', help='Path to canonical perks CSV')

    args = parser.parse_args()

    validator = DataValidator(perks_csv=args.perks)
    passed = validator.validate_csv(args.csv_file)

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
