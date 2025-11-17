"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database models
from dashboard.database import Base, get_db, Database, Scan, ScanResult, Vulnerability, Target, Plugin as DBPlugin


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def temp_db() -> Generator[Database, None, None]:
    """
    Create a temporary database for testing.
    Each test gets a fresh database.
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_casino_scanner.db"
    
    # Create database
    db = Database(db_path=str(db_path))
    db.init_db()
    
    yield db
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def db_session(temp_db: Database):
    """
    Create a database session for testing.
    """
    session = temp_db.get_session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def sample_scan_data():
    """Sample scan data for testing"""
    return {
        "scan_id": "test-scan-123",
        "name": "Test Scan",
        "scan_type": "browser",
        "region": "vietnam",
        "status": "pending",
        "plugin_name": "browser_plugin",
        "config": {
            "url": "https://example.com",
            "headless": True
        }
    }


@pytest.fixture(scope="function")
def sample_target_data():
    """Sample target data for testing"""
    return {
        "name": "Test Casino",
        "url": "https://test-casino.com",
        "region": "vietnam",
        "country_code": "VN",
        "tags": ["casino", "gambling"],
        "priority": 5,
        "status": "pending"
    }


@pytest.fixture(scope="function")
def sample_vulnerability_data():
    """Sample vulnerability data for testing"""
    return {
        "title": "Test Vulnerability",
        "description": "This is a test vulnerability",
        "severity": "high",
        "vulnerability_type": "account_creation",
        "url": "https://test-casino.com/signup",
        "exploitability": "easy",
        "profit_potential": "high",
        "technical_details": {
            "method": "test",
            "impact": "test"
        }
    }


@pytest.fixture(scope="function")
def mock_config():
    """Mock configuration for testing"""
    return {
        "apis": {
            "shodan": {
                "api_key": "test_key_12345"
            }
        },
        "browser": {
            "headless": True,
            "timeout": 30000,
            "user_agent": "Mozilla/5.0 (Test Browser)"
        },
        "output": {
            "screenshot_dir": "tests/screenshots"
        },
        "testing": {
            "signup_flow": {
                "test_email_domains": ["test.com"],
                "test_phone_prefixes": ["+84"]
            },
            "bonus_offers": {
                "test_codes": ["TEST123", "BONUS456"]
            }
        }
    }


@pytest.fixture(scope="function")
def temp_results_dir():
    """Create a temporary results directory for testing"""
    temp_dir = tempfile.mkdtemp()
    results_dir = Path(temp_dir) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    yield results_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_targets_dir():
    """Create a temporary targets directory for testing"""
    temp_dir = tempfile.mkdtemp()
    targets_dir = Path(temp_dir) / "targets"
    targets_dir.mkdir(parents=True, exist_ok=True)
    yield targets_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


# FastAPI test client fixture
@pytest.fixture(scope="function")
def test_client(temp_db):
    """Create a test FastAPI client"""
    from fastapi.testclient import TestClient
    from dashboard.api_server import app
    
    # Override database dependency
    def override_get_db():
        try:
            session = temp_db.get_session()
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def websocket_client():
    """Create a WebSocket test client"""
    from fastapi.testclient import TestClient
    from dashboard.api_server import app
    
    client = TestClient(app)
    return client

