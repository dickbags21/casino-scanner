"""
Intelligent Target Discovery System
Automatically discovers casino websites and gambling platforms in target countries
"""

import asyncio
import logging
import json
import yaml
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, urljoin
import hashlib

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    async_playwright = None
    Page = None
    Browser = None
    BrowserContext = None

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredTarget:
    """Information about a discovered casino target"""
    url: str
    name: str
    region: str
    country_code: str
    discovery_method: str
    confidence_score: float  # 0.0 to 1.0
    casino_type: str  # 'online', 'land_based', 'sportsbook', 'lottery', 'poker'
    language: str
    features_detected: List[str]
    social_media: Dict[str, str]  # platform -> url
    licensing_info: Dict[str, str]
    discovered_at: str
    last_checked: str
    status: str  # 'active', 'inactive', 'suspended'
    priority_score: float  # For scanning prioritization

    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now().isoformat()
        if not self.last_checked:
            self.last_checked = self.discovered_at
        if not self.features_detected:
            self.features_detected = []
        if not self.social_media:
            self.social_media = {}
        if not self.licensing_info:
            self.licensing_info = {}

    def calculate_priority_score(self) -> float:
        """Calculate priority score for scanning"""
        base_score = self.confidence_score

        # Boost for certain features
        feature_multipliers = {
            'signup_form': 1.2,
            'bonus_offers': 1.3,
            'live_casino': 1.1,
            'sports_betting': 1.1,
            'mobile_app': 1.2,
            'crypto_payments': 1.4,
            'high_traffic': 1.3
        }

        for feature in self.features_detected:
            if feature in feature_multipliers:
                base_score *= feature_multipliers[feature]

        # Boost for known licensing
        if self.licensing_info:
            base_score *= 1.5

        # Boost for social media presence (indicates legitimacy)
        if self.social_media:
            base_score *= 1.1

        self.priority_score = min(base_score, 1.0)  # Cap at 1.0
        return self.priority_score


class IntelligentTargetDiscovery:
    """
    Intelligent system for discovering casino targets using multiple discovery methods
    """

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None

        # Discovery sources
        self.search_engines = [
            'google', 'bing', 'duckduckgo', 'yahoo'
        ]

        self.social_platforms = [
            'twitter', 'facebook', 'instagram', 'linkedin'
        ]

        self.forum_sites = [
            'reddit.com/r/onlinegambling',
            'forum.gamblingcommission.gov.uk',
            'casino.org/forum',
            'casinomeister.com/forum'
        ]

        # Casino domain patterns
        self.casino_domain_patterns = [
            r'casino\..*', r'bet\..*', r'poker\..*', r'slots\..*',
            r'games\..*', r'play\..*', r'wager\..*', r'gamble\..*',
            r'jackpot\..*', r'blackjack\..*', r'roulette\..*'
        ]

        # Known casino TLDs by region
        self.regional_tlds = {
            'VN': ['.vn', '.com.vn', '.net.vn'],
            'LA': ['.la'],
            'KH': ['.kh'],
            'US': ['.com', '.net', '.org', '.casino', '.bet'],
            'GB': ['.co.uk', '.uk', '.com'],
            'DE': ['.de', '.com'],
            'FR': ['.fr', '.com'],
            'IT': ['.it', '.com'],
            'ES': ['.es', '.com'],
            'AU': ['.com.au', '.au'],
            'CA': ['.ca', '.com'],
            'BR': ['.com.br', '.br'],
            'MX': ['.com.mx', '.mx'],
            'AR': ['.com.ar', '.ar'],
            'CL': ['.cl', '.com'],
            'IN': ['.in', '.co.in'],
            'TH': ['.co.th', '.th'],
            'MY': ['.com.my', '.my'],
            'SG': ['.com.sg', '.sg'],
            'PH': ['.com.ph', '.ph'],
            'ID': ['.co.id', '.id'],
            'RU': ['.ru', '.com'],
            'PL': ['.pl', '.com'],
            'NL': ['.nl', '.com'],
            'BE': ['.be', '.com'],
            'CH': ['.ch', '.com'],
            'AT': ['.at', '.com'],
            'SE': ['.se', '.com'],
            'NO': ['.no', '.com'],
            'DK': ['.dk', '.com'],
            'FI': ['.fi', '.com'],
            'PT': ['.pt', '.com'],
            'GR': ['.gr', '.com'],
            'TR': ['.com.tr', '.tr'],
            'ZA': ['.co.za', '.za'],
            'EG': ['.com.eg', '.eg'],
            'NG': ['.com.ng', '.ng'],
            'KE': ['.co.ke', '.ke'],
            'MA': ['.ma', '.com'],
            'AE': ['.ae', '.com'],
            'SA': ['.com.sa', '.sa'],
            'IL': ['.co.il', '.il'],
            'HK': ['.com.hk', '.hk'],
            'TW': ['.com.tw', '.tw'],
            'NZ': ['.co.nz', '.nz']
        }

    async def start(self):
        """Start browser instance"""
        if async_playwright is None:
            raise ImportError("Playwright is not installed")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        logger.info("Intelligent target discovery browser started")

    async def stop(self):
        """Stop browser instance"""
        if self.browser:
            await self.browser.close()
        logger.info("Intelligent target discovery browser stopped")

    async def discover_targets_for_region(self, region: str, country_code: str,
                                        max_targets: int = 50) -> List[DiscoveredTarget]:
        """
        Discover casino targets for a specific region/country

        Args:
            region: Region name (e.g., 'vietnam', 'germany')
            country_code: ISO country code (e.g., 'VN', 'DE')
            max_targets: Maximum number of targets to discover

        Returns:
            List of discovered targets
        """
        logger.info(f"Starting target discovery for {region} ({country_code})")

        all_targets = []

        # Method 1: Search engine discovery
        search_targets = await self._discover_via_search_engines(region, country_code)
        all_targets.extend(search_targets)

        # Method 2: Social media discovery
        social_targets = await self._discover_via_social_media(region, country_code)
        all_targets.extend(social_targets)

        # Method 3: Forum and community discovery
        forum_targets = await self._discover_via_forums(region, country_code)
        all_targets.extend(forum_targets)

        # Method 4: Directory and listing sites
        directory_targets = await self._discover_via_directories(region, country_code)
        all_targets.extend(directory_targets)

        # Method 5: App store analysis
        app_store_targets = await self._discover_via_app_stores(region, country_code)
        all_targets.extend(app_store_targets)

        # Deduplicate and filter
        unique_targets = self._deduplicate_targets(all_targets)

        # Enrich target information
        enriched_targets = await self._enrich_targets(unique_targets[:max_targets])

        # Calculate priority scores
        for target in enriched_targets:
            target.calculate_priority_score()

        logger.info(f"Discovered {len(enriched_targets)} targets for {region}")
        return enriched_targets

    async def _discover_via_search_engines(self, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Discover targets via search engines"""
        targets = []

        # Generate search queries for the region
        search_queries = self._generate_search_queries(region, country_code)

        for query in search_queries:
            for engine in self.search_engines[:2]:  # Limit to first 2 engines
                try:
                    engine_targets = await self._search_engine_query(query, engine, country_code)
                    targets.extend(engine_targets)
                    await asyncio.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Search engine query failed: {engine} - {query} - {e}")

        return targets

    def _generate_search_queries(self, region: str, country_code: str) -> List[str]:
        """Generate relevant search queries for a region"""
        base_terms = [
            'online casino', 'casino online', 'gambling site', 'betting website',
            'poker online', 'slots online', 'sports betting', 'casino bonus'
        ]

        region_terms = [region.lower()]
        if country_code != region.upper():
            region_terms.append(country_code.lower())

        queries = []

        # Combine base terms with region terms
        for base in base_terms:
            for region_term in region_terms:
                queries.extend([
                    f'{base} {region_term}',
                    f'{base} in {region_term}',
                    f'best {base} {region_term}',
                    f'{region_term} {base} sites'
                ])

        # Add licensing queries
        queries.extend([
            f'licensed casino {region}',
            f'gambling license {region}',
            f'regulated casino {country_code}'
        ])

        return queries[:20]  # Limit queries

    async def _search_engine_query(self, query: str, engine: str, country_code: str) -> List[DiscoveredTarget]:
        """Query a specific search engine"""
        if not self.browser:
            await self.start()

        targets = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            # Construct search URL
            if engine == 'google':
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=20"
            elif engine == 'bing':
                search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&count=20"
            elif engine == 'duckduckgo':
                search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
            else:
                search_url = f"https://search.yahoo.com/search?q={query.replace(' ', '+')}&n=20"

            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout)

            # Extract links from search results
            link_selectors = [
                'a[href^="http"]',
                '.result a[href^="http"]',
                '.b_algo a[href^="http"]',
                'h2 a[href^="http"]'
            ]

            found_urls = set()

            for selector in link_selectors:
                links = await page.query_selector_all(selector)
                for link in links:
                    try:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            url = self._clean_url(href)
                            if url and self._is_casino_url(url, country_code) and url not in found_urls:
                                found_urls.add(url)

                                target = DiscoveredTarget(
                                    url=url,
                                    name=self._extract_site_name(url),
                                    region=region,
                                    country_code=country_code,
                                    discovery_method=f'search_{engine}',
                                    confidence_score=0.7,
                                    casino_type=self._guess_casino_type(url),
                                    language=self._guess_language(country_code),
                                    features_detected=[],
                                    social_media={},
                                    licensing_info={},
                                    discovered_at=datetime.now().isoformat(),
                                    last_checked='',
                                    status='pending',
                                    priority_score=0.0
                                )
                                targets.append(target)

                    except Exception as e:
                        continue

            # Limit targets per query
            targets = targets[:10]

        except Exception as e:
            logger.warning(f"Search engine query failed: {engine} - {query} - {e}")
        finally:
            await page.close()
            await context.close()

        return targets

    async def _discover_via_social_media(self, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Discover targets via social media platforms"""
        targets = []

        # Focus on casino-related social media accounts
        casino_accounts = [
            'casino', 'poker', 'betting', 'gambling', 'slots'
        ]

        for platform in self.social_platforms[:2]:  # Limit platforms
            for account_type in casino_accounts:
                try:
                    platform_targets = await self._scrape_social_platform(platform, account_type, region, country_code)
                    targets.extend(platform_targets)
                except Exception as e:
                    logger.warning(f"Social media discovery failed: {platform} - {account_type} - {e}")

        return targets

    async def _scrape_social_platform(self, platform: str, search_term: str,
                                    region: str, country_code: str) -> List[DiscoveredTarget]:
        """Scrape casino targets from a social media platform"""
        if not self.browser:
            await self.start()

        targets = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            # Construct platform search URL
            if platform == 'twitter':
                search_url = f"https://twitter.com/search?q={search_term}%20{region}&src=typed_query"
            elif platform == 'facebook':
                search_url = f"https://www.facebook.com/search/pages/?q={search_term}%20{region}"
            elif platform == 'instagram':
                search_url = f"https://www.instagram.com/explore/tags/{search_term}{region}/"
            elif platform == 'linkedin':
                search_url = f"https://www.linkedin.com/search/results/all/?keywords={search_term}%20{region}"
            else:
                return targets

            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout)

            # Extract casino website links from profiles/posts
            casino_urls = set()

            # Look for website links in profiles
            link_selectors = [
                'a[href^="http"]',
                '[data-url]',
                '.profile-link',
                '.website-link'
            ]

            for selector in link_selectors:
                links = await page.query_selector_all(selector)
                for link in links:
                    try:
                        href = await link.get_attribute('href') or await link.get_attribute('data-url')
                        if href and href.startswith('http'):
                            url = self._clean_url(href)
                            if url and self._is_casino_url(url, country_code):
                                casino_urls.add(url)
                    except:
                        continue

            # Convert found URLs to targets
            for url in casino_urls:
                target = DiscoveredTarget(
                    url=url,
                    name=self._extract_site_name(url),
                    region=region,
                    country_code=country_code,
                    discovery_method=f'social_{platform}',
                    confidence_score=0.6,
                    casino_type=self._guess_casino_type(url),
                    language=self._guess_language(country_code),
                    features_detected=[],
                    social_media={platform: search_url},
                    licensing_info={},
                    discovered_at=datetime.now().isoformat(),
                    last_checked='',
                    status='pending',
                    priority_score=0.0
                )
                targets.append(target)

        except Exception as e:
            logger.warning(f"Social platform scraping failed: {platform} - {e}")
        finally:
            await page.close()
            await context.close()

        return targets[:5]  # Limit per platform

    async def _discover_via_forums(self, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Discover targets via gambling forums and communities"""
        targets = []

        for forum_url in self.forum_sites[:3]:  # Limit forums
            try:
                forum_targets = await self._scrape_forum_site(forum_url, region, country_code)
                targets.extend(forum_targets)
            except Exception as e:
                logger.warning(f"Forum scraping failed: {forum_url} - {e}")

        return targets

    async def _scrape_forum_site(self, forum_base: str, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Scrape casino URLs from a forum site"""
        if not self.browser:
            await self.start()

        targets = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            # Search for region-specific casino discussions
            search_url = f"{forum_base}/search?q={region}%20casino"

            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout)

            # Extract URLs from forum posts
            casino_urls = set()

            link_selectors = [
                'a[href^="http"]',
                '.post-content a[href^="http"]',
                '.message a[href^="http"]'
            ]

            for selector in link_selectors:
                links = await page.query_selector_all(selector)
                for link in links:
                    try:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            url = self._clean_url(href)
                            if url and self._is_casino_url(url, country_code):
                                casino_urls.add(url)
                    except:
                        continue

            # Convert to targets
            for url in casino_urls:
                target = DiscoveredTarget(
                    url=url,
                    name=self._extract_site_name(url),
                    region=region,
                    country_code=country_code,
                    discovery_method='forum',
                    confidence_score=0.8,  # Forums often have legitimate recommendations
                    casino_type=self._guess_casino_type(url),
                    language=self._guess_language(country_code),
                    features_detected=[],
                    social_media={},
                    licensing_info={},
                    discovered_at=datetime.now().isoformat(),
                    last_checked='',
                    status='pending',
                    priority_score=0.0
                )
                targets.append(target)

        except Exception as e:
            logger.warning(f"Forum scraping failed: {forum_base} - {e}")
        finally:
            await page.close()
            await context.close()

        return targets[:5]  # Limit per forum

    async def _discover_via_directories(self, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Discover targets via casino directory and listing sites"""
        targets = []

        directory_sites = [
            'https://www.casino.org',
            'https://www.gamblingcommission.gov.uk',
            'https://www.casinomeister.com',
            'https://www.casinocity.com',
            'https://www.onlinecasinos.com'
        ]

        for directory_url in directory_sites[:3]:
            try:
                dir_targets = await self._scrape_directory_site(directory_url, region, country_code)
                targets.extend(dir_targets)
            except Exception as e:
                logger.warning(f"Directory scraping failed: {directory_url} - {e}")

        return targets

    async def _scrape_directory_site(self, directory_url: str, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Scrape casino listings from directory sites"""
        if not self.browser:
            await self.start()

        targets = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            # Search for region-specific casinos
            search_url = f"{directory_url}/search?q={region}"

            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout)

            # Extract casino links
            casino_urls = set()

            link_selectors = [
                '.casino-link a',
                '.casino-item a[href]',
                '.directory-item a',
                'a[href*="casino"]'
            ]

            for selector in link_selectors:
                links = await page.query_selector_all(selector)
                for link in links:
                    try:
                        href = await link.get_attribute('href')
                        if href:
                            # Convert relative URLs to absolute
                            if not href.startswith('http'):
                                href = urljoin(directory_url, href)

                            url = self._clean_url(href)
                            if url and self._is_casino_url(url, country_code):
                                casino_urls.add(url)
                    except:
                        continue

            # Convert to targets
            for url in casino_urls:
                target = DiscoveredTarget(
                    url=url,
                    name=self._extract_site_name(url),
                    region=region,
                    country_code=country_code,
                    discovery_method='directory',
                    confidence_score=0.9,  # Directories are usually reliable
                    casino_type=self._guess_casino_type(url),
                    language=self._guess_language(country_code),
                    features_detected=[],
                    social_media={},
                    licensing_info={},
                    discovered_at=datetime.now().isoformat(),
                    last_checked='',
                    status='pending',
                    priority_score=0.0
                )
                targets.append(target)

        except Exception as e:
            logger.warning(f"Directory scraping failed: {directory_url} - {e}")
        finally:
            await page.close()
            await context.close()

        return targets[:10]  # Limit per directory

    async def _discover_via_app_stores(self, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Discover targets via mobile app stores"""
        targets = []

        # App store search for casino apps
        app_store_urls = [
            f"https://play.google.com/store/search?q=casino&c=apps&gl={country_code}",
            f"https://apps.apple.com/{country_code.lower()}/app/id123456789"  # Would need proper app store URLs
        ]

        for store_url in app_store_urls[:1]:  # Limit for now
            try:
                store_targets = await self._scrape_app_store(store_url, region, country_code)
                targets.extend(store_targets)
            except Exception as e:
                logger.warning(f"App store scraping failed: {store_url} - {e}")

        return targets

    async def _scrape_app_store(self, store_url: str, region: str, country_code: str) -> List[DiscoveredTarget]:
        """Scrape casino apps from app stores"""
        if not self.browser:
            await self.start()

        targets = []
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(store_url, wait_until='networkidle', timeout=self.timeout)

            # Extract website links from app descriptions
            website_links = set()

            link_selectors = [
                'a[href^="http"]',
                '.website-link',
                '.developer-website a'
            ]

            for selector in link_selectors:
                links = await page.query_selector_all(selector)
                for link in links:
                    try:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            url = self._clean_url(href)
                            if url and self._is_casino_url(url, country_code):
                                website_links.add(url)
                    except:
                        continue

            # Convert to targets
            for url in website_links:
                target = DiscoveredTarget(
                    url=url,
                    name=self._extract_site_name(url),
                    region=region,
                    country_code=country_code,
                    discovery_method='app_store',
                    confidence_score=0.8,
                    casino_type='online',  # App store apps are typically online casinos
                    language=self._guess_language(country_code),
                    features_detected=['mobile_app'],
                    social_media={},
                    licensing_info={},
                    discovered_at=datetime.now().isoformat(),
                    last_checked='',
                    status='pending',
                    priority_score=0.0
                )
                targets.append(target)

        except Exception as e:
            logger.warning(f"App store scraping failed: {store_url} - {e}")
        finally:
            await page.close()
            await context.close()

        return targets[:5]

    def _deduplicate_targets(self, targets: List[DiscoveredTarget]) -> List[DiscoveredTarget]:
        """Remove duplicate targets based on URL"""
        seen_urls = set()
        unique_targets = []

        for target in targets:
            url_key = self._normalize_url(target.url)
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                unique_targets.append(target)

        return unique_targets

    async def _enrich_targets(self, targets: List[DiscoveredTarget]) -> List[DiscoveredTarget]:
        """Enrich targets with additional information by visiting sites"""
        enriched = []

        for target in targets:
            try:
                enriched_target = await self._enrich_single_target(target)
                enriched.append(enriched_target)
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to enrich target {target.url}: {e}")
                enriched.append(target)  # Add anyway

        return enriched

    async def _enrich_single_target(self, target: DiscoveredTarget) -> DiscoveredTarget:
        """Enrich a single target with site information"""
        if not self.browser:
            await self.start()

        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(target.url, wait_until='networkidle', timeout=15000)

            # Check if site is accessible
            status_code = 200  # Assume success if we got here
            if status_code == 200:
                target.status = 'active'
            else:
                target.status = 'inactive'
                return target

            target.last_checked = datetime.now().isoformat()

            # Detect features
            features = await self._detect_site_features(page)
            target.features_detected = features

            # Extract social media links
            social_links = await self._extract_social_media_links(page)
            target.social_media.update(social_links)

            # Check for licensing information
            licensing = await self._extract_licensing_info(page)
            target.licensing_info.update(licensing)

            # Boost confidence if features detected
            if features:
                target.confidence_score = min(target.confidence_score + 0.1, 1.0)

        except Exception as e:
            logger.warning(f"Site enrichment failed for {target.url}: {e}")
            target.status = 'inactive'
        finally:
            await page.close()
            await context.close()

        return target

    async def _detect_site_features(self, page: Page) -> List[str]:
        """Detect casino features on the page"""
        features = []

        # Check for signup/registration forms
        signup_selectors = [
            'form[action*="signup"]', 'form[action*="register"]',
            'input[name*="email"]', 'input[type="email"]',
            'button:has-text("Sign Up")', 'button:has-text("Register")'
        ]

        for selector in signup_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    features.append('signup_form')
                    break
            except:
                continue

        # Check for bonus offers
        bonus_keywords = ['bonus', 'free', 'deposit', 'welcome', 'promotion']
        page_text = (await page.inner_text('body')).lower()

        for keyword in bonus_keywords:
            if keyword in page_text:
                features.append('bonus_offers')
                break

        # Check for live casino
        if 'live casino' in page_text or 'live dealer' in page_text:
            features.append('live_casino')

        # Check for sports betting
        if 'sports' in page_text and ('bet' in page_text or 'odds' in page_text):
            features.append('sports_betting')

        # Check for crypto payments
        crypto_keywords = ['bitcoin', 'crypto', 'ethereum', 'blockchain']
        for keyword in crypto_keywords:
            if keyword in page_text:
                features.append('crypto_payments')
                break

        return features

    async def _extract_social_media_links(self, page: Page) -> Dict[str, str]:
        """Extract social media links from the page"""
        social_media = {}

        social_patterns = {
            'twitter': r'twitter\.com/(\w+)',
            'facebook': r'facebook\.com/(\w+)',
            'instagram': r'instagram\.com/(\w+)',
            'linkedin': r'linkedin\.com/(\w+)',
            'youtube': r'youtube\.com/(\w+)'
        }

        page_text = await page.inner_text('body')

        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                social_media[platform] = f"https://{platform}.com/{matches[0]}"

        return social_media

    async def _extract_licensing_info(self, page: Page) -> Dict[str, str]:
        """Extract licensing and regulatory information"""
        licensing = {}

        license_keywords = [
            'license', 'licensed', 'regulated', 'regulation',
            'gambling commission', 'mga', 'curacao', 'malta'
        ]

        page_text = (await page.inner_text('body')).lower()

        for keyword in license_keywords:
            if keyword in page_text:
                licensing[keyword] = 'detected'

        return licensing

    def _clean_url(self, url: str) -> Optional[str]:
        """Clean and normalize URL"""
        try:
            parsed = urlparse(url)
            # Remove tracking parameters
            cleaned = parsed._replace(query='', fragment='').geturl()
            return cleaned.rstrip('/')
        except:
            return None

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        try:
            parsed = urlparse(url.lower())
            return f"{parsed.netloc}{parsed.path}".rstrip('/')
        except:
            return url.lower()

    def _is_casino_url(self, url: str, country_code: str) -> bool:
        """Check if URL is likely a casino site"""
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc

            # Check domain patterns
            for pattern in self.casino_domain_patterns:
                if re.search(pattern, domain):
                    return True

            # Check regional TLDs
            if country_code in self.regional_tlds:
                for tld in self.regional_tlds[country_code]:
                    if domain.endswith(tld):
                        return True

            # Check for casino keywords in domain
            casino_keywords = ['casino', 'bet', 'poker', 'slots', 'games', 'play', 'wager', 'gamble']
            domain_parts = domain.replace('.', ' ').split()
            for keyword in casino_keywords:
                if keyword in domain_parts:
                    return True

            return False

        except:
            return False

    def _extract_site_name(self, url: str) -> str:
        """Extract site name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc

            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]

            # Take first part before first dot
            name = domain.split('.')[0]

            # Capitalize
            return name.title()

        except:
            return "Unknown Casino"

    def _guess_casino_type(self, url: str) -> str:
        """Guess casino type from URL"""
        url_lower = url.lower()

        if 'poker' in url_lower:
            return 'poker'
        elif 'sports' in url_lower or 'bet' in url_lower:
            return 'sportsbook'
        elif 'lottery' in url_lower or 'lotto' in url_lower:
            return 'lottery'
        else:
            return 'online'

    def _guess_language(self, country_code: str) -> str:
        """Guess primary language for country"""
        language_map = {
            'VN': 'vi', 'LA': 'lo', 'KH': 'km', 'US': 'en', 'GB': 'en',
            'DE': 'de', 'FR': 'fr', 'IT': 'it', 'ES': 'es', 'CN': 'zh',
            'JP': 'ja', 'KR': 'ko', 'AU': 'en', 'CA': 'en', 'BR': 'pt',
            'MX': 'es', 'AR': 'es', 'CL': 'es', 'IN': 'hi', 'TH': 'th',
            'MY': 'ms', 'SG': 'en', 'PH': 'tl', 'ID': 'id', 'RU': 'ru'
        }

        return language_map.get(country_code, 'en')

    def save_targets_to_config(self, targets: List[DiscoveredTarget],
                             config_path: str = "config/config.yaml"):
        """Save discovered targets to target files"""
        from pathlib import Path

        targets_dir = Path(config_path).parent.parent / "targets"

        # Group targets by region
        region_targets = {}
        for target in targets:
            region = target.region
            if region not in region_targets:
                region_targets[region] = []
            region_targets[region].append(target)

        # Save to YAML files
        for region, region_targets_list in region_targets.items():
            target_file = targets_dir / f"{region}.yaml"

            # Load existing data if file exists
            if target_file.exists():
                try:
                    with open(target_file, 'r') as f:
                        data = yaml.safe_load(f) or {'region': region, 'targets': []}
                except:
                    data = {'region': region, 'targets': []}
            else:
                data = {'region': region, 'targets': []}

            # Add new targets
            for target in region_targets_list:
                new_target = {
                    'url': target.url,
                    'name': target.name,
                    'region': target.region,
                    'description': f"Auto-discovered via {target.discovery_method}",
                    'tags': ['casino', 'gambling', 'auto-discovered', target.casino_type],
                    'priority': int(target.priority_score * 10),  # Convert to 1-10 scale
                    'status': target.status,
                    'notes': f"Discovered: {target.discovered_at}, Confidence: {target.confidence_score}",
                    'features': target.features_detected,
                    'social_media': target.social_media,
                    'licensing': target.licensing_info
                }

                # Check if target already exists
                existing_urls = {t.get('url') for t in data['targets']}
                if target.url not in existing_urls:
                    data['targets'].append(new_target)

            # Save updated data
            try:
                with open(target_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
                logger.info(f"Saved {len(region_targets_list)} targets to {target_file}")
            except Exception as e:
                logger.error(f"Failed to save targets to {target_file}: {e}")

    async def run_discovery_cycle(self, regions: List[Tuple[str, str]],
                                max_targets_per_region: int = 25) -> Dict:
        """Run a complete target discovery cycle"""
        logger.info("Starting intelligent target discovery cycle")

        results = {
            'regions_processed': len(regions),
            'total_targets_discovered': 0,
            'targets_by_region': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            for region_name, country_code in regions:
                logger.info(f"Discovering targets for {region_name} ({country_code})")

                targets = await self.discover_targets_for_region(
                    region_name, country_code, max_targets_per_region
                )

                # Save to config
                self.save_targets_to_config(targets)

                results['targets_by_region'][region_name] = {
                    'targets_found': len(targets),
                    'high_priority': len([t for t in targets if t.priority_score > 0.7]),
                    'with_features': len([t for t in targets if t.features_detected])
                }

                results['total_targets_discovered'] += len(targets)

                logger.info(f"Found {len(targets)} targets for {region_name}")

        except Exception as e:
            logger.error(f"Discovery cycle failed: {e}")
            results['error'] = str(e)

        return results


# Standalone discovery runner
async def discover_casino_targets():
    """Standalone function to discover casino targets"""
    discovery = IntelligentTargetDiscovery()

    # Example regions to discover
    regions = [
        ('vietnam', 'VN'),
        ('cambodia', 'KH'),
        ('laos', 'LA'),
        ('germany', 'DE'),
        ('united_kingdom', 'GB')
    ]

    try:
        await discovery.start()
        result = await discovery.run_discovery_cycle(regions)
        print(f"Discovery Results: {json.dumps(result, indent=2)}")
    finally:
        await discovery.stop()


if __name__ == "__main__":
    asyncio.run(discover_casino_targets())
