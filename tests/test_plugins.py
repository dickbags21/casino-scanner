"""
Unit tests for plugin system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata, ScanProgress
from dashboard.plugin_manager import get_plugin_manager


@pytest.mark.unit
@pytest.mark.plugin
class TestBasePlugin:
    """Test base plugin functionality"""
    
    def test_plugin_metadata(self):
        """Test plugin metadata structure"""
        metadata = PluginMetadata(
            name="test_plugin",
            display_name="Test Plugin",
            description="A test plugin",
            version="1.0.0"
        )
        
        assert metadata.name == "test_plugin"
        assert metadata.display_name == "Test Plugin"
        assert metadata.description == "A test plugin"
        assert metadata.version == "1.0.0"
        assert metadata.plugin_type == "scanner"  # Default value
    
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                return {"results": []}
        
        plugin = TestPlugin()
        assert plugin.config == {}
        assert plugin.enabled is True
        assert plugin.metadata.name == "test"
    
    def test_plugin_validate_config_default(self):
        """Test default config validation"""
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                return {"results": []}
        
        plugin = TestPlugin()
        is_valid, error = plugin.validate_config({})
        assert is_valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_start_scan(self):
        """Test starting a scan"""
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                return {"results": []}
        
        plugin = TestPlugin()
        scan_id = await plugin.start_scan({"test": "config"})
        
        assert scan_id is not None
        assert scan_id in plugin.get_running_scans()
    
    @pytest.mark.asyncio
    async def test_stop_scan(self):
        """Test stopping a scan"""
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                await asyncio.sleep(10)  # Long-running scan
                return {"results": []}
        
        plugin = TestPlugin()
        scan_id = await plugin.start_scan({"test": "config"})
        
        # Stop the scan
        stopped = await plugin.stop_scan(scan_id)
        assert stopped is True
        assert scan_id not in plugin.get_running_scans()
    
    @pytest.mark.asyncio
    async def test_stop_nonexistent_scan(self):
        """Test stopping a non-existent scan"""
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                return {"results": []}
        
        plugin = TestPlugin()
        stopped = await plugin.stop_scan("non-existent-id")
        assert stopped is False
    
    @pytest.mark.asyncio
    async def test_scan_with_progress_callback(self):
        """Test scan with progress callback"""
        progress_updates = []
        
        async def progress_callback(progress: ScanProgress):
            progress_updates.append(progress)
        
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                if progress_callback:
                    await progress_callback(ScanProgress(
                        scan_id="test",
                        progress=0.5,
                        status="running",
                        message="Halfway done"
                    ))
                return {"results": []}
        
        plugin = TestPlugin()
        await plugin.scan({"test": "config"}, progress_callback)
        
        assert len(progress_updates) == 1
        assert progress_updates[0].progress == 0.5
        assert progress_updates[0].status == "running"
    
    def test_get_info(self):
        """Test getting plugin info"""
        class TestPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test",
                    display_name="Test Plugin",
                    description="Test",
                    version="1.0.0"
                )
            
            async def scan(self, scan_config, progress_callback=None):
                return {"results": []}
        
        plugin = TestPlugin()
        info = plugin.get_info()
        
        assert info["name"] == "test"
        assert info["display_name"] == "Test Plugin"
        assert info["enabled"] is True
        assert "running_scans" in info


@pytest.mark.unit
@pytest.mark.plugin
class TestPluginManager:
    """Test plugin manager functionality"""
    
    def test_get_plugin_manager(self):
        """Test getting plugin manager instance"""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()
        
        # Should return the same instance (singleton)
        assert manager1 is manager2
    
    def test_list_plugins(self):
        """Test listing available plugins"""
        manager = get_plugin_manager()
        plugins = manager.list_plugins()
        
        assert isinstance(plugins, list)
        # Should have at least browser, shodan, account_creation, mobile_app plugins
        plugin_names = [p["name"] for p in plugins]
        assert "browser" in plugin_names or len(plugins) > 0
    
    def test_get_plugin(self):
        """Test getting a specific plugin"""
        manager = get_plugin_manager()
        plugins = manager.list_plugins()
        
        if plugins:
            plugin_name = plugins[0]["name"]
            plugin = manager.get_plugin(plugin_name)
            assert plugin is not None
            assert plugin.metadata.name == plugin_name
    
    def test_get_nonexistent_plugin(self):
        """Test getting a non-existent plugin"""
        manager = get_plugin_manager()
        plugin = manager.get_plugin("non_existent_plugin")
        assert plugin is None


@pytest.mark.unit
@pytest.mark.plugin
class TestBrowserPlugin:
    """Test browser plugin specifically"""
    
    def test_browser_plugin_metadata(self):
        """Test browser plugin metadata"""
        from dashboard.plugins.browser_plugin import BrowserPlugin
        
        plugin = BrowserPlugin()
        metadata = plugin.get_metadata()
        
        assert metadata.name == "browser"
        assert metadata.display_name == "Browser Scanner"
        assert metadata.plugin_type == "scanner"
    
    def test_browser_plugin_validate_config(self):
        """Test browser plugin config validation"""
        from dashboard.plugins.browser_plugin import BrowserPlugin
        
        plugin = BrowserPlugin()
        
        # Valid config
        is_valid, error = plugin.validate_config({"url": "https://example.com"})
        assert is_valid is True
        assert error is None
        
        # Invalid config (missing URL)
        is_valid, error = plugin.validate_config({})
        assert is_valid is False
        assert error == "URL must be specified"
    
    @pytest.mark.asyncio
    @pytest.mark.browser  # Mark as browser test (may require Playwright)
    async def test_browser_plugin_scan_mock(self):
        """Test browser plugin scan with mocked browser scanner"""
        from dashboard.plugins.browser_plugin import BrowserPlugin
        
        plugin = BrowserPlugin()
        
        # Mock the browser scanner
        with patch('dashboard.plugins.browser_plugin.BrowserScanner') as MockScanner:
            mock_scanner_instance = AsyncMock()
            MockScanner.return_value = mock_scanner_instance
            
            # Mock scan result
            mock_scanner_instance.test_signup_flow = AsyncMock(return_value=Mock(
                url="https://example.com",
                success=True,
                issues=[],
                fields_found=[],
                validation_errors=[],
                screenshot_path=None,
                timestamp="2024-01-01T00:00:00"
            ))
            
            scan_config = {
                "url": "https://example.com",
                "scan_type": "signup",
                "test_data": {"email": "test@example.com"}
            }
            
            result = await plugin.scan(scan_config)
            
            assert "results" in result
            assert len(result["results"]) > 0
            assert result["results"][0]["url"] == "https://example.com"


@pytest.mark.unit
@pytest.mark.plugin
class TestShodanPlugin:
    """Test Shodan plugin"""
    
    def test_shodan_plugin_metadata(self):
        """Test Shodan plugin metadata"""
        from dashboard.plugins.shodan_plugin import ShodanPlugin
        
        plugin = ShodanPlugin()
        metadata = plugin.get_metadata()
        
        assert metadata.name == "shodan"
        assert "Shodan" in metadata.display_name
        assert metadata.plugin_type == "scanner"


@pytest.mark.unit
@pytest.mark.plugin
class TestAccountCreationPlugin:
    """Test account creation plugin"""
    
    def test_account_creation_plugin_metadata(self):
        """Test account creation plugin metadata"""
        from dashboard.plugins.account_creation_plugin import AccountCreationPlugin
        
        plugin = AccountCreationPlugin()
        metadata = plugin.get_metadata()
        
        assert metadata.name == "account_creation"
        assert "Account" in metadata.display_name
        assert metadata.plugin_type == "scanner"

