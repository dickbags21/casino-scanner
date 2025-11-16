#!/usr/bin/env python3
"""
Casino Security Research Framework - Main Entry Point

⚠️  DEPRECATED: This entry point is deprecated.
    Use 'start_dashboard.py' for the dashboard or 'automated_scanner.py' for continuous scanning.
    
    This file is kept for backward compatibility only.
"""

import argparse
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Dict, List

from tools.shodan_scanner import ShodanScanner
from tools.browser_scanner import BrowserScanner
from tools.target_manager import TargetManager
from tools.reporter import Reporter, ScanReport
from tools.account_creation_scanner import AccountCreationScanner
from datetime import datetime

logger = logging.getLogger(__name__)


class CasinoResearchFramework:
    """Main framework orchestrator"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize framework
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.shodan_scanner = None
        self.browser_scanner = None
        self.account_creation_scanner = None
        self.target_manager = TargetManager()
        self.reporter = Reporter(
            results_dir=self.config['output']['results_dir'],
            logs_dir=self.config['output']['logs_dir'],
            log_level=self.config['logging']['level'],
            max_bytes=self.config['logging']['max_bytes'],
            backup_count=self.config['logging']['backup_count']
        )
        
        # Initialize Shodan if API key is provided
        shodan_key = self.config['apis']['shodan']['api_key']
        if shodan_key and shodan_key != "YOUR_SHODAN_API_KEY_HERE":
            self.shodan_scanner = ShodanScanner(
                api_key=shodan_key,
                rate_limit=self.config['apis']['shodan']['rate_limit']
            )
        else:
            logger.warning("Shodan API key not configured")
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def initialize_browser(self):
        """Initialize browser scanner"""
        browser_config = self.config['browser']
        self.browser_scanner = BrowserScanner(
            headless=browser_config['headless'],
            timeout=browser_config['timeout'],
            user_agent=browser_config.get('user_agent'),
            viewport=browser_config.get('viewport'),
            screenshot_dir=self.config['output'].get('screenshot_dir', 'results/screenshots')
        )
        await self.browser_scanner.start()

    async def initialize_account_scanner(self):
        """Initialize account creation scanner"""
        browser_config = self.config['browser']
        self.account_creation_scanner = AccountCreationScanner(
            headless=browser_config['headless'],
            timeout=browser_config['timeout'],
            max_attempts=self.config['testing']['signup_flow'].get('max_attempts', 10),
            user_agent=browser_config.get('user_agent')
        )
        await self.account_creation_scanner.start()
    
    async def run_shodan_scan(self, region: str) -> List[Dict]:
        """Run Shodan scan for a region"""
        if not self.shodan_scanner:
            logger.warning("Shodan scanner not available")
            return []
        
        region_config = self.config['regions'].get(region, {})
        if not region_config:
            logger.error(f"Region {region} not found in config")
            return []
        
        country_code = region_config['country_code']
        keywords = region_config['search_terms']
        ports = region_config.get('ports', [80, 443])
        
        logger.info(f"Starting Shodan scan for region: {region}")
        results = self.shodan_scanner.search_by_country(
            country_code=country_code,
            keywords=keywords,
            ports=ports
        )
        
        # Convert to dictionaries for reporting
        return [self._shodan_result_to_dict(r) for r in results]
    
    def _shodan_result_to_dict(self, result) -> Dict:
        """Convert ShodanResult to dictionary"""
        return {
            'ip': result.ip,
            'port': result.port,
            'hostname': result.hostname,
            'org': result.org,
            'country': result.country,
            'city': result.city,
            'product': result.product,
            'version': result.version,
            'vulns': result.vulns
        }
    
    async def test_targets(self, region: str) -> tuple[List[Dict], List[Dict], List[Dict]]:
        """Test targets for signup flows, bonus offers, and account creation vulnerabilities"""
        if not self.browser_scanner:
            await self.initialize_browser()
        if not self.account_creation_scanner:
            await self.initialize_account_scanner()

        targets = self.target_manager.get_targets(region=region, status='pending')
        signup_results = []
        bonus_results = []
        account_creation_results = []

        test_config = self.config['testing']
        region_config = self.config['regions'].get(region, {})

        for target in targets:
            logger.info(f"Testing target: {target.url}")

            # Test signup flow
            test_data = {
                'email': f"test@{test_config['signup_flow']['test_email_domains'][0]}",
                'phone': f"{test_config['signup_flow']['test_phone_prefixes'][0]}123456789"
            }

            signup_result = await self.browser_scanner.test_signup_flow(
                target.url,
                test_data=test_data
            )
            signup_results.append(self._signup_result_to_dict(signup_result))

            # Test bonus codes
            for bonus_code in test_config['bonus_offers']['test_codes']:
                bonus_result = await self.browser_scanner.test_bonus_code(
                    target.url,
                    bonus_code
                )
                bonus_results.append(self._bonus_result_to_dict(bonus_result))

            # Test account creation vulnerabilities
            account_result = await self.account_creation_scanner.scan_url(target.url)
            account_creation_results.append(self._account_creation_to_dict(account_result))

            # Update target status
            self.target_manager.update_target(
                target.url,
                region,
                status='completed'
            )

        return signup_results, bonus_results, account_creation_results
    
    def _signup_result_to_dict(self, result) -> Dict:
        """Convert SignupTestResult to dictionary"""
        return {
            'url': result.url,
            'success': result.success,
            'issues': result.issues,
            'fields_found': result.fields_found,
            'validation_errors': result.validation_errors,
            'screenshot_path': result.screenshot_path,
            'timestamp': result.timestamp
        }
    
    def _bonus_result_to_dict(self, result) -> Dict:
        """Convert BonusTestResult to dictionary"""
        return {
            'url': result.url,
            'bonus_code': result.bonus_code,
            'success': result.success,
            'message': result.message,
            'validation_bypassed': result.validation_bypassed,
            'screenshot_path': result.screenshot_path,
            'timestamp': result.timestamp
        }

    def _account_creation_to_dict(self, result) -> Dict:
        """Convert AccountCreationTestResult to dictionary"""
        return {
            'url': result.url,
            'success': result.success,
            'test_attempts': result.test_attempts,
            'forms_analyzed': result.forms_analyzed,
            'captchas_detected': result.captchas_detected,
            'validation_bypass_methods': result.validation_bypass_methods,
            'vulnerabilities': [self._vuln_to_dict(v) for v in result.vulnerabilities],
            'screenshots': result.screenshots,
            'timestamp': result.timestamp
        }

    def _vuln_to_dict(self, vuln) -> Dict:
        """Convert AccountCreationVulnerability to dictionary"""
        return {
            'title': vuln.title,
            'description': vuln.description,
            'severity': vuln.severity,
            'vulnerability_type': vuln.vulnerability_type,
            'exploitability': vuln.exploitability,
            'profit_potential': vuln.profit_potential,
            'technical_details': vuln.technical_details,
            'proof_of_concept': vuln.proof_of_concept,
            'mitigation': vuln.mitigation,
            'timestamp': vuln.timestamp
        }
    
    def analyze_findings(self, shodan_results: List[Dict],
                        signup_results: List[Dict],
                        bonus_results: List[Dict],
                        account_creation_results: List[Dict] = None) -> List[Dict]:
        """Analyze results and generate findings"""
        findings = []

        # Analyze Shodan results for vulnerabilities
        for result in shodan_results:
            if result.get('vulns'):
                findings.append({
                    'title': f"Vulnerabilities found on {result.get('ip')}",
                    'url': f"http://{result.get('ip')}:{result.get('port')}",
                    'description': f"Found {len(result['vulns'])} known vulnerabilities",
                    'severity': 'high',
                    'type': 'shodan_vuln'
                })

        # Analyze signup results
        for result in signup_results:
            if result.get('validation_errors'):
                findings.append({
                    'title': f"Signup validation issues on {result.get('url')}",
                    'url': result.get('url'),
                    'description': f"Validation errors: {', '.join(result['validation_errors'])}",
                    'severity': 'medium',
                    'type': 'signup_validation'
                })

            if not result.get('success') and not result.get('issues'):
                findings.append({
                    'title': f"Potential signup flow bypass on {result.get('url')}",
                    'url': result.get('url'),
                    'description': "Signup flow completed without validation errors",
                    'severity': 'low',
                    'type': 'signup_bypass'
                })

        # Analyze bonus results
        for result in bonus_results:
            if result.get('validation_bypassed'):
                findings.append({
                    'title': f"Bonus code validation bypassed on {result.get('url')}",
                    'url': result.get('url'),
                    'description': f"Bonus code '{result.get('bonus_code')}' was accepted",
                    'severity': 'medium',
                    'type': 'bonus_bypass'
                })

        # Analyze account creation vulnerabilities
        if account_creation_results:
            for result in account_creation_results:
                for vuln in result.get('vulnerabilities', []):
                    findings.append({
                        'title': vuln['title'],
                        'url': result.get('url'),
                        'description': vuln['description'],
                        'severity': vuln['severity'],
                        'type': vuln['vulnerability_type'],
                        'exploitability': vuln.get('exploitability'),
                        'profit_potential': vuln.get('profit_potential'),
                        'technical_details': vuln.get('technical_details'),
                        'mitigation': vuln.get('mitigation')
                    })

        return findings
    
    async def run_scan(self, region: str):
        """Run complete scan for a region"""
        logger.info(f"Starting scan for region: {region}")
        
        # Load targets
        self.target_manager.load_targets(region=region)
        targets = self.target_manager.get_targets(region=region)
        
        # Run Shodan scan
        shodan_results = []
        if self.shodan_scanner:
            shodan_results = await self.run_shodan_scan(region)
        
        # Test targets
        signup_results, bonus_results, account_creation_results = await self.test_targets(region)

        # Analyze findings
        findings = self.analyze_findings(shodan_results, signup_results, bonus_results, account_creation_results)
        
        # Generate report
        report = ScanReport(
            region=region,
            timestamp=datetime.now().isoformat(),
            targets_scanned=len(targets),
            shodan_results=shodan_results,
            signup_tests=signup_results,
            bonus_tests=bonus_results,
            account_creation_tests=account_creation_results,
            findings=findings,
            summary={
                'total_targets': len(targets),
                'shodan_results': len(shodan_results),
                'signup_tests': len(signup_results),
                'bonus_tests': len(bonus_results),
                'account_creation_tests': len(account_creation_results),
                'findings': len(findings)
            }
        )
        
        report_format = self.config['output'].get('report_format', 'json')
        report_path = self.reporter.generate_report(report, format=report_format)
        
        logger.info(f"Scan completed. Report saved to: {report_path}")
        
        # Cleanup
        if self.browser_scanner:
            await self.browser_scanner.stop()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.browser_scanner:
            await self.browser_scanner.stop()
        if self.account_creation_scanner:
            await self.account_creation_scanner.stop()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Casino Security Research Framework"
    )
    parser.add_argument(
        '--region',
        type=str,
        required=True,
        choices=['vietnam', 'laos', 'cambodia'],
        help='Region to scan'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    framework = CasinoResearchFramework(config_path=args.config)
    
    try:
        await framework.run_scan(args.region)
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
    except Exception as e:
        logger.error(f"Error during scan: {e}", exc_info=True)
    finally:
        await framework.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

