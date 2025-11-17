# Node-RED Quick Start Guide

## ✅ Setup Complete!

Node-RED has been installed and configured. Here's what to do next:

## 1. Deploy Flows in Node-RED

The flows are already copied to `~/.node-red/flows.json`, but they need to be deployed:

1. **Open Node-RED Editor**: http://localhost:1880
2. **Check if flows are loaded**: You should see 4 tabs/flows:
   - Vulnerability Alert Automation
   - Scan Orchestration
   - Target Discovery Pipeline
   - Continuous Monitoring
3. **Deploy**: Click the **Deploy** button (top right)
4. **Verify**: Check the debug panel (right sidebar) - it should show "flows deployed"

## 2. Test the Integration

Run the test script:
```bash
./test_node_red.sh
```

Or test manually:
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
```

Check the Node-RED debug panel - you should see the webhook message!

## 3. Start the Dashboard (if not running)

```bash
python3 start_dashboard.py
```

## 4. Test End-to-End

1. Open the dashboard: http://localhost:8000
2. Create a scan or trigger a vulnerability
3. Check Node-RED debug panel - you should see webhook messages

## Troubleshooting

### Flows Not Showing in Node-RED

If flows aren't visible:
1. In Node-RED editor, click Menu (☰) → Import
2. Select `~/.node-red/flows.json`
3. Click Deploy

### Webhooks Returning 404

- Make sure flows are **deployed** (click Deploy button)
- Check that flows are **enabled** (not grayed out)
- Verify webhook endpoints match: `/webhook/vulnerability-found`, etc.

### Need to Restart Node-RED

If you made changes to settings:
```bash
# Stop Node-RED (Ctrl+C if running in foreground)
# Or kill the process: pkill node-red

# Start again
node-red
```

## What's Working

✅ Node-RED installed and running  
✅ Configuration files copied  
✅ Flows file ready  
✅ FastAPI webhook endpoints configured  
✅ Integration tests created  

## Next Steps

- Deploy flows in Node-RED (see step 1 above)
- Test webhooks (see step 2 above)
- Customize flows as needed
- See `docs/NODE_RED_SETUP.md` for detailed documentation

