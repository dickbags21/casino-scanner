"""
Integration tests for Casino Scanner Dashboard
"""

import pytest
import asyncio
from datetime import datetime
from dashboard.database import Scan, ScanResult, Vulnerability, Target
from dashboard.plugin_manager import get_plugin_manager


@pytest.mark.integration
class TestScanWorkflow:
    """Test complete scan workflow"""
    
    def test_create_and_list_scan(self, test_client, db_session):
        """Test creating a scan and listing it"""
        # List scans (should be empty)
        response = test_client.get("/api/scans")
        initial_count = response.json()["total"]
        
        # Create a scan record directly (since we need a valid plugin)
        scan = Scan(
            scan_id="integration-test-123",
            name="Integration Test Scan",
            scan_type="browser",
            region="vietnam",
            status="pending",
            plugin_name="browser",
            config={"url": "https://example.com"}
        )
        db_session.add(scan)
        db_session.commit()
        
        # List scans again
        response = test_client.get("/api/scans")
        assert response.json()["total"] == initial_count + 1
        
        # Get the scan
        response = test_client.get("/api/scans/integration-test-123")
        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == "integration-test-123"
        assert data["name"] == "Integration Test Scan"
    
    def test_scan_with_results_and_vulnerabilities(self, test_client, db_session):
        """Test scan with results and vulnerabilities"""
        # Create scan
        scan = Scan(
            scan_id="integration-test-456",
            name="Test Scan with Results",
            scan_type="browser",
            status="completed",
            plugin_name="browser",
            config={}
        )
        db_session.add(scan)
        db_session.commit()
        
        # Add results
        result = ScanResult(
            scan_id=scan.id,
            result_type="signup_test",
            target_url="https://example.com",
            success=True,
            data={"test": "data"}
        )
        db_session.add(result)
        
        # Add vulnerability
        vuln = Vulnerability(
            scan_id=scan.id,
            title="Test Vulnerability",
            description="Integration test vulnerability",
            severity="high",
            vulnerability_type="account_creation"
        )
        db_session.add(vuln)
        db_session.commit()
        
        # Get scan details
        response = test_client.get(f"/api/scans/{scan.scan_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) == 1
        assert len(data["vulnerabilities"]) == 1
        assert data["vulnerabilities"][0]["title"] == "Test Vulnerability"
    
    def test_export_scan_with_data(self, test_client, db_session):
        """Test exporting scan with results and vulnerabilities"""
        # Create scan with data
        scan = Scan(
            scan_id="integration-test-789",
            name="Export Test Scan",
            scan_type="browser",
            status="completed",
            plugin_name="browser",
            config={}
        )
        db_session.add(scan)
        db_session.commit()
        
        # Add result
        result = ScanResult(
            scan_id=scan.id,
            result_type="test",
            target_url="https://example.com",
            success=True,
            data={"export": "test"}
        )
        db_session.add(result)
        db_session.commit()
        
        # Export scan
        response = test_client.get(f"/api/scans/{scan.scan_id}/export?format=json")
        assert response.status_code == 200
        data = response.json()
        
        assert data["scan_id"] == scan.scan_id
        assert len(data["results"]) == 1
        assert data["results"][0]["export"] == "test"


@pytest.mark.integration
class TestTargetWorkflow:
    """Test complete target workflow"""
    
    def test_create_update_delete_target(self, test_client, db_session):
        """Test creating, updating, and deleting a target"""
        # Create target
        target_data = {
            "name": "Integration Test Casino",
            "url": "https://integration-test.com",
            "region": "vietnam",
            "country_code": "VN",
            "tags": ["test", "integration"],
            "priority": 8,
            "status": "pending"
        }
        
        response = test_client.post("/api/targets", json=target_data)
        assert response.status_code == 200
        created_target = response.json()
        target_id = created_target["id"]
        
        # Update target
        update_data = {"priority": 10, "status": "active"}
        response = test_client.put(f"/api/targets/{target_id}", json=update_data)
        assert response.status_code == 200
        updated_target = response.json()
        assert updated_target["priority"] == 10
        assert updated_target["status"] == "active"
        
        # Delete target
        response = test_client.delete(f"/api/targets/{target_id}")
        assert response.status_code == 200
        
        # Verify deletion
        response = test_client.get(f"/api/targets/{target_id}")
        assert response.status_code == 404


@pytest.mark.integration
class TestPluginIntegration:
    """Test plugin system integration"""
    
    def test_plugin_manager_list_plugins(self):
        """Test plugin manager lists available plugins"""
        manager = get_plugin_manager()
        plugins = manager.list_plugins()
        
        assert len(plugins) > 0
        plugin_names = [p["name"] for p in plugins]
        
        # Should have at least browser plugin
        assert "browser" in plugin_names
    
    def test_plugin_get_info(self):
        """Test getting plugin info"""
        manager = get_plugin_manager()
        browser_plugin = manager.get_plugin("browser")
        
        if browser_plugin:
            info = browser_plugin.get_info()
            assert info["name"] == "browser"
            assert "display_name" in info
            assert "enabled" in info


@pytest.mark.integration
class TestStatsIntegration:
    """Test stats endpoint integration"""
    
    def test_stats_with_data(self, test_client, db_session, sample_scan_data, sample_target_data):
        """Test stats endpoint with actual data"""
        # Create scan
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        
        # Create target
        target = Target(**sample_target_data)
        db_session.add(target)
        
        # Create vulnerability
        vuln = Vulnerability(
            scan_id=scan.id,
            title="Test Vuln",
            description="Test",
            severity="high",
            vulnerability_type="test"
        )
        db_session.add(vuln)
        db_session.commit()
        
        # Get stats
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["total_scans"] >= 1
        assert stats["total_targets"] >= 1
        assert stats["total_vulnerabilities"] >= 1


@pytest.mark.integration
class TestWebhookIntegration:
    """Test webhook integration"""
    
    def test_webhook_chain(self, test_client):
        """Test webhook endpoints can receive data"""
        # Test vulnerability found webhook
        vuln_data = {
            "scan_id": "test-scan",
            "vulnerability": {
                "id": 1,
                "title": "Integration Test Vuln",
                "severity": "critical",
                "url": "https://example.com"
            }
        }
        response = test_client.post("/api/webhooks/vulnerability-found", json=vuln_data)
        assert response.status_code == 200
        
        # Test scan completed webhook
        scan_data = {
            "scan_id": "test-scan",
            "status": "completed",
            "results": {
                "total_results": 5,
                "total_vulnerabilities": 2
            }
        }
        response = test_client.post("/api/webhooks/scan-completed", json=scan_data)
        assert response.status_code == 200
        
        # Test target discovered webhook
        target_data = {
            "target": {
                "url": "https://new-casino.com",
                "region": "vietnam",
                "name": "New Casino"
            }
        }
        response = test_client.post("/api/webhooks/target-discovered", json=target_data)
        assert response.status_code == 200

