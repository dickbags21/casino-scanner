"""
Reporter Module
Handles logging and report generation
"""

import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import asdict, dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScanReport:
    """Container for scan report data"""
    region: str
    timestamp: str
    targets_scanned: int
    shodan_results: List[Dict]
    signup_tests: List[Dict]
    bonus_tests: List[Dict]
    findings: List[Dict]
    summary: Dict


class Reporter:
    """Handles report generation and logging"""
    
    def __init__(self, results_dir: str = "results", logs_dir: str = "logs",
                 log_level: str = "INFO", max_bytes: int = 10485760,
                 backup_count: int = 5):
        """
        Initialize reporter
        
        Args:
            results_dir: Directory for result files
            logs_dir: Directory for log files
            log_level: Logging level
            max_bytes: Maximum log file size
            backup_count: Number of backup log files
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_logging(log_level, max_bytes, backup_count)
    
    def setup_logging(self, level: str, max_bytes: int, backup_count: int):
        """Setup logging configuration"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # File handler with rotation
        log_file = self.logs_dir / "research.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def generate_report(self, report_data: ScanReport, format: str = "json") -> str:
        """
        Generate scan report
        
        Args:
            report_data: ScanReport object
            format: Report format (json, html, txt)
            
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            return self._generate_json_report(report_data, timestamp)
        elif format == "html":
            return self._generate_html_report(report_data, timestamp)
        else:
            return self._generate_txt_report(report_data, timestamp)
    
    def _generate_json_report(self, report_data: ScanReport, timestamp: str) -> str:
        """Generate JSON report"""
        report_path = self.results_dir / f"report_{report_data.region}_{timestamp}.json"
        
        report_dict = asdict(report_data)
        
        with open(report_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info(f"Generated JSON report: {report_path}")
        return str(report_path)
    
    def _generate_html_report(self, report_data: ScanReport, timestamp: str) -> str:
        """Generate HTML report"""
        report_path = self.results_dir / f"report_{report_data.region}_{timestamp}.html"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Research Report - {report_data.region}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ccc; padding-bottom: 5px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .finding {{ background: #fff; border-left: 4px solid #007bff; padding: 10px; margin: 10px 0; }}
        .success {{ border-left-color: #28a745; }}
        .warning {{ border-left-color: #ffc107; }}
        .error {{ border-left-color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Security Research Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Region:</strong> {report_data.region}</p>
        <p><strong>Timestamp:</strong> {report_data.timestamp}</p>
        <p><strong>Targets Scanned:</strong> {report_data.targets_scanned}</p>
        <p><strong>Shodan Results:</strong> {len(report_data.shodan_results)}</p>
        <p><strong>Signup Tests:</strong> {len(report_data.signup_tests)}</p>
        <p><strong>Bonus Tests:</strong> {len(report_data.bonus_tests)}</p>
        <p><strong>Findings:</strong> {len(report_data.findings)}</p>
    </div>
    
    <h2>Findings</h2>
"""
        
        for finding in report_data.findings:
            severity = finding.get('severity', 'info')
            html += f"""
    <div class="finding {severity}">
        <h3>{finding.get('title', 'Finding')}</h3>
        <p><strong>URL:</strong> {finding.get('url', 'N/A')}</p>
        <p><strong>Description:</strong> {finding.get('description', '')}</p>
        <p><strong>Severity:</strong> {severity}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(report_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Generated HTML report: {report_path}")
        return str(report_path)
    
    def _generate_txt_report(self, report_data: ScanReport, timestamp: str) -> str:
        """Generate text report"""
        report_path = self.results_dir / f"report_{report_data.region}_{timestamp}.txt"
        
        lines = [
            "=" * 80,
            "SECURITY RESEARCH REPORT",
            "=" * 80,
            f"Region: {report_data.region}",
            f"Timestamp: {report_data.timestamp}",
            f"Targets Scanned: {report_data.targets_scanned}",
            "",
            "SUMMARY",
            "-" * 80,
            f"Shodan Results: {len(report_data.shodan_results)}",
            f"Signup Tests: {len(report_data.signup_tests)}",
            f"Bonus Tests: {len(report_data.bonus_tests)}",
            f"Findings: {len(report_data.findings)}",
            "",
            "FINDINGS",
            "-" * 80,
        ]
        
        for finding in report_data.findings:
            lines.extend([
                f"Title: {finding.get('title', 'N/A')}",
                f"URL: {finding.get('url', 'N/A')}",
                f"Severity: {finding.get('severity', 'info')}",
                f"Description: {finding.get('description', '')}",
                ""
            ])
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Generated text report: {report_path}")
        return str(report_path)
    
    def log_finding(self, finding: Dict):
        """
        Log a security finding
        
        Args:
            finding: Dictionary with finding details
        """
        logger.warning(f"Finding: {finding.get('title', 'Unknown')} - {finding.get('url', 'N/A')}")

