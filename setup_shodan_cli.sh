#!/bin/bash
# Setup script for Shodan CLI installation and initialization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "🔍 SHODAN CLI SETUP"
    echo "═══════════════════════════════════════════════"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find pip command
find_pip() {
    if command_exists pip3; then
        echo "pip3"
    elif command_exists pip; then
        echo "pip"
    elif command_exists python3 -m pip; then
        echo "python3 -m pip"
    elif command_exists python -m pip; then
        echo "python -m pip"
    else
        echo ""
    fi
}

print_header

# Step 1: Check Python installation
print_info "Step 1: Checking Python installation..."
if ! command_exists python3 && ! command_exists python; then
    print_error "Python not found. Please install Python first."
    exit 1
fi
print_status "Python is installed"

# Step 2: Find and use pip
print_info "Step 2: Finding pip..."
PIP_CMD=$(find_pip)

if [[ -z "$PIP_CMD" ]]; then
    print_error "pip not found. Trying alternative installation methods..."
    
    # Try easy_install as fallback
    if command_exists easy_install; then
        print_info "Using easy_install to install Shodan CLI..."
        easy_install -U --user shodan
        PIP_CMD="easy_install"
    else
        print_error "Neither pip nor easy_install found."
        print_info "Please install pip first:"
        echo "   Ubuntu/Debian: sudo apt install python3-pip"
        echo "   macOS: python3 -m ensurepip --upgrade"
        exit 1
    fi
else
    print_status "Found pip: $PIP_CMD"
fi

# Step 3: Install Shodan CLI
print_info "Step 3: Installing Shodan CLI..."
if [[ "$PIP_CMD" == "easy_install" ]]; then
    # Already installed above
    print_status "Shodan CLI installed via easy_install"
else
    # Install with --user flag to avoid permission issues
    if $PIP_CMD install -U --user shodan; then
        print_status "Shodan CLI installed successfully"
    else
        print_error "Failed to install Shodan CLI"
        exit 1
    fi
fi

# Step 4: Verify installation
print_info "Step 4: Verifying installation..."
sleep 1  # Give system time to update PATH

# Check if shodan command is available
if command_exists shodan; then
    print_status "Shodan CLI command found"
else
    print_warning "shodan command not found in PATH"
    print_info "This is normal - you may need to restart your terminal"
    print_info "Or add ~/.local/bin to your PATH:"
    echo "   export PATH=\$PATH:~/.local/bin"
    echo ""
    print_info "Checking if shodan is installed in user directory..."
    
    # Check common locations
    if [[ -f ~/.local/bin/shodan ]]; then
        print_status "Found shodan at ~/.local/bin/shodan"
        print_info "Add to PATH: export PATH=\$PATH:~/.local/bin"
    elif [[ -f ~/Library/Python/*/bin/shodan ]]; then
        print_status "Found shodan in Python user bin directory"
    else
        print_warning "Could not locate shodan binary"
        print_info "Try closing and reopening your terminal, then run: shodan"
    fi
fi

# Step 5: Initialize Shodan CLI with API key
print_info "Step 5: Initializing Shodan CLI with API key..."

# Try to get API key from config file
CONFIG_FILE="config/config.yaml"
SHODAN_KEY=""

if [[ -f "$CONFIG_FILE" ]]; then
    # Try to extract API key from YAML
    SHODAN_KEY=$(grep -A 2 "shodan:" "$CONFIG_FILE" | grep "api_key:" | head -1 | sed -E 's/.*api_key:[[:space:]]*["'\'']?([^"'\'']+)["'\'']?.*/\1/' | tr -d ' ')
    
    if [[ "$SHODAN_KEY" == "YOUR_SHODAN_API_KEY_HERE" ]] || [[ -z "$SHODAN_KEY" ]]; then
        SHODAN_KEY=""
    fi
fi

if [[ -z "$SHODAN_KEY" ]]; then
    print_warning "No API key found in config file"
    print_info "You can:"
    echo "   1. Run: python3 get_shodan_key.py"
    echo "   2. Get key from: https://account.shodan.io/"
    echo "   3. Initialize manually: shodan init YOUR_API_KEY"
    echo ""
    read -p "Enter your Shodan API key now (or press Enter to skip): " SHODAN_KEY
fi

if [[ -n "$SHODAN_KEY" ]]; then
    # Try to initialize Shodan CLI
    if command_exists shodan; then
        if shodan init "$SHODAN_KEY" 2>/dev/null; then
            print_status "Shodan CLI initialized successfully"
        else
            print_warning "Failed to initialize via shodan command"
            print_info "You may need to restart terminal first, then run:"
            echo "   shodan init $SHODAN_KEY"
        fi
    else
        print_warning "shodan command not available yet"
        print_info "After restarting terminal, run:"
        echo "   shodan init $SHODAN_KEY"
    fi
else
    print_info "Skipping initialization. Run 'shodan init YOUR_API_KEY' later"
fi

# Step 6: Test installation
print_info "Step 6: Testing installation..."
if command_exists shodan; then
    echo ""
    print_status "Running 'shodan' command to show available subcommands:"
    shodan 2>&1 | head -20 || true
    echo ""
    print_status "Shodan CLI setup complete!"
else
    print_warning "Setup complete, but 'shodan' command not yet available"
    print_info "Next steps:"
    echo "   1. Close and reopen your terminal"
    echo "   2. Run: shodan"
    echo "   3. If still not found, add to PATH: export PATH=\$PATH:~/.local/bin"
    echo "   4. Initialize: shodan init YOUR_API_KEY"
fi

echo ""
print_info "For more information, visit: https://cli.shodan.io/"
echo ""

