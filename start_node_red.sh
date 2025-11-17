#!/bin/bash
# Simple script to start Node-RED with Casino Scanner configuration

set -e

echo "🔴 Starting Node-RED for Casino Scanner..."
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_FILE="$PROJECT_DIR/node-red/settings.js"

# Check if Node-RED is installed
if ! command -v node-red &> /dev/null; then
    echo "❌ Node-RED is not installed!"
    echo "Run: ./setup_node_red.sh"
    exit 1
fi

# Check if settings file exists
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "❌ Settings file not found: $SETTINGS_FILE"
    exit 1
fi

# Check if flows file exists
FLOWS_FILE="$PROJECT_DIR/node-red/flows.json"
if [ ! -f "$FLOWS_FILE" ]; then
    echo "❌ Flows file not found: $FLOWS_FILE"
    exit 1
fi

echo "✅ Configuration files found"
echo "   Settings: $SETTINGS_FILE"
echo "   Flows: $FLOWS_FILE"
echo ""

# Check if Node-RED is already running
if curl -s http://localhost:1880 > /dev/null 2>&1; then
    echo "⚠️  Node-RED is already running on http://localhost:1880"
    echo "   Stop it first or use a different port"
    exit 1
fi

echo "🚀 Starting Node-RED..."
echo "   Editor: http://localhost:1880"
echo "   Press Ctrl+C to stop"
echo ""

# Start Node-RED with custom settings file
# Use --settings flag to specify the settings file
cd "$PROJECT_DIR"
node-red --settings "$SETTINGS_FILE"

