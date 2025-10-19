#!/usr/bin/env python3
"""
Fallout 76 Wiki Mutation Scraper

Scrapes mutation data from Fallout Wiki pages and outputs clean CSV data.
"""

import re
import csv
import logging
import argparse
from typing import Optional, List
from dataclasses import dataclass, asdict, field
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
class MutationData:
    """Structured mutation data"""
    name: str
    positive_effects: str = ""
    negative_effects: str = ""
    form_id: str = ""
    exclusive_with: str = ""  # For Carnivore/Herbivore exclusivity
    source_url: str = ""

    def to_csv_row(self) -> dict:
        """Convert to CSV row dict"""
        return {
            'name': self.name,
            'positive_effects': self.positive_effects,
            'negative_effects': self.negative_effects,
            'form_id': self.form_id,
            'exclusive_with': self.exclusive_with,
            'source_url': self.source_url
        }


class MutationScraper:
    """Scraper for Fallout Wiki mutation pages"""

    def __init__(self):
        """Initialize scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_mutation(self, url: str, use_playwright: bool = False) -> Optional[MutationData]:
        """
        Scrape mutation data from a Fallout Wiki URL

        Args:
            url: Fallout Wiki mutation page URL
            use_playwright: Use Playwright for JavaScript-heavy pages

        Returns:
            MutationData object or None if scraping failed
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

            # Extract mutation name from title or h1
            name = self._extract_mutation_name(soup, url)
            if not name:
                logger.error(f"Could not extract mutation name from {url}")
                return None

            # Extract form ID from infobox
            form_id = self._extract_form_id(soup)

            # Extract positive and negative effects
            positive_effects = self._extract_positive_effects(soup)
            negative_effects = self._extract_negative_effects(soup)

            # If effects are empty, try extracting from meta description
            if not positive_effects or not negative_effects:
                meta_positive, meta_negative = self._extract_effects_from_meta(soup)
                if not positive_effects:
                    positive_effects = meta_positive
                if not negative_effects:
                    negative_effects = meta_negative

            # Determine exclusivity (Carnivore <-> Herbivore)
            exclusive_with = self._determine_exclusivity(name, soup)

            mutation = MutationData(
                name=name,
                positive_effects=positive_effects,
                negative_effects=negative_effects,
                form_id=form_id,
                exclusive_with=exclusive_with,
                source_url=url
            )

            logger.info(f"✓ Scraped: {name}")
            return mutation

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
        """Fetch HTML using Playwright (for JavaScript-heavy pages)"""
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

    def _extract_mutation_name(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract mutation name from page"""
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text
            # Remove site suffix like " | Fallout Wiki | Fandom"
            match = re.match(r'^(.+?)\s*[\|\(]', title)
            if match:
                name = match.group(1).strip()
                # Clean up "(Fallout 76)" suffix
                name = re.sub(r'\s*\(Fallout 76\)', '', name)
                return name

        # Try h1 tag
        h1 = soup.find('h1', class_='page-header__title')
        if h1:
            return h1.text.strip()

        # Try first heading
        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()

        # Fallback: extract from URL
        path = urlparse(url).path
        name = path.split('/')[-1].replace('_', ' ')
        name = re.sub(r'\s*\(Fallout 76\)', '', name)
        return name

    def _extract_form_id(self, soup: BeautifulSoup) -> str:
        """Extract Form ID from infobox"""
        # Look for Form ID in portable infobox
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            # Find label containing "Form ID" or "ID"
            for label in infobox.find_all(['h3', 'div'], class_=['pi-data-label', 'pi-header']):
                if 'form id' in label.text.lower() or label.text.strip().lower() == 'id':
                    # Get associated value
                    value_div = label.find_next_sibling('div', class_='pi-data-value')
                    if value_div:
                        form_id = value_div.text.strip()
                        # Clean up (remove prefixes like "0x")
                        form_id = re.sub(r'^0x', '', form_id)
                        return form_id[:8]  # 8 hex characters

        return ""

    def _extract_positive_effects(self, soup: BeautifulSoup) -> str:
        """Extract positive effects from page"""
        effects = []

        # Look for sections labeled "Positive effects", "Benefits", "Effects"
        for header in soup.find_all(['h2', 'h3']):
            header_text = header.text.lower()
            if 'positive' in header_text or 'benefit' in header_text or header_text.strip() == 'effects':
                # Get the following content (usually a <ul> or <p>)
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                    if next_elem.name == 'ul':
                        for li in next_elem.find_all('li'):
                            effect = li.text.strip()
                            if effect and not any(neg in effect.lower() for neg in ['negative', 'penalty', 'reduced', '-']):
                                effects.append(effect)
                    elif next_elem.name == 'p':
                        text = next_elem.text.strip()
                        if text:
                            effects.append(text)
                    next_elem = next_elem.find_next_sibling()
                break

        # Also check infobox for effect data
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            for label in infobox.find_all('div', class_='pi-data-label'):
                if 'positive' in label.text.lower() or 'benefit' in label.text.lower():
                    value_div = label.find_next_sibling('div', class_='pi-data-value')
                    if value_div:
                        effect = value_div.text.strip()
                        if effect and effect not in effects:
                            effects.append(effect)

        return "; ".join(effects) if effects else ""

    def _extract_negative_effects(self, soup: BeautifulSoup) -> str:
        """Extract negative effects from page"""
        effects = []

        # Look for sections labeled "Negative effects", "Drawbacks", "Penalties"
        for header in soup.find_all(['h2', 'h3']):
            header_text = header.text.lower()
            if 'negative' in header_text or 'drawback' in header_text or 'penalties' in header_text:
                # Get the following content
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                    if next_elem.name == 'ul':
                        for li in next_elem.find_all('li'):
                            effect = li.text.strip()
                            if effect:
                                effects.append(effect)
                    elif next_elem.name == 'p':
                        text = next_elem.text.strip()
                        if text:
                            effects.append(text)
                    next_elem = next_elem.find_next_sibling()
                break

        # Also check infobox
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            for label in infobox.find_all('div', class_='pi-data-label'):
                if 'negative' in label.text.lower() or 'penalty' in label.text.lower():
                    value_div = label.find_next_sibling('div', class_='pi-data-value')
                    if value_div:
                        effect = value_div.text.strip()
                        if effect and effect not in effects:
                            effects.append(effect)

        return "; ".join(effects) if effects else ""

    def _extract_effects_from_meta(self, soup: BeautifulSoup) -> tuple:
        """Extract positive and negative effects from meta description tag"""
        positive = ""
        negative = ""

        # Find meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})

        if meta_desc and meta_desc.get('content'):
            desc = meta_desc.get('content')

            # Pattern: "Positive effects <effects>. Negative effects <effects>."
            # Handle variations: "Positive effects:", "Positive effects: -", "Positive effects "
            pos_match = re.search(r'Positive effects?:?\s*-?\s*([^.]+?)(?:\.|Negative effects)', desc, re.IGNORECASE)
            neg_match = re.search(r'Negative effects?:?\s*-?\s*([^.]+?)(?:\.|$)', desc, re.IGNORECASE)

            if pos_match:
                positive = pos_match.group(1).strip()
            if neg_match:
                negative = neg_match.group(1).strip()

        return positive, negative

    def _determine_exclusivity(self, name: str, soup: BeautifulSoup) -> str:
        """Determine if mutation is exclusive with another (Carnivore <-> Herbivore)"""
        name_lower = name.lower()

        if 'carnivore' in name_lower:
            return "Herbivore"
        elif 'herbivore' in name_lower:
            return "Carnivore"

        # Check page content for exclusivity mentions
        page_text = soup.get_text().lower()
        if 'mutually exclusive' in page_text or 'cannot have both' in page_text:
            # Try to extract which mutation it's exclusive with
            if 'carnivore' in page_text and 'carnivore' not in name_lower:
                return "Carnivore"
            elif 'herbivore' in page_text and 'herbivore' not in name_lower:
                return "Herbivore"

        return ""


def scrape_mutation_urls(
    url_file: str,
    output_csv: str,
    use_playwright: bool = False
):
    """
    Scrape multiple mutation URLs from a file

    Args:
        url_file: Path to text file with one URL per line
        output_csv: Output CSV file path
        use_playwright: Use Playwright for fetching
    """
    scraper = MutationScraper()
    mutations = []

    # Read URLs
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    logger.info(f"Found {len(urls)} URLs to scrape")

    # Scrape each URL
    for url in urls:
        mutation = scraper.scrape_mutation(url, use_playwright=use_playwright)
        if mutation:
            mutations.append(mutation)

    # Write to CSV
    if mutations:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'positive_effects', 'negative_effects', 'form_id', 'exclusive_with', 'source_url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for mutation in mutations:
                writer.writerow(mutation.to_csv_row())

        logger.info(f"✓ Wrote {len(mutations)} mutations to {output_csv}")
    else:
        logger.warning("No mutations scraped!")


def main():
    parser = argparse.ArgumentParser(description='Scrape Fallout 76 mutation data from Wiki')
    parser.add_argument('-f', '--file', help='File with URLs (one per line)')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')
    parser.add_argument('--playwright', action='store_true', help='Use Playwright for JavaScript-heavy pages')

    args = parser.parse_args()

    if args.file:
        scrape_mutation_urls(args.file, args.output, use_playwright=args.playwright)
    elif args.url:
        scraper = MutationScraper()
        mutation = scraper.scrape_mutation(args.url, use_playwright=args.playwright)
        if mutation:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'positive_effects', 'negative_effects', 'form_id', 'exclusive_with', 'source_url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(mutation.to_csv_row())
            logger.info(f"✓ Wrote mutation to {args.output}")
    else:
        parser.error("Must provide either --file or --url")


if __name__ == "__main__":
    main()
