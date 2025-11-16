"""
Continuous Scanning Workflow System
Automated, autonomous vulnerability scanning with intelligent scheduling and reporting
"""

import asyncio
import logging
import json
import yaml  # pyright: ignore[reportMissingModuleSource]
import schedule
import time
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import threading
import sys
import os

# Import our custom modules
from auto_region_discovery import AutoRegionDiscovery
from intelligent_target_discovery import IntelligentTargetDiscovery
from account_creation_scanner import AccountCreationScanner
from browser_scanner import BrowserScanner
from shodan_scanner import ShodanScanner
from reporter import Reporter, ScanReport

logger = logging.getLogger(__name__)


@dataclass
class ScanJob:
    """Represents a scanning job in the queue"""
    job_id: str
    region: str
    country_code: str
    priority: int  # 1-10, higher = more important
    job_type: str  # 'discovery', 'vulnerability_scan', 'target_update'
    scheduled_time: datetime
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


@dataclass
class ContinuousScanConfig:
    """Configuration for continuous scanning"""
    enabled: bool = True
    scan_interval_hours: int = 24  # How often to run full scans
    discovery_interval_hours: int = 168  # Weekly target discovery
    region_expansion_interval_days: int = 7  # Weekly region expansion
    max_concurrent_scans: int = 3
    scan_timeout_minutes: int = 60
    auto_discovery_enabled: bool = True
    auto_region_expansion_enabled: bool = True
    alert_on_high_findings: bool = True
    report_generation_enabled: bool = True
    cleanup_old_reports_days: int = 30


class ContinuousScanner:
    """
    Continuous scanning orchestration system that manages automated vulnerability discovery,
    target scanning, and reporting with intelligent scheduling.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()

        # Initialize components
        self.region_discovery = AutoRegionDiscovery()
        self.target_discovery = IntelligentTargetDiscovery()
        self.account_scanner = None
        self.browser_scanner = None
        self.shodan_scanner = None
        self.reporter = Reporter(
            results_dir=self.config.get('output', {}).get('results_dir', 'results'),
            logs_dir=self.config.get('output', {}).get('logs_dir', 'logs'),
            log_level=self.config.get('logging', {}).get('level', 'INFO'),
            max_bytes=self.config.get('logging', {}).get('max_bytes', 10485760),
            backup_count=self.config.get('logging', {}).get('backup_count', 5)
        )

        # Scan configuration
        self.scan_config = ContinuousScanConfig()

        # Job management
        self.job_queue: List[ScanJob] = []
        self.active_jobs: Dict[str, ScanJob] = {}
        self.completed_jobs: List[ScanJob] = []
        self.job_counter = 0

        # Control flags
        self.running = False
        self.scan_thread: Optional[threading.Thread] = None

        # Statistics
        self.stats = {
            'total_scans': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'vulnerabilities_found': 0,
            'targets_discovered': 0,
            'regions_expanded': 0,
            'start_time': datetime.now().isoformat()
        }

        logger.info("Continuous Scanner initialized")

    def load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    async def initialize_scanners(self):
        """Initialize all scanner components"""
        try:
            # Initialize browser-based scanners
            await self.target_discovery.start()

            # Initialize account creation scanner
            browser_config = self.config.get('browser', {})
            self.account_scanner = AccountCreationScanner(
                headless=browser_config.get('headless', True),
                timeout=browser_config.get('timeout', 30000),
                max_attempts=self.config.get('testing', {}).get('signup_flow', {}).get('max_attempts', 10),
                user_agent=browser_config.get('user_agent')
            )
            await self.account_scanner.start()

            # Initialize browser scanner
            self.browser_scanner = BrowserScanner(
                headless=browser_config.get('headless', True),
                timeout=browser_config.get('timeout', 30000),
                user_agent=browser_config.get('user_agent'),
                viewport=browser_config.get('viewport'),
                screenshot_dir=self.config.get('output', {}).get('screenshot_dir', 'results/screenshots')
            )
            await self.browser_scanner.start()

            # Initialize Shodan scanner
            shodan_key = self.config.get('apis', {}).get('shodan', {}).get('api_key')
            if shodan_key and shodan_key != "YOUR_SHODAN_API_KEY_HERE":
                self.shodan_scanner = ShodanScanner(
                    api_key=shodan_key,
                    rate_limit=self.config.get('apis', {}).get('shodan', {}).get('rate_limit', 10)
                )

            logger.info("All scanners initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize scanners: {e}")
            raise

    async def shutdown_scanners(self):
        """Shutdown all scanner components"""
        try:
            await self.target_discovery.stop()
            if self.account_scanner:
                await self.account_scanner.stop()
            if self.browser_scanner:
                await self.browser_scanner.stop()
            logger.info("All scanners shut down")
        except Exception as e:
            logger.error(f"Error during scanner shutdown: {e}")

    def create_scan_job(self, region: str, country_code: str, job_type: str = 'vulnerability_scan',
                       priority: int = 5, delay_minutes: int = 0) -> str:
        """Create a new scan job"""
        self.job_counter += 1
        job_id = f"{job_type}_{region}_{self.job_counter}"

        scheduled_time = datetime.now() + timedelta(minutes=delay_minutes)

        job = ScanJob(
            job_id=job_id,
            region=region,
            country_code=country_code,
            priority=priority,
            job_type=job_type,
            scheduled_time=scheduled_time,
            status='pending',
            created_at=datetime.now()
        )

        self.job_queue.append(job)
        # Sort queue by priority (higher first) then by scheduled time
        self.job_queue.sort(key=lambda j: (-j.priority, j.scheduled_time))

        logger.info(f"Created scan job: {job_id} for {region} ({job_type})")
        return job_id

    async def run_scan_job(self, job: ScanJob) -> Dict:
        """Execute a scan job"""
        job.started_at = datetime.now()
        job.status = 'running'
        self.active_jobs[job.job_id] = job

        try:
            logger.info(f"Starting job: {job.job_id}")

            if job.job_type == 'discovery':
                result = await self.run_target_discovery(job.region, job.country_code)
            elif job.job_type == 'vulnerability_scan':
                result = await self.run_vulnerability_scan(job.region, job.country_code)
            elif job.job_type == 'region_expansion':
                result = await self.run_region_expansion()
            elif job.job_type == 'target_update':
                result = await self.run_target_update(job.region, job.country_code)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

            job.status = 'completed'
            job.completed_at = datetime.now()
            job.result = result

            self.stats['successful_scans'] += 1
            logger.info(f"Job completed successfully: {job.job_id}")

            return result

        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.now()
            job.retry_count += 1

            self.stats['failed_scans'] += 1
            logger.error(f"Job failed: {job.job_id} - {e}")

            # Retry logic
            if job.retry_count < job.max_retries:
                logger.info(f"Retrying job: {job.job_id} (attempt {job.retry_count + 1})")
                # Reschedule with exponential backoff
                delay = 2 ** job.retry_count * 5  # 5, 10, 20 minutes
                self.create_scan_job(job.region, job.country_code, job.job_type,
                                   job.priority, delay)

            return {'success': False, 'error': str(e)}

        finally:
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.completed_jobs.append(job)

    async def run_target_discovery(self, region: str, country_code: str) -> Dict:
        """Run target discovery for a region"""
        logger.info(f"Running target discovery for {region}")

        try:
            targets = await self.target_discovery.discover_targets_for_region(
                region, country_code, max_targets=50
            )

            # Save targets
            self.target_discovery.save_targets_to_config(targets)

            result = {
                'targets_discovered': len(targets),
                'high_priority_targets': len([t for t in targets if t.priority_score > 0.7]),
                'targets_with_features': len([t for t in targets if t.features_detected])
            }

            self.stats['targets_discovered'] += len(targets)
            return result

        except Exception as e:
            logger.error(f"Target discovery failed for {region}: {e}")
            raise

    async def run_vulnerability_scan(self, region: str, country_code: str) -> Dict:
        """Run vulnerability scan for a region"""
        logger.info(f"Running vulnerability scan for {region}")

        try:
            # Load targets for this region
            from tools.target_manager import TargetManager
            target_manager = TargetManager()
            targets = target_manager.get_targets(region=region, status='pending')

            if not targets:
                return {'targets_scanned': 0, 'vulnerabilities_found': 0}

            vulnerabilities_found = []
            targets_scanned = 0

            # Limit concurrent scans
            semaphore = asyncio.Semaphore(self.scan_config.max_concurrent_scans)

            async def scan_single_target(target):
                async with semaphore:
                    try:
                        logger.debug(f"Scanning target: {target.url}")

                        # Run account creation vulnerability scan
                        if self.account_scanner:
                            result = await self.account_scanner.scan_url(target.url)
                            if result.vulnerabilities:
                                vulnerabilities_found.extend(result.vulnerabilities)

                        # Update target status
                        target_manager.update_target(
                            target.url, region, status='completed'
                        )

                        return True
                    except Exception as e:
                        logger.warning(f"Failed to scan {target.url}: {e}")
                        target_manager.update_target(
                            target.url, region, status='failed'
                        )
                        return False

            # Scan targets concurrently
            scan_tasks = [scan_single_target(target) for target in targets[:20]]  # Limit for safety
            results = await asyncio.gather(*scan_tasks, return_exceptions=True)

            targets_scanned = sum(1 for r in results if r is True)

            # Generate report
            report_data = {
                'region': region,
                'targets_scanned': targets_scanned,
                'vulnerabilities_found': len(vulnerabilities_found),
                'scan_timestamp': datetime.now().isoformat(),
                'high_severity': len([v for v in vulnerabilities_found if v.severity == 'critical']),
                'medium_severity': len([v for v in vulnerabilities_found if v.severity == 'high'])
            }

            # Save report
            self.save_scan_report(region, report_data)

            self.stats['vulnerabilities_found'] += len(vulnerabilities_found)

            return report_data

        except Exception as e:
            logger.error(f"Vulnerability scan failed for {region}: {e}")
            raise

    async def run_region_expansion(self) -> Dict:
        """Run region expansion to discover new countries"""
        logger.info("Running region expansion")

        try:
            await self.region_discovery.start()
            result = await self.region_discovery.run_discovery_cycle(max_countries=10)

            if result.get('success'):
                self.stats['regions_expanded'] += result.get('countries_discovered', 0)

            return result

        except Exception as e:
            logger.error(f"Region expansion failed: {e}")
            raise
        finally:
            await self.region_discovery.stop()

    async def run_target_update(self, region: str, country_code: str) -> Dict:
        """Update existing targets for a region"""
        logger.info(f"Running target update for {region}")

        # Similar to discovery but focused on updating existing targets
        return await self.run_target_discovery(region, country_code)

    def save_scan_report(self, region: str, report_data: Dict):
        """Save scan report to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"results/continuous_scan_{region}_{timestamp}.json"

            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)

            logger.info(f"Scan report saved: {report_path}")

        except Exception as e:
            logger.error(f"Failed to save scan report: {e}")

    async def process_job_queue(self):
        """Process pending jobs in the queue"""
        while self.running:
            try:
                # Get next job that's ready to run
                now = datetime.now()
                pending_jobs = [j for j in self.job_queue
                              if j.status == 'pending' and j.scheduled_time <= now]

                if not pending_jobs:
                    await asyncio.sleep(10)  # Wait before checking again
                    continue

                # Take the highest priority job
                job = pending_jobs[0]
                self.job_queue.remove(job)

                # Check if we can run more concurrent jobs
                if len(self.active_jobs) >= self.scan_config.max_concurrent_scans:
                    await asyncio.sleep(5)
                    continue

                # Run the job
                asyncio.create_task(self.run_scan_job(job))

            except Exception as e:
                logger.error(f"Error processing job queue: {e}")
                await asyncio.sleep(30)

    def schedule_regular_scans(self):
        """Schedule regular scanning tasks"""

        # Schedule vulnerability scans for known regions
        known_regions = [
            ('vietnam', 'VN'),
            ('laos', 'LA'),
            ('cambodia', 'KH')
        ]

        # Schedule daily scans for known regions
        for region, country_code in known_regions:
            schedule.every(self.scan_config.scan_interval_hours).hours.do(
                lambda r=region, c=country_code: self.create_scan_job(r, c, 'vulnerability_scan', priority=7)
            )

        # Schedule weekly target discovery
        for region, country_code in known_regions:
            schedule.every(self.scan_config.discovery_interval_hours).hours.do(
                lambda r=region, c=country_code: self.create_scan_job(r, c, 'discovery', priority=5)
            )

        # Schedule region expansion
        if self.scan_config.auto_region_expansion_enabled:
            schedule.every(self.scan_config.region_expansion_interval_days).days.do(
                lambda: self.create_scan_job('global', 'ALL', 'region_expansion', priority=3)
            )

        logger.info("Regular scan schedules configured")

    def start_continuous_scanning(self):
        """Start the continuous scanning system"""
        if self.running:
            logger.warning("Continuous scanning already running")
            return

        self.running = True
        logger.info("Starting continuous scanning system")

        # Start the scanning thread
        self.scan_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.scan_thread.start()

        # Schedule regular tasks
        self.schedule_regular_scans()

        # Start schedule checking in a separate thread
        schedule_thread = threading.Thread(target=self._run_schedule_checker, daemon=True)
        schedule_thread.start()

    def stop_continuous_scanning(self):
        """Stop the continuous scanning system"""
        logger.info("Stopping continuous scanning system")
        self.running = False

        if self.scan_thread:
            self.scan_thread.join(timeout=30)

    def _run_async_loop(self):
        """Run the async event loop in a thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize scanners
            loop.run_until_complete(self.initialize_scanners())

            # Run the job processor
            loop.run_until_complete(self.process_job_queue())

        except Exception as e:
            logger.error(f"Error in async loop: {e}")
        finally:
            loop.run_until_complete(self.shutdown_scanners())
            loop.close()

    def _run_schedule_checker(self):
        """Run the schedule checker in a separate thread"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in schedule checker: {e}")
                time.sleep(300)  # Wait 5 minutes on error

    def get_status(self) -> Dict:
        """Get current status of the continuous scanner"""
        return {
            'running': self.running,
            'active_jobs': len(self.active_jobs),
            'queued_jobs': len(self.job_queue),
            'completed_jobs': len(self.completed_jobs),
            'stats': self.stats,
            'next_scheduled_jobs': [
                {
                    'job_id': job.job_id,
                    'region': job.region,
                    'type': job.job_type,
                    'scheduled_time': job.scheduled_time.isoformat(),
                    'priority': job.priority
                }
                for job in sorted(self.job_queue, key=lambda j: j.scheduled_time)[:5]
            ]
        }

    def trigger_manual_scan(self, region: str, country_code: str, job_type: str = 'vulnerability_scan',
                          priority: int = 8) -> str:
        """Trigger a manual scan"""
        return self.create_scan_job(region, country_code, job_type, priority, delay_minutes=0)

    def cleanup_old_reports(self):
        """Clean up old report files"""
        try:
            results_dir = Path("results")
            if not results_dir.exists():
                return

            cutoff_date = datetime.now() - timedelta(days=self.scan_config.cleanup_old_reports_days)

            deleted_count = 0
            for file_path in results_dir.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old report files")

        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")

    def generate_summary_report(self) -> Dict:
        """Generate a summary report of all scanning activity"""
        completed_jobs = [j for j in self.completed_jobs if j.result]

        summary = {
            'total_runtime_hours': (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds() / 3600,
            'total_scans': self.stats['total_scans'],
            'successful_scans': self.stats['successful_scans'],
            'failed_scans': self.stats['failed_scans'],
            'success_rate': self.stats['successful_scans'] / max(self.stats['total_scans'], 1),
            'vulnerabilities_found': self.stats['vulnerabilities_found'],
            'targets_discovered': self.stats['targets_discovered'],
            'regions_expanded': self.stats['regions_expanded'],
            'recent_jobs': [
                {
                    'job_id': job.job_id,
                    'region': job.region,
                    'type': job.job_type,
                    'status': job.status,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'result': job.result
                }
                for job in sorted(self.completed_jobs, key=lambda j: j.completed_at or datetime.min, reverse=True)[:10]
            ]
        }

        return summary


# Command-line interface functions
def start_continuous_scanner():
    """Start the continuous scanner from command line"""
    scanner = ContinuousScanner()

    def signal_handler(signum, frame):
        logger.info("Received signal, shutting down...")
        scanner.stop_continuous_scanning()
        sys.exit(0)

    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        scanner.start_continuous_scanning()
        logger.info("Continuous scanner started. Press Ctrl+C to stop.")

        # Keep main thread alive
        while scanner.running:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        scanner.stop_continuous_scanning()


def trigger_scan(region: str, country_code: str, job_type: str = 'vulnerability_scan'):
    """Trigger a manual scan"""
    scanner = ContinuousScanner()

    try:
        job_id = scanner.trigger_manual_scan(region, country_code, job_type)
        print(f"Scan job triggered: {job_id}")

        # Wait a bit for the job to complete (simple implementation)
        time.sleep(5)

    except Exception as e:
        print(f"Error triggering scan: {e}")


def get_scanner_status():
    """Get current scanner status"""
    scanner = ContinuousScanner()
    status = scanner.get_status()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Continuous Casino Scanner")
    parser.add_argument('command', choices=['start', 'scan', 'status', 'summary'],
                       help='Command to run')
    parser.add_argument('--region', help='Region for scan command')
    parser.add_argument('--country-code', help='Country code for scan command')
    parser.add_argument('--job-type', default='vulnerability_scan',
                       choices=['vulnerability_scan', 'discovery', 'target_update'],
                       help='Type of scan job')

    args = parser.parse_args()

    if args.command == 'start':
        start_continuous_scanner()
    elif args.command == 'scan':
        if not args.region or not args.country_code:
            print("Error: --region and --country-code required for scan command")
            sys.exit(1)
        trigger_scan(args.region, args.country_code, args.job_type)
    elif args.command == 'status':
        get_scanner_status()
    elif args.command == 'summary':
        scanner = ContinuousScanner()
        summary = scanner.generate_summary_report()
        print(json.dumps(summary, indent=2))
