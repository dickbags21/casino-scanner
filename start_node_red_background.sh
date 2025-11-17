#!/bin/bash
# Start Node-RED in the background

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_FILE="$PROJECT_DIR/node-red/settings.js"
LOG_FILE="/tmp/node-red-casino.log"
PID_FILE="/tmp/node-red-casino.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Node-RED is already running (PID: $PID)"
        echo "   Editor: http://localhost:1880"
        echo "   Logs: tail -f $LOG_FILE"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Check if Node-RED is installed
if ! command -v node-red &> /dev/null; then
    echo "❌ Node-RED is not installed!"
    echo "Run: ./setup_node_red.sh"
    exit 1
fi

echo "🚀 Starting Node-RED in background..."
echo "   Settings: $SETTINGS_FILE"
echo "   Logs: $LOG_FILE"
echo ""

# Start Node-RED in background
cd "$PROJECT_DIR"
nohup node-red --settings "$SETTINGS_FILE" > "$LOG_FILE" 2>&1 &
NODE_RED_PID=$!

# Save PID
echo $NODE_RED_PID > "$PID_FILE"

# Wait a moment to check if it started
sleep 2

if ps -p $NODE_RED_PID > /dev/null 2>&1; then
    echo "✅ Node-RED started successfully!"
    echo "   PID: $NODE_RED_PID"
    echo "   Editor: http://localhost:1880"
    echo "   Logs: tail -f $LOG_FILE"
    echo "   Stop: ./stop_node_red.sh"
    echo ""
    echo "📦 Deploying flows..."
    sleep 3  # Wait for Node-RED to fully start
    "$PROJECT_DIR/deploy_node_red_flows.sh" > /dev/null 2>&1 && echo "✅ Flows deployed!" || echo "⚠️  Flows may need manual deployment"
else
    echo "❌ Node-RED failed to start"
    echo "   Check logs: cat $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

