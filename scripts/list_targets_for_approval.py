#!/usr/bin/env python3
"""
List all pending targets for boss approval
"""

import yaml
from pathlib import Path
from typing import List, Dict


def load_targets(region: str) -> List[Dict]:
    """Load targets from YAML file"""
    targets_file = Path(f"targets/{region}.yaml")
    
    if not targets_file.exists():
        return []
    
    with open(targets_file, 'r') as f:
        data = yaml.safe_load(f)
    
    return data.get('targets', [])


def main():
    """Main function"""
    print("📋 Payday Loan Targets - Approval Required")
    print("=" * 80)
    print()
    
    regions = ['myanmar', 'thailand']
    all_pending = []
    
    for region in regions:
        targets = load_targets(region)
        pending = [t for t in targets if t.get('status') == 'pending']
        all_pending.extend(pending)
        
        print(f"📍 {region.upper()} ({len(pending)} pending targets)")
        print("-" * 80)
        
        for i, target in enumerate(pending, 1):
            url = target.get('url', 'N/A')
            name = target.get('name', 'N/A')
            priority = target.get('priority', 5)
            notes = target.get('notes', '')
            
            flagged = '⚠️ FLAGGED' in notes or 'flagged' in target.get('tags', [])
            flag_marker = "⚠️ " if flagged else "   "
            
            print(f"{flag_marker}{i}. {name}")
            print(f"      URL: {url}")
            print(f"      Priority: {priority}/10")
            if notes:
                print(f"      Notes: {notes}")
            print()
    
    print("=" * 80)
    print(f"📊 Total Pending: {len(all_pending)} targets")
    print()
    print("⚠️  ALL targets require boss approval before scanning!")
    print()
    print("📄 Full details: targets/TARGETS_FOR_APPROVAL.md")
    print()
    
    # Generate URL list
    print("🔗 URL List (for easy copy-paste):")
    print("-" * 80)
    for target in all_pending:
        print(target.get('url', ''))


if __name__ == "__main__":
    main()

