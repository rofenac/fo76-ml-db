#!/usr/bin/env python3
"""
Fallout 76 Wiki Collectible Scraper (Bobbleheads & Magazines)

Scrapes collectible data from Fallout Wiki pages.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CollectibleData:
    """Structured collectible data"""
    name: str
    collectible_type: str = ""      # bobblehead or magazine
    series: str = ""                 # Series name (for magazines)
    issue_number: str = ""           # Issue # (for magazines)
    effects: str = ""
    duration: str = ""
    special_modifiers: str = ""
    weight: str = ""
    value: str = ""
    form_id: str = ""
    editor_id: str = ""
    source_url: str = ""

    def to_csv_row(self) -> dict:
        """Convert to CSV row dict"""
        return {
            'name': self.name,
            'collectible_type': self.collectible_type,
            'series': self.series,
            'issue_number': self.issue_number,
            'effects': self.effects,
            'duration': self.duration,
            'special_modifiers': self.special_modifiers,
            'weight': self.weight,
            'value': self.value,
            'form_id': self.form_id,
            'editor_id': self.editor_id,
            'source_url': self.source_url
        }


class CollectibleScraper:
    """Scraper for Fallout Wiki collectible pages"""

    def __init__(self):
        """Initialize scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_collectible(self, url: str) -> Optional[CollectibleData]:
        """
        Scrape collectible data from a Fallout Wiki URL

        Args:
            url: Fallout Wiki collectible page URL

        Returns:
            CollectibleData object or None if scraping failed
        """
        logger.info(f"Scraping: {url}")

        try:
            html = self._fetch_with_requests(url)
            if not html:
                logger.error(f"Failed to fetch HTML from {url}")
                return None

            soup = BeautifulSoup(html, 'lxml')

            # Extract collectible name
            name = self._extract_name(soup, url)
            if not name:
                logger.error(f"Could not extract name from {url}")
                return None

            # Determine type (bobblehead or magazine)
            collectible_type, series, issue_number = self._determine_type_and_series(name, url)

            # Extract fields from infobox
            form_id = self._extract_form_id(soup)
            editor_id = self._extract_editor_id(soup)
            weight = self._extract_infobox_field(soup, ['weight'])
            value = self._extract_infobox_field(soup, ['value', 'caps value'])
            effects = self._extract_effects(soup)

            # Extract duration from effects if present
            duration = self._extract_duration(effects)

            # Extract SPECIAL modifiers
            special = self._extract_special_modifiers(effects)

            collectible = CollectibleData(
                name=name,
                collectible_type=collectible_type,
                series=series,
                issue_number=issue_number,
                effects=effects,
                duration=duration,
                special_modifiers=special,
                weight=weight,
                value=value,
                form_id=form_id,
                editor_id=editor_id,
                source_url=url
            )

            logger.info(f"✓ Scraped: {name} ({collectible_type})")
            return collectible

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            import traceback
            traceback.print_exc()
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

    def _extract_name(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract collectible name from page"""
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
        # URL decode
        from urllib.parse import unquote
        name = unquote(name)
        return name

    def _determine_type_and_series(self, name: str, url: str) -> tuple:
        """Determine collectible type, series, and issue number"""
        name_lower = name.lower()

        if 'bobblehead' in name_lower:
            return ('bobblehead', 'Bobbleheads', '')

        # Magazine series patterns
        magazine_series = {
            'guns and bullets': 'Guns and Bullets',
            'live & love': 'Live & Love',
            'astoundingly awesome': 'Astoundingly Awesome Tales',
            'backwoodsman': 'Backwoodsman',
            'grognak': 'Grognak the Barbarian',
            "scouts' life": "Scouts' Life",
            'tales from the west virginia hills': 'Tales from the West Virginia Hills',
            'tesla science': 'Tesla Science',
            'tumblers today': 'Tumblers Today',
            'u.s. covert operations': 'U.S. Covert Operations Manual',
            'unstoppables': 'Unstoppables',
        }

        for pattern, series_name in magazine_series.items():
            if pattern in name_lower:
                # Try to extract issue number
                issue_match = re.search(r'#?(\d+)', name)
                issue_number = issue_match.group(1) if issue_match else ''
                return ('magazine', series_name, issue_number)

        # Default to magazine if not bobblehead
        return ('magazine', '', '')

    def _extract_form_id(self, soup: BeautifulSoup) -> str:
        """Extract Form ID from infobox"""
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            item = infobox.find('div', {'data-source': 'formid'})
            if item:
                value_div = item.find('div', class_='pi-data-value')
                if value_div:
                    form_id = value_div.text.strip()
                    form_id = re.sub(r'^0x', '', form_id)
                    return form_id[:8]
        return ""

    def _extract_editor_id(self, soup: BeautifulSoup) -> str:
        """Extract Editor ID from infobox"""
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            item = infobox.find('div', {'data-source': 'edid'})
            if item:
                value_div = item.find('div', class_='pi-data-value')
                if value_div:
                    return value_div.text.strip()
        return ""

    def _extract_infobox_field(self, soup: BeautifulSoup, field_names: List[str]) -> str:
        """Extract a field from the infobox"""
        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox:
            return ""

        for field_name in field_names:
            for item in infobox.find_all('div', class_='pi-item'):
                label = item.find('h3', class_='pi-data-label') or item.find('div', class_='pi-data-label')
                if label and field_name.lower() in label.text.lower():
                    value_div = item.find('div', class_='pi-data-value')
                    if value_div:
                        return value_div.text.strip()
        return ""

    def _extract_effects(self, soup: BeautifulSoup) -> str:
        """Extract effects from page"""
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            # Find item with data-source="effects"
            effects_item = infobox.find('div', {'data-source': 'effects'})
            if effects_item:
                value_div = effects_item.find('div', class_='pi-data-value')
                if value_div:
                    return value_div.text.strip()
        return ""

    def _extract_duration(self, effects: str) -> str:
        """Extract duration from effects string"""
        # Pattern: "for X hour(s)" or "for X minute(s)"
        match = re.search(r'for (\d+(?:\.\d+)?) (hour|minute|min)', effects, re.IGNORECASE)
        if match:
            number = match.group(1)
            unit = match.group(2).lower()
            if unit.startswith('hour'):
                return f"{number} hour(s)"
            else:
                return f"{number} minute(s)"
        return ""

    def _extract_special_modifiers(self, effects: str) -> str:
        """Extract SPECIAL stat modifiers from effects"""
        special_stats = []

        # Pattern: +N SPECIAL or -N SPECIAL
        pattern = r'([+-]?\d+)\s+(STR|PER|END|CHA|INT|AGI|LCK|LUC|Strength|Perception|Endurance|Charisma|Intelligence|Agility|Luck)'

        matches = re.findall(pattern, effects, re.IGNORECASE)
        for value, stat in matches:
            # Normalize stat name
            stat_abbrev = stat[:3].upper()
            if stat_abbrev == 'LUC':
                stat_abbrev = 'LCK'
            special_stats.append(f"{value} {stat_abbrev}")

        return ", ".join(special_stats) if special_stats else ""


def scrape_collectible_urls(
    url_file: str,
    output_csv: str
):
    """Scrape multiple collectible URLs from a file"""
    scraper = CollectibleScraper()
    collectibles = []

    # Read URLs
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    logger.info(f"Found {len(urls)} URLs to scrape")

    # Scrape each URL
    for url in urls:
        collectible = scraper.scrape_collectible(url)
        if collectible:
            collectibles.append(collectible)

    # Write to CSV
    if collectibles:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'collectible_type', 'series', 'issue_number', 'effects', 'duration',
                         'special_modifiers', 'weight', 'value', 'form_id', 'editor_id', 'source_url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for collectible in collectibles:
                writer.writerow(collectible.to_csv_row())

        logger.info(f"✓ Wrote {len(collectibles)} collectibles to {output_csv}")
    else:
        logger.warning("No collectibles scraped!")

    logger.info(f"\n=== SUMMARY ===")
    logger.info(f"Total scraped: {len(collectibles)}")


def main():
    parser = argparse.ArgumentParser(description='Scrape Fallout 76 collectible data from Wiki')
    parser.add_argument('-f', '--file', help='File with URLs (one per line)')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')

    args = parser.parse_args()

    if args.file:
        scrape_collectible_urls(args.file, args.output)
    elif args.url:
        scraper = CollectibleScraper()
        collectible = scraper.scrape_collectible(args.url)
        if collectible:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'collectible_type', 'series', 'issue_number', 'effects', 'duration',
                             'special_modifiers', 'weight', 'value', 'form_id', 'editor_id', 'source_url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(collectible.to_csv_row())
            logger.info(f"✓ Wrote collectible to {args.output}")
    else:
        parser.error("Must provide either --file or --url")


if __name__ == "__main__":
    main()
