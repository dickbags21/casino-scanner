#!/usr/bin/env python3
"""
Monitor running scans and check for vulnerabilities
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import List, Dict

DASHBOARD_URL = "http://localhost:8000"


async def get_scans(status: str = None) -> List[Dict]:
    """Get scans from dashboard"""
    try:
        url = f"{DASHBOARD_URL}/api/scans"
        if status:
            url += f"?status={status}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('scans', [])
    except Exception as e:
        print(f"Error getting scans: {e}")
        return []


async def get_vulnerabilities() -> List[Dict]:
    """Get vulnerabilities from dashboard"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{DASHBOARD_URL}/api/vulnerabilities")
            if response.status_code == 200:
                data = response.json()
                return data.get('vulnerabilities', [])
    except Exception as e:
        print(f"Error getting vulnerabilities: {e}")
        return []


async def get_scan_details(scan_id: str) -> Dict:
    """Get detailed scan information"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{DASHBOARD_URL}/api/scans/{scan_id}")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error getting scan details: {e}")
        return {}


async def monitor_scans():
    """Monitor all scans"""
    print("🔍 Monitoring Scans & Vulnerabilities")
    print("=" * 80)
    print()
    
    # Get all scans
    all_scans = await get_scans()
    running_scans = [s for s in all_scans if s.get('status') == 'running']
    completed_scans = [s for s in all_scans if s.get('status') == 'completed']
    failed_scans = [s for s in all_scans if s.get('status') == 'failed']
    pending_scans = [s for s in all_scans if s.get('status') == 'pending']
    
    print(f"📊 Scan Status:")
    print(f"   ✅ Completed: {len(completed_scans)}")
    print(f"   🔄 Running: {len(running_scans)}")
    print(f"   ⏳ Pending: {len(pending_scans)}")
    print(f"   ❌ Failed: {len(failed_scans)}")
    print()
    
    # Get vulnerabilities
    vulnerabilities = await get_vulnerabilities()
    
    if vulnerabilities:
        print(f"🚨 Vulnerabilities Found: {len(vulnerabilities)}")
        print("-" * 80)
        
        # Group by severity
        critical = [v for v in vulnerabilities if v.get('severity') == 'critical']
        high = [v for v in vulnerabilities if v.get('severity') == 'high']
        medium = [v for v in vulnerabilities if v.get('severity') == 'medium']
        low = [v for v in vulnerabilities if v.get('severity') == 'low']
        
        print(f"   🔴 Critical: {len(critical)}")
        print(f"   🟠 High: {len(high)}")
        print(f"   🟡 Medium: {len(medium)}")
        print(f"   🟢 Low: {len(low)}")
        print()
        
        # Show top vulnerabilities
        if critical or high:
            print("🔥 Top Vulnerabilities:")
            print("-" * 80)
            
            for vuln in (critical + high)[:10]:
                title = vuln.get('title', 'Unknown')
                severity = vuln.get('severity', 'unknown')
                url = vuln.get('url', 'N/A')
                vuln_type = vuln.get('vulnerability_type', 'N/A')
                
                severity_icon = "🔴" if severity == "critical" else "🟠"
                print(f"{severity_icon} {title}")
                print(f"   Type: {vuln_type}")
                print(f"   URL: {url}")
                print()
    else:
        print("ℹ️  No vulnerabilities found yet (scans may still be running)")
        print()
    
    # Show running scans
    if running_scans:
        print("🔄 Currently Running Scans:")
        print("-" * 80)
        for scan in running_scans[:5]:  # Show first 5
            name = scan.get('name', 'Unknown')
            progress = scan.get('progress', 0) * 100
            scan_id = scan.get('scan_id', 'N/A')
            print(f"   {name} - {progress:.1f}% (ID: {scan_id[:8]}...)")
        print()
    
    # Show recent completed scans
    if completed_scans:
        print("✅ Recent Completed Scans:")
        print("-" * 80)
        for scan in completed_scans[:5]:  # Show first 5
            name = scan.get('name', 'Unknown')
            scan_id = scan.get('scan_id', 'N/A')
            completed = scan.get('completed_at', 'N/A')
            print(f"   {name} (ID: {scan_id[:8]}...) - {completed}")
        print()
    
    print("=" * 80)
    print(f"📊 View full details at: {DASHBOARD_URL}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(monitor_scans())
    except KeyboardInterrupt:
        print("\n⚠️  Monitoring stopped")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

