"""
Browser Scanner Plugin
Wraps tools/browser_scanner.py as a dashboard plugin
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "tools"))

from typing import Dict, Optional
import asyncio

from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata, ScanProgress
from tools.browser_scanner import BrowserScanner


class BrowserPlugin(BasePlugin):
    """Browser scanner plugin with enhanced control features"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.scanner = None
        self._browser_instances: Dict[str, BrowserScanner] = {}  # Track multiple browser instances
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="browser",
            display_name="Browser Scanner",
            description="Automated browser testing for signup flows and bonus offers",
            version="1.0.0",
            plugin_type="scanner"
        )
    
    def validate_config(self, config: Dict) -> tuple[bool, Optional[str]]:
        """Validate scan configuration"""
        if 'url' not in config:
            return False, "URL must be specified"
        return True, None
    
    async def scan(self, scan_config: Dict, progress_callback=None) -> Dict:
        """Execute browser scan"""
        url = scan_config['url']
        scan_type = scan_config.get('scan_type', 'signup')  # 'signup' or 'bonus'
        
        # Initialize scanner
        headless = self.config.get('headless', True) if self.config else True
        timeout = self.config.get('timeout', 30000) if self.config else 30000
        screenshot_dir = self.config.get('screenshot_dir', 'results/screenshots') if self.config else 'results/screenshots'
        
        self.scanner = BrowserScanner(
            headless=headless,
            timeout=timeout,
            screenshot_dir=screenshot_dir
        )
        
        try:
            await self.scanner.start()
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=0.2,
                    status='running',
                    message=f"Starting browser scan: {url}",
                    current_step="Browser Initialization",
                    total_steps=3,
                    current_step_num=1
                ))
            
            results = []
            vulnerabilities = []
            
            if scan_type == 'signup':
                # Test signup flow
                test_data = scan_config.get('test_data', {})
                
                if progress_callback:
                    await progress_callback(ScanProgress(
                        scan_id=scan_config.get('scan_id', ''),
                        progress=0.5,
                        status='running',
                        message="Testing signup flow...",
                        current_step="Signup Test",
                        total_steps=3,
                        current_step_num=2
                    ))
                
                signup_result = await self.scanner.test_signup_flow(url, test_data)
                
                result_dict = {
                    'url': signup_result.url,
                    'success': signup_result.success,
                    'issues': signup_result.issues,
                    'fields_found': signup_result.fields_found,
                    'validation_errors': signup_result.validation_errors,
                    'screenshot_path': signup_result.screenshot_path,
                    'timestamp': signup_result.timestamp
                }
                results.append(result_dict)
                
                # Check for vulnerabilities
                if not signup_result.success and signup_result.issues:
                    for issue in signup_result.issues:
                        if 'CAPTCHA' in issue or 'captcha' in issue.lower():
                            vulnerabilities.append({
                                'title': 'CAPTCHA Issue Detected',
                                'description': issue,
                                'severity': 'medium',
                                'vulnerability_type': 'captcha_bypass',
                                'url': url,
                                'exploitability': 'medium',
                                'profit_potential': 'low'
                            })
                
                if len(signup_result.validation_errors) == 0 and signup_result.success:
                    vulnerabilities.append({
                        'title': 'Weak Signup Validation',
                        'description': 'Signup form may allow weak validation',
                        'severity': 'medium',
                        'vulnerability_type': 'weak_validation',
                        'url': url,
                        'exploitability': 'easy',
                        'profit_potential': 'medium'
                    })
            
            elif scan_type == 'bonus':
                # Test bonus code
                bonus_code = scan_config.get('bonus_code', 'WELCOME')
                
                if progress_callback:
                    await progress_callback(ScanProgress(
                        scan_id=scan_config.get('scan_id', ''),
                        progress=0.5,
                        status='running',
                        message=f"Testing bonus code: {bonus_code}",
                        current_step="Bonus Test",
                        total_steps=3,
                        current_step_num=2
                    ))
                
                bonus_result = await self.scanner.test_bonus_code(url, bonus_code)
                
                result_dict = {
                    'url': bonus_result.url,
                    'bonus_code': bonus_result.bonus_code,
                    'success': bonus_result.success,
                    'message': bonus_result.message,
                    'validation_bypassed': bonus_result.validation_bypassed,
                    'screenshot_path': bonus_result.screenshot_path,
                    'timestamp': bonus_result.timestamp
                }
                results.append(result_dict)
                
                if bonus_result.validation_bypassed:
                    vulnerabilities.append({
                        'title': 'Bonus Code Validation Bypass',
                        'description': f'Bonus code {bonus_code} validation may be bypassable',
                        'severity': 'high',
                        'vulnerability_type': 'bonus_bypass',
                        'url': url,
                        'exploitability': 'easy',
                        'profit_potential': 'high'
                    })
            
            if progress_callback:
                await progress_callback(ScanProgress(
                    scan_id=scan_config.get('scan_id', ''),
                    progress=1.0,
                    status='completed',
                    message="Scan completed",
                    current_step="Complete",
                    total_steps=3,
                    current_step_num=3
                ))
            
            return {
                'scan_type': 'browser',
                'scan_subtype': scan_type,
                'results': results,
                'vulnerabilities': vulnerabilities,
                'total_results': len(results),
                'total_vulnerabilities': len(vulnerabilities)
            }
        
        finally:
            await self.scanner.stop()
    
    async def start_browser_instance(self, instance_id: Optional[str] = None, headless: bool = True) -> str:
        """
        Start a persistent browser instance for reuse
        
        Args:
            instance_id: Optional instance ID (generated if not provided)
            headless: Run in headless mode
            
        Returns:
            Instance ID
        """
        import uuid
        if instance_id is None:
            instance_id = str(uuid.uuid4())
        
        if instance_id in self._browser_instances:
            return instance_id  # Already exists
        
        config = self.config or {}
        timeout = config.get('timeout', 30000)
        screenshot_dir = config.get('screenshot_dir', 'results/screenshots')
        
        scanner = BrowserScanner(
            headless=headless,
            timeout=timeout,
            screenshot_dir=screenshot_dir
        )
        await scanner.start()
        self._browser_instances[instance_id] = scanner
        return instance_id
    
    async def stop_browser_instance(self, instance_id: str) -> bool:
        """
        Stop a specific browser instance
        
        Args:
            instance_id: Instance ID to stop
            
        Returns:
            True if stopped, False if not found
        """
        if instance_id in self._browser_instances:
            scanner = self._browser_instances[instance_id]
            await scanner.stop()
            del self._browser_instances[instance_id]
            return True
        return False
    
    async def stop_all_browser_instances(self):
        """Stop all browser instances"""
        for instance_id, scanner in list(self._browser_instances.items()):
            await scanner.stop()
        self._browser_instances.clear()
    
    def get_browser_instances(self) -> Dict[str, BrowserScanner]:
        """Get all active browser instances"""
        return self._browser_instances.copy()
    
    def get_browser_status(self) -> Dict:
        """Get browser plugin status"""
        return {
            'active_instances': len(self._browser_instances),
            'instance_ids': list(self._browser_instances.keys()),
            'enabled': self.enabled
        }
    
    async def scan_with_instance(self, instance_id: str, scan_config: Dict, progress_callback=None) -> Dict:
        """
        Execute scan using an existing browser instance
        
        Args:
            instance_id: Browser instance ID to use
            scan_config: Scan configuration
            progress_callback: Optional progress callback
            
        Returns:
            Scan results
        """
        if instance_id not in self._browser_instances:
            raise ValueError(f"Browser instance {instance_id} not found")
        
        scanner = self._browser_instances[instance_id]
        url = scan_config['url']
        scan_type = scan_config.get('scan_type', 'signup')
        
        # Temporarily replace scanner for this scan
        original_scanner = self.scanner
        self.scanner = scanner
        
        try:
            results = []
            vulnerabilities = []
            
            if scan_type == 'signup':
                test_data = scan_config.get('test_data', {})
                signup_result = await scanner.test_signup_flow(url, test_data)
                results.append({
                    'url': signup_result.url,
                    'success': signup_result.success,
                    'issues': signup_result.issues,
                    'fields_found': signup_result.fields_found,
                    'validation_errors': signup_result.validation_errors,
                    'screenshot_path': signup_result.screenshot_path,
                    'timestamp': signup_result.timestamp
                })
            elif scan_type == 'bonus':
                bonus_code = scan_config.get('bonus_code', 'WELCOME')
                bonus_result = await scanner.test_bonus_code(url, bonus_code)
                results.append({
                    'url': bonus_result.url,
                    'bonus_code': bonus_result.bonus_code,
                    'success': bonus_result.success,
                    'message': bonus_result.message,
                    'validation_bypassed': bonus_result.validation_bypassed,
                    'screenshot_path': bonus_result.screenshot_path,
                    'timestamp': bonus_result.timestamp
                })
            
            return {
                'scan_type': 'browser',
                'scan_subtype': scan_type,
                'results': results,
                'vulnerabilities': vulnerabilities,
                'instance_id': instance_id
            }
        finally:
            self.scanner = original_scanner


