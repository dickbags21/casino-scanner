#!/usr/bin/env python3
"""
Quick script to add targets to YAML files
Usage: python3 scripts/quick_add_target.py
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime


def add_target(region: str, url: str, name: str, description: str = "", 
               tags: list = None, priority: int = 5, notes: str = ""):
    """Add a target to the region's YAML file"""
    
    if tags is None:
        tags = []
    
    targets_file = Path(f"targets/{region}.yaml")
    
    if not targets_file.exists():
        print(f"❌ Target file not found: {targets_file}")
        print(f"   Create it first or use existing region (myanmar, thailand)")
        return False
    
    # Load existing targets
    with open(targets_file, 'r') as f:
        data = yaml.safe_load(f) or {}
    
    targets = data.get('targets', [])
    
    # Check if URL already exists
    for target in targets:
        if target.get('url') == url:
            print(f"⚠️  Target already exists: {url}")
            return False
    
    # Add new target
    new_target = {
        'url': url,
        'name': name,
        'region': region,
        'description': description,
        'tags': tags,
        'priority': priority,
        'status': 'pending',  # Always pending for approval
        'notes': notes or f"Requires approval - added {datetime.now().strftime('%Y-%m-%d')}"
    }
    
    targets.append(new_target)
    data['targets'] = targets
    
    # Save
    with open(targets_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Added target to {region}.yaml:")
    print(f"   {name} - {url}")
    print(f"   Status: pending (requires approval)")
    return True


def interactive_add():
    """Interactive mode to add targets"""
    print("🎯 Quick Target Adder")
    print("=" * 60)
    print()
    
    # Region
    print("Select region:")
    print("1. Myanmar")
    print("2. Thailand")
    region_choice = input("Choice (1-2): ").strip()
    region = "myanmar" if region_choice == "1" else "thailand"
    
    # URL
    url = input("URL: ").strip()
    if not url.startswith("http"):
        url = "https://" + url
    
    # Name
    name = input("Site name: ").strip()
    
    # Description
    description = input("Description (optional): ").strip()
    
    # Type
    print("\nSelect type:")
    print("1. Gambling/Casino")
    print("2. CCO (Credit Card Organization)")
    print("3. Payday Loan")
    print("4. Payment Processor")
    print("5. Other")
    type_choice = input("Choice (1-5): ").strip()
    
    type_map = {
        "1": ("gambling", "casino"),
        "2": ("cco", "credit-card"),
        "3": ("payday-loan", "online-lending"),
        "4": ("payment-processor", "payment"),
        "5": ("other",)
    }
    
    base_tags = list(type_map.get(type_choice, ("other",)))
    base_tags.append(region)
    
    # Priority
    priority = input("Priority (1-10, default 5): ").strip()
    priority = int(priority) if priority.isdigit() else 5
    
    # Notes
    notes = input("Notes (optional): ").strip()
    
    # Add target
    success = add_target(region, url, name, description, base_tags, priority, notes)
    
    if success:
        print()
        print("📋 Next steps:")
        print("1. Review the target in targets/{region}.yaml")
        print("2. Get boss approval")
        print("3. Change status from 'pending' to 'approved'")
        print("4. Run: python3 scripts/list_targets_for_approval.py")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/quick_add_target.py <region> <url> <name> [description] [tags] [priority]")
            print("Example: python3 scripts/quick_add_target.py myanmar https://example.com 'Example Site' 'Gambling site' 'gambling,casino' 7")
            sys.exit(1)
        
        region = sys.argv[1]
        url = sys.argv[2]
        name = sys.argv[3]
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else []
        priority = int(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6].isdigit() else 5
        
        add_target(region, url, name, description, tags, priority)
    else:
        # Interactive mode
        interactive_add()

