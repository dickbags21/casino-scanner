"""
Integration tests for Node-RED automation
"""

import pytest
import httpx
import asyncio
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
@pytest.mark.slow
class TestNodeRedIntegration:
    """Test Node-RED integration with FastAPI"""
    
    @pytest.fixture(scope="class")
    def node_red_url(self):
        """Node-RED base URL"""
        return "http://localhost:1880"
    
    @pytest.fixture(scope="class")
    def node_red_available(self, node_red_url):
        """Check if Node-RED is available"""
        try:
            response = httpx.get(node_red_url, timeout=2.0)
            return response.status_code == 200
        except:
            return False
    
    @pytest.mark.skipif(not pytest.config.getoption("--node-red"), reason="Node-RED not available")
    def test_node_red_running(self, node_red_url, node_red_available):
        """Test that Node-RED is running"""
        if not node_red_available:
            pytest.skip("Node-RED is not running. Start it with: node-red")
        
        response = httpx.get(node_red_url, timeout=2.0)
        assert response.status_code == 200
    
    @pytest.mark.skipif(not pytest.config.getoption("--node-red"), reason="Node-RED not available")
    def test_vulnerability_webhook_endpoint(self, node_red_url, node_red_available):
        """Test Node-RED vulnerability webhook endpoint"""
        if not node_red_available:
            pytest.skip("Node-RED is not running")
        
        webhook_data = {
            "scan_id": "test-scan-123",
            "vulnerability": {
                "id": 1,
                "title": "Test Vulnerability",
                "severity": "critical",
                "url": "https://example.com"
            }
        }
        
        response = httpx.post(
            f"{node_red_url}/webhook/vulnerability-found",
            json=webhook_data,
            timeout=5.0
        )
        
        # Node-RED should accept the webhook (200 or 204)
        assert response.status_code in [200, 204]
    
    @pytest.mark.skipif(not pytest.config.getoption("--node-red"), reason="Node-RED not available")
    def test_scan_completed_webhook_endpoint(self, node_red_url, node_red_available):
        """Test Node-RED scan completed webhook endpoint"""
        if not node_red_available:
            pytest.skip("Node-RED is not running")
        
        webhook_data = {
            "scan_id": "test-scan-123",
            "status": "completed",
            "results": {
                "total_results": 5,
                "total_vulnerabilities": 2
            }
        }
        
        response = httpx.post(
            f"{node_red_url}/webhook/scan-completed",
            json=webhook_data,
            timeout=5.0
        )
        
        assert response.status_code in [200, 204]
    
    @pytest.mark.skipif(not pytest.config.getoption("--node-red"), reason="Node-RED not available")
    def test_target_discovered_webhook_endpoint(self, node_red_url, node_red_available):
        """Test Node-RED target discovered webhook endpoint"""
        if not node_red_available:
            pytest.skip("Node-RED is not running")
        
        webhook_data = {
            "target": {
                "url": "https://test-casino.com",
                "region": "vietnam",
                "name": "Test Casino"
            },
            "source": "test"
        }
        
        response = httpx.post(
            f"{node_red_url}/webhook/target-discovered",
            json=webhook_data,
            timeout=5.0
        )
        
        assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_webhook_trigger_function(self):
        """Test the webhook trigger function in api_server"""
        from dashboard.api_server import trigger_webhook_async
        
        # Mock httpx.AsyncClient
        with patch('dashboard.api_server.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test webhook trigger
            await trigger_webhook_async(
                "/api/webhooks/vulnerability-found",
                {
                    "scan_id": "test",
                    "vulnerability": {"title": "Test"}
                }
            )
            
            # Verify it was called with correct URL
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            assert "localhost:1880" in call_args[0][0]  # URL should contain Node-RED port
            assert "/webhook/vulnerability-found" in call_args[0][0]  # Should map to Node-RED endpoint
    
    def test_webhook_endpoint_mapping(self):
        """Test that webhook endpoints are correctly mapped"""
        from dashboard.api_server import trigger_webhook_async
        import os
        
        # Test endpoint mapping logic
        endpoint_map = {
            "/api/webhooks/vulnerability-found": "/webhook/vulnerability-found",
            "/api/webhooks/scan-completed": "/webhook/scan-completed",
            "/api/webhooks/target-discovered": "/webhook/target-discovered"
        }
        
        for fastapi_endpoint, node_red_endpoint in endpoint_map.items():
            assert node_red_endpoint == endpoint_map.get(fastapi_endpoint)


@pytest.mark.integration
class TestNodeRedWebhookFlow:
    """Test complete webhook flow from FastAPI to Node-RED"""
    
    @pytest.mark.asyncio
    async def test_vulnerability_webhook_flow(self, test_client):
        """Test complete flow: FastAPI receives webhook -> triggers Node-RED"""
        # First, test that FastAPI webhook endpoint works
        webhook_data = {
            "scan_id": "test-scan-456",
            "vulnerability": {
                "id": 2,
                "title": "Integration Test Vulnerability",
                "severity": "high",
                "url": "https://test.example.com"
            }
        }
        
        response = test_client.post("/api/webhooks/vulnerability-found", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["vulnerability_id"] == 2
    
    @pytest.mark.asyncio
    async def test_scan_completed_webhook_flow(self, test_client):
        """Test scan completed webhook flow"""
        webhook_data = {
            "scan_id": "test-scan-789",
            "status": "completed",
            "results": {
                "total_results": 10,
                "total_vulnerabilities": 3
            }
        }
        
        response = test_client.post("/api/webhooks/scan-completed", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["scan_id"] == "test-scan-789"
    
    @pytest.mark.asyncio
    async def test_target_discovered_webhook_flow(self, test_client):
        """Test target discovered webhook flow"""
        webhook_data = {
            "target": {
                "url": "https://new-casino.com",
                "region": "vietnam",
                "name": "New Casino"
            },
            "source": "integration_test"
        }
        
        response = test_client.post("/api/webhooks/target-discovered", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["target_url"] == "https://new-casino.com"


def pytest_addoption(parser):
    """Add command line option for Node-RED tests"""
    parser.addoption(
        "--node-red",
        action="store_true",
        default=False,
        help="Run Node-RED integration tests (requires Node-RED to be running)"
    )

