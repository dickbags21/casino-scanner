#!/bin/bash
# 🎰 Automated Casino Scanner Setup Script
# Sets up the complete automated vulnerability discovery system

set -e  # Exit on any error

echo "🎰 AUTOMATED CASINO SCANNER SETUP"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the casino scanner root directory"
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🌐 Installing Playwright browsers..."
playwright install chromium

echo "📁 Creating necessary directories..."
mkdir -p results/screenshots
mkdir -p logs
mkdir -p alerts

echo "⚙️  Setting up configuration files..."

# Create alert configuration if it doesn't exist
if [ ! -f "config/alert_config.yaml" ]; then
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
    condition: "lambda data: data.get('classification', {}).get('overall_score', 0) >= 9.0"
    priority: 10
    channels: ['cursor_ai', 'file_alerts']
    template: critical_vulnerability_alert
    cooldown_minutes: 30
    enabled: true

  - name: high_value_opportunity
    condition: "lambda data: data.get('classification', {}).get('profit_potential_score', 0) >= 8.0"
    priority: 9
    channels: ['cursor_ai', 'file_alerts']
    template: high_value_alert
    cooldown_minutes: 60
    enabled: true
EOF
    echo "✅ Created alert configuration"
fi

echo "🔧 Making scripts executable..."
chmod +x automated_scanner.py
chmod +x casino_scanner.py
chmod +x main.py

echo "🧪 Testing system components..."

# Test import of all modules
echo "Testing module imports..."
python3 -c "
try:
    from tools.auto_region_discovery import AutoRegionDiscovery
    from tools.intelligent_target_discovery import IntelligentTargetDiscovery
    from tools.continuous_scanner import ContinuousScanner
    from tools.vulnerability_classifier import VulnerabilityClassifier
    from tools.alert_system import AlertSystem
    from automated_scanner import AutomatedCasinoScanner
    print('✅ All modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "Your automated casino vulnerability scanner is now ready!"
echo ""
echo "🚀 Quick Start Commands:"
echo "  python3 automated_scanner.py scan     # Run a single discovery cycle"
echo "  python3 automated_scanner.py status   # Check system status"
echo "  python3 automated_scanner.py alert    # Send a test alert"
echo "  python3 automated_scanner.py start    # Start continuous scanning"
echo ""
echo "📚 Available Commands:"
echo "  scan     - Run single discovery cycle"
echo "  start    - Start continuous scanning mode"
echo "  status   - Show system status and statistics"
echo "  alert    - Send test alert to verify configuration"
echo "  stop     - Stop continuous scanning"
echo ""
echo "⚠️  Important Notes:"
echo "  • Configure your API keys in config/config.yaml"
echo "  • Set up alert channels in config/alert_config.yaml"
echo "  • Check logs/automated_scanner.log for detailed information"
echo "  • Use responsibly and in accordance with applicable laws"
echo ""
echo "🎯 Next Steps:"
echo "  1. Edit config/config.yaml with your API keys"
echo "  2. Run: python3 automated_scanner.py scan"
echo "  3. Check results/ for scan reports"
echo "  4. Run: python3 automated_scanner.py start (for continuous mode)"
echo ""
echo "Happy hunting! 🎰"
