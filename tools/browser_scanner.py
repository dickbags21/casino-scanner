"""
Browser Scanner Module
Handles automated browser testing of signup flows and bonus offers
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    logging.warning("Playwright not installed. Install with: pip install playwright && playwright install")
    async_playwright = None

logger = logging.getLogger(__name__)


@dataclass
class SignupTestResult:
    """Container for signup flow test results"""
    url: str
    success: bool
    issues: List[str]
    fields_found: List[str]
    validation_errors: List[str]
    screenshot_path: Optional[str]
    timestamp: str


@dataclass
class BonusTestResult:
    """Container for bonus offer test results"""
    url: str
    bonus_code: str
    success: bool
    message: str
    validation_bypassed: bool
    screenshot_path: Optional[str]
    timestamp: str


class BrowserScanner:
    """Browser automation for testing signup flows and bonus offers"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000,
                 user_agent: str = None, viewport: Dict = None,
                 screenshot_dir: str = "results/screenshots"):
        """
        Initialize browser scanner
        
        Args:
            headless: Run browser in headless mode
            timeout: Page timeout in milliseconds
            user_agent: Custom user agent string
            viewport: Viewport dimensions {'width': int, 'height': int}
            screenshot_dir: Directory to save screenshots
        """
        self.headless = headless
        self.timeout = timeout
        self.user_agent = user_agent
        self.viewport = viewport or {'width': 1920, 'height': 1080}
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def start(self):
        """Start browser instance"""
        if async_playwright is None:
            raise ImportError("Playwright is not installed")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        
        context_options = {
            'viewport': self.viewport
        }
        
        if self.user_agent:
            context_options['user_agent'] = self.user_agent
        
        self.context = await self.browser.new_context(**context_options)
        # Set default timeout for pages created from this context
        self.context.set_default_timeout(self.timeout)
        logger.info("Browser started successfully")
    
    async def stop(self):
        """Stop browser instance"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser stopped")
    
    async def test_signup_flow(self, url: str, test_data: Dict = None) -> SignupTestResult:
        """
        Test signup flow on a target URL
        
        Args:
            url: Target URL to test
            test_data: Dictionary with test data (email, phone, etc.)
            
        Returns:
            SignupTestResult object
        """
        if not self.context:
            await self.start()
        
        test_data = test_data or {}
        issues = []
        fields_found = []
        validation_errors = []
        screenshot_path = None
        
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Take initial screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = str(self.screenshot_dir / f"signup_{timestamp}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            
            # Look for signup/register elements
            signup_selectors = [
                'a[href*="signup"]',
                'a[href*="register"]',
                'a[href*="sign-up"]',
                'button:has-text("Sign Up")',
                'button:has-text("Register")',
                'a:has-text("Sign Up")',
                'a:has-text("Register")'
            ]
            
            signup_link = None
            for selector in signup_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        signup_link = element
                        break
                except:
                    continue
            
            if not signup_link:
                issues.append("No signup/register link found")
                await page.close()
                return SignupTestResult(
                    url=url,
                    success=False,
                    issues=issues,
                    fields_found=fields_found,
                    validation_errors=validation_errors,
                    screenshot_path=screenshot_path,
                    timestamp=timestamp
                )
            
            # Click signup link
            await signup_link.click()
            await page.wait_for_timeout(2000)
            
            # Find form fields
            form_fields = await page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"], input[type="password"]')
            for field in form_fields:
                field_type = await field.get_attribute('type')
                field_name = await field.get_attribute('name') or await field.get_attribute('id') or 'unknown'
                fields_found.append(f"{field_type}:{field_name}")
            
            # Try to fill form with test data
            email = test_data.get('email', 'test@example.com')
            phone = test_data.get('phone', '+84123456789')
            password = test_data.get('password', 'Test123!@#')
            
            # Fill email field
            email_selectors = ['input[type="email"]', 'input[name*="email"]', 'input[id*="email"]']
            for selector in email_selectors:
                try:
                    email_field = await page.query_selector(selector)
                    if email_field:
                        await email_field.fill(email)
                        break
                except:
                    continue
            
            # Fill phone field
            phone_selectors = ['input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]']
            for selector in phone_selectors:
                try:
                    phone_field = await page.query_selector(selector)
                    if phone_field:
                        await phone_field.fill(phone)
                        break
                except:
                    continue
            
            # Fill password fields
            password_fields = await page.query_selector_all('input[type="password"]')
            for field in password_fields:
                try:
                    await field.fill(password)
                except:
                    pass
            
            # Take screenshot after filling
            await page.screenshot(path=screenshot_path.replace('.png', '_filled.png'), full_page=True)
            
            # Try to submit form
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Register")',
                'button:has-text("Sign Up")'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    submit_button = await page.query_selector(selector)
                    if submit_button:
                        await submit_button.click()
                        await page.wait_for_timeout(3000)
                        submitted = True
                        break
                except:
                    continue
            
            if submitted:
                # Check for validation errors
                error_selectors = [
                    '.error',
                    '.validation-error',
                    '[class*="error"]',
                    '[class*="invalid"]'
                ]
                
                for selector in error_selectors:
                    try:
                        errors = await page.query_selector_all(selector)
                        for error in errors:
                            error_text = await error.inner_text()
                            if error_text:
                                validation_errors.append(error_text)
                    except:
                        continue
            
            await page.close()
            
            success = len(validation_errors) == 0 and submitted
            
            return SignupTestResult(
                url=url,
                success=success,
                issues=issues,
                fields_found=fields_found,
                validation_errors=validation_errors,
                screenshot_path=screenshot_path,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"Error testing signup flow for {url}: {e}")
            issues.append(f"Exception: {str(e)}")
            return SignupTestResult(
                url=url,
                success=False,
                issues=issues,
                fields_found=fields_found,
                validation_errors=validation_errors,
                screenshot_path=screenshot_path,
                timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
            )
    
    async def test_bonus_code(self, url: str, bonus_code: str) -> BonusTestResult:
        """
        Test bonus code on a target URL
        
        Args:
            url: Target URL
            bonus_code: Bonus code to test
            
        Returns:
            BonusTestResult object
        """
        if not self.context:
            await self.start()
        
        screenshot_path = None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Look for bonus/promo code input
            bonus_selectors = [
                'input[name*="bonus"]',
                'input[name*="promo"]',
                'input[name*="code"]',
                'input[id*="bonus"]',
                'input[id*="promo"]',
                'input[placeholder*="bonus"]',
                'input[placeholder*="promo"]'
            ]
            
            bonus_input = None
            for selector in bonus_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        bonus_input = element
                        break
                except:
                    continue
            
            if not bonus_input:
                await page.close()
                return BonusTestResult(
                    url=url,
                    bonus_code=bonus_code,
                    success=False,
                    message="No bonus code input found",
                    validation_bypassed=False,
                    screenshot_path=None,
                    timestamp=timestamp
                )
            
            # Fill and submit bonus code
            await bonus_input.fill(bonus_code)
            await page.wait_for_timeout(1000)
            
            # Look for apply/submit button
            apply_selectors = [
                'button:has-text("Apply")',
                'button:has-text("Submit")',
                'button:has-text("Redeem")',
                'button[type="submit"]'
            ]
            
            for selector in apply_selectors:
                try:
                    apply_button = await page.query_selector(selector)
                    if apply_button:
                        await apply_button.click()
                        await page.wait_for_timeout(3000)
                        break
                except:
                    continue
            
            # Take screenshot
            screenshot_path = str(self.screenshot_dir / f"bonus_{timestamp}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            
            # Check for success/error messages
            message = "Unknown result"
            success = False
            validation_bypassed = False
            
            # Look for success indicators
            success_indicators = [
                'text="Success"',
                'text="Applied"',
                'text="Redeemed"',
                '[class*="success"]'
            ]
            
            for indicator in success_indicators:
                try:
                    element = await page.query_selector(indicator)
                    if element:
                        message = await element.inner_text()
                        success = True
                        validation_bypassed = True
                        break
                except:
                    continue
            
            # Look for error messages
            if not success:
                error_selectors = [
                    '.error',
                    '[class*="error"]',
                    '[class*="invalid"]'
                ]
                
                for selector in error_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            message = await element.inner_text()
                            break
                    except:
                        continue
            
            await page.close()
            
            return BonusTestResult(
                url=url,
                bonus_code=bonus_code,
                success=success,
                message=message,
                validation_bypassed=validation_bypassed,
                screenshot_path=screenshot_path,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"Error testing bonus code for {url}: {e}")
            return BonusTestResult(
                url=url,
                bonus_code=bonus_code,
                success=False,
                message=f"Exception: {str(e)}",
                validation_bypassed=False,
                screenshot_path=screenshot_path,
                timestamp=timestamp
            )

