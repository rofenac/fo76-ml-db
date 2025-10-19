#!/usr/bin/env python3
"""
Fallout 76 Wiki Consumable Scraper

Scrapes consumable data (food, chems, drinks, aid) from Fallout Wiki pages.
"""

import re
import csv
import logging
import argparse
from typing import Optional, List
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ConsumableData:
    """Structured consumable data"""
    name: str
    category: str = ""          # food, drink, chem, aid, alcohol, beverage
    subcategory: str = ""       # cooked, raw, stimpak, nuka-cola, etc.
    effects: str = ""
    duration: str = ""
    hp_restore: str = ""
    rads: str = ""
    hunger_satisfaction: str = ""
    thirst_satisfaction: str = ""
    special_modifiers: str = ""
    addiction_risk: str = ""
    disease_risk: str = ""
    weight: str = ""
    value: str = ""
    form_id: str = ""
    crafting_station: str = ""
    source_url: str = ""

    def to_csv_row(self) -> dict:
        """Convert to CSV row dict"""
        return {
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'effects': self.effects,
            'duration': self.duration,
            'hp_restore': self.hp_restore,
            'rads': self.rads,
            'hunger_satisfaction': self.hunger_satisfaction,
            'thirst_satisfaction': self.thirst_satisfaction,
            'special_modifiers': self.special_modifiers,
            'addiction_risk': self.addiction_risk,
            'disease_risk': self.disease_risk,
            'weight': self.weight,
            'value': self.value,
            'form_id': self.form_id,
            'crafting_station': self.crafting_station,
            'source_url': self.source_url
        }


class ConsumableScraper:
    """Scraper for Fallout Wiki consumable pages"""

    def __init__(self):
        """Initialize scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_consumable(self, url: str, use_playwright: bool = False) -> Optional[ConsumableData]:
        """
        Scrape consumable data from a Fallout Wiki URL

        Args:
            url: Fallout Wiki consumable page URL
            use_playwright: Use Playwright for JavaScript-heavy pages

        Returns:
            ConsumableData object or None if scraping failed
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

            # Extract consumable name
            name = self._extract_name(soup, url)
            if not name:
                logger.error(f"Could not extract name from {url}")
                return None

            # Determine category from URL or content
            category = self._determine_category(name, url, soup)

            # Extract all fields from infobox
            form_id = self._extract_form_id(soup)
            weight = self._extract_infobox_field(soup, ['weight'])
            value = self._extract_infobox_field(soup, ['value', 'caps value'])
            effects = self._extract_effects(soup)
            duration = self._extract_infobox_field(soup, ['duration', 'effect duration'])
            hp_restore = self._extract_infobox_field(soup, ['hp', 'hit points', 'hp restored'])
            rads = self._extract_infobox_field(soup, ['rads', 'radiation'])
            hunger = self._extract_infobox_field(soup, ['hunger', 'food'])
            thirst = self._extract_infobox_field(soup, ['thirst', 'water', 'h2o'])
            addiction = self._extract_infobox_field(soup, ['addiction', 'addiction chance'])
            disease = self._extract_infobox_field(soup, ['disease', 'disease chance'])
            crafting = self._extract_infobox_field(soup, ['crafting', 'crafted at', 'workbench'])

            # Extract SPECIAL modifiers
            special = self._extract_special_modifiers(soup, effects)

            consumable = ConsumableData(
                name=name,
                category=category,
                subcategory="",  # Could be enhanced later
                effects=effects,
                duration=duration,
                hp_restore=hp_restore,
                rads=rads,
                hunger_satisfaction=hunger,
                thirst_satisfaction=thirst,
                special_modifiers=special,
                addiction_risk=addiction,
                disease_risk=disease,
                weight=weight,
                value=value,
                form_id=form_id,
                crafting_station=crafting,
                source_url=url
            )

            logger.info(f"✓ Scraped: {name} ({category})")
            return consumable

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch HTML using requests library"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Requests fetch failed: {e}")
            return None

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch HTML using Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_load_state('networkidle')
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Playwright fetch failed: {e}")
            return None

    def _extract_name(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract consumable name from page"""
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text
            match = re.match(r'^(.+?)\s*[\|\(]', title)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'\s*\(Fallout 76\)', '', name)
                return name

        # Try h1 tag
        h1 = soup.find('h1', class_='page-header__title')
        if h1:
            return h1.text.strip()

        # Fallback: extract from URL
        path = urlparse(url).path
        name = path.split('/')[-1].replace('_', ' ')
        name = re.sub(r'\s*\(Fallout 76\)', '', name)
        return name

    def _determine_category(self, name: str, url: str, soup: BeautifulSoup) -> str:
        """Determine consumable category"""
        name_lower = name.lower()
        url_lower = url.lower()

        # Check URL and name patterns
        if 'nuka' in name_lower or 'cola' in name_lower:
            return 'beverage'
        elif any(word in name_lower for word in ['beer', 'wine', 'whiskey', 'vodka', 'rum', 'bock', 'hefe', 'nukashine', 'alcohol']):
            return 'alcohol'
        elif any(word in name_lower for word in ['stimpak', 'radaway', 'rad-x', 'med-x']):
            return 'aid'
        elif any(word in name_lower for word in ['psycho', 'mentats', 'buff', 'fury', 'overdrive', 'x-cell', 'daddy-o', 'day tripper']):
            return 'chem'
        elif any(word in name_lower for word in ['steak', 'soup', 'stew', 'roast', 'grilled', 'fried', 'cooked', 'relish', 'brain']):
            return 'food'
        elif any(word in name_lower for word in ['water', 'juice', 'tea', 'coffee']):
            return 'drink'

        # Default
        return 'food'

    def _extract_form_id(self, soup: BeautifulSoup) -> str:
        """Extract Form ID from infobox"""
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            for label in infobox.find_all(['h3', 'div'], class_=['pi-data-label', 'pi-header']):
                if 'form id' in label.text.lower() or label.text.strip().lower() == 'id':
                    value_div = label.find_next_sibling('div', class_='pi-data-value')
                    if value_div:
                        form_id = value_div.text.strip()
                        form_id = re.sub(r'^0x', '', form_id)
                        return form_id[:8]
        return ""

    def _extract_infobox_field(self, soup: BeautifulSoup, field_names: List[str]) -> str:
        """Extract a field from the infobox"""
        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox:
            return ""

        for field_name in field_names:
            for label in infobox.find_all('div', class_='pi-data-label'):
                if field_name.lower() in label.text.lower():
                    value_div = label.find_next_sibling('div', class_='pi-data-value')
                    if value_div:
                        return value_div.text.strip()
        return ""

    def _extract_effects(self, soup: BeautifulSoup) -> str:
        """Extract effects from page"""
        effects = []

        # Look in infobox for effects
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            for label in infobox.find_all('div', class_='pi-data-label'):
                if 'effect' in label.text.lower():
                    value_div = label.find_next_sibling('div', class_='pi-data-value')
                    if value_div:
                        effect = value_div.text.strip()
                        if effect and effect not in effects:
                            effects.append(effect)

        # Also check section headers
        for header in soup.find_all(['h2', 'h3']):
            header_text = header.text.lower()
            if 'effect' in header_text:
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name not in ['h2', 'h3']:
                    if next_elem.name == 'ul':
                        for li in next_elem.find_all('li'):
                            effect = li.text.strip()
                            if effect and effect not in effects:
                                effects.append(effect)
                    elif next_elem.name == 'p':
                        text = next_elem.text.strip()
                        if text and text not in effects:
                            effects.append(text)
                    next_elem = next_elem.find_next_sibling()
                break

        return "; ".join(effects) if effects else ""

    def _extract_special_modifiers(self, soup: BeautifulSoup, effects: str) -> str:
        """Extract SPECIAL stat modifiers from effects"""
        special_stats = []

        # Pattern: +N SPECIAL or -N SPECIAL
        pattern = r'([+-]?\d+)\s+(STR|PER|END|CHA|INT|AGI|LCK|Strength|Perception|Endurance|Charisma|Intelligence|Agility|Luck)'

        matches = re.findall(pattern, effects, re.IGNORECASE)
        for value, stat in matches:
            # Normalize stat name
            stat_abbrev = stat[:3].upper()
            special_stats.append(f"{value} {stat_abbrev}")

        return ", ".join(special_stats) if special_stats else ""


def scrape_consumable_urls(
    url_file: str,
    output_csv: str,
    use_playwright: bool = False
):
    """Scrape multiple consumable URLs from a file"""
    scraper = ConsumableScraper()
    consumables = []

    # Read URLs
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    logger.info(f"Found {len(urls)} URLs to scrape")

    # Scrape each URL
    for url in urls:
        consumable = scraper.scrape_consumable(url, use_playwright=use_playwright)
        if consumable:
            consumables.append(consumable)

    # Write to CSV
    if consumables:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'category', 'subcategory', 'effects', 'duration', 'hp_restore', 'rads',
                         'hunger_satisfaction', 'thirst_satisfaction', 'special_modifiers', 'addiction_risk',
                         'disease_risk', 'weight', 'value', 'form_id', 'crafting_station', 'source_url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for consumable in consumables:
                writer.writerow(consumable.to_csv_row())

        logger.info(f"✓ Wrote {len(consumables)} consumables to {output_csv}")
    else:
        logger.warning("No consumables scraped!")


def main():
    parser = argparse.ArgumentParser(description='Scrape Fallout 76 consumable data from Wiki')
    parser.add_argument('-f', '--file', help='File with URLs (one per line)')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')
    parser.add_argument('--playwright', action='store_true', help='Use Playwright for JavaScript-heavy pages')

    args = parser.parse_args()

    if args.file:
        scrape_consumable_urls(args.file, args.output, use_playwright=args.playwright)
    elif args.url:
        scraper = ConsumableScraper()
        consumable = scraper.scrape_consumable(args.url, use_playwright=args.playwright)
        if consumable:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'category', 'subcategory', 'effects', 'duration', 'hp_restore', 'rads',
                             'hunger_satisfaction', 'thirst_satisfaction', 'special_modifiers', 'addiction_risk',
                             'disease_risk', 'weight', 'value', 'form_id', 'crafting_station', 'source_url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(consumable.to_csv_row())
            logger.info(f"✓ Wrote consumable to {args.output}")
    else:
        parser.error("Must provide either --file or --url")


if __name__ == "__main__":
    main()
