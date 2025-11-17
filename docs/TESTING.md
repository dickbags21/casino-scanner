# Testing Guide - Casino Scanner Dashboard

## Overview

The Casino Scanner Dashboard has a comprehensive test suite using **pytest** (modern Python testing framework). The test suite includes unit tests, integration tests, and covers all major components of the system.

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

Or use the test runner script:

```bash
./run_tests.sh
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_database.py         # Database model tests (15+ tests)
├── test_api.py              # API endpoint tests (30+ tests)
├── test_plugins.py          # Plugin system tests (15+ tests)
├── test_tools.py            # Tools and scanner tests (15+ tests)
├── test_integration.py      # Integration tests (10+ tests)
└── README.md                # Test documentation
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# API endpoint tests
pytest -m api

# Database tests
pytest -m database

# Plugin tests
pytest -m plugin
```

### Run Specific Test File

```bash
pytest tests/test_database.py
pytest tests/test_api.py
```

### Run Specific Test

```bash
pytest tests/test_database.py::TestDatabaseModels::test_create_scan
```

### Run with Coverage

```bash
pytest --cov=dashboard --cov=tools --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run Fast Tests Only

```bash
pytest -m "unit and not slow"
```

### Verbose Output

```bash
pytest -v
pytest -vv  # Even more verbose
```

## Test Runner Script

The `run_tests.sh` script provides convenient shortcuts:

```bash
./run_tests.sh unit          # Run unit tests
./run_tests.sh integration   # Run integration tests
./run_tests.sh api           # Run API tests
./run_tests.sh coverage      # Run with coverage report
./run_tests.sh fast          # Run fast tests only
./run_tests.sh all           # Run all tests (default)
```

## Test Markers

Tests are organized using pytest markers:

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Fast unit tests (no external dependencies) |
| `@pytest.mark.integration` | Integration tests (may require services) |
| `@pytest.mark.api` | API endpoint tests |
| `@pytest.mark.database` | Database tests |
| `@pytest.mark.plugin` | Plugin system tests |
| `@pytest.mark.browser` | Browser automation tests (requires Playwright) |
| `@pytest.mark.shodan` | Shodan API tests (requires API key) |
| `@pytest.mark.slow` | Slow tests (> 1 second) |
| `@pytest.mark.websocket` | WebSocket tests |

## Test Coverage

### Current Coverage Goals

- **Minimum**: 60% overall coverage
- **API Endpoints**: 100% coverage
- **Database Models**: 90%+ coverage
- **Critical Paths**: 80%+ coverage

### View Coverage Report

```bash
pytest --cov=dashboard --cov=tools --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Writing New Tests

### Unit Test Example

```python
@pytest.mark.unit
@pytest.mark.database
class TestMyFeature:
    def test_my_function(self, db_session):
        # Arrange
        scan = Scan(scan_id="test", name="Test", scan_type="browser", status="pending", plugin_name="browser")
        db_session.add(scan)
        db_session.commit()
        
        # Act
        result = db_session.query(Scan).filter_by(scan_id="test").first()
        
        # Assert
        assert result is not None
        assert result.name == "Test"
```

### Integration Test Example

```python
@pytest.mark.integration
class TestMyWorkflow:
    def test_complete_workflow(self, test_client):
        # Create resource
        response = test_client.post("/api/targets", json={
            "name": "Test",
            "url": "https://example.com",
            "region": "vietnam"
        })
        assert response.status_code == 200
        
        # Get resource
        target_id = response.json()["id"]
        response = test_client.get(f"/api/targets/{target_id}")
        assert response.status_code == 200
```

## Available Fixtures

Common fixtures are defined in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `temp_db` | Temporary database instance |
| `db_session` | Database session |
| `sample_scan_data` | Sample scan data dictionary |
| `sample_target_data` | Sample target data dictionary |
| `sample_vulnerability_data` | Sample vulnerability data dictionary |
| `mock_config` | Mock configuration dictionary |
| `test_client` | FastAPI test client |
| `temp_results_dir` | Temporary results directory |
| `temp_targets_dir` | Temporary targets directory |

## Test Configuration

Test configuration is in `pytest.ini`:

- **Test discovery**: `test_*.py`, `*_test.py`
- **Asyncio mode**: `auto`
- **Coverage**: Dashboard and tools modules
- **Timeout**: 300 seconds per test
- **Logging**: Enabled with INFO level

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

1. **Fast unit tests** run on every commit
2. **Integration tests** run on pull requests
3. **Full test suite** runs on main branch

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
```

## Troubleshooting

### Tests Failing

1. **Check dependencies**: `pip install -r requirements.txt`
2. **Check database**: Tests use temporary databases, but ensure SQLite is available
3. **Check imports**: Ensure all modules are importable
4. **Run with verbose**: `pytest -vv` to see detailed output

### Slow Tests

- Use `pytest -m "unit and not slow"` for fast tests only
- Browser tests are marked as `@pytest.mark.browser` and may be slow
- Shodan tests require API keys and are skipped if not configured

### Coverage Issues

- Ensure all test files are in the `tests/` directory
- Check that modules are properly imported
- Use `--cov-report=term-missing` to see which lines are missing coverage

## Best Practices

1. **Write tests first** (TDD) when possible
2. **Use descriptive test names** that explain what is being tested
3. **Keep tests isolated** - each test should be independent
4. **Use fixtures** for common setup/teardown
5. **Mock external dependencies** when possible
6. **Test edge cases** and error conditions
7. **Keep tests fast** - mark slow tests appropriately
8. **Maintain high coverage** for critical paths

## Next Steps

- Add more integration tests for complex workflows
- Add performance/load tests
- Add end-to-end browser tests
- Set up CI/CD pipeline
- Add mutation testing

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

