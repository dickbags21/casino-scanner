#!/bin/bash
# Post-create script that runs after the devcontainer is created
# This sets up the environment and verifies everything is working

set -e

echo "🎰 CASINO SCANNER PRO - CONTAINER SETUP"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verify Python installation
echo -e "${GREEN}✓${NC} Checking Python installation..."
python3 --version
pip --version

# Verify Playwright browsers
echo -e "${GREEN}✓${NC} Checking Playwright browsers..."
if playwright --version > /dev/null 2>&1; then
    echo "  Playwright installed successfully"
    playwright install chromium --with-deps || true
else
    echo -e "${YELLOW}⚠${NC}  Playwright not found, installing..."
    pip install playwright
    playwright install chromium
    playwright install-deps chromium
fi

# Verify Python dependencies
echo -e "${GREEN}✓${NC} Verifying Python dependencies..."
python3 -c "
import sys
required = ['playwright', 'yaml', 'requests', 'asyncio', 'schedule']
missing = []
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f'  Missing packages: {missing}')
    sys.exit(1)
else:
    print('  All required packages installed')
"

# Test module imports
echo -e "${GREEN}✓${NC} Testing module imports..."
python3 -c "
try:
    from tools.auto_region_discovery import AutoRegionDiscovery
    from tools.intelligent_target_discovery import IntelligentTargetDiscovery
    from tools.continuous_scanner import ContinuousScanner
    from tools.vulnerability_classifier import VulnerabilityClassifier
    from tools.alert_system import AlertSystem
    print('  All modules imported successfully')
except ImportError as e:
    print(f'  Import error: {e}')
    exit(1)
"

# Create config files if they don't exist
echo -e "${GREEN}✓${NC} Setting up configuration files..."
if [ ! -f "config/config.yaml" ]; then
    echo "  Creating default config.yaml..."
    mkdir -p config
    cat > config/config.yaml << 'EOF'
# Casino Security Research Framework Configuration

apis:
  shodan:
    api_key: "YOUR_SHODAN_API_KEY_HERE"
    rate_limit: 10
    timeout: 30

browser:
  headless: true
  timeout: 30000
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  viewport:
    width: 1920
    height: 1080

regions:
  vietnam:
    country_code: "VN"
    language: "vi"
    timezone: "Asia/Ho_Chi_Minh"
    search_terms:
      - "casino"
      - "cờ bạc"
    ports: [80, 443, 8080, 8443]

output:
  results_dir: "results"
  logs_dir: "logs"
  report_format: "json"
  save_screenshots: true

logging:
  level: "INFO"
  max_bytes: 10485760
  backup_count: 5
EOF
fi

if [ ! -f "config/alert_config.yaml" ]; then
    echo "  Creating default alert_config.yaml..."
    cat > config/alert_config.yaml << 'EOF'
channels:
  - name: cursor_ai
    type: cursor_ai
    config:
      directory: ~/.cursor/casino_alerts
    enabled: true

  - name: file_alerts
    type: file
    config:
      directory: alerts
    enabled: true

rules:
  - name: critical_vulnerability
    priority: 10
    channels: ['cursor_ai', 'file_alerts']
    template: critical_vulnerability_alert
    cooldown_minutes: 30
    enabled: true
EOF
fi

# Set up Git (if not already configured)
echo -e "${GREEN}✓${NC} Checking Git configuration..."
if [ -z "$(git config user.name)" ]; then
    echo "  Git user not configured (this is OK for now)"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "  Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Results and logs
results/*
!results/.gitkeep
logs/*
!logs/.gitkeep
*.log

# Config (may contain secrets)
config/*.yaml
!config/config.yaml.example
!config/alert_config.yaml.example

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Alerts and exploits
alerts/*
exploits/generated/*
EOF
fi

# Make scripts executable
echo -e "${GREEN}✓${NC} Making scripts executable..."
chmod +x *.py *.sh 2>/dev/null || true
chmod +x tools/*.py 2>/dev/null || true

# Display helpful information
echo ""
echo "========================================"
echo -e "${GREEN}✅ CONTAINER SETUP COMPLETE!${NC}"
echo "========================================"
echo ""
echo "🚀 Quick Start Commands:"
echo "  python3 automated_scanner.py scan     # Run discovery cycle"
echo "  python3 automated_scanner.py status   # Check system status"
echo "  python3 automated_scanner.py alert    # Send test alert"
echo "  python3 automated_scanner.py start    # Start continuous mode"
echo ""
echo "📁 Project Structure:"
echo "  /workspace/                           # Project root"
echo "  /workspace/tools/                     # Scanner modules"
echo "  /workspace/config/                     # Configuration files"
echo "  /workspace/results/                   # Scan results"
echo "  /workspace/logs/                      # Application logs"
echo ""
echo "⚙️  Next Steps:"
echo "  1. Configure API keys in config/config.yaml"
echo "  2. Run: python3 automated_scanner.py scan"
echo "  3. Check results/ for scan reports"
echo ""
echo "💡 Tips:"
echo "  - All dependencies are pre-installed"
echo "  - Playwright browsers are ready to use"
echo "  - Your workspace is mounted at /workspace"
echo "  - Results persist in Docker volumes"
echo ""
echo "Happy hunting! 🎰"




