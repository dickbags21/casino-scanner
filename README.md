# 🎰 Casino Scanner Dashboard

A production-ready security research framework for managing and monitoring casino/gambling site security scans. Features a modern web dashboard, plugin-based architecture, real-time monitoring, REST API access, and Node-RED automation integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Node.js (for Node-RED automation, optional)
- (Optional) Docker & Docker Compose

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt --user
```

2. **Start the dashboard:**
```bash
python3 start_dashboard.py
```

3. **Access the dashboard:**
Open http://localhost:8000 in your browser

### Docker

```bash
docker-compose up dashboard
```

## 📋 Features

- **Web Dashboard**: Modern UI with dark mode support, terminal interface, and command palette
- **Plugin System**: Modular architecture for scanner tools
- **Real-time Monitoring**: WebSocket-based live updates
- **REST API**: Full API for automation and integration
- **Node-RED Automation**: Event-driven automation workflows
- **Data Visualization**: Charts for vulnerabilities and scan history
- **Target Management**: Organize and prioritize scan targets
- **Export**: Download scan results in JSON format
- **Keyboard Shortcuts**: Power user features (Ctrl+U for command palette)

## 🏗️ Architecture

### Components

- **FastAPI Backend**: REST API and WebSocket server
- **SQLite Database**: Stores scans, results, vulnerabilities, targets
- **Plugin System**: Wraps existing scanner tools
- **Web Dashboard**: HTML/CSS/JavaScript frontend
- **Node-RED**: Automation and workflow orchestration

### Plugins

- **Shodan Scanner**: Internet-wide device search
- **Browser Scanner**: Automated browser testing with instance management
- **Account Creation Scanner**: Account signup flow testing
- **Mobile App Scanner**: Mobile application analysis

## 📖 Usage

### Web Interface

1. Navigate to http://localhost:8000
2. Use the navigation to access:
   - **Dashboard**: Overview and statistics
   - **Scans**: Create and manage scans
   - **Vulnerabilities**: View security findings
   - **Targets**: Manage scan targets
   - **Plugins**: Configure scanner plugins
   - **Terminal**: Command-line interface (Ctrl+` to open)

### Keyboard Shortcuts

- `Ctrl+U` / `Ctrl+K` - Open command palette
- `Ctrl+N` - New scan
- `Ctrl+T` - New target
- `Ctrl+D` - Go to dashboard
- `Ctrl+S` - Go to scans
- `Ctrl+V` - Go to vulnerabilities
- `Ctrl+\`` - Open terminal
- `Ctrl+Shift+D` - Toggle dark mode
- `Escape` - Close modals/palette

### Terminal Commands

Access the terminal from the dashboard or press `Ctrl+\``:

```bash
help              # Show available commands
scan <url>        # Start a browser scan
targets           # List all targets
plugins           # List all plugins
stats             # Show dashboard statistics
browser start     # Start browser instance
browser stop      # Stop browser instance
browser status    # Check browser status
clear             # Clear terminal
```

### API

#### Create a Scan
```bash
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "plugin": "browser",
    "name": "Test Scan",
    "url": "https://example.com",
    "scan_type": "signup"
  }'
```

#### Get Statistics
```bash
curl http://localhost:8000/api/stats
```

#### List Targets
```bash
curl http://localhost:8000/api/targets
```

#### Quick Scan (Browser Extension)
```bash
curl -X POST http://localhost:8000/api/quick-scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### API Documentation

Visit http://localhost:8000/api/docs for interactive API documentation.

## 🔧 Node-RED Automation

Node-RED provides powerful automation capabilities for the Casino Scanner.

### Setup

1. **Install Node-RED** (if not already installed):
```bash
npm install -g node-red
```

2. **Configure Node-RED**:
   - Copy `node-red/settings.js` to your Node-RED user directory (usually `~/.node-red/`)
   - Import flows from `node-red/flows.json`

3. **Start Node-RED**:
```bash
node-red
```

4. **Access Node-RED Editor**:
   - Open http://localhost:1880

### Available Flows

1. **Vulnerability Alert Automation**
   - Triggers when vulnerabilities are found
   - Filters by severity (critical/high)
   - Sends alerts to multiple channels
   - Logs to file

2. **Scan Orchestration**
   - Creates and monitors scans
   - Handles failures with retry logic
   - Aggregates results

3. **Target Discovery Pipeline**
   - Scheduled daily target discovery
   - Validates and adds targets
   - Triggers scans for new targets

4. **Continuous Monitoring**
   - Real-time status updates
   - Alert on scan failures
   - Performance monitoring

### Webhook Endpoints

The dashboard provides webhook endpoints for Node-RED:

- `POST /api/webhooks/vulnerability-found` - Triggered when vulnerability found
- `POST /api/webhooks/scan-completed` - Triggered when scan completes
- `POST /api/webhooks/target-discovered` - Triggered when target discovered

### Node-RED API

- `GET /api/node-red/flows` - List available flows and webhook endpoints

## 🔧 Configuration

### Database

The SQLite database is automatically created at `dashboard/casino_scanner.db`. To reset:
```bash
rm dashboard/casino_scanner.db
# Restart dashboard to recreate
```

### Plugins

Plugins are auto-discovered from `dashboard/plugins/`. To add a new plugin:
1. Create a new file in `dashboard/plugins/`
2. Inherit from `BasePlugin`
3. Implement required methods
4. Restart the dashboard

## 📁 Project Structure

```
casino/
├── dashboard/              # Main application
│   ├── api_server.py      # FastAPI application
│   ├── database.py        # Database models
│   ├── plugin_manager.py  # Plugin system
│   ├── integration.py     # Import existing results
│   ├── plugins/           # Scanner plugins
│   ├── static/            # CSS, JavaScript
│   ├── templates/         # HTML templates
│   └── casino_scanner.db  # SQLite database
├── tools/                 # Core scanning tools
├── config/                # Configuration files
├── targets/               # Target definitions
├── docs/                  # Documentation
├── archive/               # Archived scripts
├── node-red/              # Node-RED flows and config
├── start_dashboard.py     # Startup script
├── automated_scanner.py   # Continuous scanning
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🛠️ Development

### Adding a New Plugin

1. Create `dashboard/plugins/your_plugin.py`:
```python
from dashboard.plugins.base_plugin import BasePlugin, PluginMetadata

class YourPlugin(BasePlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="your_plugin",
            display_name="Your Plugin",
            description="Plugin description"
        )
    
    def validate_config(self, config):
        # Validate configuration
        return True, None
    
    async def scan(self, config, progress_callback):
        # Run your scan
        await progress_callback(ScanProgress(progress=1.0, status='completed'))
        return {"result": "success"}
```

2. Restart the dashboard - plugin auto-discovers

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
- `POST /api/quick-scan` - Quick scan
- `POST /api/webhooks/*` - Webhook endpoints for Node-RED
- `GET /api/node-red/flows` - List Node-RED flows
- `WebSocket /ws` - Real-time updates

## 📚 Documentation

- **README.md** (this file) - Getting started guide
- **USAGE.md** - Detailed usage instructions
- **docs/ARCHITECTURE.md** - Technical architecture
- **docs/CHANGELOG.md** - Version history
- **dashboard/README.md** - Dashboard-specific documentation

## 🔒 Security Notes

⚠️ **Important**: This tool is for authorized security research only.

- No authentication implemented (single-user system)
- No rate limiting on API endpoints
- Ensure proper file permissions on database file
- Use in secure network environment
- Change Node-RED credential secret in production

## 🐛 Troubleshooting

### Dashboard won't start
- Check if port 8000 is available
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check logs in console output

### Plugins not loading
- Verify plugin files are in `dashboard/plugins/`
- Check plugin inherits from `BasePlugin`
- Restart dashboard after adding plugins

### Database errors
- Delete `dashboard/casino_scanner.db` to reset
- Check file permissions
- Ensure SQLite is available

### Node-RED not connecting
- Verify Node-RED is running on port 1880
- Check webhook endpoints are accessible
- Review Node-RED logs for errors

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

1. Follow existing code patterns
2. Add tests for new features
3. Update documentation
4. Ensure backward compatibility

## 📞 Support

For issues or questions:
- Check `docs/ARCHITECTURE.md` for technical details
- Review API docs at `/api/docs`
- Check dashboard logs for errors
- Review Node-RED flows for automation issues

---

**Status**: ✅ Production Ready  
**Version**: 2.0.0  
**Last Updated**: 2025-01-XX
