"""
Casino Review Site Parser
Parses casino review sites (like ex.casino) to extract casino listings and data
"""

import asyncio
import logging
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Page, Browser  # pyright: ignore[reportMissingImports]
except ImportError:
    logging.warning("Playwright not installed. Install with: pip install playwright && playwright install")
    async_playwright = None

logger = logging.getLogger(__name__)


@dataclass
class CasinoListing:
    """Represents a casino listing from a review site"""
    name: str
    url: str
    review_url: str
    rating: Optional[float] = None
    rating_display: Optional[str] = None  # e.g., "9.8 / 10"
    bonus_text: Optional[str] = None
    bonus_code: Optional[str] = None
    payout_percentage: Optional[float] = None
    payout_speed: Optional[str] = None
    game_count: Optional[str] = None
    countries: List[str] = None
    payment_methods: List[str] = None
    positive_features: List[str] = None
    casino_id: Optional[str] = None  # From exit links like /exit?casinoID=54
    source_site: Optional[str] = None  # The review site URL
    
    def __post_init__(self):
        if self.countries is None:
            self.countries = []
        if self.payment_methods is None:
            self.payment_methods = []
        if self.positive_features is None:
            self.positive_features = []


class CasinoReviewParser:
    """Parser for casino review sites"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize parser
        
        Args:
            headless: Run browser in headless mode
            timeout: Page timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
    
    async def start(self):
        """Start browser instance"""
        if async_playwright is None:
            raise ImportError("Playwright is not installed")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        logger.info("Browser started for review parser")
    
    async def stop(self):
        """Stop browser instance"""
        if self.browser:
            await self.browser.close()
        logger.info("Browser stopped")
    
    async def parse_ex_casino(self, url: str = "https://ex.casino", max_casinos: int = 50) -> List[CasinoListing]:
        """
        Parse ex.casino style review site
        
        Args:
            url: Base URL of the review site
            max_casinos: Maximum number of casinos to extract
            
        Returns:
            List of CasinoListing objects
        """
        if not self.browser:
            await self.start()
        
        listings = []
        context = await self.browser.new_context()
        page = await context.new_page()
        
        try:
            logger.info(f"Loading {url}...")
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Wait for casino listings to load
            await page.wait_for_selector('.casino-mikro, article[class*="casino"]', timeout=10000)
            
            # Find all casino article elements
            casino_articles = await page.query_selector_all('article.casino-mikro, article[class*="casino"]')
            logger.info(f"Found {len(casino_articles)} casino listings")
            
            for article in casino_articles[:max_casinos]:
                try:
                    listing = await self._parse_casino_article(article, page, url)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Error parsing casino article: {e}")
                    continue
            
            # Try to find more casinos by clicking "Show more" or pagination
            try:
                show_more_selectors = [
                    'a.btn-show',
                    'a:has-text("Show more")',
                    'a:has-text("Load more")',
                    '.pagination a',
                    'button:has-text("Load more")'
                ]
                
                for selector in show_more_selectors:
                    try:
                        show_more = await page.query_selector(selector)
                        if show_more and len(listings) < max_casinos:
                            await show_more.click()
                            await page.wait_for_timeout(3000)
                            
                            # Parse additional casinos
                            additional_articles = await page.query_selector_all('article.casino-mikro, article[class*="casino"]')
                            for article in additional_articles[len(listings):max_casinos]:
                                try:
                                    listing = await self._parse_casino_article(article, page, url)
                                    if listing and listing.url not in [l.url for l in listings]:
                                        listings.append(listing)
                                except:
                                    continue
                            break
                    except:
                        continue
            except:
                pass
            
            await page.close()
            await context.close()
            
            logger.info(f"Successfully parsed {len(listings)} casino listings")
            return listings
            
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            await page.close()
            await context.close()
            return listings
    
    async def _parse_casino_article(self, article, page: Page, base_url: str) -> Optional[CasinoListing]:
        """
        Parse a single casino article element
        
        HTML Structure Reference (ex.casino):
        - Casino name: <img alt="Casino Name"> in <a class="img-link">
        - Rating: <span class="rating-numbers">9.8 / 10</span> in <div class="star-rating">
        - Bonus: <p class="h6">Bonus text</p> in <article class="bonus-mini">
        - Review URL: <a class="img-link" href="/casino/casino-slug">
        - Exit URL: <a class="btn-green" href="/exit?casinoID=54">
        - Casino ID: data-history-node-id="54" on <article>
        - Payout: <strong>98.8%</strong> in .payout-block .flex-col
        - Payout speed: <strong>0-24</strong> hours in .payout-block .flex-col
        - Games: <strong>10 000+</strong> in .payout-block .flex-col
        - Countries: <span>United Kingdom</span> in .country-name
        - Payment methods: <a class="term-img" title="Method"> in .term-view (hidden section)
        - Features: <div class="flex-icon"> in .positives-block (hidden section)
        """
        try:
            # Extract casino name and URL
            name = None
            casino_url = None
            review_url = None
            casino_id = None
            
            # Extract casino ID from data-history-node-id attribute (most reliable)
            node_id = await article.get_attribute('data-history-node-id')
            if node_id:
                casino_id = node_id
            
            # Try to find name and link from img-link (primary method)
            img_link = await article.query_selector('a.img-link')
            if img_link:
                href = await img_link.get_attribute('href')
                if href:
                    review_url = urljoin(base_url, href)
                
                # Get casino name from alt text (most reliable based on HTML structure)
                img = await img_link.query_selector('img')
                if img:
                    name = await img.get_attribute('alt') or await img.get_attribute('title')
                    # Clean up name (remove " Casino" suffix if present, but keep it for now)
                    if name:
                        name = name.strip()
            
            # Try title link as fallback
            if not name:
                title_link = await article.query_selector('a[href*="casino"]')
                if title_link:
                    name = await title_link.inner_text()
                    href = await title_link.get_attribute('href')
                    if href:
                        review_url = urljoin(base_url, href)
            
            if not name:
                return None
            
            # Extract rating - look for .rating-numbers within .star-rating
            rating = None
            rating_display = None
            rating_elem = await article.query_selector('.star-rating .rating-numbers, .rating-numbers')
            if rating_elem:
                rating_text = await rating_elem.inner_text()
                rating_display = rating_text.strip()
                # Extract numeric rating (e.g., "9.8 / 10" -> 9.8)
                match = re.search(r'(\d+\.?\d*)\s*/\s*\d+', rating_text)
                if match:
                    rating = float(match.group(1))
            
            # Extract bonus information - look in .bonus-mini p.h6
            bonus_text = None
            bonus_code = None
            bonus_elem = await article.query_selector('.bonus-mini p.h6, .bonus-block p.h6')
            if bonus_elem:
                bonus_text = await bonus_elem.inner_text()
                bonus_text = bonus_text.strip()
                # Try to extract bonus code if present
                bonus_code_match = re.search(r'code[:\s]+([A-Z0-9]+)', bonus_text, re.I)
                if bonus_code_match:
                    bonus_code = bonus_code_match.group(1)
            
            # Extract payout percentage - look in .payout-block .flex-col with wallet icon
            payout_percentage = None
            payout_blocks = await article.query_selector_all('.payout-block .flex-col')
            for block in payout_blocks:
                block_text = await block.inner_text()
                if 'Payout' in block_text or '%' in block_text:
                    strong_elem = await block.query_selector('strong')
                    if strong_elem:
                        payout_text = await strong_elem.inner_text()
                        payout_match = re.search(r'(\d+\.?\d*)%', payout_text)
                        if payout_match:
                            payout_percentage = float(payout_match.group(1))
                            break
            
            # Extract payout speed - look for SVG icon with hours text
            payout_speed = None
            payout_blocks = await article.query_selector_all('.payout-block .flex-col')
            for block in payout_blocks:
                block_text = await block.inner_text()
                if 'hours' in block_text.lower() or 'payout speed' in block_text.lower():
                    strong_elem = await block.query_selector('strong')
                    if strong_elem:
                        speed_text = await block.inner_text()
                        # Extract time range (e.g., "0-24 hours payout speed")
                        speed_match = re.search(r'(\d+-\d+|\d+)\s*hours?', speed_text, re.I)
                        if speed_match:
                            payout_speed = speed_match.group(0)
                            break
            
            # Extract game count - look for dice icon with Games text
            game_count = None
            payout_blocks = await article.query_selector_all('.payout-block .flex-col')
            for block in payout_blocks:
                block_text = await block.inner_text()
                if 'Games' in block_text:
                    strong_elem = await block.query_selector('strong')
                    if strong_elem:
                        game_text = await strong_elem.inner_text()
                        # Extract game count (e.g., "10 000+")
                        game_match = re.search(r'(\d+\s*[\d\s,]*\+?)', game_text)
                        if game_match:
                            game_count = game_match.group(1).strip()
                            break
            
            # Extract countries - look in .country-name span
            countries = []
            country_elem = await article.query_selector('.country-name span, .accepted-flag .country-name span')
            if country_elem:
                country_text = await country_elem.inner_text()
                # Extract country name (e.g., "United Kingdom")
                country_text = country_text.strip()
                if country_text and country_text not in ['Available in', 'Country']:
                    countries.append(country_text)
            
            # Extract payment methods - need to expand details first if hidden
            payment_methods = []
            # Check if details are hidden and need expansion
            show_details_btn = await article.query_selector('a[data-action="show_details"]')
            if show_details_btn:
                try:
                    await show_details_btn.click()
                    await page.wait_for_timeout(500)  # Wait for content to expand
                except:
                    pass
            
            # Now extract payment methods from .term-view
            payment_links = await article.query_selector_all('.term-view a.term-img, .payment-methods-block a.term-img')
            for link in payment_links:
                title = await link.get_attribute('title')
                if title:
                    title = title.strip()
                    if title and title not in payment_methods:
                        payment_methods.append(title)
            
            # Extract positive features - also in hidden section
            positive_features = []
            feature_elems = await article.query_selector_all('.positives-block .flex-icon')
            for elem in feature_elems:
                text = await elem.inner_text()
                # Remove checkmark icons and clean text
                clean_text = re.sub(r'^[✓✔✅]\s*', '', text.strip())
                clean_text = re.sub(r'^\s*[•·]\s*', '', clean_text)  # Remove bullet points
                if clean_text and len(clean_text) > 5:  # Filter out very short text
                    positive_features.append(clean_text)
            
            # Extract casino ID from exit link if not already found
            if not casino_id:
                exit_link = await article.query_selector('a.btn-green[href*="exit"], a[href*="casinoID"]')
                if exit_link:
                    href = await exit_link.get_attribute('href')
                    if href:
                        # Extract casinoID from URL (e.g., /exit?casinoID=54)
                        id_match = re.search(r'casinoID=(\d+)', href)
                        if id_match:
                            casino_id = id_match.group(1)
            
            # Try to find actual casino URL from review page
            if review_url and not casino_url:
                # We could navigate to review page and extract the actual casino URL
                # For now, we'll use the review URL as the source
                pass
            
            listing = CasinoListing(
                name=name.strip(),
                url=casino_url or review_url or "",
                review_url=review_url or "",
                rating=rating,
                rating_display=rating_display,
                bonus_text=bonus_text,
                bonus_code=bonus_code,
                payout_percentage=payout_percentage,
                payout_speed=payout_speed,
                game_count=game_count,
                countries=countries,
                payment_methods=payment_methods,
                positive_features=positive_features,
                casino_id=casino_id,
                source_site=base_url
            )
            
            return listing
            
        except Exception as e:
            logger.error(f"Error parsing casino article: {e}")
            return None
    
    async def extract_casino_urls(self, url: str = "https://ex.casino", max_casinos: int = 50) -> List[str]:
        """
        Extract just the casino URLs from a review site
        
        Args:
            url: Review site URL
            max_casinos: Maximum casinos to extract
            
        Returns:
            List of casino URLs
        """
        listings = await self.parse_ex_casino(url, max_casinos)
        urls = []
        
        for listing in listings:
            if listing.url:
                urls.append(listing.url)
            elif listing.review_url:
                # Try to extract actual casino URL from review page
                urls.append(listing.review_url)
        
        return urls
    
    async def get_casino_details_from_review(self, review_url: str) -> Optional[Dict]:
        """
        Navigate to a casino review page and extract detailed information
        
        Args:
            review_url: URL of the casino review page
            
        Returns:
            Dictionary with detailed casino information
        """
        if not self.browser:
            await self.start()
        
        context = await self.browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(review_url, wait_until='networkidle', timeout=self.timeout)
            
            details = {
                'review_url': review_url,
                'actual_casino_url': None,
                'bonus_codes': [],
                'terms_and_conditions': None,
                'licenses': [],
                'game_providers': [],
                'additional_info': {}
            }
            
            # Try to find actual casino URL (usually in a "Visit Casino" or "Play Now" button)
            casino_link_selectors = [
                'a[href*="exit"]',
                'a.btn-green',
                'a:has-text("Play Now")',
                'a:has-text("Visit Casino")',
                'a[href^="http"]:not([href*="ex.casino"])'
            ]
            
            for selector in casino_link_selectors:
                try:
                    link = await page.query_selector(selector)
                    if link:
                        href = await link.get_attribute('href')
                        if href and not href.startswith('#'):
                            # Check if it's not the review site itself
                            parsed = urlparse(href)
                            if parsed.netloc and 'ex.casino' not in parsed.netloc:
                                details['actual_casino_url'] = href
                                break
                except:
                    continue
            
            # Extract bonus codes
            bonus_code_elems = await page.query_selector_all('code, .bonus-code, [class*="bonus-code"]')
            for elem in bonus_code_elems:
                text = await elem.inner_text()
                if text and len(text) < 50:  # Reasonable bonus code length
                    details['bonus_codes'].append(text.strip())
            
            await page.close()
            await context.close()
            
            return details
            
        except Exception as e:
            logger.error(f"Error extracting details from {review_url}: {e}")
            await page.close()
            await context.close()
            return None


async def main():
    """Test the parser"""
    parser = CasinoReviewParser(headless=False)
    
    try:
        await parser.start()
        
        print("🔍 Parsing ex.casino...")
        listings = await parser.parse_ex_casino("https://ex.casino", max_casinos=10)
        
        print(f"\n✅ Found {len(listings)} casinos:\n")
        for i, listing in enumerate(listings, 1):
            print(f"{i}. {listing.name}")
            print(f"   Rating: {listing.rating_display}")
            print(f"   URL: {listing.review_url}")
            if listing.bonus_text:
                print(f"   Bonus: {listing.bonus_text}")
            if listing.payout_percentage:
                print(f"   Payout: {listing.payout_percentage}%")
            print()
        
        # Export to JSON
        import json
        output = {
            'source': 'ex.casino',
            'timestamp': datetime.now().isoformat(),
            'casinos': [asdict(listing) for listing in listings]
        }
        
        with open('results/casino_listings.json', 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"💾 Saved to results/casino_listings.json")
        
    finally:
        await parser.stop()


if __name__ == "__main__":
    asyncio.run(main())

