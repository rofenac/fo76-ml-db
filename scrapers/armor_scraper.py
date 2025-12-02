#!/usr/bin/env python3
"""
Fallout 76 Wiki Armor Scraper

Scrapes armor data from Fallout Wiki pages and outputs clean CSV data
for import into the f76 database.
"""

import re
import csv
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ArmorData:
    """Structured armor data matching database schema"""
    name: str
    class_type: str = ""  # Light, Sturdy, Heavy, Outfit, Underarmor, etc.
    slot: str = ""  # Chest, Left Arm, Right Arm, Left Leg, Right Leg, Helmet/Mask
    damage_resistance: str = ""
    energy_resistance: str = ""
    radiation_resistance: str = ""
    cryo_resistance: str = ""
    fire_resistance: str = ""
    poison_resistance: str = ""
    set_name: str = ""  # Armor set name
    level: str = ""
    source_url: str = ""

    def to_csv_dict(self) -> Dict[str, str]:
        """Convert to dict with correct CSV column names"""
        data = asdict(self)
        csv_data = {
            'Name': data['name'],
            'Class': data['class_type'],
            'Slot': data['slot'],
            'Damage Resistance': data['damage_resistance'],
            'Energy Resistance': data['energy_resistance'],
            'Radiation Resistance': data['radiation_resistance'],
            'Cryo Resistance': data['cryo_resistance'],
            'Fire Resistance': data['fire_resistance'],
            'Poison Resistance': data['poison_resistance'],
            'Set Name': data['set_name'],
            'Level': data['level'],
            'Source URL': data['source_url']
        }
        return csv_data


class FalloutArmorScraper:
    """Scraper for Fallout Wiki armor pages"""

    def __init__(self, perks_csv_path: str = "Perks.csv"):
        """Initialize scraper with canonical perk list"""
        self.canonical_perks = self._load_canonical_perks(perks_csv_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _load_canonical_perks(self, perks_csv_path: str) -> Set[str]:
        """Load canonical perk names from Perks.csv"""
        try:
            df = pd.read_csv(perks_csv_path)
            perks = set(df['name'].str.strip())
            logger.info(f"Loaded {len(perks)} canonical perks from {perks_csv_path}")
            return perks
        except Exception as e:
            logger.error(f"Failed to load perks CSV: {e}")
            return set()

    def scrape_armor(self, url: str, use_playwright: bool = False) -> List[ArmorData]:
        """
        Scrape armor data from a Fallout Wiki URL

        Returns list of ArmorData objects (one per slot: chest, arms, legs, helmet)
        """
        logger.info(f"Scraping: {url}")

        try:
            if use_playwright:
                html = self._fetch_with_playwright(url)
            else:
                html = self._fetch_with_requests(url)

            if not html:
                logger.error(f"Failed to fetch HTML from {url}")
                return []

            soup = BeautifulSoup(html, 'lxml')

            # Extract armor set name
            set_name = self._extract_name(soup, url)

            # Extract armor pieces from the page
            armor_pieces = self._extract_armor_pieces(soup, set_name, url)

            if armor_pieces:
                logger.info(f"Successfully scraped {len(armor_pieces)} pieces for {set_name}")
            else:
                logger.warning(f"No armor pieces found for {set_name}")

            return armor_pieces

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)
            return []

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch page HTML using requests"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Requests fetch failed: {e}")
            return None

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch page HTML using Playwright for JavaScript-heavy pages"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)
                html = page.content()
                browser.close()
                return html
        except PlaywrightTimeout:
            logger.error("Playwright timeout")
            return None
        except Exception as e:
            logger.error(f"Playwright fetch failed: {e}")
            return None

    def _extract_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract armor set name from page"""
        h1 = soup.find('h1', class_='page-header__title')
        if h1:
            name = h1.get_text(strip=True)
            # Remove parenthetical like "(Fallout 76)"
            name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
            return name.strip()

        # Fallback to URL-based name
        path = urlparse(url).path
        name = path.split('/')[-1].replace('_', ' ')
        return name

    def _extract_armor_pieces(self, soup: BeautifulSoup, set_name: str, url: str) -> List[ArmorData]:
        """Extract individual armor pieces from the page"""
        pieces = []

        # Extract piece-by-piece data from tables
        piece_data = self._extract_pieces_from_tables(soup)

        if piece_data:
            for piece_info in piece_data:
                piece = ArmorData(
                    name=f"{set_name} {piece_info.get('slot', '')}".strip(),
                    class_type=piece_info.get('class', ''),
                    slot=piece_info.get('slot', ''),
                    damage_resistance=piece_info.get('damage_resistance', ''),
                    energy_resistance=piece_info.get('energy_resistance', ''),
                    radiation_resistance=piece_info.get('radiation_resistance', ''),
                    cryo_resistance=piece_info.get('cryo_resistance', ''),
                    fire_resistance=piece_info.get('fire_resistance', ''),
                    poison_resistance=piece_info.get('poison_resistance', ''),
                    set_name=set_name,
                    level=piece_info.get('level', ''),
                    source_url=url
                )
                pieces.append(piece)
            logger.info(f"Extracted {len(pieces)} individual armor pieces from tables")
        else:
            # Fallback: Try infobox extraction (old method for sets without piece tables)
            infobox = soup.find('aside', class_='portable-infobox') or soup.find('table', class_='infobox')
            if infobox:
                infobox_data = self._extract_infobox(infobox, soup)
                variants = infobox_data.get('variants', [])

                if variants:
                    for variant in variants:
                        piece = ArmorData(
                            name=f"{set_name}",
                            class_type=variant.get('class', ''),
                            slot="",  # No slot info available
                            damage_resistance=variant.get('damage_resistance', ''),
                            energy_resistance=variant.get('energy_resistance', ''),
                            radiation_resistance=variant.get('radiation_resistance', ''),
                            set_name=set_name,
                            level=infobox_data.get('level', ''),
                            source_url=url
                        )
                        pieces.append(piece)
                logger.warning(f"No piece-level data found for {set_name}, using fallback extraction")

        return pieces

    def _extract_infobox(self, infobox: BeautifulSoup, soup: BeautifulSoup) -> Dict[str, any]:
        """Extract data from the armor infobox"""
        data = {}

        # Extract resistance data from horizontal groups (icons + values)
        horiz_groups = infobox.find_all('table', class_='pi-horizontal-group')

        for group in horiz_groups:
            rows = group.find_all('tr')
            if len(rows) < 2:
                continue

            # First row has icons/labels, second row has values
            label_row = rows[0]
            value_row = rows[1]

            label_cells = label_row.find_all(['th', 'td'])
            value_cells = value_row.find_all(['th', 'td'])

            if len(label_cells) != len(value_cells):
                continue

            for label_cell, value_cell in zip(label_cells, value_cells):
                # Check for image alt text (resistance icons)
                img = label_cell.find('img')
                if img:
                    alt_text = img.get('alt', '').lower()
                    value = value_cell.get_text(strip=True)

                    if 'physical' in alt_text or 'damage' in alt_text:
                        data['damage_resistance'] = value
                    elif 'energy' in alt_text:
                        data['energy_resistance'] = value
                    elif 'radiation' in alt_text:
                        data['radiation_resistance'] = value
                    elif 'cryo' in alt_text:
                        data['cryo_resistance'] = value
                    elif 'fire' in alt_text:
                        data['fire_resistance'] = value
                    elif 'poison' in alt_text:
                        data['poison_resistance'] = value

                # Check for text labels (Class, Value, Weight, etc.)
                else:
                    label = label_cell.get_text(strip=True).lower()
                    value = value_cell.get_text(strip=True)

                    if 'class' in label or 'variant' in label or 'type' in label:
                        data['class'] = value

        # Extract other data from labeled rows
        pi_items = infobox.find_all('div', class_='pi-item')

        for item in pi_items:
            label_elem = item.find('h3', class_='pi-data-label')
            value_elem = item.find('div', class_='pi-data-value')

            if not label_elem or not value_elem:
                continue

            label = label_elem.get_text(strip=True).lower()
            value = value_elem.get_text(strip=True)

            if 'level' in label:
                data['level'] = value

        # Check for variants table (Light, Sturdy, Heavy)
        variants = self._extract_variants_from_tables(soup)
        if variants:
            data['variants'] = variants

        return data

    def _extract_pieces_from_tables(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract individual armor pieces from data tables"""
        pieces = []

        # Look for tables with piece-by-piece stats
        tables = soup.find_all('table', class_=lambda x: x and ('va-table' in x or 'wikitable' in x or 'article-table' in x))

        for table in tables:
            # Get headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text(strip=True).lower())

            # Skip if this doesn't look like a piece table
            # Check for either explicit piece indicators OR "name" + resistance columns
            has_name = 'name' in headers
            has_resistance = any(keyword in ' '.join(headers) for keyword in ['physical', 'energy', 'dr', 'er', 'resistance'])

            if not (has_name and has_resistance):
                continue

            # Find column indices
            piece_col = slot_col = level_col = class_col = None
            dr_col = er_col = rr_col = cryo_col = fire_col = poison_col = None

            for i, header in enumerate(headers):
                h_lower = header.lower()
                if 'piece' in h_lower or 'slot' in h_lower or 'armor piece' in h_lower or h_lower == 'name':
                    piece_col = i
                elif 'level' in h_lower or 'lvl' in h_lower:
                    level_col = i
                elif 'class' in h_lower or 'variant' in h_lower or 'weight class' in h_lower:
                    class_col = i
                elif 'physical' in h_lower or ('dr' in h_lower and 'durability' not in h_lower):
                    dr_col = i
                elif 'energy' in h_lower or 'er' in h_lower:
                    er_col = i
                elif 'radiation' in h_lower or 'rr' in h_lower:
                    rr_col = i
                elif 'cryo' in h_lower:
                    cryo_col = i
                elif 'fire' in h_lower:
                    fire_col = i
                elif 'poison' in h_lower:
                    poison_col = i

            # Extract data rows
            for row in table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                piece_data = {}

                # Extract slot/piece name
                if piece_col is not None and piece_col < len(cells):
                    slot_text = cells[piece_col].get_text(strip=True)
                    piece_data['slot'] = self._normalize_slot_name(slot_text)

                # If no piece column, try to infer from first cell
                if not piece_data.get('slot') and len(cells) > 0:
                    first_cell = cells[0].get_text(strip=True)
                    if any(part in first_cell.lower() for part in ['chest', 'arm', 'leg', 'helmet', 'mask']):
                        piece_data['slot'] = self._normalize_slot_name(first_cell)

                # Skip if we couldn't determine the slot
                if not piece_data.get('slot'):
                    continue

                # Extract other data
                if level_col is not None and level_col < len(cells):
                    piece_data['level'] = cells[level_col].get_text(strip=True)
                if class_col is not None and class_col < len(cells):
                    piece_data['class'] = cells[class_col].get_text(strip=True)
                if dr_col is not None and dr_col < len(cells):
                    piece_data['damage_resistance'] = cells[dr_col].get_text(strip=True)
                if er_col is not None and er_col < len(cells):
                    piece_data['energy_resistance'] = cells[er_col].get_text(strip=True)
                if rr_col is not None and rr_col < len(cells):
                    piece_data['radiation_resistance'] = cells[rr_col].get_text(strip=True)
                if cryo_col is not None and cryo_col < len(cells):
                    piece_data['cryo_resistance'] = cells[cryo_col].get_text(strip=True)
                if fire_col is not None and fire_col < len(cells):
                    piece_data['fire_resistance'] = cells[fire_col].get_text(strip=True)
                if poison_col is not None and poison_col < len(cells):
                    piece_data['poison_resistance'] = cells[poison_col].get_text(strip=True)

                pieces.append(piece_data)

        return pieces

    def _normalize_slot_name(self, slot_text: str) -> str:
        """Normalize slot names to standard format"""
        slot_lower = slot_text.lower()

        if 'chest' in slot_lower or 'torso' in slot_lower:
            return "Chest"
        elif 'left arm' in slot_lower:
            return "Left Arm"
        elif 'right arm' in slot_lower:
            return "Right Arm"
        elif 'left leg' in slot_lower:
            return "Left Leg"
        elif 'right leg' in slot_lower:
            return "Right Leg"
        elif 'helmet' in slot_lower or 'mask' in slot_lower or 'head' in slot_lower:
            return "Helmet"
        else:
            return slot_text  # Return as-is if we can't identify

    def _extract_variants_from_tables(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract armor variants (Light, Sturdy, Heavy) from data tables - deprecated, kept for fallback"""
        variants = []

        tables = soup.find_all('table', class_=lambda x: x and ('va-table' in x or 'wikitable' in x or 'article-table' in x))

        for table in tables:
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text(strip=True).lower())

            if not any(keyword in ' '.join(headers) for keyword in ['variant', 'type', 'dr', 'damage', 'resistance']):
                continue

            variant_col = dr_col = er_col = rr_col = cryo_col = fire_col = poison_col = None

            for i, header in enumerate(headers):
                if 'variant' in header or 'type' in header or 'class' in header:
                    variant_col = i
                elif 'dr' in header or 'damage' in header:
                    dr_col = i
                elif 'er' in header or 'energy' in header:
                    er_col = i
                elif 'rr' in header or 'radiation' in header:
                    rr_col = i
                elif 'cryo' in header:
                    cryo_col = i
                elif 'fire' in header:
                    fire_col = i
                elif 'poison' in header:
                    poison_col = i

            for row in table.find_all('tr')[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                variant_data = {}

                if variant_col is not None and variant_col < len(cells):
                    variant_data['class'] = cells[variant_col].get_text(strip=True)
                if dr_col is not None and dr_col < len(cells):
                    variant_data['damage_resistance'] = cells[dr_col].get_text(strip=True)
                if er_col is not None and er_col < len(cells):
                    variant_data['energy_resistance'] = cells[er_col].get_text(strip=True)
                if rr_col is not None and rr_col < len(cells):
                    variant_data['radiation_resistance'] = cells[rr_col].get_text(strip=True)
                if cryo_col is not None and cryo_col < len(cells):
                    variant_data['cryo_resistance'] = cells[cryo_col].get_text(strip=True)
                if fire_col is not None and fire_col < len(cells):
                    variant_data['fire_resistance'] = cells[fire_col].get_text(strip=True)
                if poison_col is not None and poison_col < len(cells):
                    variant_data['poison_resistance'] = cells[poison_col].get_text(strip=True)

                if variant_data.get('class'):
                    variants.append(variant_data)

        return variants

    def scrape_urls_from_file(self, urls_file: str, output_csv: str, use_playwright: bool = False):
        """Scrape multiple armor URLs and save to CSV"""
        # Read URLs
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        logger.info(f"Found {len(urls)} URLs to scrape")

        # Scrape each URL
        all_armor_pieces = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")
            pieces = self.scrape_armor(url, use_playwright=use_playwright)
            all_armor_pieces.extend(pieces)

        # Save to CSV
        if all_armor_pieces:
            self._save_to_csv(all_armor_pieces, output_csv)
            logger.info(f"Saved {len(all_armor_pieces)} armor pieces to {output_csv}")
        else:
            logger.error("No armor pieces scraped successfully")

    def _save_to_csv(self, armor_pieces: List[ArmorData], output_file: str):
        """Save armor data to CSV"""
        fieldnames = ['Name', 'Class', 'Slot', 'Damage Resistance', 'Energy Resistance',
                     'Radiation Resistance', 'Cryo Resistance', 'Fire Resistance',
                     'Poison Resistance', 'Set Name', 'Level', 'Source URL']

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for piece in armor_pieces:
                writer.writerow(piece.to_csv_dict())


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Fallout 76 armor data from Wiki')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-f', '--file', default='armor_urls.txt', help='File with URLs to scrape')
    parser.add_argument('-o', '--output', default='data/input/armor.csv', help='Output CSV file')
    parser.add_argument('-p', '--playwright', action='store_true', help='Use Playwright for JS pages')
    parser.add_argument('--perks', default='Perks.csv', help='Path to canonical perks CSV')

    args = parser.parse_args()

    scraper = FalloutArmorScraper(perks_csv_path=args.perks)

    if args.url:
        # Scrape single URL
        pieces = scraper.scrape_armor(args.url, use_playwright=args.playwright)
        if pieces:
            scraper._save_to_csv(pieces, args.output)
            print(f"\nScraped {len(pieces)} armor pieces")
            print(f"Saved to: {args.output}")
    else:
        # Scrape from file
        scraper.scrape_urls_from_file(args.file, args.output, use_playwright=args.playwright)


if __name__ == '__main__':
    main()
