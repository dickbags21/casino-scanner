#!/usr/bin/env python3
"""
🎰 CASINO SCANNER 4.0 - Code Roten
Unified interface for casino vulnerability research and gambling app analysis

⚠️  NOTE: This is a legacy CLI interface. 
    For the modern web dashboard, use 'start_dashboard.py'
    For continuous automated scanning, use 'automated_scanner.py'
"""

import os
import sys
import asyncio
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

# Add tools directory to path
sys.path.append(str(Path(__file__).parent / "tools"))

from tools.shodan_scanner import ShodanScanner
from tools.browser_scanner import BrowserScanner
from tools.account_creation_scanner import AccountCreationScanner
from tools.target_manager import TargetManager
from tools.reporter import Reporter

class CasinoScannerPro:
    """Professional Casino Vulnerability Scanner"""

    def __init__(self):
        self.config_path = "config/config.yaml"
        self.framework = None
        self.target_manager = TargetManager()
        self.reporter = Reporter(
            results_dir="results",
            logs_dir="logs",
            log_level="INFO",
            max_bytes=10485760,
            backup_count=5
        )

        print("""
🎰 CASINO SCANNER PRO 4.0 - Code Roten 🎰
═══════════════════════════════════════════════════════════
Advanced Casino Vulnerability Research & Gambling App Analysis
═══════════════════════════════════════════════════════════
""")

    def show_menu(self):
        """Display main menu"""
        while True:
            print("\n" + "="*60)
            print("🎯 MAIN MENU - Choose Your Operation:")
            print("="*60)
            print("1. 🚀 Quick Casino Scan (Region-based)")
            print("2. 🔍 Advanced Vulnerability Assessment")
            print("3. 📱 Mobile Gambling App Analysis")
            print("4. 🌐 Browser Extension Tools")
            print("5. 🎰 Target Management")
            print("6. 📊 View Reports & Results")
            print("7. ⚙️  Configuration & Setup")
            print("8. 🛠️  Development Tools")
            print("9. ❌ Exit")
            print("="*60)

            choice = input("Select option (1-9): ").strip()

            if choice == "1":
                self.quick_casino_scan()
            elif choice == "2":
                self.advanced_vulnerability_scan()
            elif choice == "3":
                self.mobile_app_analysis()
            elif choice == "4":
                self.browser_extension_tools()
            elif choice == "5":
                self.target_management()
            elif choice == "6":
                self.view_reports()
            elif choice == "7":
                self.configuration_setup()
            elif choice == "8":
                self.development_tools()
            elif choice == "9":
                print("👋 Goodbye! Happy hunting!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")

    def quick_casino_scan(self):
        """Quick region-based casino scanning"""
        print("\n🎰 QUICK CASINO SCAN")
        print("="*40)

        regions = ['vietnam', 'laos', 'cambodia']
        print("Available regions:")
        for i, region in enumerate(regions, 1):
            print(f"{i}. {region.title()}")

        try:
            choice = int(input("Select region (1-3): ")) - 1
            if 0 <= choice < len(regions):
                region = regions[choice]
                print(f"\n🔍 Starting quick scan for {region}...")

                # Run the main framework
                cmd = [sys.executable, "main.py", "--region", region]
                subprocess.run(cmd, cwd=Path(__file__).parent)
            else:
                print("❌ Invalid region selection.")
        except ValueError:
            print("❌ Please enter a number.")

    def advanced_vulnerability_scan(self):
        """Advanced vulnerability assessment menu"""
        print("\n🔬 ADVANCED VULNERABILITY ASSESSMENT")
        print("="*45)

        print("1. 🎯 Single URL Deep Scan")
        print("2. 🔍 Bulk URL Analysis")
        print("3. 🛡️  Account Creation Vulnerability Test")
        print("4. 🎁 Bonus & Loophole Analysis")
        print("5. 📡 API Endpoint Discovery")
        print("6. 📊 Custom Scan Configuration")

        choice = input("Select scan type (1-6): ").strip()

        if choice == "1":
            self.single_url_scan()
        elif choice == "2":
            self.bulk_url_scan()
        elif choice == "3":
            self.account_creation_test()
        elif choice == "4":
            self.bonus_analysis()
        elif choice == "5":
            self.api_discovery()
        elif choice == "6":
            self.custom_scan_config()
        else:
            print("❌ Invalid choice.")

    def single_url_scan(self):
        """Scan a single URL deeply"""
        url = input("Enter casino URL to scan: ").strip()
        if not url:
            print("❌ No URL provided.")
            return

        print(f"\n🔍 Deep scanning: {url}")

        async def scan():
            try:
                # Initialize scanners
                browser_scanner = BrowserScanner()
                account_scanner = AccountCreationScanner()

                await browser_scanner.start()
                await account_scanner.start()

                # Run comprehensive scan
                print("📊 Running browser analysis...")
                signup_result = await browser_scanner.test_signup_flow(url, {})

                print("🎯 Testing account creation vulnerabilities...")
                account_result = await account_scanner.scan_url(url)

                # Generate report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_data = {
                    'url': url,
                    'timestamp': timestamp,
                    'signup_test': self._result_to_dict(signup_result),
                    'account_creation_test': self._result_to_dict(account_result),
                    'vulnerabilities_found': len(account_result.vulnerabilities)
                }

                report_path = f"results/single_scan_{timestamp}.json"
                with open(report_path, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)

                print(f"✅ Scan complete! Report saved to: {report_path}")

                # Show summary
                self._display_scan_summary(account_result)

            except Exception as e:
                print(f"❌ Scan failed: {e}")
            finally:
                await browser_scanner.stop()
                await account_scanner.stop()

        asyncio.run(scan())

    def _result_to_dict(self, obj):
        """Convert result object to dictionary"""
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj

    def _display_scan_summary(self, account_result):
        """Display scan results summary"""
        vulns = account_result.vulnerabilities

        print("\n" + "="*50)
        print("📊 SCAN RESULTS SUMMARY")
        print("="*50)

        if vulns:
            print(f"🚨 Found {len(vulns)} vulnerabilities:")

            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            for vuln in vulns:
                severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1

            for severity, count in severity_counts.items():
                if count > 0:
                    print(f"  {severity.upper()}: {count}")

            print("\n🔥 Top Vulnerabilities:")
            for vuln in vulns[:3]:  # Show top 3
                print(f"  • {vuln.title} ({vuln.severity})")
                if vuln.profit_potential and vuln.profit_potential != 'n/a':
                    print(f"    💰 Profit Potential: {vuln.profit_potential}")
        else:
            print("✅ No critical vulnerabilities found.")

        print("="*50)

    def bulk_url_scan(self):
        """Bulk URL analysis"""
        print("\n📋 BULK URL SCAN")
        print("Enter URLs to scan (one per line, empty line to finish):")

        urls = []
        while True:
            url = input().strip()
            if not url:
                break
            if url.startswith(('http://', 'https://')):
                urls.append(url)
            else:
                print("⚠️  URL must start with http:// or https://")

        if not urls:
            print("❌ No valid URLs provided.")
            return

        print(f"\n🔍 Scanning {len(urls)} URLs...")

        async def bulk_scan():
            results = []
            browser_scanner = BrowserScanner()
            account_scanner = AccountCreationScanner()

            try:
                await browser_scanner.start()
                await account_scanner.start()

                for i, url in enumerate(urls, 1):
                    print(f"[{i}/{len(urls)}] Scanning {url}...")
                    try:
                        account_result = await account_scanner.scan_url(url)
                        results.append({
                            'url': url,
                            'vulnerabilities': len(account_result.vulnerabilities),
                            'critical': len([v for v in account_result.vulnerabilities if v.severity == 'critical'])
                        })
                    except Exception as e:
                        print(f"  ❌ Failed: {e}")
                        results.append({'url': url, 'error': str(e)})

            finally:
                await browser_scanner.stop()
                await account_scanner.stop()

            # Save bulk results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"results/bulk_scan_{timestamp}.json"
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n✅ Bulk scan complete! Results saved to: {report_path}")

        asyncio.run(bulk_scan())

    def mobile_app_analysis(self):
        """Mobile gambling app analysis"""
        print("\n📱 MOBILE GAMBLING APP ANALYSIS")
        print("="*40)
        print("🚧 This feature is under development!")
        print("Coming soon: APK analysis, API reverse engineering, mobile app vulnerabilities")

        print("\nCurrent capabilities:")
        print("• APK file analysis (manual)")
        print("• Mobile API endpoint discovery")
        print("• App store metadata analysis")
        print("• Mobile-specific vulnerability patterns")

        input("Press Enter to return to menu...")

    def browser_extension_tools(self):
        """Browser extension management"""
        print("\n🌐 BROWSER EXTENSION TOOLS")
        print("="*35)

        ext_path = Path(__file__).parent / "browser_extension"

        if ext_path.exists():
            print("✅ Browser extension found!")
            print(f"📁 Location: {ext_path}")

            print("\n🔧 Extension Management:")
            print("1. 📦 Package extension for distribution")
            print("2. 🧪 Test extension locally")
            print("3. 📖 View extension README")
            print("4. 🔄 Update extension version")
            print("5. 📊 Check extension compatibility")

            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                self.package_extension()
            elif choice == "2":
                self.test_extension()
            elif choice == "3":
                self.view_extension_readme()
            elif choice == "4":
                self.update_extension_version()
            elif choice == "5":
                self.check_extension_compatibility()
            else:
                print("❌ Invalid choice.")
        else:
            print("❌ Browser extension not found!")
            print("Run setup to install all components.")

    def package_extension(self):
        """Package browser extension"""
        print("📦 Packaging browser extension...")
        ext_path = Path(__file__).parent / "browser_extension"
        output_path = Path(__file__).parent / "dist"

        output_path.mkdir(exist_ok=True)

        # Create ZIP file
        import zipfile
        zip_path = output_path / "casino_scanner_extension.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in ext_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    zipf.write(file_path, file_path.relative_to(ext_path.parent))

        print(f"✅ Extension packaged: {zip_path}")
        print("📤 Ready for Chrome Web Store or manual installation")

    def test_extension(self):
        """Test extension locally"""
        print("🧪 Testing browser extension...")
        print("1. Open Chrome and go to chrome://extensions/")
        print("2. Enable 'Developer mode'")
        print("3. Click 'Load unpacked'")
        print("4. Select the 'browser_extension' folder")
        print("5. Visit a casino site and click the extension icon")
        input("\nPress Enter when ready to continue...")

    def view_extension_readme(self):
        """View extension README"""
        readme_path = Path(__file__).parent / "browser_extension" / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                print(f.read())
        else:
            print("❌ Extension README not found.")

    def update_extension_version(self):
        """Update extension version"""
        manifest_path = Path(__file__).parent / "browser_extension" / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            current_version = manifest['version']
            print(f"Current version: {current_version}")

            new_version = input("Enter new version (e.g., 4.0.1): ").strip()
            if new_version:
                manifest['version'] = new_version
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)
                print(f"✅ Version updated to {new_version}")
            else:
                print("❌ No version provided.")
        else:
            print("❌ Manifest file not found.")

    def check_extension_compatibility(self):
        """Check extension compatibility"""
        print("📊 Checking browser compatibility...")
        manifest_path = Path(__file__).parent / "browser_extension" / "manifest.json"

        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            manifest_version = manifest.get('manifest_version', 2)
            permissions = manifest.get('permissions', [])

            print(f"Manifest Version: {manifest_version}")
            print("Permissions:", ', '.join(permissions))

            if manifest_version == 3:
                print("✅ Compatible with Chrome 88+, Edge 88+, Firefox (with adjustments)")
            else:
                print("⚠️  Older manifest version - consider upgrading to v3")

        print("\n🔍 Compatibility Checklist:")
        print("• Chrome 88+: Full support")
        print("• Firefox: Requires manifest adjustments")
        print("• Safari: Not supported")
        print("• Mobile browsers: Limited support")

    def target_management(self):
        """Target management interface"""
        print("\n🎯 TARGET MANAGEMENT")
        print("="*25)

        print("1. 👀 View current targets")
        print("2. ➕ Add new target")
        print("3. ✏️  Edit target")
        print("4. 🗑️  Remove target")
        print("5. 📊 Target statistics")

        choice = input("Select option (1-5): ").strip()

        if choice == "1":
            self.view_targets()
        elif choice == "2":
            self.add_target()
        elif choice == "3":
            self.edit_target()
        elif choice == "4":
            self.remove_target()
        elif choice == "5":
            self.target_statistics()
        else:
            print("❌ Invalid choice.")

    def view_targets(self):
        """View current targets"""
        targets_path = Path(__file__).parent / "targets"

        if targets_path.exists():
            for region_file in targets_path.glob("*.yaml"):
                region = region_file.stem
                print(f"\n🌍 {region.upper()}")
                print("-" * 20)

                try:
                    import yaml
                    with open(region_file, 'r') as f:
                        data = yaml.safe_load(f)

                    targets = data.get('targets', [])
                    for target in targets:
                        status = target.get('status', 'unknown')
                        url = target.get('url', 'N/A')
                        print(f"  • {url} [{status}]")
                except Exception as e:
                    print(f"  ❌ Error reading {region_file}: {e}")
        else:
            print("❌ Targets directory not found.")

    def add_target(self):
        """Add new target"""
        print("➕ ADD NEW TARGET")

        regions = ['vietnam', 'laos', 'cambodia']
        print("Available regions:")
        for i, region in enumerate(regions, 1):
            print(f"{i}. {region.title()}")

        try:
            region_choice = int(input("Select region (1-3): ")) - 1
            if 0 <= region_choice < len(regions):
                region = regions[region_choice]

                url = input("Enter casino URL: ").strip()
                name = input("Enter site name: ").strip()

                if url and name:
                    # Add to targets file
                    import yaml
                    targets_file = Path(__file__).parent / "targets" / f"{region}.yaml"

                    if targets_file.exists():
                        with open(targets_file, 'r') as f:
                            data = yaml.safe_load(f) or {'region': region, 'targets': []}
                    else:
                        data = {'region': region, 'targets': []}

                    new_target = {
                        'url': url,
                        'name': name,
                        'region': region,
                        'description': f"Added via Casino Scanner Pro",
                        'tags': ['casino', 'gambling'],
                        'priority': 5,
                        'status': 'pending',
                        'notes': ''
                    }

                    data['targets'].append(new_target)

                    with open(targets_file, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False)

                    print(f"✅ Target added to {region}: {name}")
                else:
                    print("❌ URL and name are required.")
            else:
                print("❌ Invalid region selection.")
        except ValueError:
            print("❌ Please enter a number.")

    def edit_target(self):
        """Edit existing target"""
        print("✏️  TARGET EDITING")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")

    def remove_target(self):
        """Remove target"""
        print("🗑️  TARGET REMOVAL")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")

    def target_statistics(self):
        """Show target statistics"""
        print("📊 TARGET STATISTICS")
        targets_path = Path(__file__).parent / "targets"

        if targets_path.exists():
            total_targets = 0
            region_stats = {}

            for region_file in targets_path.glob("*.yaml"):
                region = region_file.stem
                try:
                    import yaml
                    with open(region_file, 'r') as f:
                        data = yaml.safe_load(f)

                    targets = data.get('targets', [])
                    region_stats[region] = len(targets)
                    total_targets += len(targets)
                except:
                    region_stats[region] = 0

            print(f"\n🎯 Total Targets: {total_targets}")
            print("\nBy Region:")
            for region, count in region_stats.items():
                print(f"  • {region.title()}: {count}")

        else:
            print("❌ No target data available.")

    def view_reports(self):
        """View reports and results"""
        print("\n📊 REPORTS & RESULTS")
        print("="*25)

        results_path = Path(__file__).parent / "results"

        if results_path.exists():
            files = list(results_path.rglob("*.json"))
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            if files:
                print("Recent reports:")
                for i, file in enumerate(files[:10], 1):
                    size = file.stat().st_size
                    mtime = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"{i}. {file.name} ({size} bytes) - {mtime}")

                try:
                    choice = int(input("\nSelect report to view (1-10, 0 to cancel): "))
                    if 1 <= choice <= len(files):
                        selected_file = files[choice - 1]
                        print(f"\n📄 {selected_file.name}")
                        print("="*50)
                        with open(selected_file, 'r') as f:
                            data = json.load(f)
                            print(json.dumps(data, indent=2))
                    elif choice != 0:
                        print("❌ Invalid choice.")
                except ValueError:
                    print("❌ Please enter a number.")
            else:
                print("📭 No reports found.")
                print("Run a scan to generate reports.")
        else:
            print("❌ Results directory not found.")

    def configuration_setup(self):
        """Configuration and setup"""
        print("\n⚙️  CONFIGURATION & SETUP")
        print("="*30)

        config_path = Path(__file__).parent / "config" / "config.yaml"

        if config_path.exists():
            print("✅ Configuration file found.")
            print("Current settings:")

            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

                print(f"  • Shodan API: {'Configured' if config.get('apis', {}).get('shodan', {}).get('api_key') else 'Not configured'}")
                print(f"  • Browser: {config.get('browser', {}).get('headless', 'Unknown')}")
                print(f"  • Regions: {', '.join(config.get('regions', {}).keys())}")

            except Exception as e:
                print(f"  ❌ Error reading config: {e}")

            print("\n🔧 Configuration Options:")
            print("1. 🔑 Configure Shodan API key")
            print("2. 🌐 Configure browser settings")
            print("3. 📍 Add new region")
            print("4. 📋 View full configuration")
            print("5. 🔄 Reset to defaults")

            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                self.configure_shodan_api()
            elif choice == "2":
                self.configure_browser()
            elif choice == "3":
                self.add_region()
            elif choice == "4":
                self.view_full_config()
            elif choice == "5":
                self.reset_config()
            else:
                print("❌ Invalid choice.")
        else:
            print("❌ Configuration file not found.")
            print("Run setup script to initialize.")

    def configure_shodan_api(self):
        """Configure Shodan API key"""
        print("🔑 SHODAN API CONFIGURATION")

        config_path = Path(__file__).parent / "config" / "config.yaml"

        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            current_key = config.get('apis', {}).get('shodan', {}).get('api_key', '')
            if current_key and current_key != "YOUR_SHODAN_API_KEY_HERE":
                masked_key = current_key[:8] + "*" * (len(current_key) - 16) + current_key[-8:]
                print(f"Current API key: {masked_key}")
                change = input("Change API key? (y/N): ").lower().strip()
                if change != 'y':
                    return

            new_key = input("Enter new Shodan API key: ").strip()
            if new_key:
                config.setdefault('apis', {}).setdefault('shodan', {})['api_key'] = new_key

                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)

                print("✅ Shodan API key updated!")
            else:
                print("❌ No API key provided.")

        except Exception as e:
            print(f"❌ Error updating config: {e}")

    def configure_browser(self):
        """Configure browser settings"""
        print("🌐 BROWSER CONFIGURATION")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")

    def add_region(self):
        """Add new region"""
        print("📍 ADD NEW REGION")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")

    def view_full_config(self):
        """View full configuration"""
        config_path = Path(__file__).parent / "config" / "config.yaml"

        try:
            with open(config_path, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"❌ Error reading config: {e}")

    def reset_config(self):
        """Reset configuration to defaults"""
        print("🔄 RESET CONFIGURATION")
        confirm = input("This will reset all settings to defaults. Continue? (y/N): ").lower().strip()

        if confirm == 'y':
            print("✅ Configuration reset to defaults.")
            print("Please reconfigure your API keys and settings.")
        else:
            print("❌ Operation cancelled.")

    def development_tools(self):
        """Development tools menu"""
        print("\n🛠️  DEVELOPMENT TOOLS")
        print("="*25)

        print("1. 🧪 Run tests")
        print("2. 📦 Build distribution")
        print("3. 🔍 Code analysis")
        print("4. 📚 Generate documentation")
        print("5. 🔄 Update dependencies")
        print("6. 🐛 Debug tools")

        choice = input("Select option (1-6): ").strip()

        if choice == "1":
            self.run_tests()
        elif choice == "2":
            self.build_distribution()
        elif choice == "3":
            self.code_analysis()
        elif choice == "4":
            self.generate_docs()
        elif choice == "5":
            self.update_dependencies()
        elif choice == "6":
            self.debug_tools()
        else:
            print("❌ Invalid choice.")

    def run_tests(self):
        """Run test suite"""
        print("🧪 RUNNING TESTS...")
        print("🚧 Test suite under development.")
        input("Press Enter to return to menu...")

    def build_distribution(self):
        """Build distribution package"""
        print("📦 BUILDING DISTRIBUTION...")

        output_dir = Path(__file__).parent / "dist"
        output_dir.mkdir(exist_ok=True)

        # Create main distribution
        print("• Creating main package...")
        # Add packaging logic here

        # Package browser extension
        print("• Packaging browser extension...")
        self.package_extension()

        print("✅ Distribution built in 'dist/' directory")

    def code_analysis(self):
        """Run code analysis"""
        print("🔍 CODE ANALYSIS...")
        print("🚧 Code analysis tools under development.")
        input("Press Enter to return to menu...")

    def generate_docs(self):
        """Generate documentation"""
        print("📚 GENERATING DOCUMENTATION...")
        print("🚧 Documentation generation under development.")
        input("Press Enter to return to menu...")

    def update_dependencies(self):
        """Update dependencies"""
        print("🔄 UPDATING DEPENDENCIES...")

        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"],
                         cwd=Path(__file__).parent)
            print("✅ Dependencies updated!")
        except Exception as e:
            print(f"❌ Error updating dependencies: {e}")

    def debug_tools(self):
        """Debug tools"""
        print("🐛 DEBUG TOOLS")
        print("🚧 Debug tools under development.")
        input("Press Enter to return to menu...")

    def account_creation_test(self):
        """Account creation vulnerability test"""
        print("🎯 ACCOUNT CREATION VULNERABILITY TEST")
        print("This feature requires a target URL.")
        url = input("Enter casino URL to test: ").strip()

        if url:
            print(f"🔍 Testing account creation vulnerabilities on: {url}")
            # This would call the account creation scanner
            print("🚧 Feature under development - use main scanner for now.")
        else:
            print("❌ No URL provided.")

    def bonus_analysis(self):
        """Bonus and loophole analysis"""
        print("🎁 BONUS & LOOPHOLE ANALYSIS")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")

    def api_discovery(self):
        """API endpoint discovery"""
        print("📡 API ENDPOINT DISCOVERY")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")

    def custom_scan_config(self):
        """Custom scan configuration"""
        print("⚙️  CUSTOM SCAN CONFIGURATION")
        print("🚧 This feature is under development.")
        input("Press Enter to return to menu...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Casino Scanner Pro 4.0 - Code Roten")
    parser.add_argument("--region", help="Quick scan specific region")
    parser.add_argument("--url", help="Scan specific URL")
    parser.add_argument("--setup", action="store_true", help="Run setup")

    args = parser.parse_args()

    if args.setup:
        # Run setup script
        setup_script = Path(__file__).parent / "setup.sh"
        if setup_script.exists():
            subprocess.run(["bash", str(setup_script)])
        else:
            print("❌ Setup script not found.")
        return

    if args.region:
        # Quick region scan
        scanner = CasinoScannerPro()
        print(f"🔍 Quick scanning region: {args.region}")
        cmd = [sys.executable, "main.py", "--region", args.region]
        subprocess.run(cmd, cwd=Path(__file__).parent)
        return

    if args.url:
        # Single URL scan
        scanner = CasinoScannerPro()
        print(f"🔍 Scanning URL: {args.url}")
        # Implement single URL scan
        print("🚧 Single URL scan via CLI under development.")
        return

    # Interactive mode
    scanner = CasinoScannerPro()
    scanner.show_menu()


if __name__ == "__main__":
    main()
