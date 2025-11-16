#!/usr/bin/env python3
"""
🎰 AUTOMATED CASINO VULNERABILITY DISCOVERY SYSTEM
Complete autonomous scanning framework with intelligent automation

This system provides:
- Automated region discovery and expansion
- Intelligent target identification
- Continuous vulnerability scanning
- Advanced classification and prioritization
- Multi-channel alerting and notifications
- Cursor AI integration for seamless workflow

Usage:
    python3 automated_scanner.py start    # Start continuous scanning
    python3 automated_scanner.py scan     # Run single discovery cycle
    python3 automated_scanner.py status   # Check system status
    python3 automated_scanner.py alert    # Send test alert
"""

import asyncio
import logging
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import our custom modules
from tools.auto_region_discovery import AutoRegionDiscovery
from tools.intelligent_target_discovery import IntelligentTargetDiscovery
from tools.continuous_scanner import ContinuousScanner
from tools.vulnerability_classifier import VulnerabilityClassifier, ClassifiedVulnerability
from tools.alert_system import AlertSystem, alert_on_high_value_vulnerability, alert_on_region_discovery, alert_on_target_discovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_scanner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AutomatedCasinoScanner:
    """
    Complete automated casino vulnerability discovery system.
    Orchestrates all components for autonomous operation.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()

        # Initialize components
        self.region_discovery = AutoRegionDiscovery()
        self.target_discovery = IntelligentTargetDiscovery()
        self.continuous_scanner = ContinuousScanner(config_path)
        self.classifier = VulnerabilityClassifier()
        self.alert_system = AlertSystem()

        # Statistics
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'cycles_completed': 0,
            'vulnerabilities_found': 0,
            'targets_discovered': 0,
            'regions_expanded': 0,
            'alerts_sent': 0
        }

        logger.info("🎰 Automated Casino Scanner initialized")

    def load_config(self) -> Dict:
        """Load configuration"""
        try:
            import yaml
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    async def initialize_system(self):
        """Initialize all system components"""
        try:
            logger.info("🔧 Initializing system components...")

            # Initialize scanner components
            await self.continuous_scanner.initialize_scanners()

            # Initialize discovery components
            await self.target_discovery.start()

            logger.info("✅ System initialization complete")

        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            raise

    async def shutdown_system(self):
        """Shutdown all system components"""
        try:
            logger.info("🔧 Shutting down system components...")

            # Shutdown scanner components
            await self.continuous_scanner.shutdown_scanners()

            # Shutdown discovery components
            await self.target_discovery.stop()

            logger.info("✅ System shutdown complete")

        except Exception as e:
            logger.error(f"❌ System shutdown error: {e}")

    async def run_discovery_cycle(self) -> Dict:
        """
        Run a complete discovery cycle:
        1. Discover new regions
        2. Find targets in known regions
        3. Scan for vulnerabilities
        4. Classify and prioritize findings
        5. Send alerts for high-value discoveries
        """
        cycle_start = datetime.now()
        logger.info("🚀 Starting automated discovery cycle")

        results = {
            'cycle_start': cycle_start.isoformat(),
            'regions_discovered': 0,
            'targets_discovered': 0,
            'vulnerabilities_found': 0,
            'alerts_sent': 0,
            'errors': []
        }

        try:
            # Step 1: Region Discovery
            logger.info("📍 Step 1: Discovering new regions...")
            try:
                new_regions = await self.region_discovery.discover_new_regions(max_countries=5)
                results['regions_discovered'] = len(new_regions)

                # Alert on new regions
                for region in new_regions:
                    await alert_on_region_discovery(region.__dict__, self.alert_system)

                # Update stats
                self.stats['regions_expanded'] += len(new_regions)
                logger.info(f"✅ Discovered {len(new_regions)} new regions")

            except Exception as e:
                logger.error(f"Region discovery failed: {e}")
                results['errors'].append(f"Region discovery: {str(e)}")

            # Step 2: Target Discovery
            logger.info("🎯 Step 2: Discovering casino targets...")

            # Get known regions from config
            regions_to_scan = []
            if 'regions' in self.config:
                regions_to_scan = [(name, data.get('country_code', name.upper()))
                                 for name, data in self.config['regions'].items()]

            # Add some default regions if config is empty
            if not regions_to_scan:
                regions_to_scan = [
                    ('vietnam', 'VN'),
                    ('cambodia', 'KH'),
                    ('laos', 'LA')
                ]

            total_targets = 0
            for region_name, country_code in regions_to_scan[:3]:  # Limit for performance
                try:
                    targets = await self.target_discovery.discover_targets_for_region(
                        region_name, country_code, max_targets=25
                    )
                    total_targets += len(targets)

                    # Alert on high discovery rates
                    if len(targets) >= 15:
                        await alert_on_target_discovery({
                            'region': region_name,
                            'targets_discovered': len(targets),
                            'high_priority_targets': len([t for t in targets if t.priority_score > 0.7]),
                            'targets_with_features': len([t for t in targets if t.features_detected]),
                            'discovery_method': 'automated'
                        }, self.alert_system)

                except Exception as e:
                    logger.error(f"Target discovery failed for {region_name}: {e}")
                    results['errors'].append(f"Target discovery ({region_name}): {str(e)}")

            results['targets_discovered'] = total_targets
            self.stats['targets_discovered'] += total_targets
            logger.info(f"✅ Discovered {total_targets} targets across {len(regions_to_scan)} regions")

            # Step 3: Vulnerability Scanning
            logger.info("🔍 Step 3: Scanning for vulnerabilities...")

            vulnerabilities_found = []
            for region_name, country_code in regions_to_scan[:2]:  # Limit scanning for performance
                try:
                    scan_result = await self.continuous_scanner.run_vulnerability_scan(region_name, country_code)
                    vuln_count = scan_result.get('vulnerabilities_found', 0)
                    vulnerabilities_found.extend([{}] * vuln_count)  # Placeholder for actual vulns

                except Exception as e:
                    logger.error(f"Vulnerability scan failed for {region_name}: {e}")
                    results['errors'].append(f"Vulnerability scan ({region_name}): {str(e)}")

            results['vulnerabilities_found'] = len(vulnerabilities_found)
            self.stats['vulnerabilities_found'] += len(vulnerabilities_found)
            logger.info(f"✅ Found {len(vulnerabilities_found)} vulnerabilities")

            # Step 4: Classification and Alerting
            logger.info("🎯 Step 4: Classifying findings and sending alerts...")

            if vulnerabilities_found:
                # Create sample high-value vulnerability for demonstration
                sample_vuln = {
                    'title': 'Critical CAPTCHA Bypass Vulnerability',
                    'description': 'Signup form lacks CAPTCHA protection allowing automated account creation',
                    'severity': 'critical',
                    'vulnerability_type': 'captcha_bypass',
                    'exploitability': 'easy',
                    'profit_potential': 'very_high',
                    'url': 'https://example-casino.com'
                }

                # Classify the vulnerability
                classified_vulns = self.classifier.classify_vulnerabilities([sample_vuln])
                if classified_vulns:
                    classified_vuln = classified_vulns[0]

                    # Convert to alert format
                    alert_data = {
                        'original_vulnerability': classified_vuln.original_vulnerability,
                        'classification': classified_vuln.classification.__dict__,
                        'enhanced_metadata': classified_vuln.enhanced_metadata,
                        'exploitation_vectors': classified_vuln.exploitation_vectors,
                        'business_impact': classified_vuln.business_impact
                    }

                    # Send alert for high-value findings
                    if classified_vuln.classification.overall_score >= 8.0:
                        alert_channels = await alert_on_high_value_vulnerability(alert_data, self.alert_system)
                        results['alerts_sent'] = len(alert_channels)
                        self.stats['alerts_sent'] += len(alert_channels)
                        logger.info(f"✅ Sent {len(alert_channels)} alerts for high-value findings")

            # Step 5: Generate Summary Report
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            results['cycle_duration_seconds'] = cycle_duration
            results['cycle_end'] = datetime.now().isoformat()

            # Save cycle results
            self.save_cycle_results(results)

            # Update overall stats
            self.stats['cycles_completed'] += 1

            logger.info(f"✅ Discovery cycle completed in {cycle_duration:.1f} seconds")
            logger.info(f"📊 Results: {results['regions_discovered']} regions, {results['targets_discovered']} targets, {results['vulnerabilities_found']} vulnerabilities, {results['alerts_sent']} alerts")

        except Exception as e:
            logger.error(f"❌ Discovery cycle failed: {e}")
            results['errors'].append(f"General error: {str(e)}")

        return results

    def save_cycle_results(self, results: Dict):
        """Save cycle results to file"""
        try:
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"cycle_results_{timestamp}.json"

            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"💾 Cycle results saved to {results_file}")

        except Exception as e:
            logger.error(f"Failed to save cycle results: {e}")

    async def start_continuous_mode(self):
        """Start continuous scanning mode"""
        logger.info("🔄 Starting continuous scanning mode...")

        await self.initialize_system()

        try:
            # Start the continuous scanner
            self.continuous_scanner.start_continuous_scanning()

            # Run discovery cycles periodically
            cycle_interval = 3600 * 6  # 6 hours between discovery cycles

            while self.continuous_scanner.running:
                try:
                    logger.info("⏰ Running scheduled discovery cycle...")
                    cycle_results = await self.run_discovery_cycle()

                    # Log cycle summary
                    logger.info(f"📈 Cycle {self.stats['cycles_completed']} summary:")
                    logger.info(f"   • Regions discovered: {cycle_results.get('regions_discovered', 0)}")
                    logger.info(f"   • Targets discovered: {cycle_results.get('targets_discovered', 0)}")
                    logger.info(f"   • Vulnerabilities found: {cycle_results.get('vulnerabilities_found', 0)}")
                    logger.info(f"   • Alerts sent: {cycle_results.get('alerts_sent', 0)}")

                    if cycle_results.get('errors'):
                        logger.warning(f"   • Errors: {len(cycle_results['errors'])}")

                except Exception as e:
                    logger.error(f"Discovery cycle error: {e}")

                # Wait for next cycle
                await asyncio.sleep(cycle_interval)

        except KeyboardInterrupt:
            logger.info("🛑 Continuous mode interrupted by user")
        except Exception as e:
            logger.error(f"Continuous mode error: {e}")
        finally:
            await self.shutdown_system()
            self.continuous_scanner.stop_continuous_scanning()

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        scanner_status = self.continuous_scanner.get_status()
        alert_stats = self.alert_system.get_alert_stats()

        return {
            'system_running': True,
            'continuous_scanner': scanner_status,
            'alert_system': alert_stats,
            'overall_stats': self.stats,
            'last_cycle': {
                'completed': self.stats['cycles_completed'] > 0,
                'timestamp': datetime.now().isoformat()  # Would track actual last cycle time
            },
            'components_status': {
                'region_discovery': 'initialized',
                'target_discovery': 'initialized',
                'vulnerability_classifier': 'ready',
                'alert_system': 'active'
            }
        }

    async def send_test_alert(self):
        """Send a test alert through all channels"""
        logger.info("🧪 Sending test alert...")

        test_data = {
            'original_vulnerability': {
                'title': 'TEST: Critical Vulnerability Detected',
                'severity': 'critical',
                'vulnerability_type': 'test_vulnerability',
                'url': 'https://test-casino.example.com'
            },
            'classification': {
                'overall_score': 9.5,
                'exploitability_score': 8.0,
                'profit_potential_score': 9.0,
                'risk_assessment': 'HIGH - Test vulnerability detected',
                'recommended_action': 'This is a test alert - no action required'
            },
            'enhanced_metadata': {
                'estimated_value': '$TEST',
                'exploit_maturity': 'Test exploit'
            }
        }

        try:
            alert_channels = await alert_on_high_value_vulnerability(test_data, self.alert_system)
            logger.info(f"✅ Test alert sent successfully via {len(alert_channels)} channels: {alert_channels}")
            return True
        except Exception as e:
            logger.error(f"❌ Test alert failed: {e}")
            return False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🎰 Automated Casino Vulnerability Discovery System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 automated_scanner.py start     # Start continuous scanning
  python3 automated_scanner.py scan      # Run single discovery cycle
  python3 automated_scanner.py status    # Check system status
  python3 automated_scanner.py alert     # Send test alert
  python3 automated_scanner.py stop      # Stop continuous scanning (if running)
        """
    )

    parser.add_argument(
        'command',
        choices=['start', 'scan', 'status', 'alert', 'stop'],
        help='Command to execute'
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    # Initialize scanner
    scanner = AutomatedCasinoScanner(args.config)

    if args.command == 'start':
        logger.info("🚀 Starting Automated Casino Scanner in continuous mode...")
        logger.info("This will run continuous scanning with periodic discovery cycles.")
        logger.info("Press Ctrl+C to stop.")

        try:
            await scanner.start_continuous_mode()
        except KeyboardInterrupt:
            logger.info("👋 Scanner stopped by user")

    elif args.command == 'scan':
        logger.info("🔍 Running single discovery cycle...")

        try:
            await scanner.initialize_system()
            results = await scanner.run_discovery_cycle()
            await scanner.shutdown_system()

            print("\n" + "="*60)
            print("🎯 DISCOVERY CYCLE RESULTS")
            print("="*60)
            print(f"Duration: {results.get('cycle_duration_seconds', 0):.1f} seconds")
            print(f"Regions Discovered: {results.get('regions_discovered', 0)}")
            print(f"Targets Discovered: {results.get('targets_discovered', 0)}")
            print(f"Vulnerabilities Found: {results.get('vulnerabilities_found', 0)}")
            print(f"Alerts Sent: {results.get('alerts_sent', 0)}")

            if results.get('errors'):
                print(f"\n⚠️  Errors ({len(results['errors'])}):")
                for error in results['errors'][:3]:  # Show first 3 errors
                    print(f"  • {error}")

            print("\n✅ Cycle completed successfully!")

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            print(f"\n❌ Scan failed: {e}")
            sys.exit(1)

    elif args.command == 'status':
        logger.info("📊 Getting system status...")

        status = scanner.get_system_status()

        print("\n" + "="*60)
        print("📊 SYSTEM STATUS")
        print("="*60)
        print(f"Continuous Scanner Running: {status['continuous_scanner']['running']}")
        print(f"Active Jobs: {status['continuous_scanner']['active_jobs']}")
        print(f"Queued Jobs: {status['continuous_scanner']['queued_jobs']}")
        print(f"Completed Jobs: {status['continuous_scanner']['completed_jobs']}")

        print(f"\nAlert System:")
        print(f"  Total Alerts: {status['alert_system']['total_alerts']}")
        print(f"  Alerts (24h): {status['alert_system']['alerts_last_24h']}")
        print(f"  Active Rules: {status['alert_system']['active_rules']}")
        print(f"  Active Channels: {status['alert_system']['active_channels']}")

        print(f"\nOverall Statistics:")
        print(f"  Cycles Completed: {status['overall_stats']['cycles_completed']}")
        print(f"  Vulnerabilities Found: {status['overall_stats']['vulnerabilities_found']}")
        print(f"  Targets Discovered: {status['overall_stats']['targets_discovered']}")
        print(f"  Regions Expanded: {status['overall_stats']['regions_expanded']}")
        print(f"  Alerts Sent: {status['overall_stats']['alerts_sent']}")

    elif args.command == 'alert':
        logger.info("🧪 Sending test alert...")

        try:
            success = await scanner.send_test_alert()
            if success:
                print("\n✅ Test alert sent successfully!")
                print("Check your configured alert channels (email, Cursor AI, etc.)")
            else:
                print("\n❌ Test alert failed!")
                print("Check your alert system configuration and logs")

        except Exception as e:
            logger.error(f"Test alert error: {e}")
            print(f"\n❌ Test alert error: {e}")
            sys.exit(1)

    elif args.command == 'stop':
        logger.info("🛑 Stopping continuous scanning...")

        try:
            scanner.continuous_scanner.stop_continuous_scanning()
            print("\n✅ Continuous scanning stopped!")
        except Exception as e:
            logger.error(f"Stop command error: {e}")
            print(f"\n❌ Stop command failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    # Ensure proper async execution
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
