#!/usr/bin/env python3
"""
Populate special_id foreign keys in perks table for 3NF compliance.

This script resolves the special CHAR(1) codes ('S', 'P', 'E', etc.) to
special_id foreign keys referencing the special_attributes table.

Usage:
    python database/populate_perk_fks.py
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.db_utils import get_db


def populate_special_attributes():
    """Populate special_attributes lookup table if empty."""
    db = get_db()

    # Check if already populated
    result = db.execute_query("SELECT COUNT(*) as count FROM special_attributes")
    count = result[0]['count'] if result else 0

    if count > 0:
        print(f"✓ special_attributes table already has {count} records")
        return count

    print("\nPopulating special_attributes lookup table...")

    special_data = [
        ('S', 'Strength'),
        ('P', 'Perception'),
        ('E', 'Endurance'),
        ('C', 'Charisma'),
        ('I', 'Intelligence'),
        ('A', 'Agility'),
        ('L', 'Luck')
    ]

    for code, name in special_data:
        try:
            db.execute_query(
                "INSERT INTO special_attributes (code, name) VALUES (%s, %s)",
                (code, name)
            )
        except Exception as e:
            print(f"  ⚠ Warning: Could not insert {code} ({name}): {e}")

    print(f"✓ Populated special_attributes with {len(special_data)} SPECIAL stats")
    return len(special_data)


def populate_special_fks():
    """
    Populate special_id FK in perks table by resolving special CHAR codes to IDs.
    Ensures proper 3NF compliance while maintaining backward-compatible CHAR field.
    """
    db = get_db()

    print("="*60)
    print("PERK FOREIGN KEY POPULATION")
    print("="*60)

    # First, ensure special_attributes is populated
    populate_special_attributes()

    print("\nPopulating special_id foreign keys...")

    # Get all perks with special codes
    perks = db.execute_query(
        "SELECT id, name, special FROM perks WHERE special IS NOT NULL"
    )

    if not perks:
        print("No perks found with special codes")
        return 0

    print(f"Found {len(perks)} perks to process")

    # Get special_attributes mapping
    special_attrs = db.execute_query("SELECT id, code, name FROM special_attributes")

    if not special_attrs:
        print("✗ ERROR: special_attributes table is still empty!")
        return 0

    # Build lookup map: code -> id
    special_map = {attr['code']: attr['id'] for attr in special_attrs}

    print(f"\nSpecial attribute mapping:")
    for code, attr_id in special_map.items():
        print(f"  {code} -> ID {attr_id}")

    updated_count = 0
    error_count = 0

    for perk in perks:
        perk_id = perk['id']
        perk_name = perk['name']
        special_code = perk['special']

        if special_code not in special_map:
            print(f"  ⚠ Warning: Unknown special code '{special_code}' for perk '{perk_name}'")
            error_count += 1
            continue

        special_id = special_map[special_code]

        try:
            db.execute_query(
                "UPDATE perks SET special_id = %s WHERE id = %s",
                (special_id, perk_id)
            )
            updated_count += 1
        except Exception as e:
            print(f"  ❌ ERROR updating perk '{perk_name}': {e}")
            error_count += 1

    print(f"\n✓ Successfully updated {updated_count} perks")
    if error_count > 0:
        print(f"⚠ Encountered {error_count} errors")

    return updated_count


def verify_fks():
    """Verify FK population"""
    db = get_db()

    print(f"\nVerification:")

    # Count perks with special codes
    result = db.execute_query(
        "SELECT COUNT(*) as count FROM perks WHERE special IS NOT NULL"
    )
    perks_with_special = result[0]['count'] if result else 0

    # Count perks with populated special_id FK
    result = db.execute_query(
        "SELECT COUNT(*) as count FROM perks WHERE special_id IS NOT NULL"
    )
    perks_with_fk = result[0]['count'] if result else 0

    # Verify consistency
    result = db.execute_query("""
        SELECT COUNT(*) as count
        FROM perks p
        JOIN special_attributes sa ON p.special_id = sa.id
        WHERE p.special = sa.code
    """)
    consistent_count = result[0]['count'] if result else 0

    print(f"  Perks with special code: {perks_with_special}")
    print(f"  Perks with special_id FK: {perks_with_fk}")
    print(f"  Consistent mappings: {consistent_count}")

    if perks_with_fk == perks_with_special == consistent_count:
        print(f"\n  ✅ 3NF Compliance: PERFECT!")
        print(f"     All {perks_with_special} perks have proper FK relationships")
    else:
        print(f"\n  ⚠ Some perks may have inconsistent FK mappings")

    # Show sample
    sample = db.execute_query("""
        SELECT p.name, p.special as code, sa.name as special_name
        FROM perks p
        JOIN special_attributes sa ON p.special_id = sa.id
        LIMIT 5
    """)

    if sample:
        print(f"\n  Sample perks (first 5):")
        for perk in sample:
            print(f"    {perk['name']:30} [{perk['code']}] -> {perk['special_name']}")


def main():
    try:
        # Populate FKs
        updated = populate_special_fks()

        # Verify
        verify_fks()

        print("\n" + "="*60)
        print("FK POPULATION COMPLETE")
        print("="*60)
        print(f"Updated perks: {updated}")
        print("="*60)

    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
