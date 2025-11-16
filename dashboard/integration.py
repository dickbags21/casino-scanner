"""
Integration module for importing existing scan results into database
Reads JSON files from results/ directory and imports them
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from dashboard.database import get_db, Scan, ScanResult, Vulnerability

logger = logging.getLogger(__name__)


def import_json_results(results_dir: str = "results"):
    """
    Import existing JSON scan results into database
    
    Args:
        results_dir: Directory containing JSON result files
    """
    results_path = Path(results_dir)
    if not results_path.exists():
        logger.warning(f"Results directory not found: {results_dir}")
        return
    
    db = get_db().get_session()
    imported_count = 0
    
    try:
        # Find all JSON files
        json_files = list(results_path.glob("*.json"))
        json_files.extend(results_path.glob("**/*.json"))
        
        logger.info(f"Found {len(json_files)} JSON files to import")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Determine scan type from file name or content
                scan_type = determine_scan_type(json_file, data)
                
                # Create scan record
                scan_id = f"imported_{json_file.stem}"
                
                # Check if already imported
                existing = db.query(Scan).filter(Scan.scan_id == scan_id).first()
                if existing:
                    logger.debug(f"Scan {scan_id} already imported, skipping")
                    continue
                
                # Extract timestamp
                timestamp_str = data.get('timestamp') or data.get('scan_timestamp')
                if timestamp_str:
                    try:
                        created_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.fromtimestamp(json_file.stat().st_mtime)
                else:
                    created_at = datetime.fromtimestamp(json_file.stat().st_mtime)
                
                scan = Scan(
                    scan_id=scan_id,
                    name=f"Imported: {json_file.stem}",
                    scan_type=scan_type,
                    region=data.get('region'),
                    status='completed',
                    plugin_name=scan_type,
                    config={'imported_from': str(json_file)},
                    progress=1.0,
                    created_at=created_at,
                    started_at=created_at,
                    completed_at=created_at
                )
                db.add(scan)
                db.flush()  # Get scan.id
                
                # Import results
                if 'results' in data:
                    for result_data in data['results']:
                        scan_result = ScanResult(
                            scan_id=scan.id,
                            result_type=result_data.get('result_type', scan_type),
                            target_url=result_data.get('url'),
                            target_ip=result_data.get('ip'),
                            target_port=result_data.get('port'),
                            success=result_data.get('success', False),
                            data=result_data,
                            screenshot_path=result_data.get('screenshot_path') or result_data.get('screenshot')
                        )
                        db.add(scan_result)
                
                # Import vulnerabilities
                vulnerabilities_data = []
                
                # Check various vulnerability locations
                if 'vulnerabilities' in data:
                    vulnerabilities_data.extend(data['vulnerabilities'])
                if 'account_creation_test' in data and 'vulnerabilities' in data['account_creation_test']:
                    vulnerabilities_data.extend(data['account_creation_test']['vulnerabilities'])
                if 'findings' in data:
                    vulnerabilities_data.extend(data['findings'])
                
                for vuln_data in vulnerabilities_data:
                    # Handle both dict and object-like structures
                    if isinstance(vuln_data, dict):
                        vulnerability = Vulnerability(
                            scan_id=scan.id,
                            title=vuln_data.get('title', vuln_data.get('name', 'Unknown Vulnerability')),
                            description=vuln_data.get('description', ''),
                            severity=vuln_data.get('severity', 'info'),
                            vulnerability_type=vuln_data.get('vulnerability_type', vuln_data.get('type', 'unknown')),
                            url=vuln_data.get('url'),
                            ip=vuln_data.get('ip'),
                            port=vuln_data.get('port'),
                            exploitability=vuln_data.get('exploitability', 'unknown'),
                            profit_potential=vuln_data.get('profit_potential', 'unknown'),
                            technical_details=vuln_data.get('technical_details', {}),
                            proof_of_concept=vuln_data.get('proof_of_concept'),
                            mitigation=vuln_data.get('mitigation')
                        )
                        db.add(vulnerability)
                
                db.commit()
                imported_count += 1
                logger.info(f"Imported {json_file.name} as scan {scan_id}")
                
            except Exception as e:
                logger.error(f"Error importing {json_file}: {e}")
                db.rollback()
                continue
        
        logger.info(f"Successfully imported {imported_count} scan(s)")
        return imported_count
        
    finally:
        db.close()


def determine_scan_type(file_path: Path, data: Dict) -> str:
    """
    Determine scan type from file name or content
    
    Args:
        file_path: Path to JSON file
        data: JSON data
        
    Returns:
        Scan type string
    """
    filename = file_path.name.lower()
    
    # Check filename patterns
    if 'shodan' in filename:
        return 'shodan'
    elif 'browser' in filename or 'signup' in filename:
        return 'browser'
    elif 'account' in filename or 'creation' in filename:
        return 'account_creation'
    elif 'mobile' in filename or 'app' in filename:
        return 'mobile_app'
    
    # Check data content
    if 'shodan_results' in data or 'shodan' in str(data).lower():
        return 'shodan'
    elif 'signup_test' in data or 'browser' in str(data).lower():
        return 'browser'
    elif 'account_creation_test' in data or 'account_creation' in str(data).lower():
        return 'account_creation'
    elif 'mobile_app' in str(data).lower() or 'app_id' in data:
        return 'mobile_app'
    
    # Default
    return 'unknown'


def import_all_results():
    """Import all results from results directory"""
    return import_json_results()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import_all_results()


