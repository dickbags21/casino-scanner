"""
Account Creation Scanner Plugin
Wraps tools/account_creation_scanner.py as a dashboard plugin
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "tools"))

from typing import Dict, Optional
import asyncio

from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata, ScanProgress
from tools.account_creation_scanner import AccountCreationScanner


class AccountCreationPlugin(BasePlugin):
    """Account creation scanner plugin"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.scanner = None
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="account_creation",
            display_name="Account Creation Scanner",
            description="Advanced scanner for detecting multiple account creation vulnerabilities",
            version="1.0.0",
            plugin_type="scanner"
        )
    
    def validate_config(self, config: Dict) -> tuple[bool, Optional[str]]:
        """Validate scan configuration"""
        if 'url' not in config:
            return False, "URL must be specified"
        return True, None
    
    async def scan(self, scan_config: Dict, progress_callback=None) -> Dict:
        """Execute account creation vulnerability scan"""
        url = scan_config['url']
        
        # Initialize scanner
        headless = self.config.get('headless', True) if self.config else True
        timeout = self.config.get('timeout', 30000) if self.config else 30000
        max_attempts = self.config.get('max_attempts', 10) if self.config else 10
        
        self.scanner = AccountCreationScanner(
            headless=headless,
            timeout=timeout,
            max_attempts=max_attempts
        )
        
        try:
            await self.scanner.start()
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.1,
                    status='running',
                    message=f"Scanning account creation vulnerabilities: {url}",
                    current_step="Initialization",
                    total_steps=5,
                    current_step_num=1
                ))
            
            # Run scan
            scan_result = await self.scanner.scan_url(url)
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.8,
                    status='running',
                    message=f"Found {len(scan_result.vulnerabilities)} vulnerabilities",
                    current_step="Analysis",
                    total_steps=5,
                    current_step_num=4
                ))
            
            # Convert vulnerabilities to dict format
            vulnerabilities = []
            for vuln in scan_result.vulnerabilities:
                vuln_dict = {
                    'title': vuln.title,
                    'description': vuln.description,
                    'severity': vuln.severity,
                    'vulnerability_type': vuln.vulnerability_type,
                    'url': url,
                    'exploitability': vuln.exploitability,
                    'profit_potential': vuln.profit_potential,
                    'technical_details': vuln.technical_details,
                    'proof_of_concept': vuln.proof_of_concept,
                    'mitigation': vuln.mitigation,
                    'timestamp': vuln.timestamp
                }
                vulnerabilities.append(vuln_dict)
            
            result_dict = {
                'url': scan_result.url,
                'success': scan_result.success,
                'vulnerabilities': vulnerabilities,
                'test_attempts': scan_result.test_attempts,
                'forms_analyzed': scan_result.forms_analyzed,
                'captchas_detected': scan_result.captchas_detected,
                'validation_bypass_methods': scan_result.validation_bypass_methods,
                'screenshots': scan_result.screenshots,
                'timestamp': scan_result.timestamp
            }
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=1.0,
                    status='completed',
                    message="Scan completed",
                    current_step="Complete",
                    total_steps=5,
                    current_step_num=5
                ))
            
            return {
                'scan_type': 'account_creation',
                'results': [result_dict],
                'vulnerabilities': vulnerabilities,
                'total_results': 1,
                'total_vulnerabilities': len(vulnerabilities)
            }
        
        finally:
            await self.scanner.stop()


