#!/bin/bash
# Test runner script for Casino Scanner Dashboard

set -e

echo "🧪 Casino Scanner Dashboard - Test Runner"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest is not installed${NC}"
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

case "$TEST_TYPE" in
    unit)
        echo -e "${GREEN}Running unit tests...${NC}"
        pytest -m unit $VERBOSE
        ;;
    integration)
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest -m integration $VERBOSE
        ;;
    api)
        echo -e "${GREEN}Running API tests...${NC}"
        pytest -m api $VERBOSE
        ;;
    database)
        echo -e "${GREEN}Running database tests...${NC}"
        pytest -m database $VERBOSE
        ;;
    plugin)
        echo -e "${GREEN}Running plugin tests...${NC}"
        pytest -m plugin $VERBOSE
        ;;
    coverage)
        echo -e "${GREEN}Running tests with coverage...${NC}"
        pytest --cov=dashboard --cov=tools --cov-report=term-missing --cov-report=html
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    fast)
        echo -e "${GREEN}Running fast tests (unit only, no slow)...${NC}"
        pytest -m "unit and not slow" $VERBOSE
        ;;
    all|*)
        echo -e "${GREEN}Running all tests...${NC}"
        pytest $VERBOSE
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"

