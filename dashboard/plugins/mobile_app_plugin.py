"""
Mobile App Scanner Plugin
Wraps tools/mobile_app_scanner.py as a dashboard plugin
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "tools"))

from typing import Dict, Optional
import asyncio

from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata, ScanProgress
from tools.mobile_app_scanner import MobileAppScanner


class MobileAppPlugin(BasePlugin):
    """Mobile app scanner plugin"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.scanner = None
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mobile_app",
            display_name="Mobile App Scanner",
            description="Advanced mobile gambling app vulnerability scanner for Android and iOS",
            version="1.0.0",
            plugin_type="scanner"
        )
    
    def validate_config(self, config: Dict) -> tuple[bool, Optional[str]]:
        """Validate scan configuration"""
        if 'app_path' not in config and 'app_id' not in config:
            return False, "Either 'app_path' or 'app_id' must be specified"
        return True, None
    
    async def scan(self, scan_config: Dict, progress_callback=None) -> Dict:
        """Execute mobile app scan"""
        app_path = scan_config.get('app_path')
        app_id = scan_config.get('app_id')
        platform = scan_config.get('platform', 'android')  # 'android' or 'ios'
        
        # Initialize scanner
        self.scanner = MobileAppScanner()
        
        if progress_callback:
            await progress_callback(ScanProgress(
                scan_id=scan_config.get('scan_id', ''),
                progress=0.1,
                status='running',
                message=f"Scanning mobile app: {app_path or app_id}",
                current_step="Initialization",
                total_steps=5,
                current_step_num=1
            ))
        
        results = []
        vulnerabilities = []
        
        try:
            if app_path:
                # Scan APK/IPA file
                if progress_callback:
                    await progress_callback(ScanProgress(
                        scan_id=scan_config.get('scan_id', ''),
                        progress=0.3,
                        status='running',
                        message="Analyzing app file...",
                        current_step="File Analysis",
                        total_steps=5,
                        current_step_num=2
                    ))
                
                if platform == 'android':
                    scan_result = await self.scanner.scan_apk(app_path)
                else:
                    scan_result = await self.scanner.scan_ipa(app_path)
            else:
                # Scan by app ID (would need app store integration)
                raise NotImplementedError("App ID scanning not yet implemented")
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.7,
                    status='running',
                    message=f"Found {len(scan_result.vulnerabilities)} vulnerabilities",
                    current_step="Vulnerability Analysis",
                    total_steps=5,
                    current_step_num=4
                ))
            
            # Convert vulnerabilities to dict format
            for vuln in scan_result.vulnerabilities:
                vuln_dict = {
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
                vulnerabilities.append(vuln_dict)
            
            result_dict = {
                'app_id': scan_result.app_id,
                'app_name': scan_result.app_name,
                'platform': scan_result.platform,
                'version': scan_result.version,
                'developer': scan_result.developer,
                'vulnerabilities': vulnerabilities,
                'api_endpoints': scan_result.api_endpoints,
                'permissions': scan_result.permissions,
                'network_traffic': scan_result.network_traffic,
                'storage_findings': scan_result.storage_findings,
                'timestamp': scan_result.timestamp
            }
            results.append(result_dict)
            
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
                'scan_type': 'mobile_app',
                'platform': platform,
                'results': results,
                'vulnerabilities': vulnerabilities,
                'total_results': len(results),
                'total_vulnerabilities': len(vulnerabilities)
            }
        
        except Exception as e:
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.0,
                    status='failed',
                    message=f"Error: {str(e)}",
                    current_step="Error",
                    total_steps=5,
                    current_step_num=0
                ))
            raise


