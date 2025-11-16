"""
Shodan Scanner Plugin
Wraps tools/shodan_scanner.py as a dashboard plugin
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "tools"))

from typing import Dict, Optional
import asyncio
import yaml

from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata, ScanProgress
from tools.shodan_scanner import ShodanScanner


class ShodanPlugin(BasePlugin):
    """Shodan scanner plugin"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.scanner = None
        self._init_scanner()
    
    def _init_scanner(self):
        """Initialize Shodan scanner from config"""
        # Try to load API key from config file
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        api_key = None
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    api_key = config_data.get('apis', {}).get('shodan', {}).get('api_key')
            except Exception as e:
                pass
        
        # Override with plugin config if provided
        if self.config and 'api_key' in self.config:
            api_key = self.config['api_key']
        
        if api_key and api_key != "YOUR_SHODAN_API_KEY_HERE":
            rate_limit = self.config.get('rate_limit', 10) if self.config else 10
            self.scanner = ShodanScanner(api_key=api_key, rate_limit=rate_limit)
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="shodan",
            display_name="Shodan Scanner",
            description="Reconnaissance scanner using Shodan API to discover casino infrastructure",
            version="1.0.0",
            plugin_type="scanner"
        )
    
    def validate_config(self, config: Dict) -> tuple[bool, Optional[str]]:
        """Validate scan configuration"""
        if 'query' not in config and 'region' not in config:
            return False, "Either 'query' or 'region' must be specified"
        return True, None
    
    async def scan(self, scan_config: Dict, progress_callback=None) -> Dict:
        """Execute Shodan scan"""
        if not self.scanner:
            raise ValueError("Shodan scanner not initialized. Check API key configuration.")
        
        results = []
        vulnerabilities = []
        
        # Determine scan type
        if 'query' in scan_config:
            # Direct query scan
            query = scan_config['query']
            limit = scan_config.get('limit', 100)
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.1,
                    status='running',
                    message=f"Searching Shodan: {query}",
                    current_step="Shodan Search",
                    total_steps=2,
                    current_step_num=1
                ))
            
            shodan_results = self.scanner.search(query, limit=limit)
            
            # Convert to dict format
            for result in shodan_results:
                result_dict = {
                    'ip': result.ip,
                    'port': result.port,
                    'hostname': result.hostname,
                    'org': result.org,
                    'country': result.country,
                    'city': result.city,
                    'product': result.product,
                    'version': result.version,
                    'banner': result.banner,
                    'vulns': result.vulns,
                    'timestamp': result.timestamp
                }
                results.append(result_dict)
                
                # Extract vulnerabilities
                if result.vulns:
                    for vuln in result.vulns:
                        vulnerabilities.append({
                            'title': f"Known Vulnerability: {vuln}",
                            'description': f"Vulnerability {vuln} detected on {result.ip}:{result.port}",
                            'severity': 'high',
                            'vulnerability_type': 'known_cve',
                            'url': f"http://{result.ip}:{result.port}",
                            'ip': result.ip,
                            'port': result.port,
                            'exploitability': 'medium',
                            'profit_potential': 'medium'
                        })
        
        elif 'region' in scan_config:
            # Region-based scan
            region = scan_config['region']
            keywords = scan_config.get('keywords', ['casino'])
            ports = scan_config.get('ports', [80, 443, 8080, 8443])
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.1,
                    status='running',
                    message=f"Scanning region: {region}",
                    current_step="Region Scan",
                    total_steps=len(keywords),
                    current_step_num=0
                ))
            
            # Load region config if available
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
            country_code = None
            
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                        region_config = config_data.get('regions', {}).get(region, {})
                        country_code = region_config.get('country_code')
                        if not keywords:
                            keywords = region_config.get('search_terms', ['casino'])
                        if not ports:
                            ports = region_config.get('ports', [80, 443])
                except Exception:
                    pass
            
            if not country_code:
                # Default country codes
                country_codes = {
                    'vietnam': 'VN',
                    'laos': 'LA',
                    'cambodia': 'KH'
                }
                country_code = country_codes.get(region.lower(), region.upper())
            
            shodan_results = self.scanner.search_by_country(
                country_code=country_code,
                keywords=keywords,
                ports=ports
            )
            
            # Convert to dict format
            for i, result in enumerate(shodan_results):
                result_dict = {
                    'ip': result.ip,
                    'port': result.port,
                    'hostname': result.hostname,
                    'org': result.org,
                    'country': result.country,
                    'city': result.city,
                    'product': result.product,
                    'version': result.version,
                    'banner': result.banner,
                    'vulns': result.vulns,
                    'timestamp': result.timestamp
                }
                results.append(result_dict)
                
                # Extract vulnerabilities
                if result.vulns:
                    for vuln in result.vulns:
                        vulnerabilities.append({
                            'title': f"Known Vulnerability: {vuln}",
                            'description': f"Vulnerability {vuln} detected on {result.ip}:{result.port}",
                            'severity': 'high',
                            'vulnerability_type': 'known_cve',
                            'url': f"http://{result.ip}:{result.port}",
                            'ip': result.ip,
                            'port': result.port,
                            'exploitability': 'medium',
                            'profit_potential': 'medium'
                        })
                
                if progress_callback:
                    progress = 0.1 + (i / len(shodan_results)) * 0.8
                    await progress_callback(ScanProgress(
                        scan_id=scan_config.get('scan_id', ''),
                        progress=progress,
                        status='running',
                        message=f"Found {len(results)} results",
                        current_step="Processing Results",
                        total_steps=len(shodan_results),
                        current_step_num=i + 1
                    ))
        
        return {
            'scan_type': 'shodan',
            'results': results,
            'vulnerabilities': vulnerabilities,
            'total_results': len(results),
            'total_vulnerabilities': len(vulnerabilities)
        }


