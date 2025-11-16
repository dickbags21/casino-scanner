#!/usr/bin/env python3
"""
🎰 Get Your Shodan API Key - Casino Scanner Pro Setup Helper
"""

import os
import sys
import json
import webbrowser
from pathlib import Path

def print_header():
    print("🎰 CASINO SCANNER PRO - SHODAN API SETUP")
    print("=" * 50)

def print_step(step_num, title, description=""):
    print(f"\n🔥 STEP {step_num}: {title}")
    if description:
        print(f"   {description}")

def open_browser(url):
    """Open URL in default browser"""
    try:
        webbrowser.open(url)
        print("   🌐 Opened in your default browser")
    except:
        print(f"   📋 Please visit: {url}")

def main():
    print_header()

    print_step(1, "Visit Shodan Account Page",
               "You need to create a free Shodan account to get an API key")
    open_browser("https://account.shodan.io/register")

    print("\n   📝 Instructions:")
    print("   1. Click 'Register' and create a free account")
    print("   2. Verify your email address")
    print("   3. Login to your account")

    input("\n   ⏳ Press Enter when you've registered and logged in...")

    print_step(2, "Get Your API Key",
               "Navigate to your account settings to find your API key")
    open_browser("https://account.shodan.io/")

    print("\n   🔑 Finding your API key:")
    print("   1. Login to your Shodan account")
    print("   2. Go to: https://account.shodan.io/")
    print("   3. Look for 'API Key' or 'Show API Key' section")
    print("   4. Copy the API key (it looks like: abc123def456...)")

    api_key = input("\n   🔐 Paste your API key here: ").strip()

    if not api_key or len(api_key) < 10:
        print("❌ Invalid API key. Please try again.")
        return

    print_step(3, "Configure Casino Scanner Pro",
               "We'll update your configuration file")

    # Update config file
    config_path = Path("config/config.yaml")
    if config_path.exists():
        try:
            import yaml

            # Read current config
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}

            # Set API key
            config.setdefault('apis', {}).setdefault('shodan', {})['api_key'] = api_key

            # Write back
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            print("   ✅ API key saved to config/config.yaml")

        except Exception as e:
            print(f"   ❌ Error updating config: {e}")
            print(f"   📝 Manually add to config/config.yaml:")
            print(f"   apis:\n     shodan:\n       api_key: {api_key}")
    else:
        print("   ❌ Config file not found. Please run setup first.")

    print_step(4, "Test Your API Key",
               "Let's make sure everything works")

    try:
        import shodan

        # Test the API key
        api = shodan.Shodan(api_key)
        info = api.info()

        print("   ✅ API key is valid!"        print(f"   📊 Query credits remaining: {info.get('query_credits', 'Unknown')}")
        print(f"   🔍 Scan credits remaining: {info.get('scan_credits', 'Unknown')}")

        # Test a simple search
        print("   🧪 Testing search functionality...")
        results = api.search("apache", limit=1)
        if results.get('matches'):
            print(f"   ✅ Search works! Found {len(results['matches'])} result(s)")
        else:
            print("   ⚠️ Search returned no results (this is normal for new accounts)")

    except shodan.APIError as e:
        print(f"   ❌ API Error: {e}")
        print("   💡 Make sure your API key is correct and you have credits")
    except ImportError:
        print("   ❌ Shodan library not installed. Run: pip install shodan")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")

    print_step(5, "Ready to Hunt!",
               "Your Casino Scanner Pro is now configured")

    print("\n   🚀 Quick start commands:")
    print("   python3 casino_scanner.py                    # Interactive menu")
    print("   python3 casino_scanner.py --region vietnam   # Scan Vietnam casinos")
    print("   python3 gambling_app_discovery.py            # Find gambling apps")
    print("   ./setup_casino_scanner.sh                    # Full setup")

    print("\n   🎰 Happy casino vulnerability hunting!")
    print("   Remember: Use responsibly for authorized security research only!")

if __name__ == "__main__":
    main()
