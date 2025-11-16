"""
Automated Region Discovery and Expansion System
Automatically discovers new countries and regions for casino vulnerability scanning
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import re
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    async_playwright = None

logger = logging.getLogger(__name__)


@dataclass
class CountryInfo:
    """Information about a discovered country"""
    name: str
    code: str
    language: str
    timezone: str
    gambling_legal: bool = False
    casino_density: str = "unknown"  # high, medium, low
    search_terms: List[str] = None
    domains: List[str] = None
    phone_prefixes: List[str] = None
    discovered_sources: List[str] = None

    def __post_init__(self):
        if self.search_terms is None:
            self.search_terms = [self.name.lower(), "casino", "gambling"]
        if self.domains is None:
            self.domains = [f".{self.code.lower()}"]
        if self.phone_prefixes is None:
            self.phone_prefixes = []
        if self.discovered_sources is None:
            self.discovered_sources = []


class AutoRegionDiscovery:
    """
    Automated system for discovering new regions and countries for casino scanning
    """

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None

        # Known countries database (seed data)
        self.known_countries = {
            "VN": CountryInfo("Vietnam", "VN", "vi", "Asia/Ho_Chi_Minh", True, "high",
                            ["casino", "cờ bạc", "game bài", "đánh bài"]),
            "LA": CountryInfo("Laos", "LA", "lo", "Asia/Vientiane", True, "medium",
                            ["casino", "ຄາສິໂນ", "ການພະນັນ"]),
            "KH": CountryInfo("Cambodia", "KH", "km", "Asia/Phnom_Penh", True, "high",
                            ["casino", "កាស៊ីណូ"]),
        }

        # Country code to phone prefix mapping
        self.country_phone_prefixes = {
            "VN": ["+84"], "LA": ["+856"], "KH": ["+855"],
            "US": ["+1"], "GB": ["+44"], "DE": ["+49"],
            "FR": ["+33"], "IT": ["+39"], "ES": ["+34"],
            "CN": ["+86"], "JP": ["+81"], "KR": ["+82"],
            "AU": ["+61"], "CA": ["+1"], "BR": ["+55"],
            "MX": ["+52"], "AR": ["+54"], "CL": ["+56"],
            "IN": ["+91"], "TH": ["+66"], "MY": ["+60"],
            "SG": ["+65"], "PH": ["+63"], "ID": ["+62"],
            "RU": ["+7"], "PL": ["+48"], "NL": ["+31"],
            "BE": ["+32"], "CH": ["+41"], "AT": ["+43"],
            "SE": ["+46"], "NO": ["+47"], "DK": ["+45"],
            "FI": ["+358"], "PT": ["+351"], "GR": ["+30"],
            "TR": ["+90"], "ZA": ["+27"], "EG": ["+20"],
            "NG": ["+234"], "KE": ["+254"], "MA": ["+212"],
            "AE": ["+971"], "SA": ["+966"], "IL": ["+972"],
            "HK": ["+852"], "TW": ["+886"], "NZ": ["+64"],
        }

    async def start(self):
        """Start browser instance"""
        if async_playwright is None:
            raise ImportError("Playwright is not installed")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        logger.info("Auto region discovery browser started")

    async def stop(self):
        """Stop browser instance"""
        if self.browser:
            await self.browser.close()
        logger.info("Auto region discovery browser stopped")

    async def discover_new_regions(self, max_countries: int = 20) -> List[CountryInfo]:
        """
        Discover new countries/regions with gambling potential

        Args:
            max_countries: Maximum number of countries to discover

        Returns:
            List of discovered CountryInfo objects
        """
        discovered_countries = []

        # Method 1: Search engine discovery
        search_countries = await self._discover_via_search_engines()
        discovered_countries.extend(search_countries)

        # Method 2: Wikipedia gambling pages
        wiki_countries = await self._discover_via_wikipedia()
        discovered_countries.extend(wiki_countries)

        # Method 3: Gambling forum analysis
        forum_countries = await self._discover_via_forums()
        discovered_countries.extend(forum_countries)

        # Remove duplicates and filter
        unique_countries = self._deduplicate_countries(discovered_countries)

        # Enrich with additional data
        enriched_countries = await self._enrich_country_data(unique_countries[:max_countries])

        # Filter for gambling relevance
        gambling_countries = [c for c in enriched_countries if self._assess_gambling_potential(c)]

        logger.info(f"Discovered {len(gambling_countries)} new gambling-relevant countries")
        return gambling_countries

    async def _discover_via_search_engines(self) -> List[CountryInfo]:
        """Discover countries via search engine queries"""
        countries = []

        search_queries = [
            'online casino countries legal',
            'gambling regulations by country',
            'legal online gambling worldwide',
            'casino licensing jurisdictions'
        ]

        for query in search_queries:
            try:
                page_countries = await self._search_google(query)
                countries.extend(page_countries)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                logger.warning(f"Search query failed: {query} - {e}")

        return countries

    async def _search_google(self, query: str) -> List[CountryInfo]:
        """Search Google and extract country information"""
        if not self.browser:
            await self.start()

        countries = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            # Use a simple search approach (in real implementation, use proper search API)
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=20"

            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout)

            # Extract country names from search results
            country_patterns = [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b.*(?:casino|gambling|betting)',
                r'(?:in|of|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*).*legal',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*).*online.*gambling'
            ]

            page_text = await page.inner_text('body')

            for pattern in country_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    country_name = match.strip()
                    if len(country_name) > 2 and country_name not in ['The', 'And', 'Online', 'Legal']:
                        country_code = self._country_name_to_code(country_name)
                        if country_code and country_code not in self.known_countries:
                            countries.append(CountryInfo(
                                name=country_name,
                                code=country_code,
                                language=self._guess_language(country_name),
                                timezone=self._guess_timezone(country_name),
                                discovered_sources=[f"google_search:{query}"]
                            ))

        except Exception as e:
            logger.warning(f"Google search failed: {e}")
        finally:
            await page.close()
            await context.close()

        return countries

    async def _discover_via_wikipedia(self) -> List[CountryInfo]:
        """Discover countries from Wikipedia gambling regulation pages"""
        countries = []

        wiki_pages = [
            'https://en.wikipedia.org/wiki/Gambling_law',
            'https://en.wikipedia.org/wiki/Online_gambling',
            'https://en.wikipedia.org/wiki/Casino',
            'https://en.wikipedia.org/wiki/List_of_casinos'
        ]

        for wiki_url in wiki_pages:
            try:
                page_countries = await self._scrape_wikipedia(wiki_url)
                countries.extend(page_countries)
            except Exception as e:
                logger.warning(f"Wikipedia scraping failed: {wiki_url} - {e}")

        return countries

    async def _scrape_wikipedia(self, url: str) -> List[CountryInfo]:
        """Scrape country information from Wikipedia"""
        if not self.browser:
            await self.start()

        countries = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)

            # Look for country lists in tables and content
            country_selectors = [
                'table.wikitable a[href*="/wiki/"]',
                'ul li a[href*="/wiki/"]',
                '.mw-parser-output a[href*="/wiki/"]'
            ]

            for selector in country_selectors:
                links = await page.query_selector_all(selector)
                for link in links:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()

                    if href and '/wiki/' in href and len(text) > 2:
                        # Check if it looks like a country name
                        if self._is_country_name(text):
                            country_code = self._country_name_to_code(text)
                            if country_code and country_code not in self.known_countries:
                                countries.append(CountryInfo(
                                    name=text,
                                    code=country_code,
                                    language=self._guess_language(text),
                                    timezone=self._guess_timezone(text),
                                    discovered_sources=[f"wikipedia:{url}"]
                                ))

        except Exception as e:
            logger.warning(f"Wikipedia scraping failed: {e}")
        finally:
            await page.close()
            await context.close()

        return countries

    async def _discover_via_forums(self) -> List[CountryInfo]:
        """Discover countries from gambling forums and communities"""
        countries = []

        forum_sites = [
            'https://www.reddit.com/r/onlinegambling/',
            'https://forum.gamblingcommission.gov.uk/',
            # Add more forum URLs as needed
        ]

        for forum_url in forum_sites:
            try:
                page_countries = await self._scrape_forum(forum_url)
                countries.extend(page_countries)
            except Exception as e:
                logger.warning(f"Forum scraping failed: {forum_url} - {e}")

        return countries

    async def _scrape_forum(self, url: str) -> List[CountryInfo]:
        """Scrape country mentions from forums"""
        if not self.browser:
            await self.start()

        countries = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)

            # Extract text and look for country mentions
            page_text = await page.inner_text('body')

            # Common country mentions in gambling contexts
            gambling_country_indicators = [
                r'casino.*\b([A-Z][a-z]+)\b',
                r'gambling.*\b([A-Z][a-z]+)\b',
                r'betting.*\b([A-Z][a-z]+)\b',
                r'\b([A-Z][a-z]+)\b.*license',
                r'\b([A-Z][a-z]+)\b.*regulation'
            ]

            for pattern in gambling_country_indicators:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    country_name = match.strip()
                    if self._is_country_name(country_name):
                        country_code = self._country_name_to_code(country_name)
                        if country_code and country_code not in self.known_countries:
                            countries.append(CountryInfo(
                                name=country_name,
                                code=country_code,
                                language=self._guess_language(country_name),
                                timezone=self._guess_timezone(country_name),
                                discovered_sources=[f"forum:{url}"]
                            ))

        except Exception as e:
            logger.warning(f"Forum scraping failed: {e}")
        finally:
            await page.close()
            await context.close()

        return countries

    def _deduplicate_countries(self, countries: List[CountryInfo]) -> List[CountryInfo]:
        """Remove duplicate countries from the list"""
        seen_codes = set()
        unique_countries = []

        for country in countries:
            if country.code not in seen_codes and country.code not in self.known_countries:
                seen_codes.add(country.code)
                unique_countries.append(country)

        return unique_countries

    async def _enrich_country_data(self, countries: List[CountryInfo]) -> List[CountryInfo]:
        """Enrich country data with additional information"""
        enriched = []

        for country in countries:
            # Add phone prefixes
            if country.code in self.country_phone_prefixes:
                country.phone_prefixes = self.country_phone_prefixes[country.code]

            # Add domain extensions
            country.domains.append(f".{country.code.lower()}")

            # Assess gambling legality (simplified)
            country.gambling_legal = self._assess_gambling_legality(country)

            # Estimate casino density
            country.casino_density = self._estimate_casino_density(country)

            enriched.append(country)

        return enriched

    def _assess_gambling_potential(self, country: CountryInfo) -> bool:
        """Assess if a country has gambling potential"""
        # Simple heuristic-based assessment
        high_potential_indicators = [
            'casino' in ' '.join(country.search_terms).lower(),
            country.gambling_legal,
            country.casino_density in ['high', 'medium'],
            len(country.discovered_sources) > 1  # Found in multiple sources
        ]

        return sum(high_potential_indicators) >= 2

    def _assess_gambling_legality(self, country: CountryInfo) -> bool:
        """Assess if gambling is legal in the country"""
        # Simplified assessment - in real implementation, use comprehensive legal database
        legal_countries = {
            'VN', 'LA', 'KH', 'US', 'GB', 'DE', 'FR', 'IT', 'ES',
            'AU', 'CA', 'BR', 'MX', 'AR', 'CL', 'IN', 'TH', 'MY',
            'SG', 'PH', 'ID', 'RU', 'PL', 'NL', 'BE', 'CH', 'AT',
            'SE', 'NO', 'DK', 'FI', 'PT', 'GR', 'TR', 'ZA', 'EG',
            'AE', 'SA', 'HK', 'TW', 'NZ'
        }

        return country.code in legal_countries

    def _estimate_casino_density(self, country: CountryInfo) -> str:
        """Estimate casino density in the country"""
        # Simplified estimation based on known data
        high_density = {'VN', 'KH', 'US', 'AU', 'GB', 'DE', 'IT', 'ES', 'FR'}
        medium_density = {'LA', 'TH', 'MY', 'SG', 'PH', 'ID', 'BR', 'MX', 'TR', 'ZA', 'AE'}

        if country.code in high_density:
            return 'high'
        elif country.code in medium_density:
            return 'medium'
        else:
            return 'low'

    def _country_name_to_code(self, name: str) -> Optional[str]:
        """Convert country name to ISO code"""
        # Simplified mapping - in real implementation, use a comprehensive database
        name_to_code = {
            'Vietnam': 'VN', 'Viet Nam': 'VN',
            'Laos': 'LA', 'Lao': 'LA',
            'Cambodia': 'KH', 'Kampuchea': 'KH',
            'United States': 'US', 'USA': 'US', 'America': 'US',
            'United Kingdom': 'GB', 'UK': 'GB', 'Britain': 'GB',
            'Germany': 'DE', 'Deutschland': 'DE',
            'France': 'FR', 'French': 'FR',
            'Italy': 'IT', 'Italia': 'IT',
            'Spain': 'ES', 'Espana': 'ES',
            'Australia': 'AU',
            'Canada': 'CA',
            'Brazil': 'BR', 'Brasil': 'BR',
            'Mexico': 'MX', 'México': 'MX',
            'Argentina': 'AR',
            'Chile': 'CL',
            'India': 'IN',
            'Thailand': 'TH',
            'Malaysia': 'MY',
            'Singapore': 'SG',
            'Philippines': 'PH',
            'Indonesia': 'ID',
            'Russia': 'RU',
            'Poland': 'PL',
            'Netherlands': 'NL',
            'Belgium': 'BE',
            'Switzerland': 'CH',
            'Austria': 'AT',
            'Sweden': 'SE',
            'Norway': 'NO',
            'Denmark': 'DK',
            'Finland': 'FI',
            'Portugal': 'PT',
            'Greece': 'GR',
            'Turkey': 'TR',
            'South Africa': 'ZA',
            'Egypt': 'EG',
            'Nigeria': 'NG',
            'Kenya': 'KE',
            'Morocco': 'MA',
            'UAE': 'AE', 'Dubai': 'AE',
            'Saudi Arabia': 'SA',
            'Israel': 'IL',
            'Hong Kong': 'HK',
            'Taiwan': 'TW',
            'New Zealand': 'NZ',
        }

        return name_to_code.get(name.strip())

    def _is_country_name(self, text: str) -> bool:
        """Check if text looks like a country name"""
        if len(text) < 3 or len(text) > 50:
            return False

        # Exclude common non-country words
        exclude_words = {
            'Casino', 'Gambling', 'Online', 'Legal', 'License', 'Betting',
            'Poker', 'Slots', 'Blackjack', 'Roulette', 'Baccarat', 'Craps',
            'Sports', 'Horse', 'Racing', 'Lottery', 'Bingo', 'Keno'
        }

        if text in exclude_words:
            return False

        # Should start with capital letter and not be all caps
        return text[0].isupper() and not text.isupper()

    def _guess_language(self, country_name: str) -> str:
        """Guess primary language for a country"""
        language_map = {
            'VN': 'vi', 'LA': 'lo', 'KH': 'km', 'US': 'en', 'GB': 'en',
            'DE': 'de', 'FR': 'fr', 'IT': 'it', 'ES': 'es', 'CN': 'zh',
            'JP': 'ja', 'KR': 'ko', 'AU': 'en', 'CA': 'en', 'BR': 'pt',
            'MX': 'es', 'AR': 'es', 'CL': 'es', 'IN': 'hi', 'TH': 'th',
            'MY': 'ms', 'SG': 'en', 'PH': 'tl', 'ID': 'id', 'RU': 'ru'
        }

        code = self._country_name_to_code(country_name)
        return language_map.get(code, 'en')

    def _guess_timezone(self, country_name: str) -> str:
        """Guess timezone for a country"""
        timezone_map = {
            'VN': 'Asia/Ho_Chi_Minh', 'LA': 'Asia/Vientiane', 'KH': 'Asia/Phnom_Penh',
            'US': 'America/New_York', 'GB': 'Europe/London', 'DE': 'Europe/Berlin',
            'FR': 'Europe/Paris', 'IT': 'Europe/Rome', 'ES': 'Europe/Madrid',
            'AU': 'Australia/Sydney', 'CA': 'America/Toronto', 'BR': 'America/Sao_Paulo',
            'MX': 'America/Mexico_City', 'AR': 'America/Argentina/Buenos_Aires',
            'CL': 'America/Santiago', 'IN': 'Asia/Kolkata', 'TH': 'Asia/Bangkok',
            'MY': 'Asia/Kuala_Lumpur', 'SG': 'Asia/Singapore', 'PH': 'Asia/Manila',
            'ID': 'Asia/Jakarta', 'RU': 'Europe/Moscow', 'JP': 'Asia/Tokyo',
            'KR': 'Asia/Seoul', 'CN': 'Asia/Shanghai', 'HK': 'Asia/Hong_Kong',
            'TW': 'Asia/Taipei', 'NZ': 'Pacific/Auckland', 'ZA': 'Africa/Johannesburg',
            'EG': 'Africa/Cairo', 'AE': 'Asia/Dubai', 'SA': 'Asia/Riyadh'
        }

        code = self._country_name_to_code(country_name)
        return timezone_map.get(code, 'UTC')

    def add_countries_to_config(self, countries: List[CountryInfo], config_path: str = "config/config.yaml"):
        """Add discovered countries to the configuration file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            if 'regions' not in config:
                config['regions'] = {}

            added_count = 0
            for country in countries:
                if country.code not in config['regions']:
                    config['regions'][country.code] = {
                        'country_code': country.code,
                        'language': country.language,
                        'timezone': country.timezone,
                        'search_terms': country.search_terms,
                        'domains': country.domains,
                        'ports': [80, 443, 8080, 8443]
                    }
                    added_count += 1

            if added_count > 0:
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)

                logger.info(f"Added {added_count} new countries to configuration")

                # Create target files for new countries
                self._create_target_files(countries, config_path)

        except Exception as e:
            logger.error(f"Failed to update config: {e}")

    def _create_target_files(self, countries: List[CountryInfo], config_path: str):
        """Create target YAML files for new countries"""
        targets_dir = Path(config_path).parent.parent / "targets"

        for country in countries:
            target_file = targets_dir / f"{country.code.lower()}.yaml"

            if not target_file.exists():
                target_data = {
                    'region': country.name.lower().replace(' ', '_'),
                    'targets': [{
                        'url': f"https://example-{country.code.lower()}.com",
                        'name': f"Example Casino {country.name}",
                        'region': country.name.lower().replace(' ', '_'),
                        'description': f"Sample target for {country.name} region (auto-discovered)",
                        'tags': ['casino', 'gambling', 'auto-discovered'],
                        'priority': 5,
                        'status': 'pending',
                        'notes': f"Auto-discovered on {datetime.now().isoformat()}"
                    }]
                }

                try:
                    with open(target_file, 'w') as f:
                        yaml.dump(target_data, f, default_flow_style=False)
                    logger.info(f"Created target file: {target_file}")
                except Exception as e:
                    logger.error(f"Failed to create target file {target_file}: {e}")

    async def run_discovery_cycle(self, max_countries: int = 10) -> Dict:
        """Run a complete discovery cycle"""
        logger.info("Starting automated region discovery cycle")

        try:
            # Discover new regions
            new_countries = await self.discover_new_regions(max_countries)

            # Add to configuration
            if new_countries:
                self.add_countries_to_config(new_countries)

            return {
                'success': True,
                'countries_discovered': len(new_countries),
                'countries': [c.__dict__ for c in new_countries],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Discovery cycle failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Standalone discovery runner
async def discover_regions():
    """Standalone function to discover new regions"""
    discovery = AutoRegionDiscovery()

    try:
        await discovery.start()
        result = await discovery.run_discovery_cycle()

        print(f"Discovery Results: {json.dumps(result, indent=2)}")

    finally:
        await discovery.stop()


if __name__ == "__main__":
    asyncio.run(discover_regions())
