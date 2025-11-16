"""
Multi-API Manager for Casino Scanner Pro
Manages multiple security research APIs for comprehensive analysis
"""

import requests
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class APIResult:
    """Container for API query results"""
    api_name: str
    success: bool
    data: Dict
    error: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class MultiAPIManager:
    """
    Manages multiple security research APIs
    
    Supported APIs:
    - Shodan (primary)
    - VirusTotal
    - AbuseIPDB
    - URLScan.io
    - SecurityTrails
    - WhoisXML
    """

    def __init__(self, config: Dict):
        """
        Initialize API manager with configuration
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config
        self.apis = {}
        self.rate_limits = {}
        self.last_request_times = {}
        
        # Initialize enabled APIs
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize all enabled APIs"""
        api_configs = self.config.get('apis', {})
        
        # Shodan
        if api_configs.get('shodan', {}).get('enabled', True):
            try:
                import shodan
                api_key = api_configs['shodan'].get('api_key', '')
                if api_key and api_key != "YOUR_SHODAN_API_KEY_HERE":
                    self.apis['shodan'] = shodan.Shodan(api_key)
                    self.rate_limits['shodan'] = api_configs['shodan'].get('rate_limit', 10)
                    logger.info("✅ Shodan API initialized")
            except ImportError:
                logger.warning("Shodan library not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Shodan: {e}")
        
        # VirusTotal
        if api_configs.get('virustotal', {}).get('enabled', False):
            api_key = api_configs['virustotal'].get('api_key', '')
            if api_key and api_key != "YOUR_VIRUSTOTAL_API_KEY_HERE":
                self.apis['virustotal'] = {
                    'api_key': api_key,
                    'base_url': 'https://www.virustotal.com/vtapi/v2',
                    'rate_limit': api_configs['virustotal'].get('rate_limit', 4)
                }
                logger.info("✅ VirusTotal API configured")
        
        # AbuseIPDB
        if api_configs.get('abuseipdb', {}).get('enabled', False):
            api_key = api_configs['abuseipdb'].get('api_key', '')
            if api_key and api_key != "YOUR_ABUSEIPDB_API_KEY_HERE":
                self.apis['abuseipdb'] = {
                    'api_key': api_key,
                    'base_url': 'https://api.abuseipdb.com/api/v2',
                    'rate_limit': api_configs['abuseipdb'].get('rate_limit', 2)
                }
                logger.info("✅ AbuseIPDB API configured")
        
        # URLScan.io
        if api_configs.get('urlscan', {}).get('enabled', False):
            api_key = api_configs['urlscan'].get('api_key', '')
            self.apis['urlscan'] = {
                'api_key': api_key if api_key else None,  # Optional
                'base_url': 'https://urlscan.io/api/v1',
                'rate_limit': api_configs['urlscan'].get('rate_limit', 10)
            }
            logger.info("✅ URLScan.io API configured")
    
    def _rate_limit_check(self, api_name: str):
        """Enforce rate limiting for API"""
        if api_name not in self.last_request_times:
            self.last_request_times[api_name] = 0
        
        rate_limit = self.rate_limits.get(api_name, 1)
        min_interval = 1.0 / rate_limit
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_times[api_name]
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_times[api_name] = time.time()
    
    def query_ip_shodan(self, ip: str) -> APIResult:
        """Query Shodan for IP information"""
        if 'shodan' not in self.apis:
            return APIResult('shodan', False, {}, 'Shodan API not initialized')
        
        try:
            self._rate_limit_check('shodan')
            host_info = self.apis['shodan'].host(ip)
            return APIResult('shodan', True, host_info)
        except Exception as e:
            return APIResult('shodan', False, {}, str(e))
    
    def query_url_virustotal(self, url: str) -> APIResult:
        """Query VirusTotal for URL reputation"""
        if 'virustotal' not in self.apis:
            return APIResult('virustotal', False, {}, 'VirusTotal API not configured')
        
        try:
            self._rate_limit_check('virustotal')
            api_config = self.apis['virustotal']
            
            params = {
                'apikey': api_config['api_key'],
                'resource': url
            }
            
            response = requests.get(
                f"{api_config['base_url']}/url/report",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return APIResult('virustotal', True, response.json())
            else:
                return APIResult('virustotal', False, {}, f"HTTP {response.status_code}")
        
        except Exception as e:
            return APIResult('virustotal', False, {}, str(e))
    
    def query_ip_abuseipdb(self, ip: str, days: int = 90) -> APIResult:
        """Query AbuseIPDB for IP reputation"""
        if 'abuseipdb' not in self.apis:
            return APIResult('abuseipdb', False, {}, 'AbuseIPDB API not configured')
        
        try:
            self._rate_limit_check('abuseipdb')
            api_config = self.apis['abuseipdb']
            
            headers = {
                'Key': api_config['api_key'],
                'Accept': 'application/json'
            }
            
            params = {
                'ipAddress': ip,
                'maxAgeInDays': days,
                'verbose': ''
            }
            
            response = requests.get(
                f"{api_config['base_url']}/check",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return APIResult('abuseipdb', True, response.json())
            else:
                return APIResult('abuseipdb', False, {}, f"HTTP {response.status_code}")
        
        except Exception as e:
            return APIResult('abuseipdb', False, {}, str(e))
    
    def scan_url_urlscan(self, url: str) -> APIResult:
        """Submit URL to URLScan.io for analysis"""
        if 'urlscan' not in self.apis:
            return APIResult('urlscan', False, {}, 'URLScan API not configured')
        
        try:
            self._rate_limit_check('urlscan')
            api_config = self.apis['urlscan']
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if api_config['api_key']:
                headers['API-Key'] = api_config['api_key']
            
            data = {
                'url': url,
                'public': 'on'
            }
            
            response = requests.post(
                f"{api_config['base_url']}/scan/",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return APIResult('urlscan', True, response.json())
            else:
                return APIResult('urlscan', False, {}, f"HTTP {response.status_code}")
        
        except Exception as e:
            return APIResult('urlscan', False, {}, str(e))
    
    def comprehensive_analysis(self, target: str, target_type: str = 'ip') -> Dict:
        """
        Run comprehensive analysis using all available APIs
        
        Args:
            target: IP address or URL to analyze
            target_type: 'ip' or 'url'
        
        Returns:
            Dictionary with results from all APIs
        """
        results = {
            'target': target,
            'target_type': target_type,
            'timestamp': datetime.now().isoformat(),
            'api_results': {}
        }
        
        if target_type == 'ip':
            # IP-based analysis
            if 'shodan' in self.apis:
                results['api_results']['shodan'] = self.query_ip_shodan(target).__dict__
            
            if 'abuseipdb' in self.apis:
                results['api_results']['abuseipdb'] = self.query_ip_abuseipdb(target).__dict__
        
        elif target_type == 'url':
            # URL-based analysis
            if 'virustotal' in self.apis:
                results['api_results']['virustotal'] = self.query_url_virustotal(target).__dict__
            
            if 'urlscan' in self.apis:
                results['api_results']['urlscan'] = self.scan_url_urlscan(target).__dict__
        
        return results
    
    def get_available_apis(self) -> List[str]:
        """Get list of available/configured APIs"""
        return list(self.apis.keys())
    
    def test_all_apis(self) -> Dict:
        """Test all configured APIs"""
        test_results = {}
        
        for api_name in self.apis.keys():
            try:
                if api_name == 'shodan':
                    # Test Shodan with info() call
                    info = self.apis['shodan'].info()
                    test_results[api_name] = {
                        'status': 'working',
                        'credits': info.get('query_credits', 0),
                        'scan_credits': info.get('scan_credits', 0)
                    }
                else:
                    test_results[api_name] = {
                        'status': 'configured',
                        'note': 'API configured but not tested'
                    }
            except Exception as e:
                test_results[api_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return test_results



