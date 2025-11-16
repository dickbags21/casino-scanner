"""
Shodan Scanner Module
Handles reconnaissance using Shodan API
"""

import shodan
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ShodanResult:
    """Container for Shodan scan results"""
    ip: str
    port: int
    hostname: Optional[str]
    org: Optional[str]
    country: str
    city: Optional[str]
    product: Optional[str]
    version: Optional[str]
    banner: Optional[str]
    vulns: List[str]
    timestamp: str


class ShodanScanner:
    """Shodan API integration for reconnaissance"""
    
    def __init__(self, api_key: str, rate_limit: int = 10):
        """
        Initialize Shodan scanner
        
        Args:
            api_key: Shodan API key
            rate_limit: Maximum requests per second
        """
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.api = shodan.Shodan(api_key)
        self.last_request_time = 0
        self.min_request_interval = 1.0 / rate_limit
        
    def _rate_limit_check(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search(self, query: str, limit: int = 100) -> List[ShodanResult]:
        """
        Search Shodan with a query
        
        Args:
            query: Shodan search query
            limit: Maximum results to return
            
        Returns:
            List of ShodanResult objects
        """
        self._rate_limit_check()
        
        try:
            logger.info(f"Searching Shodan with query: {query}")
            results = self.api.search(query, limit=limit)
            
            shodan_results = []
            for match in results.get('matches', []):
                result = ShodanResult(
                    ip=match.get('ip_str', ''),
                    port=match.get('port', 0),
                    hostname=match.get('hostnames', [None])[0],
                    org=match.get('org', None),
                    country=match.get('location', {}).get('country_name', 'Unknown'),
                    city=match.get('location', {}).get('city', None),
                    product=match.get('product', None),
                    version=match.get('version', None),
                    banner=match.get('data', None),
                    vulns=list(match.get('vulns', {}).keys()) if 'vulns' in match else [],
                    timestamp=match.get('timestamp', '')
                )
                shodan_results.append(result)
            
            logger.info(f"Found {len(shodan_results)} results")
            return shodan_results
            
        except shodan.APIError as e:
            logger.error(f"Shodan API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Shodan search: {e}")
            return []
    
    def search_by_country(self, country_code: str, keywords: List[str], 
                         ports: List[int] = None) -> List[ShodanResult]:
        """
        Search Shodan by country and keywords
        
        Args:
            country_code: ISO country code (e.g., 'VN', 'LA')
            keywords: List of keywords to search for
            ports: Optional list of ports to filter
            
        Returns:
            List of ShodanResult objects
        """
        queries = []
        
        for keyword in keywords:
            query = f'country:{country_code} {keyword}'
            if ports:
                port_filter = ' OR '.join([f'port:{p}' for p in ports])
                query += f' ({port_filter})'
            queries.append(query)
        
        all_results = []
        for query in queries:
            results = self.search(query, limit=50)
            all_results.extend(results)
            time.sleep(0.5)  # Additional delay between queries
        
        # Remove duplicates based on IP:port combination
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result.ip, result.port)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    def get_host_info(self, ip: str) -> Optional[Dict]:
        """
        Get detailed information about a host
        
        Args:
            ip: IP address to query
            
        Returns:
            Dictionary with host information or None
        """
        self._rate_limit_check()
        
        try:
            host = self.api.host(ip)
            return host
        except shodan.APIError as e:
            logger.error(f"Error getting host info for {ip}: {e}")
            return None
    
    def check_api_info(self) -> Dict:
        """
        Check API key status and account info
        
        Returns:
            Dictionary with API information
        """
        self._rate_limit_check()
        
        try:
            info = self.api.info()
            return info
        except shodan.APIError as e:
            logger.error(f"Error checking API info: {e}")
            return {}

