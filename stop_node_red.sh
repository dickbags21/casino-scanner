#!/bin/bash
# Stop Node-RED

PID_FILE="/tmp/node-red-casino.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  Node-RED doesn't appear to be running (no PID file)"
    # Try to find and kill by port
    PID=$(lsof -ti:1880 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo "   Found process on port 1880 (PID: $PID), killing it..."
        kill $PID
        echo "✅ Node-RED stopped"
    else
        echo "   Node-RED is not running"
    fi
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 Stopping Node-RED (PID: $PID)..."
    kill $PID
    sleep 1
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "   Force killing..."
        kill -9 $PID
    fi
    
    rm -f "$PID_FILE"
    echo "✅ Node-RED stopped"
else
    echo "⚠️  Node-RED process not found (PID: $PID)"
    rm -f "$PID_FILE"
fi

