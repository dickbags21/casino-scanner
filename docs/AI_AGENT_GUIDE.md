# AI Agent Guide - Casino Scanner Dashboard

## Quick Start for AI Agents

This guide helps AI agents quickly understand the project structure, current state, and how to work with it effectively.

## Project Overview

**Casino Scanner Dashboard** is a security research framework with:
- **Web Dashboard**: FastAPI-based UI for managing security scans
- **Plugin System**: Modular architecture for scanner tools
- **Real-time Monitoring**: WebSocket-based live updates
- **Database**: SQLite for scan history and results
- **REST API**: Full API for automation

## Current State (Last Updated: 2025-11-16)

### ✅ Completed Features
- Full FastAPI backend with 22+ API endpoints
- Plugin system with 4 plugins (Shodan, Browser, Account Creation, Mobile App)
- Web dashboard with dark mode
- SQLite database with all models
- WebSocket real-time updates
- Chart.js visualizations
- Full CRUD for targets
- Search and filter functionality
- Export scan results
- Integration layer for existing JSON results
- Docker Compose integration

### 🎯 Key Files

#### Core Backend
- `dashboard/api_server.py` - FastAPI application (800+ lines)
  - All REST endpoints
  - WebSocket handler
  - Plugin integration
- `dashboard/database.py` - SQLAlchemy models
  - Scan, ScanResult, Vulnerability, Target, Plugin models
- `dashboard/plugin_manager.py` - Plugin discovery and management
- `dashboard/integration.py` - Import existing JSON results

#### Frontend
- `dashboard/templates/index.html` - Main dashboard UI
- `dashboard/static/js/dashboard.js` - Client-side logic (700+ lines)
- `dashboard/static/css/dashboard.css` - Main styles
- `dashboard/static/css/dark-mode.css` - Dark theme

#### Plugins
- `dashboard/plugins/base_plugin.py` - Plugin interface
- `dashboard/plugins/shodan_plugin.py` - Shodan scanner wrapper
- `dashboard/plugins/browser_plugin.py` - Browser automation wrapper
- `dashboard/plugins/account_creation_plugin.py` - Account creation tester
- `dashboard/plugins/mobile_app_plugin.py` - Mobile app analyzer

#### Configuration
- `start_dashboard.py` - Dashboard startup script
- `requirements.txt` - All Python dependencies
- `docker-compose.yml` - Docker services (scanner + dashboard)
- `Dockerfile` - Container build config

## Architecture

### Request Flow
```
User → Web UI → FastAPI → Plugin Manager → Plugin → Scanner Tool → Results → Database → WebSocket → UI Update
```

### Database Schema
```
Scan (id, scan_id, name, status, plugin_name, progress, ...)
  ├── ScanResult (scan_id FK, result_type, data, ...)
  └── Vulnerability (scan_id FK, title, severity, ...)

Target (id, url, name, priority, status, ...)
Plugin (id, name, enabled, config, ...)
```

### Plugin Interface
All plugins must implement:
- `validate_config(config)` - Validate scan configuration
- `run_scan(config, progress_callback)` - Execute scan
- `get_metadata()` - Return plugin info

## Common Tasks

### Adding a New Plugin
1. Create `dashboard/plugins/your_plugin.py`
2. Inherit from `BasePlugin`
3. Implement required methods
4. Plugin auto-discovers on restart

### Adding a New API Endpoint
1. Add route in `dashboard/api_server.py`
2. Use `get_db().get_session()` for database access
3. Return JSON or use templates for HTML
4. Update `/api/docs` endpoint

### Modifying UI
1. Edit `dashboard/templates/index.html` for structure
2. Edit `dashboard/static/js/dashboard.js` for logic
3. Edit CSS files for styling
4. Changes reflect immediately (no build step)

### Database Changes
1. Modify models in `dashboard/database.py`
2. SQLAlchemy auto-creates tables on first run
3. For migrations, use Alembic (not currently set up)

## Development Workflow

### Starting the Dashboard
```bash
cd /home/d/casino
python3 start_dashboard.py
# Or with Docker:
docker-compose up dashboard
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Create scan
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"plugin": "browser", "name": "Test", "url": "https://example.com"}'

# Get stats
curl http://localhost:8000/api/stats
```

### Database Location
- SQLite file: `dashboard/casino_scanner.db`
- Can be deleted to reset (will auto-recreate)

## Important Patterns

### Error Handling
- Use FastAPI `HTTPException` for API errors
- Log errors with `logger.error()`
- Show user-friendly messages in UI

### Background Tasks
- Use FastAPI `BackgroundTasks` for long-running scans
- Update progress via callback → WebSocket → UI

### State Management
- Database is source of truth
- WebSocket for real-time updates
- No client-side state persistence needed

## Known Issues / TODOs

### Current Limitations
- No user authentication (single-user system)
- No rate limiting on API
- SQLite may not scale for very large datasets
- No automated backups

### Potential Improvements
- Add authentication/authorization
- Implement rate limiting
- Add more visualization types
- Export to PDF/CSV formats
- Add scheduled scans
- Implement plugin marketplace

## File Organization

### Keep These
- All `dashboard/` files (core application)
- `requirements.txt` (dependencies)
- `docker-compose.yml`, `Dockerfile` (deployment)
- `start_dashboard.py` (startup script)
- `config/`, `results/`, `targets/` (data directories)
- Documentation files (*.md)

### Can Delete
- `__pycache__/` directories (auto-generated)
- `*.pyc` files (compiled Python)
- `*.log` files (logs, can regenerate)
- Old plan files (if superseded)
- Temporary test files

## Quick Reference

### API Endpoints
- `GET /` - Dashboard UI
- `GET /api/health` - Health check
- `GET /api/stats` - Statistics
- `GET /api/scans` - List scans
- `POST /api/scans` - Create scan
- `GET /api/scans/{id}` - Get scan details
- `GET /api/scans/{id}/export` - Export scan
- `DELETE /api/scans/{id}` - Cancel scan
- `GET /api/targets` - List targets
- `POST /api/targets` - Create target
- `GET /api/plugins` - List plugins
- `POST /api/quick-scan` - Quick scan (browser extension)
- `WebSocket /ws` - Real-time updates

### Environment Variables
- `PYTHONUNBUFFERED=1` - For Docker logging
- No other required env vars (uses SQLite)

### Ports
- `8000` - Dashboard web UI and API

## Tips for AI Agents

1. **Always check database state**: Use `get_db().get_session()` to query
2. **Use existing patterns**: Follow code style in `api_server.py`
3. **Test with curl**: Quick way to test API changes
4. **Check browser console**: For frontend debugging
5. **Restart server**: After backend changes (auto-reload not enabled)
6. **Plugin changes**: Require server restart to discover

## Next Steps for Enhancement

1. **Authentication**: Add user login/API keys
2. **Scheduling**: Cron-like scan scheduling
3. **Notifications**: Email/Slack alerts for findings
4. **Reporting**: Automated report generation
5. **Multi-tenancy**: Support multiple users/teams
6. **Plugin Marketplace**: Share plugins between instances

---

**Last Updated**: 2025-11-16
**Status**: Production Ready ✅

