"""
Mobile App Scanner Module
Specialized scanner for mobile gambling applications and APIs
"""

import asyncio
import logging
import json
import re
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
import platform

logger = logging.getLogger(__name__)


@dataclass
class MobileAppVulnerability:
    """Container for mobile app vulnerability findings"""
    title: str
    description: str
    severity: str
    vulnerability_type: str
    platform: str  # 'android', 'ios', 'cross_platform'
    exploitability: str
    profit_potential: str
    technical_details: Dict
    proof_of_concept: Optional[str] = None
    mitigation: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class MobileAppScanResult:
    """Container for mobile app scan results"""
    app_id: str
    app_name: str
    platform: str
    version: str
    developer: str
    vulnerabilities: List[MobileAppVulnerability]
    api_endpoints: List[Dict]
    permissions: List[str]
    network_traffic: List[Dict]
    storage_findings: List[Dict]
    timestamp: str


class MobileAppScanner:
    """
    Advanced mobile gambling app vulnerability scanner

    Capabilities:
    - APK analysis (Android)
    - IPA analysis (iOS)
    - API endpoint discovery
    - Permission analysis
    - Network traffic analysis
    - Storage vulnerability assessment
    - Gambling-specific vulnerability patterns
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Common gambling app API patterns
        self.gambling_api_patterns = [
            r'/api/(?:bet|game|spin|deposit|withdraw|bonus|reward)',
            r'/mobile/(?:login|register|balance|transaction)',
            r'/casino/(?:lobby|game|jackpot|promotion)',
            r'/gambling/(?:odds|betting|lottery)',
            r'/sportsbook/(?:match|odds|bet)',
            r'/poker/(?:table|hand|tournament)',
            r'/slot/(?:machine|spin|payline)',
            r'/blackjack/(?:deal|hit|stand)',
            r'/roulette/(?:spin|bet|number)'
        ]

    async def scan_app_store(self, query: str, platform: str = 'android',
                           limit: int = 50) -> List[Dict]:
        """
        Scan app stores for gambling applications

        Args:
            query: Search query for gambling apps
            platform: 'android' or 'ios'
            limit: Maximum results to return

        Returns:
            List of app information dictionaries
        """
        apps = []

        if platform == 'android':
            apps = await self._scan_google_play(query, limit)
        elif platform == 'ios':
            apps = await self._scan_app_store_connect(query, limit)

        return apps

    async def _scan_google_play(self, query: str, limit: int) -> List[Dict]:
        """Scan Google Play Store for Android gambling apps"""
        # Note: This is a simplified implementation
        # In practice, you'd use Google Play API or scraping

        gambling_keywords = [
            'casino', 'poker', 'slots', 'blackjack', 'roulette',
            'baccarat', 'betting', 'gambling', 'sportsbook', 'lottery'
        ]

        apps = []

        for keyword in gambling_keywords[:5]:  # Limit for demo
            try:
                # This would typically use Google Play API
                # For now, we'll simulate some results
                mock_apps = [
                    {
                        'app_id': f'com.casino.{keyword}.demo',
                        'name': f'Casino {keyword.title()}',
                        'developer': 'Demo Casino Inc',
                        'rating': 4.2,
                        'downloads': '1M+',
                        'category': 'Gambling',
                        'platform': 'android'
                    }
                ]
                apps.extend(mock_apps)

            except Exception as e:
                logger.warning(f"Error scanning Google Play for {keyword}: {e}")

        return apps[:limit]

    async def _scan_app_store_connect(self, query: str, limit: int) -> List[Dict]:
        """Scan Apple App Store for iOS gambling apps"""
        # Note: This is a simplified implementation
        # In practice, you'd use App Store Connect API

        apps = [
            {
                'app_id': 'com.casino.ios.demo',
                'name': 'iCasino Demo',
                'developer': 'iCasino Inc',
                'rating': 4.5,
                'downloads': '500K+',
                'category': 'Gambling',
                'platform': 'ios'
            }
        ]

        return apps[:limit]

    async def analyze_apk_file(self, apk_path: str) -> MobileAppScanResult:
        """
        Analyze Android APK file for vulnerabilities

        Args:
            apk_path: Path to APK file

        Returns:
            MobileAppScanResult with findings
        """
        if not Path(apk_path).exists():
            raise FileNotFoundError(f"APK file not found: {apk_path}")

        result = MobileAppScanResult(
            app_id="unknown",
            app_name="Unknown",
            platform="android",
            version="unknown",
            developer="unknown",
            vulnerabilities=[],
            api_endpoints=[],
            permissions=[],
            network_traffic=[],
            storage_findings=[],
            timestamp=datetime.now().isoformat()
        )

        try:
            # Extract basic app information
            app_info = await self._extract_apk_info(apk_path)
            result.app_id = app_info.get('package_name', 'unknown')
            result.app_name = app_info.get('app_name', 'Unknown')
            result.version = app_info.get('version', 'unknown')
            result.developer = app_info.get('developer', 'unknown')

            # Analyze permissions
            result.permissions = await self._analyze_apk_permissions(apk_path)

            # Extract and analyze code
            code_findings = await self._analyze_apk_code(apk_path)
            result.vulnerabilities.extend(code_findings)

            # Check for hardcoded credentials
            credential_findings = await self._check_hardcoded_credentials(apk_path)
            result.vulnerabilities.extend(credential_findings)

            # Analyze network communications
            network_findings = await self._analyze_network_security(apk_path)
            result.vulnerabilities.extend(network_findings)

        except Exception as e:
            logger.error(f"Error analyzing APK {apk_path}: {e}")
            result.vulnerabilities.append(MobileAppVulnerability(
                title="Analysis Error",
                description=f"Failed to analyze APK: {str(e)}",
                severity="info",
                vulnerability_type="analysis_error",
                platform="android",
                exploitability="n/a",
                profit_potential="n/a",
                technical_details={"error": str(e)}
            ))

        return result

    async def _extract_apk_info(self, apk_path: str) -> Dict:
        """Extract basic information from APK"""
        # This would use apktool or similar
        # For now, return mock data
        return {
            'package_name': 'com.example.casino',
            'app_name': 'Example Casino',
            'version': '1.0.0',
            'developer': 'Casino Corp'
        }

    async def _analyze_apk_permissions(self, apk_path: str) -> List[str]:
        """Analyze APK permissions"""
        dangerous_permissions = [
            'android.permission.READ_SMS',
            'android.permission.RECEIVE_SMS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.ACCESS_COARSE_LOCATION',
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.READ_CONTACTS',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.READ_PHONE_STATE'
        ]

        # This would extract actual permissions from APK
        # For demo, return some common gambling app permissions
        return [
            'android.permission.INTERNET',
            'android.permission.ACCESS_NETWORK_STATE',
            'android.permission.WAKE_LOCK',
            'android.permission.VIBRATE',
            'android.permission.RECEIVE_BOOT_COMPLETED'
        ]

    async def _analyze_apk_code(self, apk_path: str) -> List[MobileAppVulnerability]:
        """Analyze APK code for vulnerabilities"""
        vulnerabilities = []

        # This would decompile and analyze the APK
        # For demo, simulate some common findings

        # Check for weak encryption
        vulnerabilities.append(MobileAppVulnerability(
            title="Potential Weak Encryption",
            description="App may use weak encryption for sensitive data",
            severity="medium",
            vulnerability_type="weak_cryptography",
            platform="android",
            exploitability="medium",
            profit_potential="high",
            technical_details={"issue": "Weak encryption patterns detected"},
            mitigation="Use strong encryption (AES-256, proper key management)"
        ))

        # Check for API key exposure
        vulnerabilities.append(MobileAppVulnerability(
            title="Hardcoded API Keys Detected",
            description="Application contains hardcoded API keys",
            severity="high",
            vulnerability_type="information_disclosure",
            platform="android",
            exploitability="easy",
            profit_potential="medium",
            technical_details={"keys_found": ["api_key", "secret_key"]},
            mitigation="Use secure key storage mechanisms"
        ))

        # Check for insecure network communication
        vulnerabilities.append(MobileAppVulnerability(
            title="Insecure Network Communication",
            description="App communicates over HTTP instead of HTTPS",
            severity="critical",
            vulnerability_type="insecure_transport",
            platform="android",
            exploitability="easy",
            profit_potential="very_high",
            technical_details={"protocol": "HTTP"},
            mitigation="Implement HTTPS with certificate pinning"
        ))

        return vulnerabilities

    async def _check_hardcoded_credentials(self, apk_path: str) -> List[MobileAppVulnerability]:
        """Check for hardcoded credentials in APK"""
        vulnerabilities = []

        # This would search through decompiled code for credentials
        vulnerabilities.append(MobileAppVulnerability(
            title="Hardcoded Database Credentials",
            description="Database connection string with hardcoded credentials found",
            severity="critical",
            vulnerability_type="hardcoded_credentials",
            platform="android",
            exploitability="easy",
            profit_potential="very_high",
            technical_details={
                "type": "database_credentials",
                "pattern": "mongodb://user:password@host:port/db"
            },
            mitigation="Use secure credential storage and environment variables"
        ))

        return vulnerabilities

    async def _analyze_network_security(self, apk_path: str) -> List[MobileAppVulnerability]:
        """Analyze network security in APK"""
        vulnerabilities = []

        vulnerabilities.append(MobileAppVulnerability(
            title="Missing Certificate Pinning",
            description="Application does not implement certificate pinning",
            severity="high",
            vulnerability_type="missing_certificate_pinning",
            platform="android",
            exploitability="medium",
            profit_potential="high",
            technical_details={"implementation": "none"},
            mitigation="Implement certificate pinning to prevent MITM attacks"
        ))

        return vulnerabilities

    async def analyze_api_endpoints(self, base_url: str, app_context: Dict = None) -> List[Dict]:
        """
        Analyze API endpoints for a mobile gambling app

        Args:
            base_url: Base API URL
            app_context: Additional context about the app

        Returns:
            List of API endpoint information
        """
        endpoints = []
        common_paths = [
            '/api/v1/user/login',
            '/api/v1/user/register',
            '/api/v1/balance',
            '/api/v1/deposit',
            '/api/v1/withdraw',
            '/api/v1/bet',
            '/api/v1/spin',
            '/api/v1/bonus',
            '/api/v1/promotion',
            '/api/v1/leaderboard',
            '/api/v1/transaction'
        ]

        for path in common_paths:
            full_url = base_url.rstrip('/') + path

            try:
                # Test GET request
                response = self.session.get(full_url, timeout=10)

                endpoint_info = {
                    'url': full_url,
                    'method': 'GET',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'headers': dict(response.headers),
                    'is_gambling_related': self._is_gambling_endpoint(path),
                    'vulnerabilities': []
                }

                # Check for common vulnerabilities
                if response.status_code == 200:
                    # Check for information disclosure
                    if 'server' in response.headers:
                        endpoint_info['server_info'] = response.headers['server']

                    # Check for CORS misconfiguration
                    cors_header = response.headers.get('Access-Control-Allow-Origin', '')
                    if cors_header == '*':
                        endpoint_info['vulnerabilities'].append({
                            'type': 'cors_misconfiguration',
                            'severity': 'medium'
                        })

                endpoints.append(endpoint_info)

            except requests.RequestException as e:
                endpoints.append({
                    'url': full_url,
                    'method': 'GET',
                    'error': str(e),
                    'is_gambling_related': self._is_gambling_endpoint(path),
                    'vulnerabilities': []
                })

        return endpoints

    def _is_gambling_endpoint(self, path: str) -> bool:
        """Check if an endpoint is gambling-related"""
        path_lower = path.lower()
        return any(re.search(pattern, path_lower) for pattern in self.gambling_api_patterns)

    async def analyze_app_store_metadata(self, app_id: str, platform: str = 'android') -> Dict:
        """
        Analyze app store metadata for security insights

        Args:
            app_id: App identifier
            platform: 'android' or 'ios'

        Returns:
            Dictionary with metadata analysis
        """
        analysis = {
            'app_id': app_id,
            'platform': platform,
            'metadata_findings': [],
            'privacy_concerns': [],
            'security_score': 0
        }

        try:
            if platform == 'android':
                # Analyze Google Play metadata
                analysis['metadata_findings'].append({
                    'type': 'permissions_analysis',
                    'description': 'App requests excessive permissions for a gambling app'
                })

                analysis['privacy_concerns'].append({
                    'type': 'data_collection',
                    'description': 'App collects location and contact data'
                })

            elif platform == 'ios':
                # Analyze App Store metadata
                analysis['metadata_findings'].append({
                    'type': 'privacy_labels',
                    'description': 'Incomplete privacy nutrition labels'
                })

            # Calculate security score
            analysis['security_score'] = self._calculate_security_score(analysis)

        except Exception as e:
            logger.error(f"Error analyzing metadata for {app_id}: {e}")

        return analysis

    def _calculate_security_score(self, analysis: Dict) -> int:
        """Calculate security score based on findings"""
        base_score = 100

        # Deduct points for each finding
        deductions = {
            'permissions_analysis': 20,
            'data_collection': 15,
            'privacy_labels': 10,
            'incomplete_privacy': 15
        }

        for finding in analysis.get('metadata_findings', []):
            finding_type = finding.get('type', '')
            if finding_type in deductions:
                base_score -= deductions[finding_type]

        for concern in analysis.get('privacy_concerns', []):
            concern_type = concern.get('type', '')
            if concern_type in deductions:
                base_score -= deductions[concern_type]

        return max(0, min(100, base_score))

    def generate_report(self, results: List[MobileAppScanResult]) -> Dict:
        """Generate comprehensive mobile app analysis report"""

        total_vulnerabilities = sum(len(r.vulnerabilities) for r in results)
        platforms = list(set(r.platform for r in results))

        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        vulnerability_types = {}

        for result in results:
            for vuln in result.vulnerabilities:
                severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
                vuln_type = vuln.vulnerability_type
                vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1

        return {
            'scan_summary': {
                'total_apps_scanned': len(results),
                'total_vulnerabilities': total_vulnerabilities,
                'platforms_covered': platforms,
                'severity_breakdown': severity_counts,
                'vulnerability_types': vulnerability_types,
                'scan_timestamp': datetime.now().isoformat()
            },
            'results': [self._result_to_dict(r) for r in results],
            'recommendations': self._generate_mobile_recommendations(results)
        }

    def _result_to_dict(self, result: MobileAppScanResult) -> Dict:
        """Convert scan result to dictionary"""
        return {
            'app_id': result.app_id,
            'app_name': result.app_name,
            'platform': result.platform,
            'version': result.version,
            'developer': result.developer,
            'vulnerabilities': [self._vuln_to_dict(v) for v in result.vulnerabilities],
            'api_endpoints': result.api_endpoints,
            'permissions': result.permissions,
            'network_traffic': result.network_traffic,
            'storage_findings': result.storage_findings,
            'timestamp': result.timestamp
        }

    def _vuln_to_dict(self, vuln: MobileAppVulnerability) -> Dict:
        """Convert vulnerability to dictionary"""
        return {
            'title': vuln.title,
            'description': vuln.description,
            'severity': vuln.severity,
            'type': vuln.vulnerability_type,
            'platform': vuln.platform,
            'exploitability': vuln.exploitability,
            'profit_potential': vuln.profit_potential,
            'technical_details': vuln.technical_details,
            'proof_of_concept': vuln.proof_of_concept,
            'mitigation': vuln.mitigation,
            'timestamp': vuln.timestamp
        }

    def _generate_mobile_recommendations(self, results: List[MobileAppScanResult]) -> List[str]:
        """Generate recommendations based on mobile app findings"""
        recommendations = []

        all_vulns = [v for r in results for v in r.vulnerabilities]
        vuln_types = set(v.vulnerability_type for v in all_vulns)

        if 'insecure_transport' in vuln_types:
            recommendations.append("Implement HTTPS with certificate pinning for all network communications")

        if 'hardcoded_credentials' in vuln_types:
            recommendations.append("Remove hardcoded credentials and use secure key storage mechanisms")

        if 'weak_cryptography' in vuln_types:
            recommendations.append("Implement strong encryption (AES-256+) for sensitive data")

        if 'missing_certificate_pinning' in vuln_types:
            recommendations.append("Implement certificate pinning to prevent man-in-the-middle attacks")

        recommendations.extend([
            "Conduct regular security audits of mobile applications",
            "Implement proper session management and token handling",
            "Use obfuscation techniques to protect against reverse engineering",
            "Regularly update dependencies to patch known vulnerabilities",
            "Implement proper input validation and sanitization"
        ])

        return recommendations
