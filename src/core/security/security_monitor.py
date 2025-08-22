#!/usr/bin/env python3
"""
Security Monitoring and Alerting System for Claude Code V3.6.9
Real-time security event monitoring, threat detection, and incident response
"""

import asyncio
import json
import logging
import smtplib
import sqlite3
import time
import hashlib
import aiohttp
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import re
import subprocess
import threading
from queue import Queue
import yaml

class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ThreatType(Enum):
    INTRUSION_ATTEMPT = "intrusion_attempt"
    MALWARE_DETECTION = "malware_detection"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SECURITY_POLICY_VIOLATION = "security_policy_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    CONFIGURATION_CHANGE = "configuration_change"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    timestamp: datetime
    severity: AlertSeverity
    threat_type: ThreatType
    source_ip: Optional[str]
    target: Optional[str]
    description: str
    details: Dict[str, Any]
    indicators: List[str]
    mitigation_actions: List[str]
    false_positive_score: float = 0.0
    status: str = "open"

@dataclass
class SecurityAlert:
    """Security alert for notifications"""
    alert_id: str
    event_id: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    recipients: List[str]
    channels: List[str]
    acknowledged: bool = False
    resolved: bool = False

class LogAnalyzer:
    """Log file analysis for security events"""
    
    def __init__(self, log_patterns: Dict[str, List[str]]):
        self.log_patterns = log_patterns
        self.compiled_patterns = {}
        self.compile_patterns()
    
    def compile_patterns(self):
        """Compile regex patterns for performance"""
        for threat_type, patterns in self.log_patterns.items():
            self.compiled_patterns[threat_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def analyze_log_line(self, log_line: str, log_source: str) -> List[SecurityEvent]:
        """Analyze a single log line for security events"""
        events = []
        
        for threat_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(log_line)
                if match:
                    event = self.create_security_event(
                        threat_type, log_line, match, log_source
                    )
                    events.append(event)
        
        return events
    
    def create_security_event(self, threat_type: str, log_line: str, match: re.Match, log_source: str) -> SecurityEvent:
        """Create security event from log analysis"""
        event_id = hashlib.md5(f"{threat_type}:{log_line}:{time.time()}".encode()).hexdigest()[:12]
        
        # Extract common information
        source_ip = self.extract_ip(log_line)
        timestamp = self.extract_timestamp(log_line)
        
        # Determine severity based on threat type
        severity_mapping = {
            "intrusion_attempt": AlertSeverity.HIGH,
            "malware_detection": AlertSeverity.CRITICAL,
            "data_exfiltration": AlertSeverity.CRITICAL,
            "privilege_escalation": AlertSeverity.HIGH,
            "brute_force_attack": AlertSeverity.MEDIUM,
            "sql_injection": AlertSeverity.HIGH,
            "xss_attack": AlertSeverity.MEDIUM,
            "ddos_attack": AlertSeverity.HIGH,
            "unauthorized_access": AlertSeverity.HIGH,
            "security_policy_violation": AlertSeverity.MEDIUM,
            "anomalous_behavior": AlertSeverity.LOW,
            "configuration_change": AlertSeverity.INFO
        }
        
        severity = severity_mapping.get(threat_type, AlertSeverity.MEDIUM)
        
        return SecurityEvent(
            event_id=event_id,
            timestamp=timestamp or datetime.now(),
            severity=severity,
            threat_type=ThreatType(threat_type),
            source_ip=source_ip,
            target=log_source,
            description=f"{threat_type.replace('_', ' ').title()} detected in {log_source}",
            details={
                "log_line": log_line,
                "matched_pattern": match.pattern,
                "matched_text": match.group(0),
                "log_source": log_source
            },
            indicators=[match.group(0)] if match else [],
            mitigation_actions=self.get_mitigation_actions(threat_type)
        )
    
    def extract_ip(self, log_line: str) -> Optional[str]:
        """Extract IP address from log line"""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        match = re.search(ip_pattern, log_line)
        return match.group(0) if match else None
    
    def extract_timestamp(self, log_line: str) -> Optional[datetime]:
        """Extract timestamp from log line"""
        # Common log timestamp patterns
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',  # DD/MMM/YYYY:HH:MM:SS
            r'\w{3} \d{2} \d{2}:\d{2}:\d{2}',        # MMM DD HH:MM:SS
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                try:
                    # Try to parse the timestamp
                    timestamp_str = match.group(0)
                    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
        
        return None
    
    def get_mitigation_actions(self, threat_type: str) -> List[str]:
        """Get suggested mitigation actions for threat type"""
        mitigation_map = {
            "intrusion_attempt": [
                "Block source IP address",
                "Review access logs",
                "Check for privilege escalation",
                "Monitor for lateral movement"
            ],
            "malware_detection": [
                "Isolate affected system",
                "Run full system scan",
                "Check for persistence mechanisms",
                "Review recent file changes"
            ],
            "data_exfiltration": [
                "Block network traffic",
                "Review data access logs",
                "Check for unauthorized file access",
                "Assess data sensitivity"
            ],
            "brute_force_attack": [
                "Implement account lockout",
                "Block source IP",
                "Monitor for successful logins",
                "Review password policies"
            ],
            "sql_injection": [
                "Block malicious requests",
                "Review database logs",
                "Check for data extraction",
                "Update input validation"
            ],
            "ddos_attack": [
                "Implement rate limiting",
                "Block attack sources",
                "Scale infrastructure",
                "Monitor service availability"
            ]
        }
        
        return mitigation_map.get(threat_type, ["Investigate further", "Monitor for escalation"])

class ThreatDetector:
    """Real-time threat detection engine"""
    
    def __init__(self):
        self.detection_rules = self.load_detection_rules()
        self.behavioral_baselines = {}
        self.threat_intelligence = self.load_threat_intelligence()
    
    def load_detection_rules(self) -> Dict[str, Any]:
        """Load threat detection rules"""
        return {
            "failed_login_threshold": {
                "threshold": 5,
                "time_window": 300,  # 5 minutes
                "action": "block_ip"
            },
            "sql_injection_patterns": [
                r"('|(\\'))|\s*(union|select|insert|delete|update|drop|create|alter|exec|execute)\s+",
                r"(;|--|\*/|\*)",
                r"(char|ascii|substring|length|mid|convert)\s*\("
            ],
            "xss_patterns": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe|<object|<embed"
            ],
            "file_access_anomalies": {
                "sensitive_files": [
                    "/etc/passwd", "/etc/shadow", "web.config", 
                    ".env", "config.yaml", "secrets.json"
                ],
                "unusual_access_times": ["22:00-06:00"],
                "bulk_access_threshold": 10
            },
            "network_anomalies": {
                "connection_spike_threshold": 100,
                "data_transfer_spike": 1073741824,  # 1GB
                "suspicious_ports": [23, 135, 139, 445, 1433, 3389]
            }
        }
    
    def load_threat_intelligence(self) -> Dict[str, List[str]]:
        """Load threat intelligence feeds"""
        return {
            "malicious_ips": [
                # Example malicious IPs (in real implementation, load from threat feeds)
                "192.168.1.100", "10.0.0.50"
            ],
            "malicious_domains": [
                "malicious-domain.com", "phishing-site.net"
            ],
            "malware_signatures": [
                "EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
                "malware_signature_hash"
            ]
        }
    
    async def detect_brute_force(self, events: List[SecurityEvent]) -> List[SecurityEvent]:
        """Detect brute force attacks"""
        detected_events = []
        
        # Group failed login attempts by source IP
        failed_logins = {}
        current_time = datetime.now()
        
        for event in events:
            if "failed" in event.description.lower() and "login" in event.description.lower():
                source_ip = event.source_ip
                if source_ip:
                    if source_ip not in failed_logins:
                        failed_logins[source_ip] = []
                    failed_logins[source_ip].append(event)
        
        # Check for brute force patterns
        for source_ip, login_events in failed_logins.items():
            recent_attempts = [
                e for e in login_events 
                if (current_time - e.timestamp).total_seconds() <= 300  # 5 minutes
            ]
            
            if len(recent_attempts) >= 5:
                event_id = hashlib.md5(f"brute_force:{source_ip}:{current_time}".encode()).hexdigest()[:12]
                
                brute_force_event = SecurityEvent(
                    event_id=event_id,
                    timestamp=current_time,
                    severity=AlertSeverity.HIGH,
                    threat_type=ThreatType.BRUTE_FORCE_ATTACK,
                    source_ip=source_ip,
                    target="authentication_system",
                    description=f"Brute force attack detected from {source_ip}",
                    details={
                        "failed_attempts": len(recent_attempts),
                        "time_window": "5 minutes",
                        "attack_pattern": "multiple_failed_logins"
                    },
                    indicators=[f"ip:{source_ip}", f"attempts:{len(recent_attempts)}"],
                    mitigation_actions=[
                        f"Block IP {source_ip}",
                        "Implement account lockout",
                        "Monitor for successful logins",
                        "Review authentication logs"
                    ]
                )
                
                detected_events.append(brute_force_event)
        
        return detected_events
    
    async def detect_anomalous_behavior(self, system_metrics: Dict[str, Any]) -> List[SecurityEvent]:
        """Detect anomalous system behavior"""
        detected_events = []
        current_time = datetime.now()
        
        # CPU usage anomaly
        cpu_usage = system_metrics.get("cpu_percent", 0)
        if cpu_usage > 90:
            event_id = hashlib.md5(f"cpu_anomaly:{cpu_usage}:{current_time}".encode()).hexdigest()[:12]
            
            cpu_event = SecurityEvent(
                event_id=event_id,
                timestamp=current_time,
                severity=AlertSeverity.MEDIUM,
                threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                source_ip=None,
                target="system",
                description="Abnormally high CPU usage detected",
                details={
                    "cpu_usage": cpu_usage,
                    "threshold": 90,
                    "potential_causes": ["crypto_mining", "ddos_participation", "malware_execution"]
                },
                indicators=[f"cpu_usage:{cpu_usage}%"],
                mitigation_actions=[
                    "Investigate running processes",
                    "Check for malware",
                    "Monitor network traffic",
                    "Review system logs"
                ]
            )
            
            detected_events.append(cpu_event)
        
        # Memory usage anomaly
        memory_usage = system_metrics.get("memory_percent", 0)
        if memory_usage > 85:
            event_id = hashlib.md5(f"memory_anomaly:{memory_usage}:{current_time}".encode()).hexdigest()[:12]
            
            memory_event = SecurityEvent(
                event_id=event_id,
                timestamp=current_time,
                severity=AlertSeverity.MEDIUM,
                threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                source_ip=None,
                target="system",
                description="Abnormally high memory usage detected",
                details={
                    "memory_usage": memory_usage,
                    "threshold": 85,
                    "potential_causes": ["memory_leak", "malware", "resource_exhaustion"]
                },
                indicators=[f"memory_usage:{memory_usage}%"],
                mitigation_actions=[
                    "Investigate memory-intensive processes",
                    "Check for memory leaks",
                    "Monitor application performance",
                    "Review system resources"
                ]
            )
            
            detected_events.append(memory_event)
        
        # Network anomaly
        network_connections = system_metrics.get("network_connections", 0)
        if network_connections > 500:
            event_id = hashlib.md5(f"network_anomaly:{network_connections}:{current_time}".encode()).hexdigest()[:12]
            
            network_event = SecurityEvent(
                event_id=event_id,
                timestamp=current_time,
                severity=AlertSeverity.MEDIUM,
                threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                source_ip=None,
                target="network",
                description="Unusually high number of network connections",
                details={
                    "connection_count": network_connections,
                    "threshold": 500,
                    "potential_causes": ["ddos_attack", "botnet_activity", "application_bug"]
                },
                indicators=[f"connections:{network_connections}"],
                mitigation_actions=[
                    "Investigate network connections",
                    "Check for suspicious processes",
                    "Monitor network traffic",
                    "Review firewall logs"
                ]
            )
            
            detected_events.append(network_event)
        
        return detected_events
    
    def check_threat_intelligence(self, event: SecurityEvent) -> bool:
        """Check event against threat intelligence"""
        # Check malicious IPs
        if event.source_ip and event.source_ip in self.threat_intelligence["malicious_ips"]:
            event.severity = AlertSeverity.CRITICAL
            event.indicators.append(f"malicious_ip:{event.source_ip}")
            return True
        
        # Check for malicious patterns in event details
        event_text = json.dumps(event.details).lower()
        for domain in self.threat_intelligence["malicious_domains"]:
            if domain in event_text:
                event.severity = AlertSeverity.HIGH
                event.indicators.append(f"malicious_domain:{domain}")
                return True
        
        return False

class AlertManager:
    """Security alert management and notification system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_queue = Queue()
        self.notification_channels = self.setup_notification_channels()
        
    def setup_notification_channels(self) -> Dict[str, Any]:
        """Setup notification channels"""
        channels = {}
        
        # Email notifications
        if self.config.get("email", {}).get("enabled", False):
            channels["email"] = {
                "smtp_server": self.config["email"]["smtp_server"],
                "smtp_port": self.config["email"]["smtp_port"],
                "username": self.config["email"]["username"],
                "password": self.config["email"]["password"],
                "from_address": self.config["email"]["from_address"]
            }
        
        # Slack notifications
        if self.config.get("slack", {}).get("enabled", False):
            channels["slack"] = {
                "webhook_url": self.config["slack"]["webhook_url"]
            }
        
        # Teams notifications
        if self.config.get("teams", {}).get("enabled", False):
            channels["teams"] = {
                "webhook_url": self.config["teams"]["webhook_url"]
            }
        
        return channels
    
    async def create_alert(self, event: SecurityEvent) -> SecurityAlert:
        """Create alert from security event"""
        alert_id = hashlib.md5(f"alert:{event.event_id}:{time.time()}".encode()).hexdigest()[:12]
        
        # Determine recipients based on severity
        recipients = self.get_recipients_for_severity(event.severity)
        channels = self.get_channels_for_severity(event.severity)
        
        alert = SecurityAlert(
            alert_id=alert_id,
            event_id=event.event_id,
            severity=event.severity,
            title=f"{event.threat_type.value.replace('_', ' ').title()} - {event.severity.value.upper()}",
            description=event.description,
            timestamp=event.timestamp,
            recipients=recipients,
            channels=channels
        )
        
        return alert
    
    def get_recipients_for_severity(self, severity: AlertSeverity) -> List[str]:
        """Get notification recipients based on severity"""
        recipients = []
        
        severity_mapping = {
            AlertSeverity.CRITICAL: self.config.get("recipients", {}).get("critical", []),
            AlertSeverity.HIGH: self.config.get("recipients", {}).get("high", []),
            AlertSeverity.MEDIUM: self.config.get("recipients", {}).get("medium", []),
            AlertSeverity.LOW: self.config.get("recipients", {}).get("low", []),
            AlertSeverity.INFO: self.config.get("recipients", {}).get("info", [])
        }
        
        return severity_mapping.get(severity, [])
    
    def get_channels_for_severity(self, severity: AlertSeverity) -> List[str]:
        """Get notification channels based on severity"""
        channels = []
        
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            channels.extend(["email", "slack", "teams"])
        elif severity == AlertSeverity.MEDIUM:
            channels.extend(["email", "slack"])
        else:
            channels.append("email")
        
        # Filter to only enabled channels
        enabled_channels = [ch for ch in channels if ch in self.notification_channels]
        
        return enabled_channels
    
    async def send_email_alert(self, alert: SecurityAlert):
        """Send email alert"""
        if "email" not in self.notification_channels:
            return
        
        email_config = self.notification_channels["email"]
        
        try:
            msg = MimeMultipart()
            msg['From'] = email_config["from_address"]
            msg['To'] = ", ".join(alert.recipients)
            msg['Subject'] = f"SECURITY ALERT: {alert.title}"
            
            body = f"""
SECURITY ALERT NOTIFICATION

Alert ID: {alert.alert_id}
Severity: {alert.severity.value.upper()}
Timestamp: {alert.timestamp}

Description: {alert.description}

Event Details:
- Event ID: {alert.event_id}
- Threat Type: {alert.severity.value}

This is an automated security alert. Please investigate immediately.
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["from_address"], alert.recipients, text)
            server.quit()
            
            logging.info(f"Email alert sent for {alert.alert_id}")
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {str(e)}")
    
    async def send_slack_alert(self, alert: SecurityAlert):
        """Send Slack alert"""
        if "slack" not in self.notification_channels:
            return
        
        slack_config = self.notification_channels["slack"]
        
        try:
            # Determine color based on severity
            color_map = {
                AlertSeverity.CRITICAL: "#FF0000",  # Red
                AlertSeverity.HIGH: "#FF8C00",      # Orange
                AlertSeverity.MEDIUM: "#FFD700",    # Yellow
                AlertSeverity.LOW: "#00FF00",       # Green
                AlertSeverity.INFO: "#0000FF"       # Blue
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#808080"),
                        "title": f"🚨 {alert.title}",
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "Alert ID",
                                "value": alert.alert_id,
                                "short": True
                            },
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ],
                        "footer": "Claude Code Security Monitor",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(slack_config["webhook_url"], json=payload) as response:
                    if response.status == 200:
                        logging.info(f"Slack alert sent for {alert.alert_id}")
                    else:
                        logging.error(f"Failed to send Slack alert: {response.status}")
                        
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {str(e)}")
    
    async def send_alert(self, alert: SecurityAlert):
        """Send alert through configured channels"""
        for channel in alert.channels:
            if channel == "email":
                await self.send_email_alert(alert)
            elif channel == "slack":
                await self.send_slack_alert(alert)
            # Add more channels as needed

class SecurityMonitor:
    """Main security monitoring system"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.db_path = Path("security/security_events.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.log_analyzer = LogAnalyzer(self.config.get("log_patterns", {}))
        self.threat_detector = ThreatDetector()
        self.alert_manager = AlertManager(self.config.get("notifications", {}))
        
        # Initialize database
        self.init_database()
        
        # Event processing
        self.event_queue = Queue()
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security/security_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load monitoring configuration"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            "log_patterns": {
                "brute_force_attack": [
                    r"Failed password for .* from (\d+\.\d+\.\d+\.\d+)",
                    r"authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)",
                    r"Invalid user .* from (\d+\.\d+\.\d+\.\d+)"
                ],
                "sql_injection": [
                    r"SELECT.*FROM.*WHERE.*\=.*\'\;\-\-",
                    r"UNION.*SELECT",
                    r"DROP.*TABLE",
                    r"INSERT.*INTO.*VALUES"
                ],
                "xss_attack": [
                    r"<script.*>",
                    r"javascript:",
                    r"onload\=",
                    r"onerror\="
                ],
                "intrusion_attempt": [
                    r"Unauthorized access attempt",
                    r"Access denied for user",
                    r"Permission denied",
                    r"403 Forbidden"
                ]
            },
            "monitoring": {
                "log_files": [
                    "/var/log/auth.log",
                    "/var/log/nginx/access.log",
                    "/var/log/nginx/error.log",
                    "security/audit.log"
                ],
                "check_interval": 60,  # seconds
                "max_events_per_check": 1000
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_address": ""
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "recipients": {
                    "critical": ["security-team@company.com"],
                    "high": ["security-team@company.com"],
                    "medium": ["security-team@company.com"],
                    "low": ["security-admin@company.com"],
                    "info": ["security-admin@company.com"]
                }
            }
        }
    
    def init_database(self):
        """Initialize security events database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP,
                    severity TEXT,
                    threat_type TEXT,
                    source_ip TEXT,
                    target TEXT,
                    description TEXT,
                    details TEXT,
                    indicators TEXT,
                    mitigation_actions TEXT,
                    false_positive_score REAL,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    alert_id TEXT PRIMARY KEY,
                    event_id TEXT,
                    severity TEXT,
                    title TEXT,
                    description TEXT,
                    timestamp TIMESTAMP,
                    recipients TEXT,
                    channels TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES security_events (event_id)
                )
            ''')
    
    def store_event(self, event: SecurityEvent):
        """Store security event in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO security_events 
                (event_id, timestamp, severity, threat_type, source_ip, target, 
                 description, details, indicators, mitigation_actions, 
                 false_positive_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.timestamp,
                event.severity.value,
                event.threat_type.value,
                event.source_ip,
                event.target,
                event.description,
                json.dumps(event.details),
                json.dumps(event.indicators),
                json.dumps(event.mitigation_actions),
                event.false_positive_score,
                event.status
            ))
    
    def store_alert(self, alert: SecurityAlert):
        """Store security alert in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO security_alerts 
                (alert_id, event_id, severity, title, description, timestamp, 
                 recipients, channels, acknowledged, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.event_id,
                alert.severity.value,
                alert.title,
                alert.description,
                alert.timestamp,
                json.dumps(alert.recipients),
                json.dumps(alert.channels),
                alert.acknowledged,
                alert.resolved
            ))
    
    async def monitor_logs(self):
        """Monitor log files for security events"""
        log_files = self.config.get("monitoring", {}).get("log_files", [])
        
        # Track file positions to avoid re-reading
        file_positions = {}
        
        while self.running:
            for log_file in log_files:
                log_path = Path(log_file)
                if not log_path.exists():
                    continue
                
                try:
                    # Get current file size
                    current_size = log_path.stat().st_size
                    last_position = file_positions.get(str(log_path), 0)
                    
                    # Only read new content
                    if current_size > last_position:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            f.seek(last_position)
                            new_lines = f.readlines()
                            file_positions[str(log_path)] = f.tell()
                        
                        # Analyze new log lines
                        for line in new_lines:
                            line = line.strip()
                            if line:
                                events = self.log_analyzer.analyze_log_line(line, str(log_path))
                                for event in events:
                                    await self.process_event(event)
                
                except Exception as e:
                    self.logger.error(f"Error monitoring log file {log_file}: {str(e)}")
            
            # Wait before next check
            await asyncio.sleep(self.config.get("monitoring", {}).get("check_interval", 60))
    
    async def monitor_system_metrics(self):
        """Monitor system metrics for anomalies"""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "network_connections": len(psutil.net_connections()),
                    "process_count": len(psutil.pids())
                }
                
                # Detect anomalies
                anomaly_events = await self.threat_detector.detect_anomalous_behavior(system_metrics)
                
                for event in anomaly_events:
                    await self.process_event(event)
                
            except Exception as e:
                self.logger.error(f"Error monitoring system metrics: {str(e)}")
            
            # Check metrics every 5 minutes
            await asyncio.sleep(300)
    
    async def process_event(self, event: SecurityEvent):
        """Process a security event"""
        try:
            # Check against threat intelligence
            self.threat_detector.check_threat_intelligence(event)
            
            # Store event
            self.store_event(event)
            
            # Create and send alert if needed
            if event.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                alert = await self.alert_manager.create_alert(event)
                self.store_alert(alert)
                await self.alert_manager.send_alert(alert)
            
            self.logger.info(f"Processed security event: {event.event_id} - {event.description}")
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {str(e)}")
    
    async def start_monitoring(self):
        """Start the security monitoring system"""
        self.running = True
        self.logger.info("Starting security monitoring system")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.monitor_logs()),
            asyncio.create_task(self.monitor_system_metrics())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop the security monitoring system"""
        self.running = False
        self.logger.info("Stopping security monitoring system")
    
    def get_events_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of security events"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get event counts by severity
            cursor.execute('''
                SELECT severity, COUNT(*) as count
                FROM security_events 
                WHERE timestamp > ?
                GROUP BY severity
            ''', (cutoff_time,))
            
            severity_counts = dict(cursor.fetchall())
            
            # Get event counts by threat type
            cursor.execute('''
                SELECT threat_type, COUNT(*) as count
                FROM security_events 
                WHERE timestamp > ?
                GROUP BY threat_type
            ''', (cutoff_time,))
            
            threat_type_counts = dict(cursor.fetchall())
            
            # Get total events
            cursor.execute('''
                SELECT COUNT(*) as total
                FROM security_events 
                WHERE timestamp > ?
            ''', (cutoff_time,))
            
            total_events = cursor.fetchone()[0]
            
            return {
                "time_period_hours": hours,
                "total_events": total_events,
                "severity_distribution": severity_counts,
                "threat_type_distribution": threat_type_counts,
                "summary_generated_at": datetime.now().isoformat()
            }


async def main():
    """Main execution for security monitoring"""
    monitor = SecurityMonitor()
    
    try:
        print("Starting Claude Code Security Monitor...")
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nShutting down security monitor...")
        monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())