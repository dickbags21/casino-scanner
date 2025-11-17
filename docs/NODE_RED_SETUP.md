# Node-RED Integration Setup Guide

This guide explains how to set up and test Node-RED automation integration with the Casino Scanner Dashboard.

## Overview

Node-RED provides event-driven automation workflows that respond to events from the Casino Scanner Dashboard:

- **Vulnerability Alerts**: Automatically alert when critical/high vulnerabilities are found
- **Scan Orchestration**: Automate scan execution and monitoring
- **Target Discovery**: Process newly discovered targets
- **Continuous Monitoring**: Real-time status updates and alerting

## Prerequisites

- Node.js and npm installed
- Node-RED installed globally: `npm install -g node-red`
- Casino Scanner Dashboard running (optional for testing)

## Quick Setup

### 1. Run Setup Script

```bash
./setup_node_red.sh
```

This script will:
- Check if Node-RED is installed (install if missing)
- Copy settings and flows to `~/.node-red/`
- Configure paths automatically
- Verify Node-RED status

### 2. Start Node-RED

```bash
node-red
```

Or run in background:
```bash
nohup node-red > /tmp/node-red.log 2>&1 &
```

### 3. Access Node-RED Editor

Open http://localhost:1880 in your browser.

The flows should be automatically loaded. If not:
1. Click the menu (☰) → Import
2. Select `~/.node-red/flows.json`
3. Click Deploy

### 4. Test Integration

```bash
./test_node_red.sh
```

This will test:
- Node-RED is running
- Webhook endpoints are accessible
- FastAPI dashboard integration (if running)

## Manual Setup

If you prefer manual setup:

### 1. Install Node-RED

```bash
npm install -g node-red
```

### 2. Copy Configuration Files

```bash
# Copy settings
cp node-red/settings.js ~/.node-red/settings.js

# Copy flows
cp node-red/flows.json ~/.node-red/flows.json
```

### 3. Update Paths in settings.js

Edit `~/.node-red/settings.js` and update:
- `userDir`: Path to your Node-RED directory
- `flowFile`: Path to flows.json
- `httpStatic`: Path to static files (if needed)

### 4. Start Node-RED

```bash
node-red
```

## Webhook Endpoints

Node-RED exposes these webhook endpoints:

| Endpoint | Purpose | Triggered By |
|----------|---------|--------------|
| `/webhook/vulnerability-found` | Vulnerability alerts | FastAPI when vulnerability discovered |
| `/webhook/scan-completed` | Scan completion | FastAPI when scan finishes |
| `/webhook/target-discovered` | Target discovery | FastAPI when new target found |

## FastAPI → Node-RED Integration

The FastAPI dashboard automatically sends webhooks to Node-RED when:

1. **Vulnerability Found**: During scan execution, when a vulnerability is discovered
2. **Scan Completed**: When a scan finishes (success or failure)
3. **Target Discovered**: When a new target is discovered during region/target discovery

### Configuration

The webhook URL is configurable via environment variable:

```bash
export NODE_RED_URL="http://localhost:1880"
```

Default: `http://localhost:1880`

## Testing

### Run Integration Tests

```bash
# Run all Node-RED tests (requires Node-RED running)
pytest -m node-red --node-red

# Run specific test file
pytest tests/test_node_red_integration.py --node-red

# Run with verbose output
pytest -m node-red --node-red -v
```

### Manual Testing

1. **Start Node-RED**: `node-red`
2. **Start Dashboard**: `python3 start_dashboard.py`
3. **Run Test Script**: `./test_node_red.sh`
4. **Check Node-RED Debug Panel**: Open http://localhost:1880 and check the debug tab (right sidebar)

### Test Webhooks Manually

```bash
# Test vulnerability webhook
curl -X POST http://localhost:1880/webhook/vulnerability-found \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "test-123",
    "vulnerability": {
      "id": 1,
      "title": "Test Vulnerability",
      "severity": "critical",
      "url": "https://example.com"
    }
  }'

# Test scan completed webhook
curl -X POST http://localhost:1880/webhook/scan-completed \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "test-123",
    "status": "completed",
    "results": {
      "total_results": 5,
      "total_vulnerabilities": 2
    }
  }'
```

## Node-RED Flows

### Flow 1: Vulnerability Alert Automation

**Trigger**: `/webhook/vulnerability-found`

**Actions**:
- Filters by severity (critical/high only)
- Formats alert messages
- Logs to debug panel
- Can be extended to send to Slack, Discord, email, etc.

### Flow 2: Scan Orchestration

**Trigger**: Scheduled or manual

**Actions**:
- Calls FastAPI `/api/scans` endpoint
- Monitors progress
- Handles failures with retry logic

### Flow 3: Target Discovery Pipeline

**Trigger**: Scheduled (daily) or manual

**Actions**:
- Calls region discovery
- Validates targets
- Adds to database via API
- Triggers scans for new targets

### Flow 4: Continuous Monitoring

**Trigger**: WebSocket events from dashboard

**Actions**:
- Real-time status updates
- Alert on scan failures
- Performance monitoring

## Customization

### Adding New Automation

1. Open Node-RED editor: http://localhost:1880
2. Create new flow or modify existing
3. Add nodes as needed (HTTP, function, debug, etc.)
4. Deploy changes

### Extending Webhooks

To add new webhook endpoints:

1. **In Node-RED**: Add new "http in" node
2. **In FastAPI**: Add webhook trigger in `dashboard/api_server.py`
3. **Update mapping**: Add endpoint mapping in `trigger_webhook_async()`

Example:
```python
# In api_server.py
endpoint_map = {
    "/api/webhooks/vulnerability-found": "/webhook/vulnerability-found",
    "/api/webhooks/my-new-webhook": "/webhook/my-new-webhook"  # Add this
}
```

## Troubleshooting

### Node-RED Not Starting

- Check if port 1880 is already in use: `lsof -i :1880`
- Check Node-RED logs: `~/.node-red/node-red.log`
- Verify Node.js version: `node --version` (should be 14+)

### Webhooks Not Working

1. **Check Node-RED is running**: `curl http://localhost:1880`
2. **Check flows are deployed**: Open Node-RED editor, verify flows are active
3. **Check debug panel**: Look for incoming webhook messages
4. **Check FastAPI logs**: Look for webhook trigger messages
5. **Verify endpoint mapping**: Check `trigger_webhook_async()` function

### Flows Not Loading

- Verify `flows.json` is in `~/.node-red/`
- Check file permissions
- Manually import via Node-RED UI: Menu → Import → Select flows.json

### Webhook Timeout

- Increase timeout in `trigger_webhook_async()` (default: 5 seconds)
- Check Node-RED flow processing time
- Verify Node-RED is not overloaded

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_RED_URL` | `http://localhost:1880` | Node-RED base URL |
| `NODE_RED_CREDENTIAL_SECRET` | `casino-scanner-secret-change-in-production` | Credential encryption secret |

## Production Considerations

1. **Change credential secret**: Set `NODE_RED_CREDENTIAL_SECRET` environment variable
2. **Use HTTPS**: Configure Node-RED with SSL/TLS
3. **Authentication**: Enable Node-RED authentication
4. **Backup flows**: Regularly backup `~/.node-red/flows.json`
5. **Monitoring**: Set up monitoring for Node-RED process
6. **Logging**: Configure proper logging for production

## Resources

- [Node-RED Documentation](https://nodered.org/docs/)
- [Node-RED API](https://nodered.org/docs/api/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Casino Scanner Dashboard API Docs](http://localhost:8000/api/docs)

## Support

For issues or questions:
1. Check Node-RED debug panel
2. Review FastAPI logs
3. Run test script: `./test_node_red.sh`
4. Check integration tests: `pytest tests/test_node_red_integration.py --node-red`

