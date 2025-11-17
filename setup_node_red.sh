#!/bin/bash
# Setup script for Node-RED integration with Casino Scanner Dashboard

set -e

echo "🔴 Node-RED Setup for Casino Scanner Dashboard"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node-RED is installed
if ! command -v node-red &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node-RED is not installed${NC}"
    echo "Installing Node-RED..."
    npm install -g node-red
    echo -e "${GREEN}✅ Node-RED installed${NC}"
else
    echo -e "${GREEN}✅ Node-RED is already installed${NC}"
    node-red --version
fi

# Create Node-RED user directory if it doesn't exist
NODE_RED_DIR="$HOME/.node-red"
if [ ! -d "$NODE_RED_DIR" ]; then
    echo "Creating Node-RED user directory: $NODE_RED_DIR"
    mkdir -p "$NODE_RED_DIR"
fi

# Copy settings file
echo ""
echo -e "${BLUE}📋 Copying Node-RED settings...${NC}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_SOURCE="$PROJECT_DIR/node-red/settings.js"
SETTINGS_TARGET="$NODE_RED_DIR/settings.js"

# Update paths in settings.js to use absolute paths
if [ -f "$SETTINGS_SOURCE" ]; then
    # Create a modified settings file with correct paths
    sed "s|/home/d/casino|$PROJECT_DIR|g" "$SETTINGS_SOURCE" > "$SETTINGS_TARGET"
    echo -e "${GREEN}✅ Settings file copied to $SETTINGS_TARGET${NC}"
else
    echo -e "${RED}❌ Settings file not found: $SETTINGS_SOURCE${NC}"
    exit 1
fi

# Copy flows file
echo ""
echo -e "${BLUE}📋 Copying Node-RED flows...${NC}"
FLOWS_SOURCE="$PROJECT_DIR/node-red/flows.json"
FLOWS_TARGET="$NODE_RED_DIR/flows.json"

if [ -f "$FLOWS_SOURCE" ]; then
    cp "$FLOWS_SOURCE" "$FLOWS_TARGET"
    echo -e "${GREEN}✅ Flows file copied to $FLOWS_TARGET${NC}"
    echo -e "${YELLOW}ℹ️  You can import these flows via Node-RED UI or they will load automatically${NC}"
else
    echo -e "${RED}❌ Flows file not found: $FLOWS_SOURCE${NC}"
    exit 1
fi

# Create static directory if needed
STATIC_DIR="$NODE_RED_DIR/static"
if [ ! -d "$STATIC_DIR" ]; then
    mkdir -p "$STATIC_DIR"
    echo -e "${GREEN}✅ Created static directory: $STATIC_DIR${NC}"
fi

# Check if Node-RED is running
echo ""
echo -e "${BLUE}🔍 Checking if Node-RED is running...${NC}"
if curl -s http://localhost:1880 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Node-RED is already running on http://localhost:1880${NC}"
    echo -e "${YELLOW}ℹ️  You may need to restart Node-RED for settings to take effect${NC}"
else
    echo -e "${YELLOW}ℹ️  Node-RED is not running${NC}"
    echo ""
    echo -e "${BLUE}To start Node-RED:${NC}"
    echo "  node-red"
    echo ""
    echo -e "${BLUE}Or run in background:${NC}"
    echo "  nohup node-red > /tmp/node-red.log 2>&1 &"
fi

echo ""
echo -e "${GREEN}✅ Node-RED setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Start Node-RED: node-red"
echo "2. Open Node-RED editor: http://localhost:1880"
echo "3. Deploy the flows (they should be auto-loaded)"
echo "4. Start the Casino Scanner Dashboard: python3 start_dashboard.py"
echo "5. Test the integration: ./test_node_red.sh"
echo ""
echo -e "${BLUE}Webhook endpoints in Node-RED:${NC}"
echo "  - http://localhost:1880/webhook/vulnerability-found"
echo "  - http://localhost:1880/webhook/scan-completed"
echo "  - http://localhost:1880/webhook/target-discovered"
echo ""

