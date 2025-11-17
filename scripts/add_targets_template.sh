#!/bin/bash
# Quick template for adding new targets
# Usage: ./scripts/add_targets_template.sh

cat << 'EOF'
# Template for adding targets to YAML files

# For Myanmar targets: targets/myanmar.yaml
# For Thailand targets: targets/thailand.yaml

# Template entry:
- url: "https://example-site.com"
  name: "Site Name"
  region: "myanmar"  # or "thailand"
  description: "Brief description"
  tags:
    - "gambling"      # or "cco" or "payday-loan" or "casino"
    - "online-lending"
    - "myanmar"       # or "thailand"
  priority: 7        # 1-10, higher = more important
  status: "pending"  # Always start as "pending" for approval
  notes: "Requires approval - [type of site]"

# Tag suggestions:
# - "gambling" - Gambling/casino sites
# - "cco" - Credit card organizations
# - "payday-loan" - Payday loan sites
# - "casino" - Casino sites
# - "online-lending" - Online lending platforms
# - "payment-processor" - Payment processing services
# - "flagged" - Known scam/illegal operations (requires explicit approval)
EOF

