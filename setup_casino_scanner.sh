#!/bin/bash

# Casino Scanner Pro 4.0 - Complete Setup Script
# Sets up the entire casino vulnerability research framework

set -e

echo "🎰 CASINO SCANNER PRO 4.0 - CODE ROTEN"
echo "═══════════════════════════════════════════════"
echo "Complete setup for casino vulnerability research"
echo "═══════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo -e "${PURPLE}🎯${NC} $1"
}

# Check if running as root (not recommended for most operations)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root is not recommended for development"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    PACKAGE_MANAGER="apt"
    if command -v pacman &> /dev/null; then
        PACKAGE_MANAGER="pacman"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    PACKAGE_MANAGER="brew"
else
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

print_info "Detected OS: $OS with $PACKAGE_MANAGER"

# Function to install packages based on OS
install_package() {
    local package=$1

    if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
        sudo apt update
        sudo apt install -y "$package"
    elif [[ "$PACKAGE_MANAGER" == "pacman" ]]; then
        sudo pacman -S --noconfirm "$package"
    elif [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
        sudo dnf install -y "$package"
    elif [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        brew install "$package"
    fi
}

# Check Python version
print_header "Checking Python Version"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ -z "$python_version" ]]; then
    print_error "Python 3 not found. Installing..."
    if [[ "$OS" == "linux" ]]; then
        install_package "python3"
    elif [[ "$OS" == "macos" ]]; then
        print_info "Please install Python 3 from https://www.python.org/downloads/"
        exit 1
    fi
else
    print_status "Python version: $python_version"
fi

# Check pip
print_header "Checking pip"
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 not found. Installing..."
    if [[ "$OS" == "linux" ]]; then
        install_package "python3-pip"
    elif [[ "$OS" == "macos" ]]; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py
        rm get-pip.py
    fi
fi
print_status "pip3 is available"

# Install Python dependencies
print_header "Installing Python Dependencies"
pip3 install --upgrade pip
pip3 install -r requirements.txt
print_status "Python dependencies installed"

# Install Playwright browsers
print_header "Installing Playwright Browsers"
playwright install chromium
print_status "Playwright browsers installed"

# Setup directories
print_header "Setting up Project Structure"
mkdir -p results/screenshots
mkdir -p results/mobile_apps
mkdir -p logs
mkdir -p dist
print_status "Project directories created"

# Setup Shodan API key
print_header "Shodan API Configuration"
config_file="config/config.yaml"
if [[ -f "$config_file" ]]; then
    shodan_key=$(grep "api_key:" "$config_file" | head -1 | cut -d'"' -f2)
    if [[ "$shodan_key" == "YOUR_SHODAN_API_KEY_HERE" ]] || [[ -z "$shodan_key" ]]; then
        print_warning "Shodan API key not configured"
        echo "🔑 Option 1: Use our automated setup script"
        echo "   python3 get_shodan_key.py"
        echo ""
        echo "🔑 Option 2: Manual setup"
        echo "   1. Visit: https://account.shodan.io/register"
        echo "   2. Create free account"
        echo "   3. Get API key from: https://account.shodan.io/"
        echo ""

        read -p "Run automated setup now? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            print_info "Running automated Shodan API setup..."
            if python3 get_shodan_key.py; then
                print_status "Shodan API setup completed"
            else
                print_error "Automated setup failed"
                read -p "Enter your Shodan API key manually (or press Enter to skip): " shodan_key
                if [[ -n "$shodan_key" ]]; then
                    sed -i.bak "s/YOUR_SHODAN_API_KEY_HERE/$shodan_key/" "$config_file"
                    print_status "Shodan API key configured manually"
                fi
            fi
        else
            read -p "Enter your Shodan API key manually (or press Enter to skip): " shodan_key
            if [[ -n "$shodan_key" ]]; then
                sed -i.bak "s/YOUR_SHODAN_API_KEY_HERE/$shodan_key/" "$config_file"
                print_status "Shodan API key configured manually"
            else
                print_warning "Shodan API key not configured. Some features will be limited."
                echo "💡 You can run: python3 get_shodan_key.py"
            fi
        fi
    else
        print_status "Shodan API key already configured"
        # Test the key
        if python3 -c "import shodan; api = shodan.Shodan('$shodan_key'); print('✅ API key valid')" 2>/dev/null; then
            print_status "API key tested and working"
        else
            print_warning "API key may be invalid - run: python3 get_shodan_key.py"
        fi
    fi
else
    print_error "Config file not found: $config_file"
fi

# Setup Shodan CLI (optional)
print_header "Shodan CLI Setup (Optional)"
print_info "The Shodan CLI provides command-line access to Shodan"
print_info "This is optional - the Python library is already installed"
read -p "Install Shodan CLI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ -f "setup_shodan_cli.sh" ]]; then
        print_info "Running Shodan CLI setup..."
        bash setup_shodan_cli.sh
    else
        print_info "Installing Shodan CLI via pip..."
        pip3 install -U --user shodan
        print_status "Shodan CLI installed"
        print_info "Initialize with: shodan init YOUR_API_KEY"
        print_info "Or run: ./setup_shodan_cli.sh for full setup"
    fi
else
    print_info "Skipping Shodan CLI installation"
    print_info "You can install it later with: ./setup_shodan_cli.sh"
fi

# Install mobile app analysis tools
print_header "Installing Mobile App Analysis Tools"

# Install apktool (for Android APK analysis)
if ! command -v apktool &> /dev/null; then
    print_info "Installing apktool..."
    if [[ "$OS" == "linux" ]]; then
        wget -O /tmp/apktool.jar https://github.com/iBotPeaches/Apktool/releases/download/v2.8.1/apktool_2.8.1.jar
        sudo mv /tmp/apktool.jar /usr/local/bin/apktool.jar
        sudo chmod +x /usr/local/bin/apktool.jar

        # Create apktool script
        sudo tee /usr/local/bin/apktool > /dev/null << 'EOF'
#!/bin/bash
java -jar /usr/local/bin/apktool.jar "$@"
EOF
        sudo chmod +x /usr/local/bin/apktool
    elif [[ "$OS" == "macos" ]]; then
        brew install apktool
    fi
    print_status "apktool installed"
else
    print_status "apktool already installed"
fi

# Install JADX (for Android decompilation)
if ! command -v jadx &> /dev/null; then
    print_info "Installing JADX..."
    if [[ "$OS" == "linux" ]]; then
        wget -O /tmp/jadx.zip https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
        unzip -q /tmp/jadx.zip -d /tmp/
        sudo mv /tmp/jadx-1.4.7 /opt/jadx
        sudo ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx
        sudo ln -sf /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui
        rm -rf /tmp/jadx.zip /tmp/jadx-1.4.7
    elif [[ "$OS" == "macos" ]]; then
        brew install jadx
    fi
    print_status "JADX installed"
else
    print_status "JADX already installed"
fi

# Install scrcpy (for Android screen mirroring)
if ! command -v scrcpy &> /dev/null; then
    print_info "Installing scrcpy..."
    if [[ "$OS" == "linux" ]]; then
        install_package "scrcpy"
    elif [[ "$OS" == "macos" ]]; then
        brew install scrcpy
    fi
    print_status "scrcpy installed"
else
    print_status "scrcpy already installed"
fi

# Install mitmproxy (for network traffic analysis)
if ! command -v mitmproxy &> /dev/null; then
    print_info "Installing mitmproxy..."
    pip3 install mitmproxy
    print_status "mitmproxy installed"
else
    print_status "mitmproxy already installed"
fi

# Install Frida (for dynamic analysis)
if ! command -v frida &> /dev/null; then
    print_info "Installing Frida..."
    pip3 install frida-tools
    print_status "Frida installed"
else
    print_status "Frida already installed"
fi

# Create desktop shortcuts/scripts
print_header "Creating Launch Scripts"

# Create main launcher script
cat > casino_scanner.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Casino Scanner Pro
Comment=Casino Vulnerability Research Framework
Exec=python3 casino_scanner.py
Icon=applications-system
Terminal=true
Categories=Development;Security;
EOF

# Make scripts executable
chmod +x casino_scanner.py
chmod +x setup_casino_scanner.sh

# Create quick scan scripts for each region
for region in vietnam laos cambodia; do
    cat > scan_${region}.sh << EOF
#!/bin/bash
python3 casino_scanner.py --region $region
EOF
    chmod +x scan_${region}.sh
done

print_status "Launch scripts created"

# Final setup checks
print_header "Final Setup Checks"

# Check if all tools are available
tools=("python3" "pip3" "playwright" "apktool" "jadx" "scrcpy" "mitmproxy" "frida")
for tool in "${tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        print_status "$tool: Available"
    else
        print_warning "$tool: Not found"
    fi
done

# Check configurations
if [[ -f "config/config.yaml" ]]; then
    print_status "Configuration file: Found"
else
    print_error "Configuration file: Missing"
fi

if [[ -d "tools/" ]]; then
    print_status "Tools directory: Found"
else
    print_error "Tools directory: Missing"
fi

if [[ -d "browser_extension/" ]]; then
    print_status "Browser extension: Found"
else
    print_warning "Browser extension: Missing (optional)"
fi

# Create .env file template
if [[ ! -f ".env" ]]; then
    cat > .env << 'EOF'
# Casino Scanner Pro Environment Variables
# Copy this file and rename to .env, then fill in your values

# Shodan API Key (if not using config.yaml)
SHODAN_API_KEY=

# Browser settings
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000

# Mobile app analysis
ANDROID_SDK_PATH=
JAVA_HOME=

# Database settings (for future use)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=casino_scanner
DB_USER=
DB_PASSWORD=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/casino_scanner.log

# API Keys for various services
GOOGLE_PLAY_API_KEY=
APP_STORE_API_KEY=
VIRUSTOTAL_API_KEY=

# Custom settings
CUSTOM_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
SCAN_TIMEOUT=300
MAX_CONCURRENT_SCANS=5
EOF
    print_status ".env template created"
fi

# Success message
echo ""
echo "═══════════════════════════════════════════════"
print_status "CASINO SCANNER PRO 4.0 SETUP COMPLETE!"
echo "═══════════════════════════════════════════════"
echo ""
echo "🎯 Quick Start:"
echo "   • INSTANT RESULTS: python3 quick_casino_hunt.py"
echo "   • Full interface: python3 casino_scanner.py"
echo "   • Setup API key: python3 get_shodan_key.py"
echo ""
echo "🎰 Available Commands:"
echo "   • Interactive mode: python3 casino_scanner.py"
echo "   • Quick region scan: python3 casino_scanner.py --region vietnam"
echo "   • Single URL scan: python3 casino_scanner.py --url https://casino-site.com"
echo "   • INSTANT casino hunt: python3 quick_casino_hunt.py"
echo "   • Setup: ./setup_casino_scanner.sh"
echo ""
echo "🌐 Browser Extension:"
echo "   • Load browser_extension/ in Chrome/Firefox"
echo "   • Click extension icon on casino sites"
echo ""
echo "📱 Mobile App Analysis:"
echo "   • APK analysis: python3 casino_scanner.py (then select mobile analysis)"
echo "   • API discovery: Integrated into web scanning"
echo ""
echo "⚠️  Important:"
echo "   • Configure your Shodan API key in config/config.yaml"
echo "   • Get API keys from: https://account.shodan.io/"
echo "   • Use responsibly and follow local laws"
echo ""
echo "🎲 Happy hunting for casino vulnerabilities!"
echo ""
echo "═══════════════════════════════════════════════"
