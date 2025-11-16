"""
Base Plugin Interface for Casino Scanner Dashboard
All scanner tools implement this interface to become plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import uuid


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    display_name: str
    description: str
    version: str
    author: str = "Casino Scanner"
    plugin_type: str = "scanner"  # 'scanner', 'analyzer', 'reporter', etc.


@dataclass
class ScanProgress:
    """Scan progress information"""
    scan_id: str
    progress: float  # 0.0 to 1.0
    status: str  # 'running', 'completed', 'failed'
    message: str = ""
    current_step: str = ""
    total_steps: int = 0
    current_step_num: int = 0


class BasePlugin(ABC):
    """Base plugin interface that all scanner plugins must implement"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize plugin
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.metadata = self.get_metadata()
        self.enabled = True
        self._scan_tasks: Dict[str, asyncio.Task] = {}
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata
        
        Returns:
            PluginMetadata object
        """
        pass
    
    @abstractmethod
    async def scan(self, scan_config: Dict, progress_callback=None) -> Dict:
        """
        Execute scan
        
        Args:
            scan_config: Scan configuration
            progress_callback: Optional callback function(progress: ScanProgress)
            
        Returns:
            Dictionary with scan results
        """
        pass
    
    def validate_config(self, config: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate scan configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None
    
    async def start_scan(self, scan_config: Dict, scan_id: Optional[str] = None, progress_callback=None) -> str:
        """
        Start a scan asynchronously
        
        Args:
            scan_config: Scan configuration
            scan_id: Optional scan ID (generated if not provided)
            progress_callback: Optional progress callback
            
        Returns:
            Scan ID
        """
        if scan_id is None:
            scan_id = str(uuid.uuid4())
        
        async def run_scan():
            try:
                return await self.scan(scan_config, progress_callback)
            except Exception as e:
                if progress_callback:
                    await progress_callback(ScanProgress(
                        scan_id=scan_id,
                        progress=0.0,
                        status='failed',
                        message=str(e)
                    ))
                raise
        
        task = asyncio.create_task(run_scan())
        self._scan_tasks[scan_id] = task
        return scan_id
    
    async def stop_scan(self, scan_id: str) -> bool:
        """
        Stop a running scan
        
        Args:
            scan_id: Scan ID to stop
            
        Returns:
            True if scan was stopped, False if not found
        """
        if scan_id in self._scan_tasks:
            task = self._scan_tasks[scan_id]
            task.cancel()
            del self._scan_tasks[scan_id]
            return True
        return False
    
    def get_running_scans(self) -> List[str]:
        """Get list of running scan IDs"""
        return [scan_id for scan_id, task in self._scan_tasks.items() if not task.done()]
    
    def get_info(self) -> Dict:
        """
        Get plugin information
        
        Returns:
            Dictionary with plugin info
        """
        return {
            'name': self.metadata.name,
            'display_name': self.metadata.display_name,
            'description': self.metadata.description,
            'version': self.metadata.version,
            'author': self.metadata.author,
            'plugin_type': self.metadata.plugin_type,
            'enabled': self.enabled,
            'running_scans': len(self.get_running_scans())
        }


