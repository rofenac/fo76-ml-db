#!/usr/bin/env python3
"""
Fallout 76 Legendary Effects Scraper

Scrapes legendary weapon and armor effects from Fallout Wiki.
"""

import re
import csv
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class LegendaryEffect:
    """Legendary effect data"""
    name: str
    category: str = 'Prefix'  # Prefix, Major, Minor, Additional
    star_level: int = 1
    item_type: str = 'weapon'  # weapon, armor, both
    description: str = ''
    effect_value: str = ''
    notes: str = ''
    form_id: str = ''
    source_url: str = ''
    condition_type: str = ''
    condition_description: str = ''

    def to_csv_dict(self) -> Dict[str, str]:
        """Convert to CSV dictionary"""
        return asdict(self)


class LegendaryEffectScraper:
    """Scraper for Fallout 76 legendary effects"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_effects(self, url: str) -> List[LegendaryEffect]:
        """Scrape legendary effects from a wiki page"""
        logger.info(f"Scraping effects from: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch: {e}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        effects = []

        # Determine item type from URL
        item_type = 'armor' if 'armor' in url.lower() else 'weapon'

        # Find all section headers (h2, h3, h4) and check their text
        all_headers = soup.find_all(['h2', 'h3', 'h4'])

        for section_header in all_headers:
            header_text = section_header.get_text(strip=True)

            # Check if this header indicates a star level
            if not re.search(r'(\d+[-\s]star|★+)', header_text, re.IGNORECASE):
                continue

            # Extract star level from header text
            star_level = self._extract_star_level(header_text)
            logger.debug(f"Found section: {header_text} (star level: {star_level})")

            # Find the next table after this header
            table = section_header.find_next('table')
            if not table:
                logger.debug(f"No table found after header: {header_text}")
                continue

            # Parse effect rows
            rows = table.find_all('tr')[1:]  # Skip header row
            logger.debug(f"Found {len(rows)} rows in table")

            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                effect = self._parse_effect_row(cells, url, star_level, item_type)
                if effect:
                    effects.append(effect)

        logger.info(f"Found {len(effects)} effects")
        return effects

    def _extract_star_level(self, header_text: str) -> int:
        """Extract star level from section header"""
        # Count star symbols
        star_count = header_text.count('★')
        if star_count > 0:
            return star_count

        # Look for numeric star level (e.g., "1-star", "2-star")
        match = re.search(r'(\d+)[-\s]?star', header_text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        return 1  # Default

    def _parse_effect_row(self, cells: List, source_url: str, star_level: int = 1, item_type: str = 'weapon') -> Optional[LegendaryEffect]:
        """Parse a single effect row"""
        try:
            # Common patterns:
            # [Name, Description, Notes, FormID]

            effect = LegendaryEffect(name='', source_url=source_url, star_level=star_level, item_type=item_type)

            # Try to identify which cell is which
            name_cell = cells[0]
            desc_cell = cells[1] if len(cells) > 1 else None
            notes_cell = cells[2] if len(cells) > 2 else None
            form_id_cell = cells[3] if len(cells) > 3 else None

            # Extract name
            name = name_cell.get_text(strip=True)
            if not name or len(name) < 2:
                return None

            # Clean up name (remove star indicators, parentheses, etc.)
            effect.name = re.sub(r'\s*[\*★]+\s*', '', name)
            effect.name = re.sub(r'\s*\([^)]+\)\s*$', '', effect.name).strip()

            # Extract description
            if desc_cell:
                effect.description = desc_cell.get_text(separator=' ', strip=True)

            # Extract notes
            if notes_cell:
                effect.notes = notes_cell.get_text(separator=' ', strip=True)

            # Extract form ID
            if form_id_cell:
                form_id = form_id_cell.get_text(strip=True)
                # Clean up form ID (remove spaces, convert to uppercase)
                if form_id and len(form_id) <= 8:
                    effect.form_id = form_id.upper().strip()

            # Extract effect value from description (e.g., "+50%", "up to 130%")
            if effect.description:
                value_match = re.search(r'(\+?\d+%|up to \+?\d+%)', effect.description, re.IGNORECASE)
                if value_match:
                    effect.effect_value = value_match.group(1)

            # Infer category from context
            effect.category = self._infer_category(effect.name, effect.description, effect.star_level)

            # Extract conditions (e.g., "at low health", "during the day")
            condition = self._extract_condition(effect.description)
            if condition:
                effect.condition_type = condition[0]
                effect.condition_description = condition[1]

            return effect

        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def _infer_category(self, name: str, description: str, star_level: int) -> str:
        """Infer effect category"""
        # Primary damage/survival effects are usually Prefix (1 star)
        prefix_keywords = ['bloodied', 'anti-armor', 'two shot', 'furious', 'instigating',
                          'junkies', 'quad', 'unyielding', 'vanguard', 'bolstering',
                          'chameleon', 'life saving', 'regenerating', 'weightless']

        major_keywords = ['explosive', 'faster fire rate', 'swing speed', 'limb damage',
                         'ap refresh', 'increased durability', 'sentinel', 'cavalier']

        minor_keywords = ['faster reload', 'reduced weight', 'vats', 'perception',
                         'agility', 'less damage', 'poison resistance', 'rad resistance']

        name_lower = name.lower()

        if any(kw in name_lower for kw in prefix_keywords):
            return 'Prefix'
        elif any(kw in name_lower or kw in description.lower() for kw in major_keywords):
            return 'Major'
        elif any(kw in name_lower or kw in description.lower() for kw in minor_keywords):
            return 'Minor'
        elif star_level >= 4:
            return 'Additional'

        # Default based on star level
        if star_level == 1:
            return 'Prefix'
        elif star_level == 2:
            return 'Major'
        elif star_level == 3:
            return 'Minor'
        else:
            return 'Additional'

    def _infer_item_type(self, name: str, description: str) -> str:
        """Infer if effect is for weapons, armor, or both"""
        armor_keywords = ['sentinel', 'cavalier', 'unyielding', 'vanguard', 'bolstering',
                         'chameleon', 'life saving', 'regenerating', 'weightless',
                         'damage resistance', 'energy resistance', 'rad resistance']

        weapon_keywords = ['damage', 'fire rate', 'explosive', 'bullets', 'ammo',
                          'limb damage', 'reload', 'recoil', 'accuracy', 'aim']

        text = f"{name} {description}".lower()

        is_armor = any(kw in text for kw in armor_keywords)
        is_weapon = any(kw in text for kw in weapon_keywords)

        if is_armor and not is_weapon:
            return 'armor'
        elif is_weapon and not is_armor:
            return 'weapon'
        else:
            return 'weapon'  # Default to weapon if unclear

    def _extract_condition(self, description: str) -> Optional[tuple]:
        """Extract condition type and description"""
        desc_lower = description.lower()

        conditions = [
            (r'(at|when|while|if).*low health', 'health_threshold', 'at low health'),
            (r'(at|during).*night', 'time_of_day', 'at night'),
            (r'(at|during).*day', 'time_of_day', 'during the day'),
            (r'in (v\.?a\.?t\.?s\.?|vats)', 'vats', 'in VATS'),
            (r'(while|when|if).*aiming', 'aiming', 'while aiming'),
            (r'(while|when|if).*standing still', 'movement', 'while standing still'),
            (r'(while|when|if).*not in combat', 'combat_state', 'while not in combat'),
            (r'target.*full health', 'target_health', 'target at full health'),
            (r'consecutive hit', 'consecutive_hits', 'consecutive hits on same target'),
        ]

        for pattern, cond_type, cond_desc in conditions:
            if re.search(pattern, desc_lower):
                return (cond_type, cond_desc)

        return None

    def scrape_from_urls_file(self, urls_file: str, output_csv: str):
        """Scrape effects from URLs in file"""
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        logger.info(f"Found {len(urls)} URLs to scrape")

        all_effects = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")
            effects = self.scrape_effects(url)
            all_effects.extend(effects)
            time.sleep(1)  # Rate limiting

        # Save to CSV
        if all_effects:
            self._save_to_csv(all_effects, output_csv)
            logger.info(f"Saved {len(all_effects)} legendary effects to {output_csv}")
        else:
            logger.error("No effects scraped successfully")

    def _save_to_csv(self, effects: List[LegendaryEffect], output_file: str):
        """Save effects to CSV"""
        if not effects:
            return

        fieldnames = list(effects[0].to_csv_dict().keys())

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for effect in effects:
                writer.writerow(effect.to_csv_dict())


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Fallout 76 legendary effects')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-f', '--file', default='legendary_effect_urls.txt', help='File with URLs to scrape')
    parser.add_argument('-o', '--output', default='legendary_effects_scraped.csv', help='Output CSV file')

    args = parser.parse_args()

    scraper = LegendaryEffectScraper()

    if args.url:
        effects = scraper.scrape_effects(args.url)
        if effects:
            scraper._save_to_csv(effects, args.output)
            print(f"\nScraped {len(effects)} effects")
            print(f"Saved to: {args.output}")
    else:
        scraper.scrape_from_urls_file(args.file, args.output)


if __name__ == '__main__':
    main()
