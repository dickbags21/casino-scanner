# Casino Scanner - Architecture Documentation

## Overview

The Casino Scanner is a security research framework for discovering and analyzing vulnerabilities in casino/gambling websites. It consists of a modern web dashboard, automated scanning tools, and a plugin-based architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Dashboard (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   REST API   │  │  WebSocket   │  │   Plugins    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Tools Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Browser    │  │    Shodan    │  │   Account    │     │
│  │   Scanner    │  │   Scanner    │  │  Creation    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Mobile     │  │   Target     │  │  Continuous  │     │
│  │   App        │  │  Discovery   │  │   Scanner    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   SQLite     │  │   JSON       │  │   Logs       │     │
│  │  Database    │  │   Results    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Dashboard (`dashboard/`)

**FastAPI Application** (`api_server.py`)
- REST API endpoints for all operations
- WebSocket support for real-time updates
- Plugin integration
- Webhook endpoints for Node-RED automation

**Database** (`database.py`)
- SQLAlchemy ORM models
- SQLite database (casino_scanner.db)
- Stores: Scans, Results, Vulnerabilities, Targets, Plugins

**Plugin System** (`plugin_manager.py`, `plugins/`)
- Base plugin interface
- Auto-discovery mechanism
- Plugin registry and management
- Current plugins: Browser, Shodan, Account Creation, Mobile App

**Frontend** (`static/`, `templates/`)
- Modern web UI with dark mode
- Real-time monitoring via WebSocket
- Terminal interface
- Command palette (Ctrl+U/Ctrl+K)

### Core Tools (`tools/`)

**Browser Scanner** (`browser_scanner.py`)
- Playwright-based automation
- Signup flow testing
- Bonus code validation testing
- Screenshot capture

**Shodan Scanner** (`shodan_scanner.py`)
- Internet-wide device search
- Casino-specific queries
- Result aggregation

**Account Creation Scanner** (`account_creation_scanner.py`)
- Form analysis
- CAPTCHA detection
- Validation testing

**Mobile App Scanner** (`mobile_app_scanner.py`)
- APK analysis
- App store discovery
- Mobile-specific vulnerabilities

**Continuous Scanner** (`continuous_scanner.py`)
- Scheduled scanning
- Job queue management
- Autonomous operation

**Target Discovery** (`intelligent_target_discovery.py`, `auto_region_discovery.py`)
- Region auto-discovery
- Target identification
- Multi-source aggregation

**Vulnerability Classifier** (`vulnerability_classifier.py`)
- ML-based scoring
- Priority ranking
- Impact assessment

**Alert System** (`alert_system.py`)
- Multi-channel notifications
- Configurable rules
- Integration with external services

## Data Flow

1. **User Action** → Dashboard UI or API
2. **API Endpoint** → Validates request
3. **Plugin Manager** → Routes to appropriate plugin
4. **Plugin** → Executes scanner tool
5. **Results** → Saved to database
6. **WebSocket** → Real-time update to UI
7. **Webhook** → Triggers Node-RED automation (if configured)

## Entry Points

### Primary Entry Points

- **`start_dashboard.py`** - Start web dashboard (port 8000)
- **`automated_scanner.py`** - Continuous autonomous scanning

### Legacy Entry Points

- **`main.py`** - Deprecated, use start_dashboard.py
- **`casino_scanner.py`** - Legacy CLI interface

## Configuration

- **`config/config.yaml`** - Main configuration file
  - API keys (Shodan, etc.)
  - Scanning parameters
  - Regional settings

- **`targets/*.yaml`** - Target definitions by region

## Database Schema

- **Scans** - Scan metadata, status, progress
- **ScanResults** - Individual findings per scan
- **Vulnerabilities** - Security issues discovered
- **Targets** - URLs/sites to scan
- **Plugins** - Plugin registry and config

## Plugin Architecture

All scanner tools implement the `BasePlugin` interface:

```python
class BasePlugin:
    - get_metadata() -> PluginMetadata
    - validate_config(config) -> (bool, error)
    - scan(config, progress_callback) -> Dict
    - start_scan() / stop_scan()
```

Plugins are auto-discovered from `dashboard/plugins/` directory.

## API Endpoints

### Core Endpoints
- `GET /api/stats` - Dashboard statistics
- `GET /api/scans` - List scans
- `POST /api/scans` - Create scan
- `GET /api/scans/{id}` - Get scan details
- `GET /api/targets` - List targets
- `POST /api/targets` - Create target
- `GET /api/plugins` - List plugins

### Webhook Endpoints (Node-RED)
- `POST /api/webhooks/vulnerability-found` - Trigger automation
- `POST /api/webhooks/scan-completed` - Post-scan actions
- `POST /api/webhooks/target-discovered` - New target processing

### WebSocket
- `WS /ws` - Real-time updates (subscribe to scan_id)

## Node-RED Integration

Node-RED provides automation workflows:
- Vulnerability alert automation
- Scan orchestration
- Target discovery pipeline
- Continuous monitoring

See `node-red/flows.json` for flow definitions.

## Security Considerations

- No authentication (single-user system)
- No rate limiting on API endpoints
- SQLite file permissions important
- Input validation on API endpoints
- SQL injection protection (SQLAlchemy)

## Performance

- **Database**: SQLite (suitable for <100K scans)
- **Concurrency**: FastAPI async support
- **Real-time**: WebSocket for live updates
- **Scalability**: Can migrate to PostgreSQL if needed

## Future Enhancements

- User authentication
- Scheduled scans
- Email notifications
- PDF report generation
- Multi-user support
- Advanced Node-RED workflows

