#!/usr/bin/env python3
"""
Fallout 76 Wiki Legendary Perk Scraper

Scrapes legendary perk data from Fallout Wiki pages and outputs clean CSV data
for the LegendaryPerks.csv file.
"""

import re
import csv
import logging
from typing import Optional, List
from dataclasses import dataclass, asdict
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
class LegendaryPerkRankData:
    """Data for a single rank of a legendary perk"""
    rank: int
    description: str
    effect_value: str = ""
    effect_type: str = ""
    form_id: str = ""


@dataclass
class LegendaryPerkData:
    """Structured legendary perk data with all ranks"""
    name: str
    race: str = "Human, Ghoul"  # Most are universal, some are ghoul-only
    ranks: List[LegendaryPerkRankData] = None

    def __post_init__(self):
        if self.ranks is None:
            self.ranks = []

    def to_csv_rows(self) -> List[dict]:
        """Convert to list of CSV row dicts (one per rank)"""
        rows = []
        for rank_data in self.ranks:
            rows.append({
                'name': self.name,
                'rank': rank_data.rank,
                'description': rank_data.description,
                'effect_value': rank_data.effect_value,
                'effect_type': rank_data.effect_type,
                'form_id': rank_data.form_id,
                'race': self.race
            })
        return rows


class LegendaryPerkScraper:
    """Scraper for Fallout Wiki legendary perk pages"""

    def __init__(self):
        """Initialize scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_legendary_perk(self, url: str, use_playwright: bool = False) -> Optional[LegendaryPerkData]:
        """
        Scrape legendary perk data from a Fallout Wiki URL

        Args:
            url: Fallout Wiki legendary perk page URL
            use_playwright: Use Playwright for JavaScript-heavy pages

        Returns:
            LegendaryPerkData object or None if scraping failed
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

            # Extract perk data
            perk_name = self._extract_name(soup, url)
            ranks = self._extract_ranks(soup, perk_name)

            # Determine race (ghoul-specific perks)
            race = "Ghoul" if perk_name in ["Action Diet", "Feral Rage"] else "Human, Ghoul"

            perk = LegendaryPerkData(
                name=perk_name,
                race=race,
                ranks=ranks
            )

            logger.info(f"Successfully scraped: {perk.name} ({len(ranks)} ranks)")
            return perk

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
        """Extract perk name from page"""
        # Try h1 page title
        h1 = soup.find('h1', class_='page-header__title')
        if h1:
            name = h1.get_text(strip=True)
            # Remove parenthetical like "(Fallout 76)"
            name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
            return name.strip()

        # Try infobox title
        infobox = soup.find('aside', class_='portable-infobox') or soup.find('table', class_='infobox')
        if infobox:
            title = infobox.find('h2', class_='pi-title')
            if title:
                return title.get_text(strip=True)

        # Fallback to URL-based name
        path = urlparse(url).path
        name = path.split('/')[-1].replace('_', ' ')
        # Decode URL encoding
        name = requests.utils.unquote(name)
        return name

    def _extract_ranks(self, soup: BeautifulSoup, perk_name: str) -> List[LegendaryPerkRankData]:
        """
        Extract all rank data from the page

        Legendary perks typically have 4 ranks, each with:
        - Rank number (1-4)
        - Description with specific values
        - Form ID

        Ranks are displayed as repeating groups of pi-data rows:
        - Effects (description)
        - Unlocked (level requirement)
        - Perk coins (cost)
        - Editor ID
        - Form ID
        """
        ranks = []

        # Try extracting from infobox portable-infobox structure
        infobox = soup.find('aside', class_='portable-infobox')

        if infobox:
            # Find sections with pi-data rows
            sections = infobox.find_all('section', class_='pi-item')

            for section in sections:
                data_rows = section.find_all('div', class_='pi-data')

                # Group data by rank (each rank starts with "Effects")
                current_rank_data = {}
                rank_num = 0

                for row in data_rows:
                    label_elem = row.find('h3', class_='pi-data-label')
                    value_elem = row.find('div', class_='pi-data-value')

                    if not label_elem or not value_elem:
                        continue

                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)

                    # New rank detected when we see "Effects" again
                    if label == 'Effects':
                        # Save previous rank if exists
                        if current_rank_data and 'description' in current_rank_data:
                            effect_value, effect_type = self._parse_effect_value(current_rank_data['description'])
                            ranks.append(LegendaryPerkRankData(
                                rank=rank_num,
                                description=current_rank_data['description'],
                                effect_value=effect_value,
                                effect_type=effect_type,
                                form_id=current_rank_data.get('form_id', '')
                            ))

                        # Start new rank
                        rank_num += 1
                        current_rank_data = {'description': self._clean_description(value)}

                    elif label == 'Form ID':
                        current_rank_data['form_id'] = value.strip()

                # Save last rank
                if current_rank_data and 'description' in current_rank_data:
                    effect_value, effect_type = self._parse_effect_value(current_rank_data['description'])
                    ranks.append(LegendaryPerkRankData(
                        rank=rank_num,
                        description=current_rank_data['description'],
                        effect_value=effect_value,
                        effect_type=effect_type,
                        form_id=current_rank_data.get('form_id', '')
                    ))

        # If we didn't find ranks in infobox, try alternative methods
        if not ranks:
            ranks = self._extract_ranks_fallback(soup, perk_name)

        # Deduplicate ranks (Wiki pages often have duplicate sections)
        # Keep only unique rank numbers (prefer first occurrence)
        seen_ranks = {}
        for rank in ranks:
            if rank.rank not in seen_ranks:
                seen_ranks[rank.rank] = rank

        ranks = list(seen_ranks.values())

        # Sort by rank number
        ranks.sort(key=lambda r: r.rank)

        if not ranks:
            logger.warning(f"No ranks found for {perk_name}")

        return ranks

    def _extract_rank_number(self, section) -> Optional[int]:
        """Extract rank number from a section (1-4)"""
        # Look for "Rank 1", "Rank 2", etc. in headers or title
        header = section.find('h2', class_='pi-item-spacing')
        if header:
            header_text = header.get_text(strip=True)

            # Match "Rank 1", "Rank 2", etc.
            match = re.search(r'Rank\s+(\d+)', header_text, re.IGNORECASE)
            if match:
                return int(match.group(1))

            # Match star ratings ★, ★★, ★★★, ★★★★
            star_count = header_text.count('★')
            if 1 <= star_count <= 4:
                return star_count

        return None

    def _extract_ranks_fallback(self, soup: BeautifulSoup, perk_name: str) -> List[LegendaryPerkRankData]:
        """
        Fallback method to extract ranks from non-standard page layouts

        This handles pages where rank data isn't in the standard infobox format
        """
        ranks = []

        # Look for sections with rank indicators in h2/h3 headers
        headers = soup.find_all(['h2', 'h3'])

        for header in headers:
            header_text = header.get_text(strip=True)

            # Try to extract rank number
            rank_num = None

            # Match "Rank 1", "Rank 2", etc.
            match = re.search(r'Rank\s+(\d+)', header_text, re.IGNORECASE)
            if match:
                rank_num = int(match.group(1))
            else:
                # Match star ratings
                star_count = header_text.count('★')
                if 1 <= star_count <= 4:
                    rank_num = star_count

            if rank_num is None:
                continue

            # Found a rank header, now extract data from following content
            description = ""
            form_id = ""

            # Look for next sibling elements
            next_elem = header.find_next_sibling()
            search_depth = 0

            while next_elem and search_depth < 10:
                # Stop at next header
                if next_elem.name in ['h2', 'h3']:
                    break

                text = next_elem.get_text(strip=True).lower()

                # Look for effects/description
                if 'effect' in text and not description:
                    # Get the value (might be in next element or same element)
                    value_text = next_elem.get_text(strip=True)
                    # Remove the label part
                    value_text = re.sub(r'^[Ee]ffects?:?\s*', '', value_text)
                    if value_text:
                        description = self._clean_description(value_text)

                # Look for Form ID
                if 'form id' in text and not form_id:
                    form_id_match = re.search(r'([0-9A-Fa-f]{8})', next_elem.get_text())
                    if form_id_match:
                        form_id = form_id_match.group(1).upper()

                next_elem = next_elem.find_next_sibling()
                search_depth += 1

            if description:
                effect_value, effect_type = self._parse_effect_value(description)
                ranks.append(LegendaryPerkRankData(
                    rank=rank_num,
                    description=description,
                    effect_value=effect_value,
                    effect_type=effect_type,
                    form_id=form_id
                ))

        return ranks

    def _parse_effect_value(self, description: str) -> tuple[str, str]:
        """
        Parse numeric effect values from description text

        Returns:
            (effect_value, effect_type) tuple

        Examples:
            "10% damage" -> ("10", "percentage")
            "+5 STR" -> ("5", "flat")
            "150% more rounds" -> ("150", "percentage")
        """
        # Look for percentage values
        percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%', description)
        if percentage_match:
            return (percentage_match.group(1), "percentage")

        # Look for flat bonus (+ or - prefix)
        flat_match = re.search(r'[+\-]\s*(\d+(?:\.\d+)?)', description)
        if flat_match:
            return (flat_match.group(1), "flat")

        # Look for any number as fallback
        number_match = re.search(r'(\d+(?:\.\d+)?)', description)
        if number_match:
            return (number_match.group(1), "value")

        return ("", "")

    def _clean_description(self, text: str) -> str:
        """Clean up description text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove wiki markup artifacts
        text = re.sub(r'\[edit\s*\|\s*edit source\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\d+\]', '', text)  # Remove citation markers like [1]

        # Remove "Main article:" prefix
        text = re.sub(r'^Main article:\s*', '', text, flags=re.IGNORECASE)

        # Trim
        text = text.strip()

        return text

    def scrape_urls_from_file(self, urls_file: str, output_csv: str, use_playwright: bool = False):
        """
        Scrape multiple legendary perk URLs and save to CSV

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
        perks = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")
            perk = self.scrape_legendary_perk(url, use_playwright=use_playwright)
            if perk:
                perks.append(perk)

        # Save to CSV
        if perks:
            self._save_to_csv(perks, output_csv)
            logger.info(f"Saved {len(perks)} legendary perks to {output_csv}")
        else:
            logger.error("No legendary perks scraped successfully")

    def _save_to_csv(self, perks: List[LegendaryPerkData], output_file: str):
        """Save legendary perks data to CSV with all ranks"""
        fieldnames = ['name', 'rank', 'description', 'effect_value', 'effect_type', 'form_id', 'race']

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for perk in perks:
                # Each perk can have multiple ranks, write one row per rank
                for row in perk.to_csv_rows():
                    writer.writerow(row)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Fallout 76 legendary perk data from Wiki')
    parser.add_argument('-u', '--url', help='Single URL to scrape')
    parser.add_argument('-f', '--file', default='legendary_perk_urls.txt',
                       help='File with URLs to scrape (default: legendary_perk_urls.txt)')
    parser.add_argument('-o', '--output', default='LegendaryPerks.csv',
                       help='Output CSV file (default: LegendaryPerks.csv)')
    parser.add_argument('-p', '--playwright', action='store_true',
                       help='Use Playwright for JavaScript-heavy pages')

    args = parser.parse_args()

    scraper = LegendaryPerkScraper()

    if args.url:
        # Scrape single URL
        perk = scraper.scrape_legendary_perk(args.url, use_playwright=args.playwright)
        if perk:
            scraper._save_to_csv([perk], args.output)
            print(f"\nScraped legendary perk: {perk.name}")
            print(f"Ranks found: {len(perk.ranks)}")
            if perk.ranks:
                print(f"Rank 1 description: {perk.ranks[0].description[:100]}...")
            print(f"Saved to: {args.output}")
    else:
        # Scrape from file
        scraper.scrape_urls_from_file(args.file, args.output, use_playwright=args.playwright)


if __name__ == '__main__':
    main()
