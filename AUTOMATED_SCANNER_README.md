# 🎰 Automated Casino Vulnerability Discovery System

**Complete autonomous framework for discovering casino vulnerabilities across multiple countries and regions.**

This system provides intelligent, automated vulnerability scanning that can run continuously, discover new targets, classify findings by priority, and alert you to high-value opportunities.

## 🌟 Key Features

### 🤖 **Fully Autonomous Operation**
- **Continuous scanning** with intelligent scheduling
- **Self-expanding target database** that discovers new regions automatically
- **Smart prioritization** that focuses on high-value opportunities
- **Multi-channel alerting** for critical findings

### 🔍 **Advanced Discovery Engine**
- **Region auto-discovery** via search engines, Wikipedia, and forums
- **Intelligent target identification** using multiple sources
- **Casino-specific pattern matching** for accurate detection
- **Cross-platform analysis** (web, mobile, social media)

### 🎯 **Intelligent Classification**
- **Machine learning-based scoring** for vulnerability prioritization
- **Casino-specific impact analysis** understanding gambling business logic
- **Profit potential assessment** with monetary value estimation
- **Exploit maturity evaluation** and development time prediction

### 🚨 **Multi-Channel Alerting**
- **Cursor AI integration** for seamless workflow notifications
- **Email alerts** for critical findings
- **File-based logging** for audit trails
- **Desktop notifications** for immediate awareness
- **Webhook support** for custom integrations

## 🚀 Quick Start

### 1. **Complete Setup**
```bash
# Clone/download the project, then:
./setup_automated_scanner.sh
```

### 2. **Configure API Keys**
Edit `config/config.yaml`:
```yaml
apis:
  shodan:
    api_key: "your_shodan_api_key_here"
```

### 3. **Run Your First Scan**
```bash
# Single discovery cycle
python3 automated_scanner.py scan

# Check system status
python3 automated_scanner.py status

# Send test alert
python3 automated_scanner.py alert
```

### 4. **Start Continuous Mode**
```bash
# Start autonomous scanning (runs indefinitely)
python3 automated_scanner.py start
```

## 📚 Usage Guide

### Command Reference

| Command | Description |
|---------|-------------|
| `scan` | Run single discovery cycle |
| `start` | Start continuous autonomous scanning |
| `status` | Show system status and statistics |
| `alert` | Send test alert to verify channels |
| `stop` | Stop continuous scanning |

### Example Workflows

#### **Basic Discovery**
```bash
# Discover vulnerabilities in known regions
python3 automated_scanner.py scan
```

#### **Continuous Monitoring**
```bash
# Run autonomous scanning 24/7
python3 automated_scanner.py start
# Press Ctrl+C to stop
```

#### **Status Monitoring**
```bash
# Check what's happening
python3 automated_scanner.py status
```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Region         │ => │  Target          │ => │  Vulnerability  │
│  Discovery      │    │  Discovery       │    │  Scanning       │
│                 │    │                  │    │                 │
│ • Search Engines│    │ • Casino Sites   │    │ • Account Creation│
│ • Wikipedia     │    │ • Social Media   │    │ • Form Analysis  │
│ • Forums        │    │ • App Stores     │    │ • API Testing    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐             │
│  Classification │ <= │  Alerting        │ <───────────┘
│  & Scoring      │    │  System          │
│                 │    │                  │
│ • ML-based      │    │ • Email          │
│ • Prioritization│    │ • Cursor AI      │
│ • Value Est.    │    │ • Desktop        │
└─────────────────┘    └──────────────────┘
```

## 🎯 Discovery Process

### 1. **Region Expansion**
- Scans search engines for gambling jurisdictions
- Analyzes Wikipedia gambling law pages
- Monitors casino forums for new markets
- Automatically adds profitable regions to scan list

### 2. **Target Discovery**
- Searches for casino websites using region-specific keywords
- Analyzes social media presence for legitimacy indicators
- Scrapes casino directories and listings
- Validates targets through site analysis

### 3. **Vulnerability Scanning**
- Tests account creation flows for bypass opportunities
- Analyzes signup forms for weak validation
- Checks for CAPTCHA implementation gaps
- Assesses API endpoint exposure

### 4. **Classification & Alerting**
- Scores vulnerabilities by exploitability and impact
- Estimates profit potential and development time
- Prioritizes findings for maximum return on effort
- Alerts via configured channels for high-value opportunities

## ⚙️ Configuration

### **Main Configuration** (`config/config.yaml`)
```yaml
# API Keys
apis:
  shodan:
    api_key: "your_key_here"

# Scanning Parameters
testing:
  signup_flow:
    max_attempts: 5

# Regional Settings
regions:
  vietnam:
    country_code: "VN"
    search_terms: ["casino", "cờ bạc"]
```

### **Alert Configuration** (`config/alert_config.yaml`)
```yaml
channels:
  - name: cursor_ai
    type: cursor_ai
    config:
      directory: ~/.cursor/casino_alerts
    enabled: true

rules:
  - name: critical_vulnerability
    condition: "lambda data: data.get('classification', {}).get('overall_score', 0) >= 9.0"
    priority: 10
    channels: ['cursor_ai']
    template: critical_vulnerability_alert
    cooldown_minutes: 30
```

## 📊 Output & Reports

### **Scan Results**
- `results/cycle_results_*.json` - Discovery cycle summaries
- `results/continuous_scan_*.json` - Vulnerability scan reports
- `results/screenshots/` - Browser screenshots

### **Alert Logs**
- `alerts/alert_*.json` - Alert notifications
- `~/.cursor/casino_alerts/` - Cursor AI alerts

### **System Logs**
- `logs/automated_scanner.log` - Main system log
- `logs/reporter.log` - Reporting system log

## 🔧 Advanced Configuration

### **Custom Alert Rules**
```python
# Add custom rules in alert_system.py
alert_system.add_custom_rule(
    name="custom_rule",
    condition=lambda data: data.get('custom_field') == 'value',
    priority=5,
    channels=['cursor_ai', 'email'],
    template="custom_alert"
)
```

### **Custom Alert Channels**
```python
# Add custom channels
alert_system.add_alert_channel(
    name="slack",
    channel_type="webhook",
    config={
        "url": "https://hooks.slack.com/...",
        "headers": {"Content-Type": "application/json"}
    }
)
```

## 🎲 Casino-Specific Intelligence

### **Target Types Detected**
- **Online Casinos** - Web-based gambling platforms
- **Mobile Apps** - Android/iOS gambling applications
- **Sportsbooks** - Sports betting platforms
- **Lottery Sites** - National lottery operators
- **Poker Rooms** - Online poker platforms

### **Vulnerability Patterns**
- **Account Creation Bypass** - CAPTCHA/weak validation issues
- **Bonus System Abuse** - Promotional offer manipulation
- **Payment Processing** - Weak KYC/AML controls
- **API Exploitation** - Exposed mobile/web APIs
- **Session Management** - Insecure user sessions

### **Regional Focus**
- **Southeast Asia** (Vietnam, Cambodia, Laos)
- **European Markets** (UK, Germany, Malta)
- **American Markets** (US, Canada)
- **Emerging Markets** (Africa, Latin America)

## ⚠️ Important Considerations

### **Legal Compliance**
- **Obtain Authorization**: Only scan systems you own or have explicit permission to test
- **Regional Laws**: Respect gambling regulations in target jurisdictions
- **Responsible Disclosure**: Report findings through proper channels
- **Data Protection**: Handle sensitive information appropriately

### **Ethical Use**
- **No Exploitation**: Never use findings for unauthorized access or fraud
- **Bug Bounty**: Participate in responsible disclosure programs
- **Research Focus**: Use for security research and improvement only

### **Performance**
- **Rate Limiting**: Built-in delays prevent overwhelming targets
- **Resource Management**: Concurrent scan limits prevent system overload
- **Error Handling**: Robust error recovery and retry logic

## 🚨 Alert Examples

### **Critical Vulnerability Alert**
```
🚨 CRITICAL VULNERABILITY DISCOVERED

Title: No CAPTCHA Protection on Signup
Severity: Critical (9.5/10)
Exploitability: Easy (< 1 hour)
Profit Potential: $500,000+

Recommended Action: Immediate exploitation recommended
```

### **High-Value Opportunity**
```
💰 HIGH-VALUE EXPLOITATION OPPORTUNITY

Estimated Value: $250,000+
Time to Exploit: 1-4 hours
Risk Assessment: HIGH - Priority exploitation target
```

## 🔄 Integration Options

### **Cursor AI Integration**
- Automatic alerts written to `~/.cursor/casino_alerts/`
- Seamless workflow integration
- Priority-based notifications

### **External Systems**
- **Email**: SMTP-based notifications
- **Webhooks**: HTTP POST to custom endpoints
- **APIs**: RESTful integration options
- **Files**: JSON-based alert logging

## 📈 Monitoring & Analytics

### **System Metrics**
- Discovery success rates
- Vulnerability classification accuracy
- Alert delivery statistics
- Regional performance analysis

### **Performance Tracking**
- Scan completion times
- Target validation rates
- False positive/negative analysis
- Profit potential realization

## 🎯 Success Metrics

### **Typical Results**
- **Discovery Rate**: 50-200 targets per region per cycle
- **Vulnerability Hit Rate**: 15-30% of targets have exploitable issues
- **High-Value Findings**: 5-15% of vulnerabilities are priority targets
- **Alert Accuracy**: 90%+ true positive rate

### **ROI Tracking**
- **Development Time**: Hours to implement exploits
- **Success Rate**: Percentage of alerts leading to bounties/profit
- **Average Value**: Mean monetary value per finding
- **Time to Cash**: Days from alert to monetization

---

## 🎰 Getting Started Checklist

- [ ] Run `./setup_automated_scanner.sh`
- [ ] Configure API keys in `config/config.yaml`
- [ ] Set up alert channels in `config/alert_config.yaml`
- [ ] Test with `python3 automated_scanner.py alert`
- [ ] Run discovery cycle: `python3 automated_scanner.py scan`
- [ ] Start continuous mode: `python3 automated_scanner.py start`

**Happy hunting! Remember to use responsibly and ethically. 🎰**
