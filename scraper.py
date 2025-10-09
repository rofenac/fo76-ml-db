#!/usr/bin/env python3
"""
Fallout 76 Wiki Weapon Scraper

Scrapes weapon data from Fallout Wiki pages and outputs clean CSV data
matching the format in human_corrected_weapons_clean.csv
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
class WeaponData:
    """Structured weapon data matching CSV format"""
    name: str
    type: str = ""
    class_: str = ""  # 'class' is a reserved keyword
    level: str = ""
    damage: str = ""
    projectile: str = ""
    perks: str = ""
    form_id: str = ""
    editor_id: str = ""
    source_url: str = ""

    def to_csv_dict(self) -> Dict[str, str]:
        """Convert to dict with correct CSV column names"""
        data = asdict(self)
        # Map internal field names to CSV column names
        csv_data = {
            'Name': data['name'],
            'Type': data['type'],
            'Class': data['class_'],
            'Level': data['level'],
            'Damage': data['damage'],
            'Projectile': data['projectile'],
            'Perks': data['perks'],
            'Form ID': data['form_id'],
            'Editor ID': data['editor_id'],
            'Source URL': data['source_url']
        }
        return csv_data


class FalloutWikiScraper:
    """Scraper for Fallout Wiki weapon pages"""

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

    def scrape_weapon(self, url: str, use_playwright: bool = False) -> Optional[WeaponData]:
        """
        Scrape weapon data from a Fallout Wiki URL

        Args:
            url: Fallout Wiki weapon page URL
            use_playwright: Use Playwright for JavaScript-heavy pages

        Returns:
            WeaponData object or None if scraping failed
        """
        logger.info(f"Scraping: {url}")

        try:
            if use_playwright:
                html = self._fetch_with_playwright(url)
            else:
                html = self._fetch_with_requests(url)

            if not html:
                logger.error(f"Failed to fetch HTML from {url}")
                return None

            soup = BeautifulSoup(html, 'lxml')

            # Extract weapon data
            weapon = WeaponData(
                name=self._extract_name(soup, url),
                source_url=url
            )

            # Extract from infobox
            infobox_data = self._extract_infobox(soup)
            weapon.type = infobox_data.get('type', 'Ranged')
            weapon.class_ = infobox_data.get('class', '')
            weapon.level = infobox_data.get('level', '')
            weapon.damage = infobox_data.get('damage', '')
            weapon.projectile = infobox_data.get('projectile', '')
            weapon.form_id = infobox_data.get('form_id', '')
            weapon.editor_id = infobox_data.get('editor_id', '')

            # Extract perks
            perks_list = self._extract_perks(soup)
            weapon.perks = self._format_perks(perks_list)

            logger.info(f"Successfully scraped: {weapon.name}")
            return weapon

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)
            return None

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
        """Extract weapon name from page"""
        # Try h1 page title
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

    def _extract_infobox(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract data from the weapon infobox"""
        data = {}

        # Find the infobox (usually has class 'infobox' or 'portable-infobox')
        infobox = soup.find('aside', class_='portable-infobox') or soup.find('table', class_='infobox')

        if not infobox:
            logger.warning("No infobox found on page")
            return data

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
            if 'type' in label and 'weapon' in label:
                data['type'] = value
            elif 'class' in label:
                data['class'] = value
            elif 'level' in label:
                data['level'] = value
            elif 'damage' in label and 'form' not in label:
                data['damage'] = value
            elif 'projectile' in label:
                data['projectile'] = value
            elif 'form id' in label or 'form_id' in label:
                # Clean Form ID - keep only the hex value
                form_id = re.search(r'([0-9A-Fa-f]{8})', value)
                if form_id:
                    data['form_id'] = form_id.group(1).upper()
            elif 'editor id' in label or 'editor_id' in label or 'base id' in label:
                # Editor ID might have quotes or extra formatting
                editor_id = value.strip('"').strip("'")
                data['editor_id'] = editor_id

        return data

    def _extract_perks(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract perks that affect this weapon

        Returns list of dicts with 'name' and optional 'conditions'
        """
        perks = []

        # Find the infobox - perks are usually in there
        infobox = soup.find('aside', class_='portable-infobox') or soup.find('table', class_='infobox')

        if infobox:
            # Extract perks from infobox categories
            perks_from_infobox = self._extract_perks_from_infobox(infobox)
            if perks_from_infobox:
                perks.extend(perks_from_infobox)
                return perks

        # Fallback: Look for traditional perks section
        perk_headings = [
            'Perks that affect this weapon',
            'Weapon perks',
            'Applicable perks',
            'Related perks'
        ]

        perk_section = None
        for heading_text in perk_headings:
            heading = soup.find(['h2', 'h3'], string=re.compile(heading_text, re.IGNORECASE))
            if heading:
                perk_section = heading
                break

        if not perk_section:
            logger.warning("No perks section found")
            return perks

        # Find content after heading - usually a list
        content = perk_section.find_next(['ul', 'ol', 'div', 'table'])

        if not content:
            logger.warning("No perk content found after heading")
            return perks

        # Extract perks from list items
        if content.name in ['ul', 'ol']:
            items = content.find_all('li', recursive=False)
            for item in items:
                perk_data = self._parse_perk_item(item.get_text())
                if perk_data:
                    perks.extend(perk_data)

        # Extract from tables
        elif content.name == 'table':
            rows = content.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    # Look for perk links
                    links = cell.find_all('a')
                    for link in links:
                        perk_name = link.get_text(strip=True)
                        if perk_name and self._is_valid_perk(perk_name):
                            perks.append({'name': perk_name, 'condition': None})

        return perks

    def _extract_perks_from_infobox(self, infobox: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract perks from infobox perk categories

        Perks are organized in categories like:
        - Damage (perks that increase damage)
        - Legendary
        - Sneak
        - Penetration
        - Weight
        - Other
        """
        perks = []

        # Common perk category headings
        perk_categories = ['Damage', 'Legendary', 'Sneak', 'Penetration', 'Weight', 'Other']

        for category in perk_categories:
            # Find all h3 with this text (there may be duplicates, e.g., "Damage" for stats and perks)
            h3_elements = infobox.find_all('h3', string=lambda x: x and x.strip() == category)

            for h3 in h3_elements:
                parent = h3.find_parent('div', class_='pi-item')
                if not parent:
                    continue

                value_div = parent.find('div', class_='pi-data-value')
                if not value_div:
                    continue

                # Check if this contains perks (has links) or just stats (numbers only)
                links = value_div.find_all('a')
                if not links:
                    # No perk links, probably just stats
                    continue

                # Get the raw text to parse structure
                raw_text = value_div.get_text(separator='|', strip=True)

                # Parse the perks from this category
                category_perks = self._parse_infobox_perk_category(value_div, category)
                perks.extend(category_perks)

        return perks

    def _parse_infobox_perk_category(self, value_div: BeautifulSoup, category: str) -> List[Dict[str, any]]:
        """
        Parse perks from an infobox category value div

        Examples:
        - "Bloody Mess"
        - "Packin' Light (pistol only) Arms Keeper (rifle only)"
        - "Gunsmith · Quick Hands · Sniper (scoped only) Pistol: Gun Runner ..."
        """
        perks = []

        # Get all text nodes and links in order
        raw_text = value_div.get_text(separator=' ', strip=True)

        # Extract all perk links (these are the actual perks)
        links = value_div.find_all('a')

        # Track which text we've seen to understand context
        full_text = value_div.get_text()

        for link in links:
            perk_name = link.get_text(strip=True)

            # Skip non-perk links (like "Expert", "Master" standalone)
            if perk_name in ['Expert', 'Master'] and self._is_variant_modifier(link, full_text):
                continue

            if not self._is_valid_perk(perk_name):
                continue

            # Determine condition from surrounding text
            condition = self._extract_perk_condition(link, full_text, category)

            perks.append({'name': perk_name, 'condition': condition})

        return perks

    def _is_variant_modifier(self, link: BeautifulSoup, full_text: str) -> bool:
        """Check if 'Expert' or 'Master' is a modifier (e.g., 'Gunslinger (Expert, Master)')"""
        # Get text around the link
        parent_text = link.parent.get_text() if link.parent else ""

        # If it's in parentheses with commas, it's likely a modifier
        if '(' in parent_text and ')' in parent_text and ',' in parent_text:
            return True

        return False

    def _extract_perk_condition(self, link: BeautifulSoup, full_text: str, category: str) -> Optional[str]:
        """
        Extract condition for a perk from surrounding text

        Examples:
        - "Sniper (scoped only)" -> "scoped only"
        - "Pistol: Gun Runner" -> "Pistol"
        - "Arms Keeper (rifle only)" -> "rifle only"
        """
        # Get the link's position in text
        perk_name = link.get_text(strip=True)

        # Look for parenthetical condition immediately after the perk
        # Find the link's immediate context
        parent = link.parent
        if parent:
            parent_text = parent.get_text()

            # Check for pattern: "PerkName (condition)"
            match = re.search(rf'{re.escape(perk_name)}\s*\(([^)]+)\)', parent_text)
            if match:
                condition = match.group(1).strip()
                return condition

        # Look for category prefix before the perk (e.g., "Pistol: Gun Runner")
        # Search backwards from link
        preceding_text = self._get_preceding_text(link, full_text)
        category_match = re.search(r'(Pistol|Rifle|Heavy|Melee|Auto pistol|Non-auto pistol|Auto rifle|Non-auto rifle)\s*:\s*$', preceding_text, re.IGNORECASE)
        if category_match:
            return category_match.group(1).strip()

        return None

    def _get_preceding_text(self, link: BeautifulSoup, full_text: str, max_chars: int = 50) -> str:
        """Get text immediately preceding a link"""
        link_text = link.get_text()
        link_pos = full_text.find(link_text)
        if link_pos > 0:
            start = max(0, link_pos - max_chars)
            return full_text[start:link_pos]
        return ""

    def _parse_perk_item(self, text: str) -> List[Dict[str, any]]:
        """
        Parse a perk line which may contain multiple perks and conditions

        Examples:
            "Bloody Mess"
            "Gunslinger (Expert, Master)"
            "Sniper (scoped only)"
            "Pistol: Gun Runner, Modern Renegade, Crack Shot (sighted only)"
        """
        perks = []

        # Handle category prefix (e.g., "Pistol:", "Rifle:")
        category_match = re.match(r'^(Pistol|Rifle|Heavy|Melee|Auto|Non-auto)\s*:\s*(.+)$', text, re.IGNORECASE)
        category = None
        if category_match:
            category = category_match.group(1)
            text = category_match.group(2)

        # Split by common delimiters (semicolon, comma for separate perks)
        perk_parts = re.split(r'[;,]', text)

        for part in perk_parts:
            part = part.strip()
            if not part:
                continue

            # Extract perk name and conditions
            # Pattern: "Perk Name (condition1, condition2)"
            match = re.match(r'^([^(]+?)(?:\s*\(([^)]+)\))?\s*$', part)
            if not match:
                continue

            perk_name = match.group(1).strip()
            conditions = match.group(2).strip() if match.group(2) else None

            # Handle "Expert", "Master" variants
            if conditions and re.match(r'^(Expert|Master)(,\s*(Expert|Master))*$', conditions, re.IGNORECASE):
                # This means the base perk and variants apply
                base_perks = self._expand_perk_variants(perk_name)
                for bp in base_perks:
                    perks.append({'name': bp, 'condition': category})
            elif self._is_valid_perk(perk_name):
                full_condition = f"{category}; {conditions}" if category and conditions else (category or conditions)
                perks.append({'name': perk_name, 'condition': full_condition})

        return perks

    def _expand_perk_variants(self, base_name: str) -> List[str]:
        """Expand a perk to include Expert/Master variants if they exist"""
        variants = [base_name]
        expert = f"{base_name} Expert"
        master = f"{base_name} Master"

        if expert in self.canonical_perks:
            variants.append(expert)
        if master in self.canonical_perks:
            variants.append(master)

        return [v for v in variants if self._is_valid_perk(v)]

    def _is_valid_perk(self, perk_name: str) -> bool:
        """Check if perk name exists in canonical list"""
        if not self.canonical_perks:
            return True  # No validation if perks not loaded

        # Fuzzy match - check exact and close variants
        perk_clean = perk_name.strip()

        if perk_clean in self.canonical_perks:
            return True

        # Check without suffixes like "only"
        perk_clean = re.sub(r'\s+(only|bonus|damage)$', '', perk_clean, flags=re.IGNORECASE)

        return perk_clean in self.canonical_perks

    def _format_perks(self, perks_list: List[Dict[str, any]]) -> str:
        """
        Format perks list to match CSV format

        Format: "Perk1; Perk2; Category: Perk3 (condition), Perk4"
        """
        if not perks_list:
            return ""

        # Group by condition/category
        groups = {}
        for perk in perks_list:
            condition = perk.get('condition')
            name = perk['name']

            if condition:
                if condition not in groups:
                    groups[condition] = []
                groups[condition].append(name)
            else:
                if 'general' not in groups:
                    groups['general'] = []
                groups['general'].append(name)

        # Format output
        parts = []

        # General perks first (no conditions)
        if 'general' in groups:
            parts.extend(groups.pop('general'))

        # Category-specific perks
        for condition, perk_names in sorted(groups.items()):
            if ';' in condition:
                # Has both category and condition
                cat, cond = condition.split(';', 1)
                formatted = f"{cat.strip()}: " + ", ".join(f"{p} ({cond.strip()})" for p in perk_names)
            else:
                # Just category or just condition
                formatted = f"{condition}: " + ", ".join(perk_names)
            parts.append(formatted)

        return "; ".join(parts)

    def scrape_urls_from_file(self, urls_file: str, output_csv: str, use_playwright: bool = False):
        """
        Scrape multiple weapon URLs and save to CSV

        Args:
            urls_file: Path to file with one URL per line
            output_csv: Path to output CSV file
            use_playwright: Use Playwright instead of requests
        """
        # Read URLs
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        logger.info(f"Found {len(urls)} URLs to scrape")

        # Scrape each URL
        weapons = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")
            weapon = self.scrape_weapon(url, use_playwright=use_playwright)
            if weapon:
                weapons.append(weapon)

        # Save to CSV
        if weapons:
            self._save_to_csv(weapons, output_csv)
            logger.info(f"Saved {len(weapons)} weapons to {output_csv}")
        else:
            logger.error("No weapons scraped successfully")

    def _save_to_csv(self, weapons: List[WeaponData], output_file: str):
        """Save weapons data to CSV"""
        fieldnames = ['Name', 'Type', 'Class', 'Level', 'Damage', 'Projectile',
                     'Perks', 'Form ID', 'Editor ID', 'Source URL']

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for weapon in weapons:
                writer.writerow(weapon.to_csv_dict())


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Fallout 76 weapon data from Wiki')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-f', '--file', default='urls.txt', help='File with URLs to scrape (default: urls.txt)')
    parser.add_argument('-o', '--output', default='weapons_scraped.csv', help='Output CSV file')
    parser.add_argument('-p', '--playwright', action='store_true', help='Use Playwright for JavaScript-heavy pages')
    parser.add_argument('--perks', default='Perks.csv', help='Path to canonical perks CSV')

    args = parser.parse_args()

    scraper = FalloutWikiScraper(perks_csv_path=args.perks)

    if args.url:
        # Scrape single URL
        weapon = scraper.scrape_weapon(args.url, use_playwright=args.playwright)
        if weapon:
            scraper._save_to_csv([weapon], args.output)
            print(f"\nScraped weapon: {weapon.name}")
            print(f"Saved to: {args.output}")
    else:
        # Scrape from file
        scraper.scrape_urls_from_file(args.file, args.output, use_playwright=args.playwright)


if __name__ == '__main__':
    main()
