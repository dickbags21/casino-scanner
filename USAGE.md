# Usage Guide

## Quick Start

1. **Setup the environment:**
```bash
./setup.sh
```

2. **Configure API keys:**
Edit `config/config.yaml` and add your Shodan API key:
```yaml
apis:
  shodan:
    api_key: "YOUR_ACTUAL_SHODAN_API_KEY"
```

3. **Add targets:**
Edit the target files in `targets/` directory:
- `targets/vietnam.yaml`
- `targets/laos.yaml`
- `targets/cambodia.yaml`

Example target entry:
```yaml
- url: "https://example-casino.vn"
  name: "Example Casino"
  region: "vietnam"
  description: "Target description"
  tags:
    - "casino"
    - "gambling"
  priority: 5
  status: "pending"
```

4. **Run a scan:**
```bash
python main.py --region vietnam
```

## Project Structure

```
casino/
├── config/              # Configuration files
│   └── config.yaml      # Main config (add your API keys here)
├── tools/               # Core scanning tools
│   ├── shodan_scanner.py    # Shodan API integration
│   ├── browser_scanner.py   # Browser automation (Playwright)
│   ├── target_manager.py    # Target management
│   └── reporter.py          # Report generation
├── targets/             # Target definitions by region
│   ├── vietnam.yaml
│   ├── laos.yaml
│   └── cambodia.yaml
├── results/             # Scan results and reports
│   └── screenshots/     # Screenshots from browser tests
├── logs/                # Application logs
├── main.py              # Main entry point
└── requirements.txt     # Python dependencies
```

## Features

### Shodan Integration
- Automated reconnaissance using Shodan API
- Country-specific searches
- Port filtering
- Vulnerability detection

### Browser Automation
- Automated signup flow testing
- Bonus code validation testing
- Screenshot capture
- Form field detection
- Validation error detection

### Multi-Region Support
- Pre-configured for Vietnam, Laos, Cambodia
- Easy to add new regions
- Region-specific search terms and configurations

### Reporting
- JSON, HTML, and text report formats
- Detailed findings with severity levels
- Screenshot integration
- Timestamped reports

## Configuration Options

### Browser Settings
```yaml
browser:
  headless: true          # Run browser in headless mode
  timeout: 30000          # Page timeout in milliseconds
  user_agent: "..."       # Custom user agent
  viewport:
    width: 1920
    height: 1080
```

### Region Settings
Each region has:
- Country code
- Language settings
- Timezone
- Search terms (in local language)
- Domain extensions
- Port filters

### Testing Parameters
```yaml
testing:
  signup_flow:
    test_email_domains: [...]
    test_phone_prefixes: [...]
    max_attempts: 5
  bonus_offers:
    test_codes: ["WELCOME", "BONUS", ...]
    check_validation: true
```

## Adding New Regions

1. Add region config to `config/config.yaml`:
```yaml
regions:
  new_region:
    country_code: "XX"
    language: "xx"
    timezone: "Asia/Region"
    search_terms: [...]
    domains: [...]
    ports: [...]
```

2. Create target file: `targets/new_region.yaml`

3. Update `main.py` choices if needed

## Output

Reports are saved in `results/` directory with format:
- `report_{region}_{timestamp}.json`
- `report_{region}_{timestamp}.html`
- `report_{region}_{timestamp}.txt`

Screenshots are saved in `results/screenshots/`

Logs are saved in `logs/research.log`

## Troubleshooting

### Shodan API Errors
- Check API key in `config/config.yaml`
- Verify API key has sufficient credits
- Check rate limits

### Browser Issues
- Ensure Playwright is installed: `playwright install chromium`
- Check browser timeout settings
- Try running with `headless: false` to see what's happening

### Target Not Found
- Verify target URL is accessible
- Check target file format (YAML syntax)
- Ensure target status is "pending"

## Ethical Use

⚠️ **IMPORTANT**: This tool is for authorized security research only. Always:
- Get proper authorization before testing
- Follow responsible disclosure practices
- Respect rate limits and terms of service
- Do not use for malicious purposes

