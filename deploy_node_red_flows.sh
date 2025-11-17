#!/bin/bash
# Deploy Node-RED flows automatically using the Admin API

set -e

echo "📦 Deploying Node-RED flows..."
echo ""

NODE_RED_URL="http://localhost:1880"
FLOWS_FILE="/home/d/casino/node-red/flows.json"

# Check if Node-RED is running
if ! curl -s "$NODE_RED_URL" > /dev/null 2>&1; then
    echo "❌ Node-RED is not running!"
    echo "   Start it with: ./start_node_red_background.sh"
    exit 1
fi

# Check if flows file exists
if [ ! -f "$FLOWS_FILE" ]; then
    echo "❌ Flows file not found: $FLOWS_FILE"
    exit 1
fi

echo "✅ Node-RED is running"
echo "✅ Flows file found: $FLOWS_FILE"
echo ""

# Read flows JSON
FLOWS_JSON=$(cat "$FLOWS_FILE")

# Deploy flows using Node-RED Admin API
echo "🚀 Deploying flows..."
RESPONSE=$(curl -s -X POST "$NODE_RED_URL/flows" \
    -H "Content-Type: application/json" \
    -d "$FLOWS_JSON" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Flows deployed successfully!"
    echo ""
    echo "🎉 Node-RED is ready!"
    echo "   Editor: http://localhost:1880"
    echo "   Test: ./test_node_red.sh"
else
    echo "⚠️  Deployment returned HTTP $HTTP_CODE"
    echo "   Response: $BODY"
    echo ""
    echo "💡 Try opening http://localhost:1880 and clicking Deploy manually"
fi

