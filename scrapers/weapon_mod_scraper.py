#!/usr/bin/env python3
"""
Fallout 76 Wiki Weapon Mod Scraper

Scrapes weapon modification data from Fallout Wiki weapon pages.
Extracts mod tables for each slot (receiver, barrel, stock, magazine, sight, muzzle, grip).
"""

import re
import csv
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COMBAT_RELEVANT_SLOTS = {
    'receiver', 'barrel', 'stock', 'magazine', 'sight', 'muzzle', 'grip',
    'capacitor', 'dish', 'snappy', 'fore grip', 'foregrip', 'mod'
}
SKIP_SLOTS = {'appearance', 'paint', 'skin'}

STAT_MAPPINGS = [
    ('damage', 'damage_change'),
    ('fire rate', 'fire_rate_change'),
    ('range', 'range_change'),
    ('accuracy', 'accuracy_change'),
    ('ap cost', 'ap_cost_change'),
    ('ap', 'ap_cost_change'),
    ('recoil', 'recoil_change'),
    ('spread', 'spread_change'),
    ('weight', 'weight_change'),
    ('value', 'value_change_percent'),
    ('magazine', 'mag_size_change'),
    ('mag', 'mag_size_change'),
    ('reload', 'reload_speed_change'),
    ('crit', 'crit_damage_bonus'),
    ('hip', 'hip_fire_accuracy_bonus'),
    ('penetrat', 'armor_penetration'),
]


@dataclass
class WeaponModData:
    weapon_name: str
    slot: str
    mod_name: str
    damage_change: Optional[str] = None
    damage_change_is_percent: bool = False
    fire_rate_change: Optional[str] = None
    range_change: Optional[str] = None
    accuracy_change: Optional[str] = None
    ap_cost_change: Optional[str] = None
    recoil_change: Optional[str] = None
    spread_change: Optional[str] = None
    converts_to_auto: bool = False
    converts_to_semi: bool = False
    crit_damage_bonus: Optional[str] = None
    hip_fire_accuracy_bonus: Optional[str] = None
    armor_penetration: Optional[str] = None
    is_suppressed: bool = False
    is_scoped: bool = False
    mag_size_change: Optional[str] = None
    reload_speed_change: Optional[str] = None
    weight_change: Optional[str] = None
    value_change_percent: Optional[str] = None
    required_perk: Optional[str] = None
    required_perk_rank: Optional[int] = None
    form_id: Optional[str] = None
    source_url: str = ""

    def to_csv_dict(self) -> Dict[str, str]:
        return {
            'weapon_name': self.weapon_name,
            'slot': self.slot,
            'mod_name': self.mod_name,
            'damage_change': self.damage_change or '',
            'damage_change_is_percent': '1' if self.damage_change_is_percent else '0',
            'fire_rate_change': self.fire_rate_change or '',
            'range_change': self.range_change or '',
            'accuracy_change': self.accuracy_change or '',
            'ap_cost_change': self.ap_cost_change or '',
            'recoil_change': self.recoil_change or '',
            'spread_change': self.spread_change or '',
            'converts_to_auto': '1' if self.converts_to_auto else '0',
            'converts_to_semi': '1' if self.converts_to_semi else '0',
            'crit_damage_bonus': self.crit_damage_bonus or '',
            'hip_fire_accuracy_bonus': self.hip_fire_accuracy_bonus or '',
            'armor_penetration': self.armor_penetration or '',
            'is_suppressed': '1' if self.is_suppressed else '0',
            'is_scoped': '1' if self.is_scoped else '0',
            'mag_size_change': self.mag_size_change or '',
            'reload_speed_change': self.reload_speed_change or '',
            'weight_change': self.weight_change or '',
            'value_change_percent': self.value_change_percent or '',
            'required_perk': self.required_perk or '',
            'required_perk_rank': str(self.required_perk_rank) if self.required_perk_rank else '',
            'form_id': self.form_id or '',
            'source_url': self.source_url,
        }


class WeaponModScraper:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_weapon_mods(self, url: str, use_playwright: bool = True) -> List[WeaponModData]:
        logger.info(f"Scraping mods from: {url}")
        try:
            if use_playwright:
                html = self._fetch_with_playwright(url)
            else:
                html = self._fetch_with_requests(url)

            if not html:
                logger.error(f"Failed to fetch HTML from {url}")
                return []

            soup = BeautifulSoup(html, 'lxml')
            weapon_name = self._extract_weapon_name(soup, url)
            logger.info(f"Weapon: {weapon_name}")

            mods = []
            tab_mods = self._extract_mods_from_tabs(soup, weapon_name, url)
            if tab_mods:
                mods.extend(tab_mods)

            table_mods = self._extract_mods_from_tables(soup, weapon_name, url)
            for mod in table_mods:
                if not any(m.mod_name == mod.mod_name and m.slot == mod.slot for m in mods):
                    mods.append(mod)

            logger.info(f"Found {len(mods)} mods for {weapon_name}")
            return mods
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)
            return []

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Requests fetch failed: {e}")
            return None

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=60000)
                time.sleep(2)
                html = page.content()
                browser.close()
                return html
        except PlaywrightTimeout:
            logger.error("Playwright timeout")
            return None
        except Exception as e:
            logger.error(f"Playwright fetch failed: {e}")
            return None

    def _extract_weapon_name(self, soup: BeautifulSoup, url: str) -> str:
        h1 = soup.find('h1', class_='page-header__title')
        if h1:
            name = h1.get_text(strip=True)
            name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
            return name.strip()
        path = urlparse(url).path
        name = path.split('/')[-1].replace('_', ' ')
        return re.sub(r'\s*\([^)]*\)\s*$', '', name)

    def _extract_mods_from_tabs(self, soup: BeautifulSoup, weapon_name: str, url: str) -> List[WeaponModData]:
        mods = []
        tabbers = soup.find_all('div', class_='wds-tabber')
        
        for tabber in tabbers:
            tabs_wrapper = tabber.find('ul', class_='wds-tabs')
            if tabs_wrapper:
                tab_labels = tabs_wrapper.find_all('li')
            else:
                tab_labels = []
            
            tab_contents = tabber.find_all('div', class_='wds-tab__content')
            
            for label, content in zip(tab_labels, tab_contents):
                slot_name = label.get_text(strip=True).lower()
                if slot_name in SKIP_SLOTS:
                    continue
                slot = self._normalize_slot_name(slot_name)
                if not slot:
                    continue
                tables = content.find_all('table')
                for table in tables:
                    table_mods = self._parse_mod_table(table, weapon_name, slot, url)
                    mods.extend(table_mods)
        return mods

    def _extract_mods_from_tables(self, soup: BeautifulSoup, weapon_name: str, url: str) -> List[WeaponModData]:
        mods = []
        tables = soup.find_all('table', class_=lambda x: x and ('wikitable' in x or 'article-table' in x))
        for table in tables:
            slot = self._find_slot_from_context(table) or self._infer_slot_from_table(table)
            if slot:
                table_mods = self._parse_mod_table(table, weapon_name, slot, url)
                mods.extend(table_mods)
        return mods

    def _normalize_slot_name(self, raw_slot: str) -> Optional[str]:
        raw_slot = raw_slot.lower().strip()
        slot_map = {
            'receiver': 'receiver', 'receivers': 'receiver',
            'barrel': 'barrel', 'barrels': 'barrel',
            'stock': 'stock', 'stocks': 'stock',
            'grip': 'grip', 'grips': 'grip', 'fore grip': 'grip', 'foregrip': 'grip',
            'magazine': 'magazine', 'magazines': 'magazine', 'mag': 'magazine',
            'sight': 'sight', 'sights': 'sight', 'scope': 'sight', 'scopes': 'sight', 'optics': 'sight',
            'muzzle': 'muzzle', 'muzzles': 'muzzle',
            'capacitor': 'receiver', 'dish': 'barrel',
        }
        for key, value in slot_map.items():
            if key in raw_slot:
                return value
        return None

    def _find_slot_from_context(self, table) -> Optional[str]:
        for sibling in table.previous_siblings:
            if sibling.name in ['h2', 'h3', 'h4']:
                text = sibling.get_text(strip=True).lower()
                slot = self._normalize_slot_name(text)
                if slot:
                    return slot
        return None

    def _infer_slot_from_table(self, table) -> Optional[str]:
        caption = table.find('caption')
        if caption:
            return self._normalize_slot_name(caption.get_text(strip=True))
        return None

    def _parse_mod_table(self, table, weapon_name: str, slot: str, url: str) -> List[WeaponModData]:
        mods = []
        all_rows = table.find_all('tr')
        if len(all_rows) < 2:
            return mods

        # Find header row
        header_row = None
        header_row_idx = 0
        for i, row in enumerate(all_rows[:3]):
            cells = row.find_all(['th', 'td'])
            texts = [c.get_text(strip=True).lower() for c in cells[:3]]
            for c in cells:
                img = c.find('img')
                if img and (img.get('alt') or img.get('title')):
                    texts.append((img.get('alt') or img.get('title')).lower())
            if 'mod' in texts or any('damage' in t or 'fire rate' in t for t in texts):
                header_row = row
                header_row_idx = i
                break

        if not header_row:
            header_row = all_rows[0]
            header_row_idx = 0

        # Parse headers (check for image alt text)
        headers = []
        for th in header_row.find_all(['th', 'td']):
            header_text = th.get_text(strip=True).lower()
            if not header_text:
                img = th.find('img')
                if img:
                    header_text = (img.get('alt') or img.get('title') or '').lower()
            headers.append(header_text)

        if not headers:
            return mods

        # Map headers to fields
        header_mapping = {}
        for i, header in enumerate(headers):
            if header in ['name', 'mod', 'modification', 'mod name']:
                header_mapping['name'] = i
            for stat_key, field_name in STAT_MAPPINGS:
                if stat_key in header:
                    header_mapping[field_name] = i
                    break
            if 'perk' in header or 'require' in header:
                header_mapping['perk'] = i

        if 'name' not in header_mapping and headers:
            header_mapping['name'] = 0

        # Parse data rows
        for row in all_rows[header_row_idx + 1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            mod = self._parse_mod_row(cells, header_mapping, weapon_name, slot, url)
            if mod:
                mods.append(mod)
        return mods

    def _parse_mod_row(self, cells, header_mapping: Dict, weapon_name: str, slot: str, url: str) -> Optional[WeaponModData]:
        try:
            name_idx = header_mapping.get('name', 0)
            if name_idx >= len(cells):
                return None

            mod_name = cells[name_idx].get_text(strip=True)
            if not mod_name or mod_name.lower() in ['standard', 'none', 'default', '—', '-']:
                return None

            mod = WeaponModData(weapon_name=weapon_name, slot=slot, mod_name=mod_name, source_url=url)

            # Parse stat columns
            for field_name, idx in header_mapping.items():
                if field_name in ['name', 'perk'] or idx >= len(cells):
                    continue
                value = self._parse_stat_value(cells[idx].get_text(strip=True))
                if value:
                    setattr(mod, field_name, value)

            # Check for special properties
            mod_name_lower = mod_name.lower()
            if 'automatic' in mod_name_lower or 'auto' in mod_name_lower:
                mod.converts_to_auto = True
            if 'hardened' in mod_name_lower or 'semi' in mod_name_lower:
                mod.converts_to_semi = True
            if 'suppressor' in mod_name_lower or 'suppressed' in mod_name_lower or 'silencer' in mod_name_lower:
                mod.is_suppressed = True
            if 'scope' in mod_name_lower or 'recon' in mod_name_lower or 'night vision' in mod_name_lower:
                mod.is_scoped = True
            if 'reflex' in mod_name_lower or 'glow' in mod_name_lower:
                mod.is_scoped = False

            # Parse perk requirement from cell (not text)
            perk_idx = header_mapping.get('perk')
            if perk_idx is not None and perk_idx < len(cells):
                perk, rank = self._parse_perk_requirement(cells[perk_idx])
                mod.required_perk = perk
                mod.required_perk_rank = rank

            return mod
        except Exception as e:
            logger.warning(f"Error parsing mod row: {e}")
            return None

    def _parse_stat_value(self, text: str) -> Optional[str]:
        if not text or text in ['—', '-', 'N/A', '']:
            return None
        text = text.strip()
        if '%' in text:
            return text
        match = re.search(r'([+-]?\d+(?:\.\d+)?)', text)
        if match:
            return match.group(1)
        return None

    def _parse_perk_requirement(self, cell) -> tuple:
        """Parse perk name and rank from requirements cell HTML"""
        # Find perk link
        link = cell.find('a')
        if link:
            perk_name = link.get_text(strip=True)
            # Look for rank number after the link
            next_text = link.next_sibling
            if next_text and isinstance(next_text, str):
                rank_match = re.search(r'(\d+)', next_text)
                if rank_match:
                    return (perk_name, int(rank_match.group(1)))
            return (perk_name, 1)
        return (None, None)

    def scrape_urls_from_file(self, urls_file: str, output_csv: str, use_playwright: bool = True):
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        logger.info(f"Found {len(urls)} URLs to scrape")
        all_mods = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")
            mods = self.scrape_weapon_mods(url, use_playwright=use_playwright)
            all_mods.extend(mods)
            if i < len(urls):
                time.sleep(1)

        if all_mods:
            self._save_to_csv(all_mods, output_csv)
            logger.info(f"Saved {len(all_mods)} mods to {output_csv}")
        else:
            logger.warning("No mods scraped successfully")

    def _save_to_csv(self, mods: List[WeaponModData], output_file: str):
        fieldnames = [
            'weapon_name', 'slot', 'mod_name',
            'damage_change', 'damage_change_is_percent',
            'fire_rate_change', 'range_change', 'accuracy_change',
            'ap_cost_change', 'recoil_change', 'spread_change',
            'converts_to_auto', 'converts_to_semi',
            'crit_damage_bonus', 'hip_fire_accuracy_bonus', 'armor_penetration',
            'is_suppressed', 'is_scoped',
            'mag_size_change', 'reload_speed_change',
            'weight_change', 'value_change_percent',
            'required_perk', 'required_perk_rank',
            'form_id', 'source_url'
        ]
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for mod in mods:
                writer.writerow(mod.to_csv_dict())


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape Fallout 76 weapon mod data from Wiki')
    parser.add_argument('-u', '--url', help='Single weapon URL to scrape')
    parser.add_argument('-f', '--file', default='weapon_mod_urls.txt', help='File with weapon URLs')
    parser.add_argument('-o', '--output', default='data/input/weapon_mods.csv', help='Output CSV file')
    parser.add_argument('--no-playwright', action='store_true', help='Use requests instead of Playwright')
    args = parser.parse_args()

    scraper = WeaponModScraper()
    use_playwright = not args.no_playwright

    if args.url:
        mods = scraper.scrape_weapon_mods(args.url, use_playwright=use_playwright)
        if mods:
            scraper._save_to_csv(mods, args.output)
            print(f"\nScraped {len(mods)} mods")
            print(f"Saved to: {args.output}")
            for mod in mods[:5]:
                print(f"  - [{mod.slot}] {mod.mod_name}: perk={mod.required_perk} rank={mod.required_perk_rank}")
            if len(mods) > 5:
                print(f"  ... and {len(mods) - 5} more")
    else:
        scraper.scrape_urls_from_file(args.file, args.output, use_playwright=use_playwright)


if __name__ == '__main__':
    main()
