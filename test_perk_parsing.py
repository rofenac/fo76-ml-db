#!/usr/bin/env python3
"""Test the perk parsing logic to verify correctness."""

import csv
import re
from typing import List

def smart_comma_split(text: str) -> List[str]:
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

def parse_perks_field(perks_raw: str) -> List[str]:
    """
    Parse the perks_raw field into individual perk names.
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
        if ':' in section:
            # Split on colon and process the perk list part
            prefix, perk_list = section.split(':', 1)
            section = perk_list.strip()

        # Split on commas, but not commas inside parentheses
        perk_parts = smart_comma_split(section)

        for perk_part in perk_parts:
            if not perk_part:
                continue

            # Extract base perk name and variants
            perk_names = extract_perk_names(perk_part)
            perks.extend(perk_names)

    # Remove duplicates while preserving order
    seen = set()
    unique_perks = []
    for perk in perks:
        if perk not in seen:
            seen.add(perk)
            unique_perks.append(perk)

    return unique_perks

def extract_perk_names(perk_str: str) -> List[str]:
    """Extract perk name(s) from a string."""
    # Remove trailing conditions
    perk_str = re.sub(r'\s*\((?:scoped|sighted|unscoped|pistol|rifle)(?:\s+only)?\)\s*(?:only)?', '', perk_str, flags=re.IGNORECASE)
    perk_str = re.sub(r'\s+only\s*$', '', perk_str, flags=re.IGNORECASE)
    perk_str = perk_str.strip()

    # Check for variants in parentheses like "(Expert, Master)"
    variant_match = re.search(r'^(.+?)\s*\(([^)]+)\)$', perk_str)

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
                perk_names.append(f"{base_name} {variant.title()}")
                has_ranks = True

        # If we found rank variants, also include the base perk
        if has_ranks:
            perk_names.insert(0, base_name)
        else:
            # Not rank variants, just return the base name
            perk_names = [base_name]

        return perk_names
    else:
        # No variants, just return the perk name
        return [perk_str]


# Load canonical perk names
print("Loading canonical perk names from Perks.csv...")
canonical_perks = set()
with open('Perks.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        canonical_perks.add(row['name'].strip())

print(f"Loaded {len(canonical_perks)} canonical perks\n")

# Test with actual weapon data
print("=" * 80)
print("TESTING PERK PARSING WITH ACTUAL WEAPON DATA")
print("=" * 80)

with open('human_corrected_weapons_clean.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        weapon_name = row['Name']
        perks_raw = row['Perks']

        if not perks_raw:
            print(f"\n{weapon_name}: NO PERKS")
            continue

        print(f"\n{weapon_name}")
        print("-" * 80)
        print(f"Raw perks field:\n  {perks_raw}\n")

        # Parse perks
        parsed_perks = parse_perks_field(perks_raw)

        print(f"Parsed {len(parsed_perks)} perks:")

        valid_perks = []
        invalid_perks = []

        for perk in parsed_perks:
            if perk in canonical_perks:
                valid_perks.append(perk)
                print(f"  ✓ {perk}")
            else:
                invalid_perks.append(perk)
                print(f"  ✗ {perk} (NOT IN CANONICAL LIST)")

        print(f"\nSummary: {len(valid_perks)} valid, {len(invalid_perks)} invalid")

        if invalid_perks:
            print("\nInvalid perks that need attention:")
            for perk in invalid_perks:
                print(f"  - '{perk}'")

print("\n" + "=" * 80)
