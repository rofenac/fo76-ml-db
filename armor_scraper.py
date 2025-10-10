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
    type: str = ""  # Light, Sturdy, Heavy, Outfit, etc.
    slot: str = ""  # Chest, Left Arm, Right Arm, Left Leg, Right Leg, Helmet
    armor_rating: str = ""
    energy_resistance: str = ""
    radiation_resistance: str = ""
    set_name: str = ""  # Armor set name
    level: str = ""
    weight: str = ""
    value: str = ""
    form_id: str = ""
    editor_id: str = ""
    perks_raw: str = ""
    source_url: str = ""

    def to_csv_dict(self) -> Dict[str, str]:
        """Convert to dict with correct CSV column names"""
        data = asdict(self)
        csv_data = {
            'Name': data['name'],
            'Type': data['type'],
            'Slot': data['slot'],
            'Armor Rating': data['armor_rating'],
            'Energy Resistance': data['energy_resistance'],
            'Radiation Resistance': data['radiation_resistance'],
            'Set Name': data['set_name'],
            'Level': data['level'],
            'Weight': data['weight'],
            'Value': data['value'],
            'Form ID': data['form_id'],
            'Editor ID': data['editor_id'],
            'Perks': data['perks_raw'],
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

        # Find the infobox
        infobox = soup.find('aside', class_='portable-infobox') or soup.find('table', class_='infobox')

        if not infobox:
            logger.warning(f"No infobox found for {set_name}")
            return pieces

        # Extract common data from infobox
        infobox_data = self._extract_infobox(infobox)

        # Extract perks
        perks_list = self._extract_perks(soup)
        perks_str = self._format_perks(perks_list)

        # Determine armor type from variants or description
        armor_type = infobox_data.get('type', '')

        # For armor sets with multiple pieces, create entries for each slot
        # Common slots: Chest, Helmet, Left Arm, Right Arm, Left Leg, Right Leg
        slots = ['Chest', 'Helmet', 'Left Arm', 'Right Arm', 'Left Leg', 'Right Leg']

        # If we have specific data for individual pieces, use it
        # Otherwise, create a single entry for the armor set
        if infobox_data.get('has_multiple_pieces'):
            for slot in slots:
                piece = ArmorData(
                    name=f"{set_name} {slot.lower()}",
                    type=armor_type,
                    slot=slot,
                    armor_rating=infobox_data.get('armor_rating', ''),
                    energy_resistance=infobox_data.get('energy_resistance', ''),
                    radiation_resistance=infobox_data.get('radiation_resistance', ''),
                    set_name=set_name,
                    level=infobox_data.get('level', ''),
                    weight=infobox_data.get('weight', ''),
                    value=infobox_data.get('value', ''),
                    form_id=infobox_data.get('form_id', ''),
                    editor_id=infobox_data.get('editor_id', ''),
                    perks_raw=perks_str,
                    source_url=url
                )
                pieces.append(piece)
        else:
            # Single piece or full set entry
            piece = ArmorData(
                name=set_name,
                type=armor_type,
                slot=infobox_data.get('slot', ''),
                armor_rating=infobox_data.get('armor_rating', ''),
                energy_resistance=infobox_data.get('energy_resistance', ''),
                radiation_resistance=infobox_data.get('radiation_resistance', ''),
                set_name=set_name,
                level=infobox_data.get('level', ''),
                weight=infobox_data.get('weight', ''),
                value=infobox_data.get('value', ''),
                form_id=infobox_data.get('form_id', ''),
                editor_id=infobox_data.get('editor_id', ''),
                perks_raw=perks_str,
                source_url=url
            )
            pieces.append(piece)

        return pieces

    def _extract_infobox(self, infobox: BeautifulSoup) -> Dict[str, str]:
        """Extract data from the armor infobox"""
        data = {}

        # Extract data rows
        rows = infobox.find_all(['tr', 'div'], class_=lambda x: x and ('pi-data' in x or 'infobox-data' in x))

        for row in rows:
            label_elem = row.find(['th', 'h3'], class_=lambda x: x and ('pi-data-label' in x or 'infobox-label' in x))
            value_elem = row.find(['td', 'div'], class_=lambda x: x and ('pi-data-value' in x or 'infobox-data' in x))

            if not label_elem or not value_elem:
                continue

            label = label_elem.get_text(strip=True).lower()
            value = value_elem.get_text(strip=True)

            # Map labels to data fields
            if 'type' in label or 'variant' in label:
                data['type'] = value
            elif 'armor' in label and 'rating' in label:
                data['armor_rating'] = value
            elif 'dr' in label or 'physical' in label:
                data['armor_rating'] = value
            elif 'energy' in label and 'resistance' in label:
                data['energy_resistance'] = value
            elif 'er' in label:
                data['energy_resistance'] = value
            elif 'radiation' in label and 'resistance' in label:
                data['radiation_resistance'] = value
            elif 'rr' in label:
                data['radiation_resistance'] = value
            elif 'level' in label:
                data['level'] = value
            elif 'weight' in label:
                data['weight'] = value
            elif 'value' in label:
                data['value'] = value
            elif 'form id' in label:
                form_id = re.search(r'([0-9A-Fa-f]{8})', value)
                if form_id:
                    data['form_id'] = form_id.group(1).upper()
            elif 'editor id' in label or 'base id' in label:
                editor_id = value.strip('"').strip("'")
                data['editor_id'] = editor_id
            elif 'slot' in label or 'piece' in label:
                data['slot'] = value

        # Check if this is a multi-piece armor set
        if 'chest' in data.get('slot', '').lower() or 'torso' in data.get('slot', '').lower():
            data['has_multiple_pieces'] = True

        return data

    def _extract_perks(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """Extract perks that affect this armor"""
        perks = []

        # Find the infobox
        infobox = soup.find('aside', class_='portable-infobox') or soup.find('table', class_='infobox')

        if infobox:
            # Look for perk categories in infobox
            perk_categories = ['Weight', 'Protection', 'Defense', 'Perks', 'Other']

            for category in perk_categories:
                h3_elements = infobox.find_all('h3', string=lambda x: x and x.strip() == category)

                for h3 in h3_elements:
                    parent = h3.find_parent('div', class_='pi-item')
                    if not parent:
                        continue

                    value_div = parent.find('div', class_='pi-data-value')
                    if not value_div:
                        continue

                    links = value_div.find_all('a')
                    for link in links:
                        perk_name = link.get_text(strip=True)
                        if perk_name and self._is_valid_perk(perk_name):
                            perks.append({'name': perk_name, 'condition': None})

        return perks

    def _is_valid_perk(self, perk_name: str) -> bool:
        """Check if perk name exists in canonical list"""
        if not self.canonical_perks:
            return True

        perk_clean = perk_name.strip()
        if perk_clean in self.canonical_perks:
            return True

        perk_clean = re.sub(r'\s+(only|bonus)$', '', perk_clean, flags=re.IGNORECASE)
        return perk_clean in self.canonical_perks

    def _format_perks(self, perks_list: List[Dict[str, any]]) -> str:
        """Format perks list to semicolon-separated string"""
        if not perks_list:
            return ""

        perk_names = [p['name'] for p in perks_list]
        return "; ".join(perk_names)

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
        fieldnames = ['Name', 'Type', 'Slot', 'Armor Rating', 'Energy Resistance',
                     'Radiation Resistance', 'Set Name', 'Level', 'Weight', 'Value',
                     'Form ID', 'Editor ID', 'Perks', 'Source URL']

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
    parser.add_argument('-o', '--output', default='armor_scraped.csv', help='Output CSV file')
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
