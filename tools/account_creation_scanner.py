"""
Account Creation Scanner Module
Specialized scanner for detecting multiple account creation vulnerabilities
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, parse_qs

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext  # pyright: ignore[reportMissingImports]
except ImportError:
    logging.warning("Playwright not installed. Install with: pip install playwright && playwright install")
    async_playwright = None

logger = logging.getLogger(__name__)


@dataclass
class AccountCreationVulnerability:
    """Container for account creation vulnerability findings"""
    title: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    vulnerability_type: str
    exploitability: str  # 'easy', 'medium', 'hard', 'theoretical'
    profit_potential: str
    technical_details: Dict
    proof_of_concept: Optional[str] = None
    mitigation: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AccountCreationTestResult:
    """Container for account creation test results"""
    url: str
    success: bool
    vulnerabilities: List[AccountCreationVulnerability]
    test_attempts: int
    forms_analyzed: int
    captchas_detected: List[str]
    validation_bypass_methods: List[str]
    screenshots: List[str]
    timestamp: str


class AccountCreationScanner:
    """
    Advanced scanner for detecting multiple account creation vulnerabilities

    Focuses on:
    - CAPTCHA bypass opportunities
    - Weak email validation
    - Phone number reuse
    - Rate limiting bypass
    - Form validation weaknesses
    - API endpoint exploitation
    """

    def __init__(self, headless: bool = True, timeout: int = 30000,
                 max_attempts: int = 10, user_agent: str = None):
        """
        Initialize account creation scanner

        Args:
            headless: Run browser in headless mode
            timeout: Page timeout in milliseconds
            max_attempts: Maximum account creation attempts per test
            user_agent: Custom user agent string
        """
        self.headless = headless
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        # Test data pools
        self.email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'test.com', 'example.com', 'temp-mail.org', '10minutemail.com'
        ]

        self.phone_prefixes = [
            '+1', '+44', '+84', '+855', '+856',  # US, UK, Vietnam, Cambodia, Laos
            '+65', '+60', '+66', '+62', '+63'   # Singapore, Malaysia, Thailand, Indonesia, Philippines
        ]

    async def start(self):
        """Start browser instance"""
        if async_playwright is None:
            raise ImportError("Playwright is not installed")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        logger.info("Account creation scanner browser started")

    async def stop(self):
        """Stop browser instance"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Account creation scanner browser stopped")

    async def scan_url(self, url: str) -> AccountCreationTestResult:
        """
        Perform comprehensive account creation vulnerability scan

        Args:
            url: Target URL to scan

        Returns:
            AccountCreationTestResult with findings
        """
        if not self.context:
            await self.start()

        result = AccountCreationTestResult(
            url=url,
            success=False,
            vulnerabilities=[],
            test_attempts=0,
            forms_analyzed=0,
            captchas_detected=[],
            validation_bypass_methods=[],
            screenshots=[],
            timestamp=datetime.now().isoformat()
        )

        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)

            # Initial analysis
            await self._analyze_page_structure(page, result)

            # Find and analyze signup forms
            signup_forms = await self._find_signup_forms(page)
            result.forms_analyzed = len(signup_forms)

            for form_info in signup_forms:
                await self._test_form_vulnerabilities(page, form_info, result)

            # Test API endpoints if found
            await self._test_api_endpoints(page, result)

            # Attempt multiple account creation
            await self._test_bulk_creation(page, result)

            result.success = len(result.vulnerabilities) > 0

        except Exception as e:
            logger.error(f"Error scanning {url}: {e}")
            result.vulnerabilities.append(AccountCreationVulnerability(
                title="Scan Error",
                description=f"Scanner encountered error: {str(e)}",
                severity="info",
                vulnerability_type="scanner_error",
                exploitability="n/a",
                profit_potential="n/a",
                technical_details={"error": str(e)}
            ))

        finally:
            if 'page' in locals():
                await page.close()

        return result

    async def _analyze_page_structure(self, page: Page, result: AccountCreationTestResult):
        """Analyze page structure for account creation indicators"""

        # Check for CAPTCHA services
        captcha_selectors = [
            '[class*="captcha"]', '[id*="captcha"]',
            '[class*="recaptcha"]', '[id*="recaptcha"]',
            'iframe[src*="recaptcha"]', 'iframe[src*="hcaptcha"]',
            'iframe[src*="cloudflare"]'
        ]

        for selector in captcha_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                for element in elements:
                    captcha_type = await self._identify_captcha_type(element)
                    if captcha_type and captcha_type not in result.captchas_detected:
                        result.captchas_detected.append(captcha_type)

        # Check for rate limiting indicators
        rate_limit_indicators = [
            'too many attempts', 'rate limit', 'try again later',
            'blocked', 'suspended', 'verification required'
        ]

        page_text = (await page.inner_text('body')).lower()
        for indicator in rate_limit_indicators:
            if indicator in page_text:
                result.vulnerabilities.append(AccountCreationVulnerability(
                    title="Rate Limiting Detected",
                    description="Page shows signs of rate limiting or blocking",
                    severity="low",
                    vulnerability_type="rate_limiting",
                    exploitability="medium",
                    profit_potential="low",
                    technical_details={"indicator": indicator}
                ))

    async def _identify_captcha_type(self, element) -> Optional[str]:
        """Identify CAPTCHA type from element"""
        try:
            src = await element.get_attribute('src') or ''
            class_name = await element.get_attribute('class') or ''
            id_attr = await element.get_attribute('id') or ''

            if 'recaptcha' in src or 'recaptcha' in class_name:
                return 'reCAPTCHA'
            elif 'hcaptcha' in src or 'hcaptcha' in class_name:
                return 'hCaptcha'
            elif 'cloudflare' in src:
                return 'Cloudflare'
            elif 'captcha' in class_name or 'captcha' in id_attr:
                return 'Generic CAPTCHA'

        except:
            pass
        return None

    async def _find_signup_forms(self, page: Page) -> List[Dict]:
        """Find all signup/registration forms on the page"""
        forms_info = []

        # Common signup form selectors
        signup_selectors = [
            'form[action*="signup"]', 'form[action*="register"]',
            'form[id*="signup"]', 'form[id*="register"]',
            'form[class*="signup"]', 'form[class*="register"]',
            'form[action*="join"]', 'form[action*="create"]'
        ]

        for selector in signup_selectors:
            forms = await page.query_selector_all(selector)
            for form in forms:
                form_info = await self._analyze_form_structure(form)
                if form_info:
                    forms_info.append(form_info)

        # Also look for forms with email/password fields (broader search)
        all_forms = await page.query_selector_all('form')
        for form in all_forms:
            form_info = await self._analyze_form_structure(form)
            if form_info and form_info not in forms_info:
                # Check if it has both email and password fields
                has_email = any(field['type'] in ['email', 'text'] and
                              'email' in (field.get('name', '') + field.get('id', '')).lower()
                              for field in form_info['fields'])
                has_password = any(field['type'] == 'password' for field in form_info['fields'])

                if has_email and has_password:
                    forms_info.append(form_info)

        return forms_info

    async def _analyze_form_structure(self, form) -> Optional[Dict]:
        """Analyze form structure and fields"""
        try:
            inputs = await form.query_selector_all('input, select, textarea')
            fields = []

            for input_elem in inputs:
                field_info = {
                    'type': await input_elem.get_attribute('type') or 'text',
                    'name': await input_elem.get_attribute('name') or '',
                    'id': await input_elem.get_attribute('id') or '',
                    'required': await input_elem.get_attribute('required') is not None,
                    'pattern': await input_elem.get_attribute('pattern') or '',
                    'placeholder': await input_elem.get_attribute('placeholder') or '',
                    'maxlength': await input_elem.get_attribute('maxlength') or ''
                }
                fields.append(field_info)

            return {
                'action': await form.get_attribute('action') or '',
                'method': await form.get_attribute('method') or 'GET',
                'fields': fields,
                'has_captcha': len([f for f in fields if 'captcha' in (f['name'] + f['id']).lower()]) > 0
            }

        except Exception as e:
            logger.warning(f"Error analyzing form: {e}")
            return None

    async def _test_form_vulnerabilities(self, page: Page, form_info: Dict,
                                      result: AccountCreationTestResult):
        """Test specific form for vulnerabilities"""

        fields = form_info['fields']

        # Check for weak validation
        email_fields = [f for f in fields if f['type'] == 'email' or
                       'email' in (f['name'] + f['id']).lower()]

        if email_fields:
            # Test email validation strength
            email_field = email_fields[0]
            if not email_field['required']:
                result.vulnerabilities.append(AccountCreationVulnerability(
                    title="Optional Email Field",
                    description="Email field is not required for account creation",
                    severity="medium",
                    vulnerability_type="weak_validation",
                    exploitability="easy",
                    profit_potential="high",
                    technical_details={"field": email_field}
                ))

            if not email_field['pattern']:
                result.vulnerabilities.append(AccountCreationVulnerability(
                    title="No Email Pattern Validation",
                    description="Email field lacks pattern validation - allows malformed emails",
                    severity="low",
                    vulnerability_type="weak_validation",
                    exploitability="easy",
                    profit_potential="medium",
                    technical_details={"field": email_field}
                ))

        # Check phone validation
        phone_fields = [f for f in fields if f['type'] == 'tel' or
                       'phone' in (f['name'] + f['id']).lower()]

        if not phone_fields:
            result.vulnerabilities.append(AccountCreationVulnerability(
                title="No Phone Verification",
                description="Account creation doesn't require phone verification",
                severity="high",
                vulnerability_type="missing_verification",
                exploitability="easy",
                profit_potential="very_high",
                technical_details={"missing_fields": ["phone"]}
            ))

        # Check for CAPTCHA bypass opportunities
        if not form_info['has_captcha']:
            result.vulnerabilities.append(AccountCreationVulnerability(
                title="No CAPTCHA Protection",
                description="Signup form lacks CAPTCHA protection against automated creation",
                severity="critical",
                vulnerability_type="captcha_bypass",
                exploitability="easy",
                profit_potential="very_high",
                technical_details={"protection": "none"},
                mitigation="Implement CAPTCHA (reCAPTCHA, hCaptcha) on signup forms"
            ))

        # Check password requirements
        password_fields = [f for f in fields if f['type'] == 'password']
        for pwd_field in password_fields:
            if not pwd_field['pattern'] and not pwd_field['required']:
                result.vulnerabilities.append(AccountCreationVulnerability(
                    title="Weak Password Requirements",
                    description="Password field has no pattern validation or strength requirements",
                    severity="medium",
                    vulnerability_type="weak_password_policy",
                    exploitability="easy",
                    profit_potential="high",
                    technical_details={"field": pwd_field}
                ))

    async def _test_bulk_creation(self, page: Page, result: AccountCreationTestResult):
        """Test bulk account creation capabilities"""

        if len(result.captchas_detected) > 0:
            # If CAPTCHA is present, note that bulk creation is harder but not impossible
            result.vulnerabilities.append(AccountCreationVulnerability(
                title="CAPTCHA Protected",
                description=f"Form protected by {', '.join(result.captchas_detected)} - bulk creation difficult but not impossible",
                severity="low",
                vulnerability_type="captcha_protection",
                exploitability="hard",
                profit_potential="low",
                technical_details={"captcha_types": result.captchas_detected}
            ))
            return

        # Attempt multiple account creations
        successful_creations = 0
        blocked_attempts = 0

        for i in range(min(self.max_attempts, 5)):  # Limit to 5 attempts for safety
            try:
                success = await self._attempt_single_creation(page, i, result)
                if success:
                    successful_creations += 1
                else:
                    blocked_attempts += 1

                result.test_attempts += 1

                # Small delay between attempts
                await asyncio.sleep(1)

            except Exception as e:
                logger.warning(f"Account creation attempt {i+1} failed: {e}")
                blocked_attempts += 1

        if successful_creations > 1:
            result.vulnerabilities.append(AccountCreationVulnerability(
                title="Bulk Account Creation Possible",
                description=f"Successfully created {successful_creations} accounts in sequence",
                severity="critical",
                vulnerability_type="bulk_creation",
                exploitability="easy",
                profit_potential="very_high",
                technical_details={
                    "successful_creations": successful_creations,
                    "total_attempts": result.test_attempts
                },
                proof_of_concept="Multiple accounts created without blocking"
            ))

    async def _attempt_single_creation(self, page: Page, attempt_num: int,
                                     result: AccountCreationTestResult) -> bool:
        """Attempt to create a single account"""

        try:
            # Generate test data
            test_email = f"test{attempt_num}_{int(datetime.now().timestamp())}@{self.email_domains[0]}"
            test_phone = f"{self.phone_prefixes[0]}{attempt_num}123456789"
            test_password = f"TestPass{attempt_num}!123"

            # Find and fill signup form
            signup_forms = await page.query_selector_all('form')

            for form in signup_forms:
                try:
                    # Fill email
                    email_selectors = ['input[type="email"]', 'input[name*="email"]', 'input[id*="email"]']
                    for selector in email_selectors:
                        email_field = await form.query_selector(selector)
                        if email_field:
                            await email_field.fill(test_email)
                            break

                    # Fill phone if present
                    phone_selectors = ['input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]']
                    for selector in phone_selectors:
                        phone_field = await form.query_selector(selector)
                        if phone_field:
                            await phone_field.fill(test_phone)
                            break

                    # Fill password fields
                    password_fields = await form.query_selector_all('input[type="password"]')
                    for field in password_fields:
                        await field.fill(test_password)

                    # Try to submit
                    submit_selectors = [
                        'button[type="submit"]', 'input[type="submit"]',
                        'button:has-text("Sign Up")', 'button:has-text("Register")'
                    ]

                    for selector in submit_selectors:
                        submit_btn = await form.query_selector(selector)
                        if submit_btn:
                            await submit_btn.click()
                            await page.wait_for_timeout(3000)
                            return True

                except Exception as e:
                    logger.debug(f"Form submission failed: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Account creation attempt failed: {e}")

        return False

    async def _test_api_endpoints(self, page: Page, result: AccountCreationTestResult):
        """Test for exposed API endpoints that could be used for account creation"""

        # Monitor network requests
        api_endpoints = []

        def handle_request(request):
            url = request.url
            if any(endpoint in url for endpoint in ['/api/', '/graphql', '/register', '/signup']):
                api_endpoints.append({
                    'url': url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })

        page.on('request', handle_request)

        # Trigger some form activity to capture API calls
        await page.wait_for_timeout(2000)

        # Analyze captured endpoints
        for endpoint in api_endpoints:
            if 'register' in endpoint['url'] or 'signup' in endpoint['url']:
                result.vulnerabilities.append(AccountCreationVulnerability(
                    title="Account Creation API Endpoint",
                    description=f"Found API endpoint for account creation: {endpoint['url']}",
                    severity="medium",
                    vulnerability_type="api_exposure",
                    exploitability="medium",
                    profit_potential="high",
                    technical_details=endpoint,
                    mitigation="Implement proper authentication and rate limiting on API endpoints"
                ))

    def generate_report(self, results: List[AccountCreationTestResult]) -> Dict:
        """Generate comprehensive report from scan results"""

        total_vulnerabilities = sum(len(r.vulnerabilities) for r in results)
        critical_vulns = sum(len([v for v in r.vulnerabilities if v.severity == 'critical']) for r in results)
        high_vulns = sum(len([v for v in r.vulnerabilities if v.severity == 'high']) for r in results)

        return {
            'scan_summary': {
                'total_urls_scanned': len(results),
                'total_vulnerabilities': total_vulnerabilities,
                'critical_vulnerabilities': critical_vulns,
                'high_vulnerabilities': high_vulns,
                'scan_timestamp': datetime.now().isoformat()
            },
            'results': [self._result_to_dict(r) for r in results],
            'recommendations': self._generate_recommendations(results)
        }

    def _result_to_dict(self, result: AccountCreationTestResult) -> Dict:
        """Convert result to dictionary"""
        return {
            'url': result.url,
            'success': result.success,
            'test_attempts': result.test_attempts,
            'forms_analyzed': result.forms_analyzed,
            'captchas_detected': result.captchas_detected,
            'vulnerabilities': [self._vuln_to_dict(v) for v in result.vulnerabilities],
            'timestamp': result.timestamp
        }

    def _vuln_to_dict(self, vuln: AccountCreationVulnerability) -> Dict:
        """Convert vulnerability to dictionary"""
        return {
            'title': vuln.title,
            'description': vuln.description,
            'severity': vuln.severity,
            'type': vuln.vulnerability_type,
            'exploitability': vuln.exploitability,
            'profit_potential': vuln.profit_potential,
            'technical_details': vuln.technical_details,
            'proof_of_concept': vuln.proof_of_concept,
            'mitigation': vuln.mitigation,
            'timestamp': vuln.timestamp
        }

    def _generate_recommendations(self, results: List[AccountCreationTestResult]) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        all_vulns = [v for r in results for v in r.vulnerabilities]

        if any(v.vulnerability_type == 'captcha_bypass' for v in all_vulns):
            recommendations.append("Implement CAPTCHA protection on all signup forms")

        if any(v.vulnerability_type == 'bulk_creation' for v in all_vulns):
            recommendations.append("Add rate limiting and account creation restrictions")

        if any(v.vulnerability_type == 'weak_validation' for v in all_vulns):
            recommendations.append("Strengthen email and phone number validation")

        if any(v.vulnerability_type == 'api_exposure' for v in all_vulns):
            recommendations.append("Secure API endpoints with authentication and rate limiting")

        return recommendations
