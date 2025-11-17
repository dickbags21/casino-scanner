#!/bin/bash
# Test script for Node-RED integration with Casino Scanner Dashboard

set -e

echo "🧪 Testing Node-RED Integration"
echo "==============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node-RED is running
echo -e "${BLUE}1. Checking Node-RED status...${NC}"
if curl -s http://localhost:1880 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Node-RED is running on http://localhost:1880${NC}"
else
    echo -e "${RED}❌ Node-RED is not running${NC}"
    echo "   Start Node-RED with: node-red"
    exit 1
fi

# Check if FastAPI dashboard is running
echo ""
echo -e "${BLUE}2. Checking FastAPI dashboard status...${NC}"
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FastAPI dashboard is running on http://localhost:8000${NC}"
    DASHBOARD_RUNNING=true
else
    echo -e "${YELLOW}⚠️  FastAPI dashboard is not running${NC}"
    echo "   Start it with: python3 start_dashboard.py"
    echo "   (Tests will continue but webhook triggers won't work)"
    DASHBOARD_RUNNING=false
fi

# Test Node-RED webhook endpoints
echo ""
echo -e "${BLUE}3. Testing Node-RED webhook endpoints...${NC}"

# Test vulnerability-found webhook
echo -e "${BLUE}   Testing /webhook/vulnerability-found...${NC}"
VULN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:1880/webhook/vulnerability-found \
    -H "Content-Type: application/json" \
    -d '{
        "scan_id": "test-scan-123",
        "vulnerability": {
            "id": 1,
            "title": "Test Vulnerability",
            "severity": "critical",
            "url": "https://example.com"
        }
    }')

VULN_HTTP_CODE=$(echo "$VULN_RESPONSE" | tail -n1)
if [ "$VULN_HTTP_CODE" = "200" ] || [ "$VULN_HTTP_CODE" = "204" ]; then
    echo -e "${GREEN}   ✅ Vulnerability webhook responded (HTTP $VULN_HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Vulnerability webhook returned HTTP $VULN_HTTP_CODE${NC}"
fi

# Test scan-completed webhook
echo -e "${BLUE}   Testing /webhook/scan-completed...${NC}"
SCAN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:1880/webhook/scan-completed \
    -H "Content-Type: application/json" \
    -d '{
        "scan_id": "test-scan-123",
        "status": "completed",
        "results": {
            "total_results": 5,
            "total_vulnerabilities": 2
        }
    }')

SCAN_HTTP_CODE=$(echo "$SCAN_RESPONSE" | tail -n1)
if [ "$SCAN_HTTP_CODE" = "200" ] || [ "$SCAN_HTTP_CODE" = "204" ]; then
    echo -e "${GREEN}   ✅ Scan completed webhook responded (HTTP $SCAN_HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Scan completed webhook returned HTTP $SCAN_HTTP_CODE${NC}"
fi

# Test target-discovered webhook
echo -e "${BLUE}   Testing /webhook/target-discovered...${NC}"
TARGET_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:1880/webhook/target-discovered \
    -H "Content-Type: application/json" \
    -d '{
        "target": {
            "url": "https://test-casino.com",
            "region": "vietnam",
            "name": "Test Casino"
        },
        "source": "test"
    }')

TARGET_HTTP_CODE=$(echo "$TARGET_RESPONSE" | tail -n1)
if [ "$TARGET_HTTP_CODE" = "200" ] || [ "$TARGET_HTTP_CODE" = "204" ]; then
    echo -e "${GREEN}   ✅ Target discovered webhook responded (HTTP $TARGET_HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Target discovered webhook returned HTTP $TARGET_HTTP_CODE${NC}"
fi

# Test FastAPI webhook endpoints (if dashboard is running)
if [ "$DASHBOARD_RUNNING" = true ]; then
    echo ""
    echo -e "${BLUE}4. Testing FastAPI webhook endpoints...${NC}"
    
    # Test vulnerability-found endpoint
    echo -e "${BLUE}   Testing /api/webhooks/vulnerability-found...${NC}"
    API_VULN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/webhooks/vulnerability-found \
        -H "Content-Type: application/json" \
        -d '{
            "scan_id": "test-scan-123",
            "vulnerability": {
                "id": 1,
                "title": "Test Vulnerability",
                "severity": "critical",
                "url": "https://example.com"
            }
        }')
    
    API_VULN_HTTP_CODE=$(echo "$API_VULN_RESPONSE" | tail -n1)
    if [ "$API_VULN_HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}   ✅ FastAPI vulnerability webhook responded (HTTP $API_VULN_HTTP_CODE)${NC}"
    else
        echo -e "${YELLOW}   ⚠️  FastAPI vulnerability webhook returned HTTP $API_VULN_HTTP_CODE${NC}"
    fi
    
    # Test Node-RED flows endpoint
    echo -e "${BLUE}   Testing /api/node-red/flows...${NC}"
    FLOWS_RESPONSE=$(curl -s http://localhost:8000/api/node-red/flows)
    if echo "$FLOWS_RESPONSE" | grep -q "flows"; then
        echo -e "${GREEN}   ✅ Node-RED flows endpoint working${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Node-RED flows endpoint returned unexpected response${NC}"
    fi
fi

# Check Node-RED debug output
echo ""
echo -e "${BLUE}5. Checking Node-RED debug output...${NC}"
echo -e "${YELLOW}   ℹ️  Check Node-RED debug panel (right sidebar) for webhook messages${NC}"
echo -e "${YELLOW}   ℹ️  Open http://localhost:1880 and check the debug tab${NC}"

echo ""
echo -e "${GREEN}✅ Integration tests complete!${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  - Node-RED: Running on http://localhost:1880"
if [ "$DASHBOARD_RUNNING" = true ]; then
    echo "  - FastAPI Dashboard: Running on http://localhost:8000"
else
    echo "  - FastAPI Dashboard: Not running"
fi
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Open Node-RED editor: http://localhost:1880"
echo "  2. Check debug panel for webhook messages"
echo "  3. Verify flows are deployed and active"
echo "  4. Run a scan from the dashboard to trigger webhooks"
echo ""

