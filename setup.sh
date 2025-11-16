#!/bin/bash
# Setup script for Casino Security Research Framework

echo "Setting up Casino Security Research Framework..."

# Create necessary directories
mkdir -p results/screenshots
mkdir -p logs
mkdir -p targets

# Create .gitkeep files
touch results/.gitkeep
touch results/screenshots/.gitkeep
touch logs/.gitkeep

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Create config from template if it doesn't exist
if [ ! -f config/config.yaml ]; then
    echo "Creating config/config.yaml from template..."
    cp config/config.yaml.template config/config.yaml 2>/dev/null || echo "Please create config/config.yaml manually"
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/config.yaml and add your Shodan API key"
echo "2. Add targets to targets/*.yaml files"
echo "3. Run: python main.py --region vietnam"

