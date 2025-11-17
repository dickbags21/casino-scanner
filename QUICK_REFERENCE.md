# Quick Reference - Casino Scanner

## 🎯 Adding New Targets

### For CCOs, Gambling Sites, Payment Processors

**Quick Add (Easiest):**
```bash
python3 scripts/quick_add_target.py
```

**Manual Add:**
1. Edit `targets/myanmar.yaml` or `targets/thailand.yaml`
2. Add entry with `status: "pending"`
3. Get boss approval
4. Change to `status: "approved"`

**Template:**
```yaml
- url: "https://example.com"
  name: "Site Name"
  region: "myanmar"  # or "thailand"
  description: "CCO / Gambling / Payment site"
  tags:
    - "cco"          # or "gambling" or "payment-processor"
    - "myanmar"      # or "thailand"
  priority: 7
  status: "pending"  # Always pending first!
  notes: "Requires approval - [type]"
```

## 📋 View Pending Targets

```bash
python3 scripts/list_targets_for_approval.py
```

## 🚀 Start Services

```bash
# Start dashboard
python3 start_dashboard.py

# Start Node-RED
./start_node_red_background.sh

# Stop Node-RED
./stop_node_red.sh
```

## 🧪 Test Everything

```bash
# Test Node-RED
./test_node_red.sh

# Run tests
pytest

# Validate targets
python3 scripts/discover_payday_loans.py
```

## 📁 Key Files

- **Targets:** `targets/myanmar.yaml`, `targets/thailand.yaml`
- **Approval List:** `targets/TARGETS_FOR_APPROVAL.md`
- **Dashboard:** http://localhost:8000
- **Node-RED:** http://localhost:1880

## ✅ Workflow

1. Add targets → `status: "pending"`
2. List for approval → `python3 scripts/list_targets_for_approval.py`
3. Get boss approval
4. Update status → `status: "approved"`
5. Run scans → `python3 automated_scanner.py --region myanmar`

## 🏷️ Tag Suggestions

- `"gambling"` - Gambling/casino sites
- `"cco"` - Credit card organizations  
- `"payday-loan"` - Payday loan sites
- `"payment-processor"` - Payment processors
- `"casino"` - Casino sites
- `"flagged"` - Known scams (needs explicit approval)

## ⚠️ Important

- **Always start with `status: "pending"`**
- **Get approval before scanning**
- **Flag known scams** with `"flagged"` tag
- **Document everything** in notes

