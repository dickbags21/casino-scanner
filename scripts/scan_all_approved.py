#!/usr/bin/env python3
"""
Scan all approved targets in Myanmar and Thailand
Runs comprehensive scans to find vulnerabilities
"""

import asyncio
import sys
import yaml
import httpx
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DASHBOARD_URL = "http://localhost:8000"


async def load_approved_targets(region: str) -> List[Dict]:
    """Load approved targets from YAML file"""
    targets_file = Path(f"targets/{region}.yaml")
    
    if not targets_file.exists():
        logger.warning(f"Target file not found: {targets_file}")
        return []
    
    with open(targets_file, 'r') as f:
        data = yaml.safe_load(f)
    
    targets = data.get('targets', [])
    approved = [t for t in targets if t.get('status') == 'approved']
    
    logger.info(f"Found {len(approved)} approved targets in {region}")
    return approved


async def create_target_in_dashboard(target: Dict) -> int:
    """Create target in dashboard database"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{DASHBOARD_URL}/api/targets",
                json={
                    "name": target.get('name', ''),
                    "url": target.get('url', ''),
                    "region": target.get('region', ''),
                    "country_code": target.get('region', '').upper()[:2],
                    "tags": target.get('tags', []),
                    "priority": target.get('priority', 5),
                    "status": "active",
                    "notes": target.get('notes', '')
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('id')
            else:
                logger.error(f"Failed to create target: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error creating target: {e}")
        return None


async def scan_target(target_url: str, target_name: str, scan_type: str = "signup"):
    """Start a scan for a target using direct scan API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{DASHBOARD_URL}/api/scans",
                json={
                    "plugin": "browser",
                    "name": f"Scan: {target_name}",
                    "url": target_url,
                    "scan_type": scan_type
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                scan_id = data.get('scan_id')
                logger.info(f"✅ Scan started for {target_url} - Scan ID: {scan_id}")
                return scan_id
            else:
                logger.error(f"Failed to start scan: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        return None


async def check_dashboard_running() -> bool:
    """Check if dashboard is running"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{DASHBOARD_URL}/api/health")
            return response.status_code == 200
    except:
        return False


async def scan_all_approved():
    """Scan all approved targets"""
    print("🎯 Scanning All Approved Targets")
    print("=" * 80)
    print()
    
    # Check if dashboard is running
    print("🔍 Checking dashboard status...")
    if not await check_dashboard_running():
        print("❌ Dashboard is not running!")
        print("   Start it with: python3 start_dashboard.py")
        return
    
    print("✅ Dashboard is running")
    print()
    
    # Load approved targets
    regions = ['myanmar', 'thailand']
    all_targets = []
    
    for region in regions:
        targets = await load_approved_targets(region)
        all_targets.extend(targets)
        print(f"📋 {region.upper()}: {len(targets)} approved targets")
    
    print()
    print(f"📊 Total approved targets: {len(all_targets)}")
    print()
    
    if not all_targets:
        print("⚠️  No approved targets found!")
        print("   Update targets/*.yaml files and set status: 'approved'")
        return
    
    # Confirm
    print("🚀 Ready to scan all approved targets")
    print("   This will:")
    print("   1. Create targets in dashboard")
    print("   2. Start browser scans for each target")
    print("   3. Look for vulnerabilities (signup flows, account creation, etc.)")
    print()
    
    # Process targets
    scan_count = 0
    error_count = 0
    
    for i, target in enumerate(all_targets, 1):
        url = target.get('url', '')
        name = target.get('name', 'Unknown')
        region = target.get('region', 'unknown')
        
        print(f"[{i}/{len(all_targets)}] Processing: {name}")
        print(f"   URL: {url}")
        print(f"   Region: {region}")
        
        # Create target in dashboard
        target_id = await create_target_in_dashboard(target)
        
        # Start scan directly (target creation is optional)
        scan_id = await scan_target(url, name, "signup")
        
        if scan_id:
            scan_count += 1
            print(f"   ✅ Scan started (ID: {scan_id})")
        else:
            error_count += 1
            print(f"   ❌ Failed to start scan")
        
        print()
        
        # Small delay between targets
        await asyncio.sleep(2)
    
    # Summary
    print("=" * 80)
    print("📊 Scan Summary")
    print("=" * 80)
    print(f"✅ Scans started: {scan_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📋 Total targets: {len(all_targets)}")
    print()
    print("🔍 Monitor scans at: http://localhost:8000")
    print("📊 View results in dashboard")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(scan_all_approved())
    except KeyboardInterrupt:
        print("\n⚠️  Scans interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

