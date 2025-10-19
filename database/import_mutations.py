#!/usr/bin/env python3
"""
Import mutations from Mutations.csv into MySQL database

Usage:
    python import_mutations.py
"""

import csv
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'database': os.getenv('DB_NAME', 'f76')
}

# File paths
MUTATIONS_CSV = 'data/input/Mutations.csv'


def import_mutations():
    """Import mutations from CSV"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Read mutations CSV
    with open(MUTATIONS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mutations = list(reader)

    print(f"\nImporting {len(mutations)} mutations...")

    insert_sql = """
        INSERT INTO mutations (name, positive_effects, negative_effects, form_id, exclusive_with, source_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            positive_effects = VALUES(positive_effects),
            negative_effects = VALUES(negative_effects),
            form_id = VALUES(form_id),
            exclusive_with = VALUES(exclusive_with),
            source_url = VALUES(source_url)
    """

    imported_count = 0
    for mutation in mutations:
        try:
            cursor.execute(insert_sql, (
                mutation['name'],
                mutation['positive_effects'],
                mutation['negative_effects'],
                mutation['form_id'] or None,
                mutation['exclusive_with'] or None,
                mutation['source_url']
            ))
            imported_count += 1
        except Exception as e:
            print(f"ERROR importing {mutation['name']}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✓ Successfully imported {imported_count}/{len(mutations)} mutations")
    return imported_count


def verify_import():
    """Verify mutations were imported correctly"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as count FROM mutations")
    result = cursor.fetchone()
    total_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM mutations WHERE exclusive_with != ''")
    result = cursor.fetchone()
    exclusive_count = result['count']

    cursor.execute("SELECT name, exclusive_with FROM mutations WHERE exclusive_with != ''")
    exclusive_mutations = cursor.fetchall()

    cursor.close()
    conn.close()

    print(f"\nVerification:")
    print(f"  Total mutations: {total_count}")
    print(f"  Exclusive mutations: {exclusive_count}")
    if exclusive_mutations:
        print(f"  Exclusivity pairs:")
        for m in exclusive_mutations:
            print(f"    - {m['name']} <-> {m['exclusive_with']}")

    return total_count


def main():
    print("="*60)
    print("MUTATION IMPORT SCRIPT")
    print("="*60)

    try:
        # Import mutations
        imported = import_mutations()

        # Verify
        total = verify_import()

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Mutations in database: {total}")
        print("="*60)

    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
        print(f"Make sure {MUTATIONS_CSV} exists")
        exit(1)
    except mysql.connector.Error as e:
        print(f"\nDATABASE ERROR: {e}")
        exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
