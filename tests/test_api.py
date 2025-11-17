"""
Unit tests for FastAPI endpoints
"""

import pytest
import json
from datetime import datetime
from dashboard.database import Scan, ScanResult, Vulnerability, Target


@pytest.mark.unit
@pytest.mark.api
class TestHealthEndpoints:
    """Test health and stats endpoints"""
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_stats_endpoint(self, test_client, db_session, sample_scan_data):
        """Test stats endpoint"""
        # Create some test data
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_scans" in data
        assert "total_vulnerabilities" in data
        assert "total_targets" in data
        assert isinstance(data["total_scans"], int)


@pytest.mark.unit
@pytest.mark.api
class TestScanEndpoints:
    """Test scan-related endpoints"""
    
    def test_list_scans_empty(self, test_client):
        """Test listing scans when none exist"""
        response = test_client.get("/api/scans")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["scans"]) == 0
    
    def test_list_scans_with_data(self, test_client, db_session, sample_scan_data):
        """Test listing scans with data"""
        # Create test scans
        for i in range(3):
            scan_data = sample_scan_data.copy()
            scan_data["scan_id"] = f"test-scan-{i}"
            scan = Scan(**scan_data)
            db_session.add(scan)
        db_session.commit()
        
        response = test_client.get("/api/scans")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["scans"]) == 3
    
    def test_list_scans_with_status_filter(self, test_client, db_session, sample_scan_data):
        """Test listing scans filtered by status"""
        # Create scans with different statuses
        for status in ["pending", "running", "completed"]:
            scan_data = sample_scan_data.copy()
            scan_data["scan_id"] = f"test-scan-{status}"
            scan_data["status"] = status
            scan = Scan(**scan_data)
            db_session.add(scan)
        db_session.commit()
        
        response = test_client.get("/api/scans?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert all(scan["status"] == "completed" for scan in data["scans"])
    
    def test_get_scan_not_found(self, test_client):
        """Test getting a non-existent scan"""
        response = test_client.get("/api/scans/non-existent-id")
        assert response.status_code == 404
    
    def test_get_scan_success(self, test_client, db_session, sample_scan_data):
        """Test getting an existing scan"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        response = test_client.get(f"/api/scans/{sample_scan_data['scan_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == sample_scan_data["scan_id"]
        assert data["name"] == sample_scan_data["name"]
    
    def test_create_scan_missing_plugin(self, test_client):
        """Test creating scan without plugin"""
        response = test_client.post("/api/scans", json={})
        assert response.status_code == 400
        assert "Plugin name is required" in response.json()["detail"]
    
    def test_create_scan_invalid_plugin(self, test_client):
        """Test creating scan with invalid plugin"""
        response = test_client.post("/api/scans", json={
            "plugin": "non_existent_plugin",
            "name": "Test Scan"
        })
        assert response.status_code == 404
    
    def test_delete_scan(self, test_client, db_session, sample_scan_data):
        """Test deleting a scan"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        response = test_client.delete(f"/api/scans/{sample_scan_data['scan_id']}")
        assert response.status_code == 200
        
        # Verify scan is deleted
        response = test_client.get(f"/api/scans/{sample_scan_data['scan_id']}")
        assert response.status_code == 404
    
    def test_export_scan_json(self, test_client, db_session, sample_scan_data):
        """Test exporting scan as JSON"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        # Add a result
        result = ScanResult(
            scan_id=scan.id,
            result_type="test",
            target_url="https://example.com",
            success=True,
            data={"test": "data"}
        )
        db_session.add(result)
        db_session.commit()
        
        response = test_client.get(f"/api/scans/{sample_scan_data['scan_id']}/export?format=json")
        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == sample_scan_data["scan_id"]
        assert "results" in data
        assert "vulnerabilities" in data


@pytest.mark.unit
@pytest.mark.api
class TestPluginEndpoints:
    """Test plugin-related endpoints"""
    
    def test_list_plugins(self, test_client):
        """Test listing plugins"""
        response = test_client.get("/api/plugins")
        assert response.status_code == 200
        data = response.json()
        assert "plugins" in data
        assert isinstance(data["plugins"], list)
    
    def test_get_plugin_not_found(self, test_client):
        """Test getting a non-existent plugin"""
        response = test_client.get("/api/plugins/non_existent")
        assert response.status_code == 404
    
    def test_get_plugin_success(self, test_client):
        """Test getting an existing plugin"""
        # First list plugins to get a valid name
        response = test_client.get("/api/plugins")
        plugins = response.json()["plugins"]
        
        if plugins:
            plugin_name = plugins[0]["name"]
            response = test_client.get(f"/api/plugins/{plugin_name}")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == plugin_name


@pytest.mark.unit
@pytest.mark.api
class TestTargetEndpoints:
    """Test target-related endpoints"""
    
    def test_list_targets_empty(self, test_client):
        """Test listing targets when none exist"""
        response = test_client.get("/api/targets")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["targets"]) == 0
    
    def test_create_target(self, test_client, sample_target_data):
        """Test creating a target"""
        response = test_client.post("/api/targets", json=sample_target_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_target_data["name"]
        assert data["url"] == sample_target_data["url"]
        assert "id" in data
    
    def test_get_target(self, test_client, db_session, sample_target_data):
        """Test getting a target"""
        target = Target(**sample_target_data)
        db_session.add(target)
        db_session.commit()
        
        response = test_client.get(f"/api/targets/{target.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == target.id
        assert data["name"] == sample_target_data["name"]
    
    def test_update_target(self, test_client, db_session, sample_target_data):
        """Test updating a target"""
        target = Target(**sample_target_data)
        db_session.add(target)
        db_session.commit()
        
        update_data = {"priority": 10, "status": "active"}
        response = test_client.put(f"/api/targets/{target.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == 10
        assert data["status"] == "active"
    
    def test_delete_target(self, test_client, db_session, sample_target_data):
        """Test deleting a target"""
        target = Target(**sample_target_data)
        db_session.add(target)
        db_session.commit()
        
        response = test_client.delete(f"/api/targets/{target.id}")
        assert response.status_code == 200
        
        # Verify target is deleted
        response = test_client.get(f"/api/targets/{target.id}")
        assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.api
class TestVulnerabilityEndpoints:
    """Test vulnerability-related endpoints"""
    
    def test_list_vulnerabilities_empty(self, test_client):
        """Test listing vulnerabilities when none exist"""
        response = test_client.get("/api/vulnerabilities")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["vulnerabilities"]) == 0
    
    def test_list_vulnerabilities_with_data(self, test_client, db_session, sample_scan_data, sample_vulnerability_data):
        """Test listing vulnerabilities with data"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        vuln = Vulnerability(scan_id=scan.id, **sample_vulnerability_data)
        db_session.add(vuln)
        db_session.commit()
        
        response = test_client.get("/api/vulnerabilities")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["vulnerabilities"]) >= 1
    
    def test_list_vulnerabilities_filtered_by_severity(self, test_client, db_session, sample_scan_data):
        """Test listing vulnerabilities filtered by severity"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        # Create vulnerabilities with different severities
        for severity in ["critical", "high", "medium"]:
            vuln = Vulnerability(
                scan_id=scan.id,
                title=f"{severity} vulnerability",
                description="Test",
                severity=severity,
                vulnerability_type="test"
            )
            db_session.add(vuln)
        db_session.commit()
        
        response = test_client.get("/api/vulnerabilities?severity=high")
        assert response.status_code == 200
        data = response.json()
        assert all(v["severity"] == "high" for v in data["vulnerabilities"])


@pytest.mark.unit
@pytest.mark.api
class TestWebhookEndpoints:
    """Test webhook endpoints"""
    
    def test_vulnerability_found_webhook(self, test_client):
        """Test vulnerability found webhook"""
        webhook_data = {
            "scan_id": "test-scan-123",
            "vulnerability": {
                "id": 1,
                "title": "Test Vulnerability",
                "severity": "high",
                "url": "https://example.com"
            }
        }
        response = test_client.post("/api/webhooks/vulnerability-found", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
    
    def test_scan_completed_webhook(self, test_client):
        """Test scan completed webhook"""
        webhook_data = {
            "scan_id": "test-scan-123",
            "status": "completed",
            "results": {
                "total_results": 5,
                "total_vulnerabilities": 2
            }
        }
        response = test_client.post("/api/webhooks/scan-completed", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
    
    def test_target_discovered_webhook(self, test_client):
        """Test target discovered webhook"""
        webhook_data = {
            "target": {
                "url": "https://example.com",
                "region": "vietnam",
                "name": "Test Target"
            }
        }
        response = test_client.post("/api/webhooks/target-discovered", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"


@pytest.mark.unit
@pytest.mark.api
class TestNodeRedEndpoints:
    """Test Node-RED related endpoints"""
    
    def test_get_node_red_flows(self, test_client):
        """Test getting Node-RED flows"""
        response = test_client.get("/api/node-red/flows")
        assert response.status_code == 200
        data = response.json()
        assert "flows" in data
        assert isinstance(data["flows"], list)

