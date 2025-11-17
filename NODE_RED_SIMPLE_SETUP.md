# Node-RED Simple Setup - No Node.js Knowledge Required! 🎯

I've set up everything so you can use Node-RED without knowing Node.js. Just run these simple commands:

## 🚀 Quick Start (3 Commands)

### 1. Start Node-RED (in background)

```bash
./start_node_red_background.sh
```

That's it! Node-RED will:

- ✅ Load your flows automatically from `node-red/flows.json`
- ✅ Use your settings from `node-red/settings.js`
- ✅ Start on <http://localhost:1880>
- ✅ Run in the background

### 2. Check if it's running

```bash
curl http://localhost:1880
```

If you see HTML, it's working!

### 3. Stop Node-RED (when needed)

```bash
./stop_node_red.sh
```

## 📋 What Each Script Does

| Script | What It Does |
|--------|--------------|
| `./start_node_red_background.sh` | Starts Node-RED in background (recommended) |
| `./start_node_red.sh` | Starts Node-RED in foreground (see logs) |
| `./stop_node_red.sh` | Stops Node-RED |
| `./test_node_red.sh` | Tests if everything is working |

## 🔍 Check Status

**Is Node-RED running?**

```bash
curl http://localhost:1880
```

**View logs:**

```bash
tail -f /tmp/node-red-casino.log
```

**Check if flows are loaded:**

```bash
./test_node_red.sh
```

## 🎨 Optional: Open Node-RED Editor

If you want to see the visual editor (optional):

1. Start Node-RED: `./start_node_red_background.sh`
2. Open browser: <http://localhost:1880>
3. You'll see your 4 flows already loaded!

**You don't need to do anything in the editor** - the flows are already configured and will work automatically.

## ✅ What's Already Configured

- ✅ Flows file: `node-red/flows.json` (4 automation flows)
- ✅ Settings file: `node-red/settings.js` (all configured)
- ✅ Webhook endpoints ready
- ✅ Integration with FastAPI dashboard

## 🧪 Test It

After starting Node-RED, test the integration:

```bash
# Test if webhooks work
curl -X POST http://localhost:1880/webhook/vulnerability-found \
  -H "Content-Type: application/json" \
  -d '{"scan_id":"test","vulnerability":{"title":"Test","severity":"critical"}}'
```

Check the logs to see if it worked:

```bash
tail -f /tmp/node-red-casino.log
```

## 🆘 Troubleshooting

**Node-RED won't start:**

```bash
# Check if port 1880 is in use
lsof -i :1880

# Check logs
cat /tmp/node-red-casino.log
```

**Flows not working:**

- Make sure Node-RED is running: `curl http://localhost:1880`
- Check logs: `tail -f /tmp/node-red-casino.log`
- Restart: `./stop_node_red.sh && ./start_node_red_background.sh`

**Need to restart:**

```bash
./stop_node_red.sh
./start_node_red_background.sh
```

## 📝 Summary

**You only need to remember:**

1. `./start_node_red_background.sh` - Start it
2. `./stop_node_red.sh` - Stop it
3. `./test_node_red.sh` - Test it

Everything else is automatic! 🎉
