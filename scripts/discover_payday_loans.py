#!/usr/bin/env python3
"""
Payday Loan Site Discovery Script
Discovers and validates payday loan sites in Myanmar and Thailand
"""

import asyncio
import httpx
import yaml
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_url(url: str, timeout: float = 5.0) -> Dict:
    """Check if a URL is accessible"""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            return {
                "url": url,
                "accessible": True,
                "status_code": response.status_code,
                "final_url": str(response.url),
                "content_length": len(response.content),
                "has_forms": "form" in response.text.lower() or "input" in response.text.lower(),
                "error": None
            }
    except httpx.TimeoutException:
        return {
            "url": url,
            "accessible": False,
            "status_code": None,
            "error": "Timeout"
        }
    except httpx.ConnectError:
        return {
            "url": url,
            "accessible": False,
            "status_code": None,
            "error": "Connection error"
        }
    except Exception as e:
        return {
            "url": url,
            "accessible": False,
            "status_code": None,
            "error": str(e)
        }


async def validate_targets(region: str) -> List[Dict]:
    """Validate targets for a region"""
    targets_file = Path(f"targets/{region}.yaml")
    
    if not targets_file.exists():
        logger.error(f"Target file not found: {targets_file}")
        return []
    
    with open(targets_file, 'r') as f:
        data = yaml.safe_load(f)
    
    targets = data.get('targets', [])
    logger.info(f"Validating {len(targets)} targets for {region}")
    
    results = []
    for target in targets:
        if target.get('status') == 'pending':
            url = target.get('url')
            logger.info(f"Checking: {url}")
            result = await check_url(url)
            result['name'] = target.get('name')
            result['region'] = region
            results.append(result)
            await asyncio.sleep(1)  # Be polite
    
    return results


async def main():
    """Main function"""
    print("🔍 Payday Loan Site Discovery & Validation")
    print("=" * 60)
    print()
    
    regions = ['myanmar', 'thailand']
    all_results = []
    
    for region in regions:
        print(f"📋 Validating {region.upper()} targets...")
        results = await validate_targets(region)
        all_results.extend(results)
        print(f"   Checked {len(results)} targets")
        print()
    
    # Print summary
    print("📊 Validation Summary")
    print("=" * 60)
    
    accessible = [r for r in all_results if r.get('accessible')]
    inaccessible = [r for r in all_results if not r.get('accessible')]
    
    print(f"✅ Accessible: {len(accessible)}")
    print(f"❌ Inaccessible: {len(inaccessible)}")
    print()
    
    if accessible:
        print("✅ Accessible Sites:")
        for result in accessible:
            status = result.get('status_code', 'N/A')
            print(f"   - {result['url']} (HTTP {status})")
        print()
    
    if inaccessible:
        print("❌ Inaccessible Sites:")
        for result in inaccessible:
            error = result.get('error', 'Unknown')
            print(f"   - {result['url']} ({error})")
        print()
    
    # Save results
    results_file = Path("results/target_validation.json")
    results_file.parent.mkdir(exist_ok=True)
    
    import json
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "regions": regions,
            "total_checked": len(all_results),
            "accessible": len(accessible),
            "inaccessible": len(inaccessible),
            "results": all_results
        }, f, indent=2)
    
    print(f"💾 Results saved to: {results_file}")
    print()
    print("⚠️  Remember: All targets require boss approval before scanning!")


if __name__ == "__main__":
    asyncio.run(main())

