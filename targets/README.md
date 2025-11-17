# Target Management

This directory contains target definitions for security scanning.

## Regions

- `myanmar.yaml` - Myanmar targets
- `thailand.yaml` - Thailand targets
- `vietnam.yaml` - Vietnam targets (existing)
- `laos.yaml` - Laos targets (existing)
- `cambodia.yaml` - Cambodia targets (existing)

## Target Types

### Payday Loans / Online Lending
- Payday loan services
- Instant loan platforms
- Cash advance services
- Online lending platforms

### Gambling / Casino Sites
- Online casinos
- Sports betting sites
- Lottery platforms
- Poker sites

### CCOs (Credit Card Organizations)
- Credit card companies
- Payment processors
- Financial services
- Money transfer services

### Payment Processors
- Payment gateways
- Money transfer services
- Digital wallets
- Cryptocurrency exchanges

## Adding Targets

### Quick Add (Interactive)
```bash
python3 scripts/quick_add_target.py
```

### Quick Add (Command Line)
```bash
python3 scripts/quick_add_target.py myanmar https://example.com "Site Name" "Description" "gambling,casino" 7
```

### Manual Add
Edit the YAML file directly:
```yaml
- url: "https://example.com"
  name: "Site Name"
  region: "myanmar"
  description: "Description"
  tags:
    - "gambling"
    - "casino"
  priority: 7
  status: "pending"  # Always start as pending
  notes: "Requires approval"
```

## Approval Process

1. **Add targets** with `status: "pending"`
2. **List pending targets**: `python3 scripts/list_targets_for_approval.py`
3. **Get boss approval**
4. **Update status** to `"approved"` for approved targets
5. **Run scans** on approved targets

## Status Values

- `pending` - Awaiting approval (default)
- `approved` - Approved for scanning
- `rejected` - Not approved
- `active` - Currently being scanned
- `completed` - Scan completed
- `archived` - No longer relevant

## Priority Levels

- **1-3**: Low priority
- **4-6**: Medium priority
- **7-8**: High priority
- **9-10**: Critical priority (flagged sites, known scams)

## Flagged Targets

Targets with `"flagged"` tag require **explicit written approval** before scanning. These are typically:
- Known scam operations
- Sites subject to law enforcement action
- High-risk targets

## Viewing Targets

```bash
# List all pending targets
python3 scripts/list_targets_for_approval.py

# View specific region
cat targets/myanmar.yaml
cat targets/thailand.yaml
```

## Best Practices

1. **Always start with `status: "pending"`** - Never add targets as approved
2. **Use descriptive tags** - Makes filtering easier
3. **Add notes** - Explain why the target is interesting
4. **Set appropriate priority** - Higher for more important targets
5. **Flag known scams** - Use `"flagged"` tag and require explicit approval
6. **Document sources** - Note where you found the target in notes

## Target Discovery

Use these tools to discover new targets:
- `scripts/discover_payday_loans.py` - Discover payday loan sites
- `tools/intelligent_target_discovery.py` - Automated discovery
- `tools/auto_region_discovery.py` - Region-specific discovery

## Legal & Ethical

⚠️ **Always ensure:**
- You have legal authorization to scan
- Targets are not protected by law
- You have proper approvals
- You document all approvals
- You comply with local regulations

