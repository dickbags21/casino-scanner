"""
Plugin Manager for Casino Scanner Dashboard
Handles plugin discovery, registration, and management
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Type
import logging

from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin registration and discovery"""
    
    def __init__(self):
        """Initialize plugin manager"""
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
    
    def register_plugin(self, plugin_class: Type[BasePlugin], config: Optional[Dict] = None):
        """
        Register a plugin class
        
        Args:
            plugin_class: Plugin class that extends BasePlugin
            config: Optional plugin configuration
        """
        try:
            plugin_instance = plugin_class(config)
            metadata = plugin_instance.get_metadata()
            self.plugins[metadata.name] = plugin_instance
            self.plugin_classes[metadata.name] = plugin_class
            logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")
    
    def discover_plugins(self, plugin_dir: Path = None):
        """
        Discover and register plugins from plugin directory
        
        Args:
            plugin_dir: Directory containing plugin modules (defaults to dashboard/plugins)
        """
        if plugin_dir is None:
            plugin_dir = Path(__file__).parent / "plugins"
        
        logger.info(f"Discovering plugins in {plugin_dir}")
        
        # Import all Python files in plugins directory
        for plugin_file in plugin_dir.glob("*_plugin.py"):
            if plugin_file.name == "base_plugin.py":
                continue
            
            try:
                module_name = f"dashboard.plugins.{plugin_file.stem}"
                module = importlib.import_module(module_name)
                
                # Find all classes that extend BasePlugin
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BasePlugin) and 
                        obj != BasePlugin and 
                        obj.__module__ == module_name):
                        self.register_plugin(obj)
                        break
            except Exception as e:
                logger.error(f"Failed to load plugin from {plugin_file}: {e}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get plugin instance by name
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all registered plugins
        
        Returns:
            Dictionary of plugin_name -> plugin_instance
        """
        return self.plugins.copy()
    
    def get_enabled_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all enabled plugins
        
        Returns:
            Dictionary of enabled plugins
        """
        return {name: plugin for name, plugin in self.plugins.items() if plugin.enabled}
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            True if enabled, False if not found
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            True if disabled, False if not found
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
    
    def create_plugin_instance(self, plugin_name: str, config: Optional[Dict] = None) -> Optional[BasePlugin]:
        """
        Create a new instance of a plugin
        
        Args:
            plugin_name: Plugin name
            config: Optional configuration
            
        Returns:
            New plugin instance or None
        """
        plugin_class = self.plugin_classes.get(plugin_name)
        if plugin_class:
            return plugin_class(config)
        return None
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        Get plugin information
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            Plugin info dictionary or None
        """
        plugin = self.plugins.get(plugin_name)
        if plugin:
            return plugin.get_info()
        return None
    
    def list_plugins(self) -> List[Dict]:
        """
        List all plugins with their information
        
        Returns:
            List of plugin info dictionaries
        """
        return [plugin.get_info() for plugin in self.plugins.values()]


# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        # Auto-discover plugins
        _plugin_manager.discover_plugins()
    return _plugin_manager

