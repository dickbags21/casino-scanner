"""
Advanced Alerting System for Casino Vulnerability Findings
Intelligent notifications for high-value discoveries with Cursor AI integration
"""

import json
import logging
import smtplib
import requests
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import threading
from pathlib import Path
import os

logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """Configuration for alert triggering"""
    name: str
    condition: Callable[[Dict], bool]
    priority: int  # 1-10, higher = more important
    channels: List[str]  # ['email', 'webhook', 'cursor_ai', 'file']
    template: str
    cooldown_minutes: int = 60  # Minimum time between similar alerts
    enabled: bool = True
    last_triggered: Optional[datetime] = None

    def should_trigger(self, data: Dict) -> bool:
        """Check if this alert rule should trigger"""
        if not self.enabled:
            return False

        # Check condition
        if not self.condition(data):
            return False

        # Check cooldown
        if self.last_triggered:
            cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return False

        return True

    def mark_triggered(self):
        """Mark this rule as triggered"""
        self.last_triggered = datetime.now()


@dataclass
class AlertChannel:
    """Configuration for alert delivery channels"""
    name: str
    type: str  # 'email', 'webhook', 'cursor_ai', 'file', 'desktop'
    config: Dict[str, Any]
    enabled: bool = True

    async def send_alert(self, alert_data: Dict) -> bool:
        """Send alert through this channel"""
        try:
            if not self.enabled:
                return False

            if self.type == 'email':
                return await self._send_email_alert(alert_data)
            elif self.type == 'webhook':
                return await self._send_webhook_alert(alert_data)
            elif self.type == 'cursor_ai':
                return await self._send_cursor_ai_alert(alert_data)
            elif self.type == 'file':
                return await self._write_file_alert(alert_data)
            elif self.type == 'desktop':
                return await self._send_desktop_alert(alert_data)
            else:
                logger.warning(f"Unknown alert channel type: {self.type}")
                return False

        except Exception as e:
            logger.error(f"Failed to send alert via {self.name}: {e}")
            return False

    async def _send_email_alert(self, alert_data: Dict) -> bool:
        """Send email alert"""
        try:
            smtp_config = self.config.get('smtp', {})

            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_email', 'alerts@casino-scanner.com')
            msg['To'] = self.config.get('to_email', '')
            msg['Subject'] = alert_data.get('subject', 'Casino Scanner Alert')

            body = alert_data.get('message', '')
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(smtp_config.get('server', 'localhost'),
                                smtp_config.get('port', 587))

            if smtp_config.get('use_tls', True):
                server.starttls()

            if smtp_config.get('username') and smtp_config.get('password'):
                server.login(smtp_config['username'], smtp_config['password'])

            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            logger.error(f"Email alert failed: {e}")
            return False

    async def _send_webhook_alert(self, alert_data: Dict) -> bool:
        """Send webhook alert"""
        try:
            url = self.config.get('url', '')
            headers = self.config.get('headers', {'Content-Type': 'application/json'})

            response = requests.post(url, json=alert_data, headers=headers,
                                   timeout=self.config.get('timeout', 10))

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Webhook alert failed: {e}")
            return False

    async def _send_cursor_ai_alert(self, alert_data: Dict) -> bool:
        """Send alert to Cursor AI (special integration)"""
        try:
            # This would integrate with Cursor AI's API or messaging system
            # For now, we'll simulate this by writing to a special file that Cursor can monitor

            cursor_alerts_dir = Path.home() / '.cursor' / 'casino_alerts'
            cursor_alerts_dir.mkdir(exist_ok=True)

            alert_file = cursor_alerts_dir / f"alert_{int(time.time())}.json"

            with open(alert_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'casino_vulnerability_alert',
                    'priority': alert_data.get('priority', 'medium'),
                    'message': alert_data.get('message', ''),
                    'data': alert_data
                }, f, indent=2)

            # Also try to send to any configured Cursor API endpoint
            cursor_api_url = self.config.get('api_url')
            if cursor_api_url:
                response = requests.post(cursor_api_url, json=alert_data,
                                       headers={'Authorization': self.config.get('api_key', '')},
                                       timeout=5)
                return response.status_code == 200

            return True

        except Exception as e:
            logger.error(f"Cursor AI alert failed: {e}")
            return False

    async def _write_file_alert(self, alert_data: Dict) -> bool:
        """Write alert to file"""
        try:
            alerts_dir = Path(self.config.get('directory', 'alerts'))
            alerts_dir.mkdir(exist_ok=True)

            alert_file = alerts_dir / f"alert_{int(time.time())}.json"

            with open(alert_file, 'w') as f:
                json.dump(alert_data, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"File alert failed: {e}")
            return False

    async def _send_desktop_alert(self, alert_data: Dict) -> bool:
        """Send desktop notification"""
        try:
            # This would use system notification APIs
            # For now, we'll use a simple approach
            title = alert_data.get('title', 'Casino Scanner Alert')
            message = alert_data.get('summary', '')

            # Try to use notify-send on Linux
            if os.name == 'posix':
                os.system(f'notify-send "{title}" "{message}"')
                return True
            else:
                # Windows/Mac notification would go here
                logger.info(f"Desktop alert: {title} - {message}")
                return True

        except Exception as e:
            logger.error(f"Desktop alert failed: {e}")
            return False


class AlertSystem:
    """
    Intelligent alerting system for casino vulnerability findings.
    Provides multi-channel notifications with smart filtering and prioritization.
    """

    def __init__(self, config_path: str = "config/alert_config.yaml"):
        self.config_path = config_path
        self.channels: Dict[str, AlertChannel] = {}
        self.rules: List[AlertRule] = []
        self.alert_history: List[Dict] = []
        self.max_history_size = 1000

        # Default alert rules for casino vulnerabilities
        self._initialize_default_rules()

        # Load configuration
        self.load_config()

        logger.info("Alert system initialized")

    def _initialize_default_rules(self):
        """Initialize default alert rules"""

        # Critical vulnerability alert
        self.rules.append(AlertRule(
            name="critical_vulnerability",
            condition=lambda data: (
                data.get('classification', {}).get('overall_score', 0) >= 9.0 and
                data.get('original_vulnerability', {}).get('severity') == 'critical'
            ),
            priority=10,
            channels=['cursor_ai', 'email', 'webhook'],
            template="critical_vulnerability_alert",
            cooldown_minutes=30
        ))

        # High-value opportunity alert
        self.rules.append(AlertRule(
            name="high_value_opportunity",
            condition=lambda data: (
                data.get('classification', {}).get('profit_potential_score', 0) >= 8.0 and
                data.get('classification', {}).get('exploitability_score', 0) >= 7.0
            ),
            priority=9,
            channels=['cursor_ai', 'webhook'],
            template="high_value_alert",
            cooldown_minutes=60
        ))

        # Bulk account creation vulnerability
        self.rules.append(AlertRule(
            name="bulk_account_creation",
            condition=lambda data: (
                'bulk' in data.get('original_vulnerability', {}).get('vulnerability_type', '') or
                'captcha' in data.get('original_vulnerability', {}).get('vulnerability_type', '')
            ),
            priority=8,
            channels=['cursor_ai', 'file'],
            template="bulk_creation_alert",
            cooldown_minutes=120
        ))

        # New region discovered
        self.rules.append(AlertRule(
            name="new_region_discovered",
            condition=lambda data: data.get('event_type') == 'region_discovered',
            priority=7,
            channels=['cursor_ai', 'file'],
            template="new_region_alert",
            cooldown_minutes=1440  # Daily
        ))

        # High target discovery rate
        self.rules.append(AlertRule(
            name="target_discovery_spike",
            condition=lambda data: (
                data.get('event_type') == 'target_discovery' and
                data.get('targets_discovered', 0) >= 20
            ),
            priority=6,
            channels=['cursor_ai'],
            template="discovery_spike_alert",
            cooldown_minutes=360  # 6 hours
        ))

    def load_config(self):
        """Load alert configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)

                # Load channels
                for channel_config in config.get('channels', []):
                    channel = AlertChannel(**channel_config)
                    self.channels[channel.name] = channel

                # Load custom rules
                for rule_config in config.get('rules', []):
                    rule = AlertRule(**rule_config)
                    self.rules.append(rule)

                logger.info(f"Loaded {len(self.channels)} channels and {len(self.rules)} rules from config")

        except Exception as e:
            logger.warning(f"Failed to load alert config: {e}")

    def save_config(self):
        """Save current configuration"""
        try:
            config = {
                'channels': [channel.__dict__ for channel in self.channels.values()],
                'rules': [rule.__dict__ for rule in self.rules]
            }

            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            logger.info("Alert configuration saved")

        except Exception as e:
            logger.error(f"Failed to save alert config: {e}")

    async def process_alert(self, alert_data: Dict) -> List[str]:
        """
        Process an alert and send notifications through appropriate channels

        Args:
            alert_data: Alert data dictionary

        Returns:
            List of channels that were successfully notified
        """
        triggered_channels = []

        try:
            # Check each rule
            for rule in self.rules:
                if rule.should_trigger(alert_data):
                    logger.info(f"Alert rule '{rule.name}' triggered")

                    # Format the alert message
                    formatted_alert = self._format_alert(rule.template, alert_data)

                    # Send through each channel
                    for channel_name in rule.channels:
                        if channel_name in self.channels:
                            channel = self.channels[channel_name]
                            success = await channel.send_alert(formatted_alert)
                            if success:
                                triggered_channels.append(channel_name)
                                logger.info(f"Alert sent via {channel_name}")
                            else:
                                logger.warning(f"Failed to send alert via {channel_name}")

                    # Mark rule as triggered
                    rule.mark_triggered()

                    # Record in history
                    self._record_alert_history(alert_data, rule, triggered_channels)

        except Exception as e:
            logger.error(f"Error processing alert: {e}")

        return triggered_channels

    def _format_alert(self, template: str, data: Dict) -> Dict:
        """Format alert data using template"""

        if template == "critical_vulnerability_alert":
            return {
                'subject': '🚨 CRITICAL CASINO VULNERABILITY FOUND',
                'title': 'Critical Vulnerability Alert',
                'priority': 'critical',
                'message': self._format_critical_vulnerability_alert(data),
                'summary': f"Critical vulnerability found: {data.get('original_vulnerability', {}).get('title', 'Unknown')}",
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

        elif template == "high_value_alert":
            return {
                'subject': '💰 HIGH-VALUE EXPLOITATION OPPORTUNITY',
                'title': 'High-Value Opportunity Alert',
                'priority': 'high',
                'message': self._format_high_value_alert(data),
                'summary': f"High-value opportunity: ${data.get('enhanced_metadata', {}).get('estimated_value', 'Unknown')}",
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

        elif template == "bulk_creation_alert":
            return {
                'subject': '🤖 BULK ACCOUNT CREATION VULNERABILITY',
                'title': 'Bulk Creation Vulnerability',
                'priority': 'high',
                'message': self._format_bulk_creation_alert(data),
                'summary': 'Automated account creation vulnerability detected',
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

        elif template == "new_region_alert":
            return {
                'subject': '🗺️ NEW GAMBLING REGION DISCOVERED',
                'title': 'New Region Discovered',
                'priority': 'medium',
                'message': self._format_new_region_alert(data),
                'summary': f"New gambling region discovered: {data.get('region', 'Unknown')}",
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

        elif template == "discovery_spike_alert":
            return {
                'subject': '📈 HIGH TARGET DISCOVERY RATE',
                'title': 'Target Discovery Spike',
                'priority': 'medium',
                'message': self._format_discovery_spike_alert(data),
                'summary': f"High target discovery rate: {data.get('targets_discovered', 0)} targets found",
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

        else:
            # Generic alert
            return {
                'subject': '🎰 CASINO SCANNER ALERT',
                'title': 'Casino Scanner Alert',
                'priority': 'medium',
                'message': json.dumps(data, indent=2),
                'summary': 'General alert from casino scanner',
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

    def _format_critical_vulnerability_alert(self, data: Dict) -> str:
        """Format critical vulnerability alert"""
        vuln = data.get('original_vulnerability', {})
        classification = data.get('classification', {})
        business_impact = data.get('business_impact', {})

        return f"""
        <h2>🚨 CRITICAL VULNERABILITY DISCOVERED</h2>

        <h3>{vuln.get('title', 'Unknown Vulnerability')}</h3>

        <p><strong>Severity:</strong> {vuln.get('severity', 'Unknown')}</p>
        <p><strong>Type:</strong> {vuln.get('vulnerability_type', 'Unknown')}</p>
        <p><strong>URL:</strong> {vuln.get('url', 'Unknown')}</p>

        <p><strong>Risk Assessment:</strong> {classification.get('risk_assessment', 'Unknown')}</p>
        <p><strong>Exploitability:</strong> {classification.get('exploitability_score', 0)}/10</p>
        <p><strong>Profit Potential:</strong> {classification.get('profit_potential_score', 0)}/10</p>

        <h4>Business Impact:</h4>
        <ul>
            <li>Financial Loss: {business_impact.get('financial_loss_potential', 'Unknown')}</li>
            <li>Regulatory Fines: {business_impact.get('regulatory_fines', 'Unknown')}</li>
            <li>Time to Remediate: {business_impact.get('time_to_remediate', 'Unknown')}</li>
        </ul>

        <p><strong>Recommended Action:</strong> {classification.get('recommended_action', 'Investigate immediately')}</p>

        <p><em>This alert was automatically generated by the Casino Vulnerability Scanner</em></p>
        """

    def _format_high_value_alert(self, data: Dict) -> str:
        """Format high-value opportunity alert"""
        vuln = data.get('original_vulnerability', {})
        classification = data.get('classification', {})
        metadata = data.get('enhanced_metadata', {})

        return f"""
        <h2>💰 HIGH-VALUE EXPLOITATION OPPORTUNITY</h2>

        <h3>{vuln.get('title', 'Unknown Opportunity')}</h3>

        <p><strong>Estimated Value:</strong> {metadata.get('estimated_value', 'Unknown')}</p>
        <p><strong>Time to Exploit:</strong> {classification.get('time_to_exploit', 'Unknown')}</p>
        <p><strong>Exploitability:</strong> {classification.get('exploitability_score', 0)}/10</p>

        <p><strong>URL:</strong> {vuln.get('url', 'Unknown')}</p>
        <p><strong>Type:</strong> {vuln.get('vulnerability_type', 'Unknown')}</p>

        <h4>Exploitation Vectors:</h4>
        <ul>
        {"".join(f"<li>{vector}</li>" for vector in data.get('exploitation_vectors', [])[:3])}
        </ul>

        <p><strong>Recommended Action:</strong> {classification.get('recommended_action', 'Consider exploitation')}</p>

        <p><em>Opportunity automatically identified by intelligent classification system</em></p>
        """

    def _format_bulk_creation_alert(self, data: Dict) -> str:
        """Format bulk account creation alert"""
        vuln = data.get('original_vulnerability', {})
        classification = data.get('classification', {})

        return f"""
        <h2>🤖 BULK ACCOUNT CREATION VULNERABILITY</h2>

        <h3>{vuln.get('title', 'Bulk Creation Vulnerability')}</h3>

        <p><strong>Impact:</strong> Unlimited automated account creation possible</p>
        <p><strong>Exploitability:</strong> {classification.get('exploitability_score', 0)}/10</p>
        <p><strong>Profit Potential:</strong> {classification.get('profit_potential_score', 0)}/10</p>

        <p><strong>URL:</strong> {vuln.get('url', 'Unknown')}</p>

        <h4>Potential Abuse:</h4>
        <ul>
            <li>Bonus system exploitation</li>
            <li>Referral program manipulation</li>
            <li>Affiliate fraud</li>
            <li>Account farming operations</li>
        </ul>

        <p><strong>Recommended Action:</strong> {classification.get('recommended_action', 'Implement immediate mitigation')}</p>

        <p><em>Automated detection of mass account creation vulnerability</em></p>
        """

    def _format_new_region_alert(self, data: Dict) -> str:
        """Format new region discovery alert"""
        return f"""
        <h2>🗺️ NEW GAMBLING REGION DISCOVERED</h2>

        <h3>Region: {data.get('region', 'Unknown')}</h3>
        <h3>Country Code: {data.get('country_code', 'Unknown')}</h3>

        <p><strong>Discovery Method:</strong> {data.get('discovery_method', 'Unknown')}</p>
        <p><strong>Confidence Score:</strong> {data.get('confidence_score', 0)}</p>
        <p><strong>Gambling Legal:</strong> {data.get('gambling_legal', 'Unknown')}</p>

        <p><strong>Potential Targets:</strong> {data.get('estimated_targets', 'Unknown')}</p>

        <p>The automated region discovery system has identified a new jurisdiction with gambling potential.</p>

        <p><em>Region automatically discovered by intelligent scanning system</em></p>
        """

    def _format_discovery_spike_alert(self, data: Dict) -> str:
        """Format target discovery spike alert"""
        return f"""
        <h2>📈 TARGET DISCOVERY SPIKE DETECTED</h2>

        <p><strong>Targets Discovered:</strong> {data.get('targets_discovered', 0)}</p>
        <p><strong>Region:</strong> {data.get('region', 'Multiple')}</p>
        <p><strong>Time Period:</strong> Recent scan cycle</p>

        <p><strong>High Priority Targets:</strong> {data.get('high_priority_targets', 0)}</p>
        <p><strong>Targets with Features:</strong> {data.get('targets_with_features', 0)}</p>

        <p>The target discovery system has found an unusually high number of potential casino targets.</p>

        <p><em>Automated detection of target discovery activity spike</em></p>
        """

    def _record_alert_history(self, alert_data: Dict, rule: AlertRule, channels: List[str]):
        """Record alert in history"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'rule_name': rule.name,
            'rule_priority': rule.priority,
            'channels_triggered': channels,
            'alert_data': alert_data
        }

        self.alert_history.append(history_entry)

        # Trim history if too large
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]

    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]

    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        recent_24h = [h for h in self.alert_history if h['timestamp'] >= last_24h.isoformat()]
        recent_7d = [h for h in self.alert_history if h['timestamp'] >= last_7d.isoformat()]

        return {
            'total_alerts': len(self.alert_history),
            'alerts_last_24h': len(recent_24h),
            'alerts_last_7d': len(recent_7d),
            'active_rules': len([r for r in self.rules if r.enabled]),
            'active_channels': len([c for c in self.channels.values() if c.enabled]),
            'most_triggered_rule': self._get_most_triggered_rule()
        }

    def _get_most_triggered_rule(self) -> Optional[str]:
        """Get the most frequently triggered rule"""
        if not self.alert_history:
            return None

        rule_counts = {}
        for entry in self.alert_history:
            rule_name = entry.get('rule_name', 'unknown')
            rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1

        return max(rule_counts.items(), key=lambda x: x[1])[0] if rule_counts else None

    async def test_alert_channels(self) -> Dict[str, bool]:
        """Test all alert channels"""
        test_data = {
            'event_type': 'test_alert',
            'message': 'This is a test alert from the Casino Vulnerability Scanner',
            'timestamp': datetime.now().isoformat()
        }

        results = {}
        for channel_name, channel in self.channels.items():
            try:
                success = await channel.send_alert(test_data)
                results[channel_name] = success
                logger.info(f"Test alert to {channel_name}: {'SUCCESS' if success else 'FAILED'}")
            except Exception as e:
                results[channel_name] = False
                logger.error(f"Test alert to {channel_name} failed: {e}")

        return results

    def add_custom_rule(self, name: str, condition: Callable[[Dict], bool],
                       priority: int, channels: List[str], template: str,
                       cooldown_minutes: int = 60) -> bool:
        """Add a custom alert rule"""
        try:
            rule = AlertRule(
                name=name,
                condition=condition,
                priority=priority,
                channels=channels,
                template=template,
                cooldown_minutes=cooldown_minutes,
                enabled=True
            )

            self.rules.append(rule)
            logger.info(f"Added custom alert rule: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add custom rule: {e}")
            return False

    def add_alert_channel(self, name: str, channel_type: str, config: Dict[str, Any]) -> bool:
        """Add a new alert channel"""
        try:
            channel = AlertChannel(
                name=name,
                type=channel_type,
                config=config,
                enabled=True
            )

            self.channels[name] = channel
            logger.info(f"Added alert channel: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add alert channel: {e}")
            return False


# Integration functions for the continuous scanner
async def alert_on_high_value_vulnerability(vulnerability_data: Dict, alert_system: AlertSystem):
    """Alert on high-value vulnerability discovery"""
    await alert_system.process_alert({
        'event_type': 'vulnerability_discovered',
        'original_vulnerability': vulnerability_data.get('original_vulnerability', {}),
        'classification': vulnerability_data.get('classification', {}),
        'enhanced_metadata': vulnerability_data.get('enhanced_metadata', {}),
        'exploitation_vectors': vulnerability_data.get('exploitation_vectors', []),
        'business_impact': vulnerability_data.get('business_impact', {})
    })


async def alert_on_region_discovery(region_data: Dict, alert_system: AlertSystem):
    """Alert on new region discovery"""
    await alert_system.process_alert({
        'event_type': 'region_discovered',
        'region': region_data.get('name', 'Unknown'),
        'country_code': region_data.get('code', 'Unknown'),
        'gambling_legal': region_data.get('gambling_legal', False),
        'casino_density': region_data.get('casino_density', 'unknown'),
        'estimated_targets': 'Unknown',  # Would be calculated
        'discovery_method': 'automated_scanning'
    })


async def alert_on_target_discovery(discovery_results: Dict, alert_system: AlertSystem):
    """Alert on high target discovery rates"""
    await alert_system.process_alert({
        'event_type': 'target_discovery',
        'region': discovery_results.get('region', 'Unknown'),
        'targets_discovered': discovery_results.get('targets_discovered', 0),
        'high_priority_targets': discovery_results.get('high_priority_targets', 0),
        'targets_with_features': discovery_results.get('targets_with_features', 0),
        'discovery_method': discovery_results.get('discovery_method', 'automated')
    })


# Standalone alert testing
async def test_alert_system():
    """Test the alert system"""
    alert_system = AlertSystem()

    # Add a test email channel (configure as needed)
    alert_system.add_alert_channel(
        'test_email',
        'email',
        {
            'to_email': 'test@example.com',
            'smtp': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'username': 'your_email@gmail.com',
                'password': 'your_password',
                'use_tls': True
            }
        }
    )

    # Add Cursor AI channel
    alert_system.add_alert_channel(
        'cursor_ai',
        'cursor_ai',
        {
            'api_url': 'https://api.cursor.ai/alerts',
            'api_key': 'your_cursor_api_key'
        }
    )

    # Test channels
    test_results = await alert_system.test_alert_channels()
    print("Channel test results:", test_results)

    # Test vulnerability alert
    test_vuln_data = {
        'original_vulnerability': {
            'title': 'Critical CAPTCHA Bypass Vulnerability',
            'severity': 'critical',
            'vulnerability_type': 'captcha_bypass',
            'url': 'https://example-casino.com'
        },
        'classification': {
            'overall_score': 9.5,
            'exploitability_score': 8.5,
            'profit_potential_score': 9.0,
            'risk_assessment': 'EXTREME - Immediate action required',
            'recommended_action': 'Immediate exploitation recommended'
        },
        'enhanced_metadata': {
            'estimated_value': '$500,000+'
        }
    }

    await alert_on_high_value_vulnerability(test_vuln_data, alert_system)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_alert_system())
