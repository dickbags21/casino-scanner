# Test Suite for Casino Scanner Dashboard

This directory contains the comprehensive test suite for the Casino Scanner Dashboard project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_database.py         # Database model tests
├── test_api.py              # API endpoint tests
├── test_plugins.py          # Plugin system tests
├── test_tools.py            # Tools and scanner tests
├── test_integration.py      # Integration tests
└── README.md                # This file
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_database.py
```

### Run Tests by Marker
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Database tests only
pytest -m database

# Plugin tests only
pytest -m plugin
```

### Run with Coverage
```bash
pytest --cov=dashboard --cov=tools --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test
```bash
pytest tests/test_database.py::TestDatabaseModels::test_create_scan
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Fast unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require services)
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.plugin` - Plugin tests
- `@pytest.mark.browser` - Browser automation tests (requires Playwright)
- `@pytest.mark.shodan` - Shodan API tests (requires API key)
- `@pytest.mark.slow` - Slow tests (> 1 second)
- `@pytest.mark.websocket` - WebSocket tests

## Test Categories

### Unit Tests
- **test_database.py**: Database models, relationships, queries
- **test_api.py**: API endpoints, request/response handling
- **test_plugins.py**: Plugin system, base plugin, plugin manager
- **test_tools.py**: Tools and scanners (target manager, classifiers, etc.)

### Integration Tests
- **test_integration.py**: End-to-end workflows, component interactions

## Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_db` - Temporary database for testing
- `db_session` - Database session
- `sample_scan_data` - Sample scan data
- `sample_target_data` - Sample target data
- `sample_vulnerability_data` - Sample vulnerability data
- `mock_config` - Mock configuration
- `test_client` - FastAPI test client
- `temp_results_dir` - Temporary results directory
- `temp_targets_dir` - Temporary targets directory

## Writing New Tests

### Example Unit Test
```python
@pytest.mark.unit
@pytest.mark.database
class TestMyFeature:
    def test_my_function(self, db_session):
        # Test code here
        assert True
```

### Example Integration Test
```python
@pytest.mark.integration
class TestMyWorkflow:
    def test_complete_workflow(self, test_client):
        # Test workflow here
        response = test_client.get("/api/endpoint")
        assert response.status_code == 200
```

## Coverage Goals

- **Target Coverage**: 60% minimum (configured in pytest.ini)
- **Critical Paths**: 80%+ coverage
- **API Endpoints**: 100% coverage
- **Database Models**: 90%+ coverage

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

- Fast unit tests run on every commit
- Integration tests run on pull requests
- Full test suite runs on main branch

## Notes

- Browser tests require Playwright to be installed
- Shodan tests require a valid API key (use environment variable)
- Some tests use mocks to avoid external dependencies
- Database tests use temporary databases (cleaned up automatically)

