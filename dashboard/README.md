"""
Dashboard README
"""

# Casino Scanner Dashboard

A centralized web dashboard and REST API framework for the Casino Scanner security research toolkit.

## Features

- **Web Dashboard**: Modern browser-based UI with real-time monitoring
- **REST API**: Full REST API for automation and integration
- **Plugin Architecture**: All scanner tools work as plugins
- **Real-time Updates**: WebSocket support for live scan progress
- **Data Visualization**: Charts and statistics for scan results
- **SQLite Database**: Lightweight database for scan history

## Quick Start

### Start Dashboard

```bash
python3 start_dashboard.py
```

Or with Docker:

```bash
docker-compose up dashboard
```

Then open http://localhost:8000 in your browser.

### Import Existing Results

The dashboard will automatically import existing JSON results from the `results/` directory on first start.

To manually import:

```python
from dashboard.integration import import_all_results
import_all_results()
```

## API Endpoints

- `GET /api/stats` - Dashboard statistics
- `GET /api/scans` - List scans
- `POST /api/scans` - Create new scan
- `GET /api/scans/{scan_id}` - Get scan details
- `DELETE /api/scans/{scan_id}` - Cancel scan
- `GET /api/plugins` - List plugins
- `GET /api/vulnerabilities` - List vulnerabilities
- `GET /api/targets` - List targets
- `WebSocket /ws` - Real-time updates

## Plugins

All scanner tools are available as plugins:

- **shodan** - Shodan reconnaissance scanner
- **browser** - Browser automation scanner
- **account_creation** - Account creation vulnerability scanner
- **mobile_app** - Mobile app scanner

## Architecture

- `dashboard/api_server.py` - FastAPI application
- `dashboard/database.py` - SQLite database models
- `dashboard/plugin_manager.py` - Plugin registry and management
- `dashboard/plugins/` - Plugin implementations
- `dashboard/integration.py` - Import existing results
- `dashboard/static/` - Static files (CSS, JS)
- `dashboard/templates/` - HTML templates


