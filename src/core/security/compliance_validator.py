#!/usr/bin/env python3
"""
Compliance Validation Framework for Claude Code V3.6.9
Automated compliance checking against security frameworks
"""

import re
import json
import yaml
import subprocess
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

class ComplianceFramework(Enum):
    OWASP_TOP_10 = "OWASP_TOP_10_2023"
    NIST_CSF = "NIST_CSF"
    SOC2_TYPE_II = "SOC2_TYPE_II"
    ISO_27001 = "ISO_27001"
    PCI_DSS = "PCI_DSS"
    GDPR = "GDPR"
    HIPAA = "HIPAA"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    NEEDS_REVIEW = "needs_review"

@dataclass
class ComplianceRule:
    framework: ComplianceFramework
    rule_id: str
    title: str
    description: str
    requirement: str
    control_objectives: List[str]
    validation_methods: List[str]
    automated_check: bool
    weight: float  # Importance weight (0.0 - 1.0)
    references: List[str]

@dataclass
class ComplianceResult:
    rule_id: str
    framework: ComplianceFramework
    status: ComplianceStatus
    score: float  # 0.0 - 100.0
    findings: List[str]
    evidence: List[str]
    recommendations: List[str]
    assessed_at: datetime
    assessor: str = "automated"

class OWASPTop10Validator:
    """OWASP Top 10 2023 compliance validator"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.rules = self._load_owasp_rules()
    
    def _load_owasp_rules(self) -> List[ComplianceRule]:
        """Load OWASP Top 10 compliance rules"""
        return [
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A01",
                title="Broken Access Control",
                description="Failures related to access control policies",
                requirement="Implement proper access controls and authorization checks",
                control_objectives=[
                    "Deny by default except for public resources",
                    "Implement access control mechanisms once and re-use",
                    "Model access controls to enforce ownership",
                    "Disable web server directory listing",
                    "Log access control failures and alert administrators"
                ],
                validation_methods=["static_analysis", "code_review", "dynamic_testing"],
                automated_check=True,
                weight=1.0,
                references=["https://owasp.org/Top10/A01_2021-Broken_Access_Control/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A02",
                title="Cryptographic Failures",
                description="Failures related to cryptography which often lead to exposure of sensitive data",
                requirement="Protect data in transit and at rest using strong cryptography",
                control_objectives=[
                    "Classify data processed and stored by the application",
                    "Don't store sensitive data unnecessarily",
                    "Encrypt all sensitive data at rest",
                    "Ensure up-to-date and strong standard algorithms",
                    "Use proper key management"
                ],
                validation_methods=["static_analysis", "configuration_review", "cryptographic_review"],
                automated_check=True,
                weight=1.0,
                references=["https://owasp.org/Top10/A02_2021-Cryptographic_Failures/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A03",
                title="Injection",
                description="Code injection flaws such as SQL, NoSQL, OS, and LDAP injection",
                requirement="Validate, filter, and sanitize all user input",
                control_objectives=[
                    "Use safe APIs which avoid interpreter entirely",
                    "Use positive server-side input validation",
                    "Escape special characters using specific escape syntax",
                    "Use LIMIT and other SQL controls within queries",
                    "Use parameterized queries or prepared statements"
                ],
                validation_methods=["static_analysis", "dynamic_testing", "code_review"],
                automated_check=True,
                weight=1.0,
                references=["https://owasp.org/Top10/A03_2021-Injection/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A04",
                title="Insecure Design",
                description="Missing or ineffective control design",
                requirement="Use secure design patterns and threat modeling",
                control_objectives=[
                    "Establish and use a secure development lifecycle",
                    "Establish and use a library of secure design patterns",
                    "Use threat modeling for critical authentication",
                    "Integrate security language and controls into user stories",
                    "Write unit and integration tests to validate all critical flows"
                ],
                validation_methods=["design_review", "threat_modeling", "architecture_review"],
                automated_check=False,
                weight=0.8,
                references=["https://owasp.org/Top10/A04_2021-Insecure_Design/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A05",
                title="Security Misconfiguration",
                description="Security misconfigurations in any part of the application stack",
                requirement="Implement secure configurations and hardening",
                control_objectives=[
                    "A repeatable hardening process makes it fast and easy to deploy another environment",
                    "A minimal platform without unnecessary features",
                    "Review and update configurations appropriate to all security notes",
                    "A segmented application architecture provides effective separation",
                    "Automated process to verify effectiveness of configurations"
                ],
                validation_methods=["configuration_scan", "security_assessment", "penetration_testing"],
                automated_check=True,
                weight=0.9,
                references=["https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A06",
                title="Vulnerable and Outdated Components",
                description="Using components with known vulnerabilities",
                requirement="Maintain up-to-date and secure components",
                control_objectives=[
                    "Remove unused dependencies and unnecessary features",
                    "Continuously inventory versions of both client-side and server-side components",
                    "Monitor for security vulnerabilities in components",
                    "Only obtain components from official sources over secure links",
                    "Monitor for unmaintained libraries and components"
                ],
                validation_methods=["dependency_scan", "vulnerability_assessment", "software_composition_analysis"],
                automated_check=True,
                weight=1.0,
                references=["https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A07",
                title="Identification and Authentication Failures",
                description="Failures related to user identity confirmation and authentication",
                requirement="Implement strong authentication and session management",
                control_objectives=[
                    "Implement multi-factor authentication to prevent automated attacks",
                    "Do not ship or deploy with any default credentials",
                    "Implement weak password checks",
                    "Align password length, complexity and rotation policies",
                    "Harden registration, credential recovery, and API pathways"
                ],
                validation_methods=["authentication_testing", "session_analysis", "credential_policy_review"],
                automated_check=True,
                weight=1.0,
                references=["https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A08",
                title="Software and Data Integrity Failures",
                description="Code and infrastructure that do not protect against integrity violations",
                requirement="Implement integrity controls for software and data",
                control_objectives=[
                    "Use digital signatures or similar mechanisms to verify software integrity",
                    "Ensure libraries and dependencies are consuming trusted repositories",
                    "Use a software supply chain security tool",
                    "Ensure that your CI/CD pipeline has proper segregation",
                    "Ensure unsigned or unencrypted serialized data is not sent to untrusted clients"
                ],
                validation_methods=["integrity_verification", "supply_chain_analysis", "serialization_review"],
                automated_check=True,
                weight=0.8,
                references=["https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A09",
                title="Security Logging and Monitoring Failures",
                description="Insufficient logging and monitoring capabilities",
                requirement="Implement comprehensive logging and monitoring",
                control_objectives=[
                    "Ensure all login, access control failures can be logged",
                    "Ensure that logs are generated in a format that log management solutions can consume",
                    "Ensure log data is encoded correctly to prevent injections",
                    "Ensure high-value transactions have an audit trail",
                    "Establish effective monitoring and alerting"
                ],
                validation_methods=["logging_assessment", "monitoring_review", "incident_response_testing"],
                automated_check=True,
                weight=0.9,
                references=["https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/"]
            ),
            ComplianceRule(
                framework=ComplianceFramework.OWASP_TOP_10,
                rule_id="A10",
                title="Server-Side Request Forgery",
                description="SSRF flaws that allow attackers to send crafted requests",
                requirement="Validate and sanitize all user-supplied input data",
                control_objectives=[
                    "Sanitize and validate all client-supplied input data",
                    "Enforce the URL schema, port, and destination with a positive allow list",
                    "Do not send raw responses to clients",
                    "Disable HTTP redirections",
                    "Be aware of the URL consistency to avoid attacks such as DNS rebinding"
                ],
                validation_methods=["input_validation_testing", "network_segmentation_review", "whitelist_validation"],
                automated_check=True,
                weight=0.8,
                references=["https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/"]
            )
        ]
    
    async def validate_a01_access_control(self) -> ComplianceResult:
        """Validate A01: Broken Access Control"""
        findings = []
        evidence = []
        score = 100.0
        
        # Check for authorization bypasses
        auth_patterns = [
            r'if\s*\(\s*user\.is_admin\s*\)\s*{[^}]*}',  # Simple admin checks
            r'@RequiresRoles\s*\(\s*["\']admin["\']',     # Role-based annotations
            r'hasRole\s*\(\s*["\']',                      # Role checking functions
            r'checkPermission\s*\(',                     # Permission checks
        ]
        
        # Scan for access control implementations
        source_files = list(self.base_dir.rglob("*.py")) + list(self.base_dir.rglob("*.js"))
        auth_implementations = 0
        total_files = 0
        
        for file_path in source_files:
            if any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '__pycache__']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                total_files += 1
                
                for pattern in auth_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        auth_implementations += 1
                        evidence.append(f"Access control found in {file_path}")
                        break
                        
                # Check for potential bypasses
                bypass_patterns = [
                    r'#.*TODO.*auth',
                    r'//.*TODO.*auth',
                    r'bypass.*auth',
                    r'skip.*auth',
                    r'disable.*auth'
                ]
                
                for pattern in bypass_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings.append(f"Potential authorization bypass in {file_path}")
                        score -= 10
                        
            except Exception:
                continue
        
        # Calculate score based on implementation coverage
        if total_files > 0:
            coverage = auth_implementations / total_files * 100
            if coverage < 20:
                findings.append("Low access control implementation coverage")
                score -= 30
            elif coverage < 50:
                findings.append("Medium access control implementation coverage")
                score -= 15
        
        # Check for default access policies
        config_files = list(self.base_dir.rglob("*.yaml")) + list(self.base_dir.rglob("*.json"))
        deny_by_default = False
        
        for config_file in config_files:
            try:
                content = config_file.read_text()
                if re.search(r'default.*deny|deny.*default', content, re.IGNORECASE):
                    deny_by_default = True
                    evidence.append(f"Deny-by-default policy found in {config_file}")
                    break
            except Exception:
                continue
        
        if not deny_by_default:
            findings.append("No deny-by-default access policy found")
            score -= 20
        
        status = self._determine_status(score)
        
        return ComplianceResult(
            rule_id="A01",
            framework=ComplianceFramework.OWASP_TOP_10,
            status=status,
            score=max(0, score),
            findings=findings,
            evidence=evidence,
            recommendations=self._get_a01_recommendations(findings),
            assessed_at=datetime.now()
        )
    
    async def validate_a02_crypto_failures(self) -> ComplianceResult:
        """Validate A02: Cryptographic Failures"""
        findings = []
        evidence = []
        score = 100.0
        
        # Check for weak cryptographic algorithms
        weak_crypto_patterns = [
            r'MD5\s*\(',
            r'SHA1\s*\(',
            r'DES\s*\(',
            r'RC4\s*\(',
            r'md5\s*\(',
            r'sha1\s*\(',
            r'hashlib\.md5',
            r'hashlib\.sha1',
            r'Cipher\.AES.*MODE_ECB'
        ]
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'secret\s*=\s*["\'][^"\']{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']{8,}["\']',
            r'private[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'-----BEGIN.*PRIVATE KEY-----'
        ]
        
        source_files = list(self.base_dir.rglob("*.py")) + list(self.base_dir.rglob("*.js")) + list(self.base_dir.rglob("*.java"))
        
        for file_path in source_files:
            if any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '__pycache__']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Check for weak crypto
                for pattern in weak_crypto_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append(f"Weak cryptographic algorithm found in {file_path}: {match.group()}")
                        score -= 15
                
                # Check for hardcoded secrets
                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append(f"Hardcoded secret found in {file_path}")
                        score -= 20
                
                # Check for strong crypto usage
                strong_crypto_patterns = [
                    r'AES.*256',
                    r'SHA256',
                    r'SHA512',
                    r'bcrypt',
                    r'scrypt',
                    r'PBKDF2'
                ]
                
                for pattern in strong_crypto_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(f"Strong cryptography found in {file_path}")
                        break
                        
            except Exception:
                continue
        
        # Check for TLS configuration
        tls_configs = list(self.base_dir.rglob("*.conf")) + list(self.base_dir.rglob("nginx.conf"))
        tls_v12_plus = False
        
        for config_file in tls_configs:
            try:
                content = config_file.read_text()
                if re.search(r'TLSv1\.[23]|ssl_protocols.*TLSv1\.[23]', content):
                    tls_v12_plus = True
                    evidence.append(f"TLS 1.2+ configuration found in {config_file}")
                    
                if re.search(r'SSLv[23]|TLSv1\.0|TLSv1\.1', content):
                    findings.append(f"Insecure TLS version found in {config_file}")
                    score -= 10
                    
            except Exception:
                continue
        
        if not tls_v12_plus:
            findings.append("No TLS 1.2+ configuration found")
            score -= 15
        
        status = self._determine_status(score)
        
        return ComplianceResult(
            rule_id="A02",
            framework=ComplianceFramework.OWASP_TOP_10,
            status=status,
            score=max(0, score),
            findings=findings,
            evidence=evidence,
            recommendations=self._get_a02_recommendations(findings),
            assessed_at=datetime.now()
        )
    
    async def validate_a03_injection(self) -> ComplianceResult:
        """Validate A03: Injection"""
        findings = []
        evidence = []
        score = 100.0
        
        # SQL injection patterns
        sql_injection_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE).*\+.*',
            r'execute\s*\(\s*["\'].*\+.*["\']',
            r'query\s*\(\s*["\'].*\+.*["\']',
            r'f["\'].*SELECT.*{.*}.*["\']',
            r'cursor\.execute\s*\([^)]*%[^)]*\)'
        ]
        
        # Command injection patterns
        command_injection_patterns = [
            r'os\.system\s*\(\s*.*\+',
            r'subprocess\.(call|run|Popen).*shell\s*=\s*True',
            r'exec\s*\(\s*.*\+',
            r'eval\s*\(\s*.*\+',
            r'Runtime\.getRuntime\(\)\.exec'
        ]
        
        # Safe coding patterns
        safe_patterns = [
            r'prepared.*statement',
            r'parameterized.*query',
            r'bind.*param',
            r'placeholder',
            r'cursor\.execute\s*\([^)]*\?\s*,',  # SQLite parameterized
            r'cursor\.execute\s*\([^)]*%s[^)]*,',  # MySQL parameterized
        ]
        
        source_files = list(self.base_dir.rglob("*.py")) + list(self.base_dir.rglob("*.js")) + list(self.base_dir.rglob("*.java"))
        
        for file_path in source_files:
            if any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '__pycache__']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Check for SQL injection vulnerabilities
                for pattern in sql_injection_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append(f"Potential SQL injection in {file_path}: {match.group()}")
                        score -= 20
                
                # Check for command injection vulnerabilities
                for pattern in command_injection_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append(f"Potential command injection in {file_path}: {match.group()}")
                        score -= 20
                
                # Check for safe coding practices
                for pattern in safe_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(f"Safe coding pattern found in {file_path}")
                        break
                        
            except Exception:
                continue
        
        # Check for input validation
        validation_patterns = [
            r'validate.*input',
            r'sanitize',
            r'escape.*html',
            r'filter.*input',
            r'clean.*input'
        ]
        
        validation_found = False
        for file_path in source_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                for pattern in validation_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        validation_found = True
                        evidence.append(f"Input validation found in {file_path}")
                        break
                if validation_found:
                    break
            except Exception:
                continue
        
        if not validation_found:
            findings.append("No input validation mechanisms found")
            score -= 25
        
        status = self._determine_status(score)
        
        return ComplianceResult(
            rule_id="A03",
            framework=ComplianceFramework.OWASP_TOP_10,
            status=status,
            score=max(0, score),
            findings=findings,
            evidence=evidence,
            recommendations=self._get_a03_recommendations(findings),
            assessed_at=datetime.now()
        )
    
    async def validate_a05_security_misconfiguration(self) -> ComplianceResult:
        """Validate A05: Security Misconfiguration"""
        findings = []
        evidence = []
        score = 100.0
        
        # Check for debug mode in production
        debug_patterns = [
            r'DEBUG\s*=\s*True',
            r'debug\s*:\s*true',
            r'development.*mode',
            r'console\.log\s*\(',
            r'print\s*\(',
            r'echo\s*["\'].*debug'
        ]
        
        # Check for default credentials
        default_cred_patterns = [
            r'password.*admin',
            r'password.*password',
            r'user.*admin.*password.*admin',
            r'root.*root',
            r'guest.*guest'
        ]
        
        # Check for insecure headers
        config_files = list(self.base_dir.rglob("*.conf")) + list(self.base_dir.rglob("*.config")) + list(self.base_dir.rglob("*.yaml"))
        source_files = list(self.base_dir.rglob("*.py")) + list(self.base_dir.rglob("*.js"))
        
        # Check source files
        for file_path in source_files:
            if any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '__pycache__']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Check for debug mode
                for pattern in debug_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings.append(f"Debug mode enabled in {file_path}")
                        score -= 15
                
                # Check for default credentials
                for pattern in default_cred_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings.append(f"Default credentials found in {file_path}")
                        score -= 25
                        
            except Exception:
                continue
        
        # Check configuration files
        for config_file in config_files:
            try:
                content = config_file.read_text()
                
                # Check for security headers
                security_headers = [
                    'X-Frame-Options',
                    'X-Content-Type-Options',
                    'X-XSS-Protection',
                    'Strict-Transport-Security',
                    'Content-Security-Policy'
                ]
                
                headers_found = 0
                for header in security_headers:
                    if header in content:
                        headers_found += 1
                        evidence.append(f"Security header {header} found in {config_file}")
                
                if headers_found < 3:
                    findings.append(f"Missing security headers in {config_file}")
                    score -= 10
                
                # Check for insecure configurations
                insecure_configs = [
                    r'server.*tokens.*on',
                    r'autoindex.*on',
                    r'ssl_verify_client.*off'
                ]
                
                for pattern in insecure_configs:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings.append(f"Insecure configuration in {config_file}")
                        score -= 10
                        
            except Exception:
                continue
        
        # Check for unnecessary services/features
        dockerfile_paths = list(self.base_dir.rglob("Dockerfile"))
        for dockerfile in dockerfile_paths:
            try:
                content = dockerfile.read_text()
                
                # Check for unnecessary packages
                unnecessary_packages = ['telnet', 'ftp', 'rsh', 'wget', 'curl']
                for package in unnecessary_packages:
                    if re.search(rf'(apt-get|yum|apk).*install.*{package}', content, re.IGNORECASE):
                        findings.append(f"Unnecessary package {package} installed in {dockerfile}")
                        score -= 5
                
                # Check for running as root
                if not re.search(r'USER\s+\w+', content):
                    findings.append(f"Container running as root in {dockerfile}")
                    score -= 15
                else:
                    evidence.append(f"Non-root user configured in {dockerfile}")
                    
            except Exception:
                continue
        
        status = self._determine_status(score)
        
        return ComplianceResult(
            rule_id="A05",
            framework=ComplianceFramework.OWASP_TOP_10,
            status=status,
            score=max(0, score),
            findings=findings,
            evidence=evidence,
            recommendations=self._get_a05_recommendations(findings),
            assessed_at=datetime.now()
        )
    
    def _determine_status(self, score: float) -> ComplianceStatus:
        """Determine compliance status based on score"""
        if score >= 90:
            return ComplianceStatus.COMPLIANT
        elif score >= 70:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        elif score >= 50:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    def _get_a01_recommendations(self, findings: List[str]) -> List[str]:
        """Get A01 specific recommendations"""
        recommendations = []
        
        if any("bypass" in finding for finding in findings):
            recommendations.append("Remove or fix authorization bypass mechanisms")
        
        if any("coverage" in finding for finding in findings):
            recommendations.append("Implement access controls in all application components")
        
        if any("default" in finding for finding in findings):
            recommendations.append("Implement deny-by-default access control policies")
        
        recommendations.extend([
            "Use centralized authorization mechanisms",
            "Implement proper session management",
            "Log and monitor access control failures",
            "Regularly review and test access controls"
        ])
        
        return recommendations
    
    def _get_a02_recommendations(self, findings: List[str]) -> List[str]:
        """Get A02 specific recommendations"""
        recommendations = []
        
        if any("weak" in finding.lower() for finding in findings):
            recommendations.append("Replace weak cryptographic algorithms with strong alternatives")
        
        if any("hardcoded" in finding.lower() for finding in findings):
            recommendations.append("Remove hardcoded secrets and use secure key management")
        
        if any("TLS" in finding for finding in findings):
            recommendations.append("Update TLS configuration to use version 1.2 or higher")
        
        recommendations.extend([
            "Use AES-256 for symmetric encryption",
            "Use SHA-256 or SHA-512 for hashing",
            "Implement proper key management practices",
            "Encrypt sensitive data at rest and in transit"
        ])
        
        return recommendations
    
    def _get_a03_recommendations(self, findings: List[str]) -> List[str]:
        """Get A03 specific recommendations"""
        recommendations = []
        
        if any("SQL injection" in finding for finding in findings):
            recommendations.append("Use parameterized queries and prepared statements")
        
        if any("command injection" in finding for finding in findings):
            recommendations.append("Avoid system command execution; use safe APIs instead")
        
        if any("validation" in finding for finding in findings):
            recommendations.append("Implement comprehensive input validation")
        
        recommendations.extend([
            "Use positive input validation (allow lists)",
            "Escape special characters appropriately",
            "Use ORM frameworks with built-in protection",
            "Implement output encoding"
        ])
        
        return recommendations
    
    def _get_a05_recommendations(self, findings: List[str]) -> List[str]:
        """Get A05 specific recommendations"""
        recommendations = []
        
        if any("debug" in finding.lower() for finding in findings):
            recommendations.append("Disable debug mode in production environments")
        
        if any("default" in finding.lower() for finding in findings):
            recommendations.append("Change all default credentials")
        
        if any("headers" in finding.lower() for finding in findings):
            recommendations.append("Implement all security headers")
        
        if any("root" in finding.lower() for finding in findings):
            recommendations.append("Run containers with non-root users")
        
        recommendations.extend([
            "Implement security hardening procedures",
            "Use automated configuration management",
            "Regular security configuration reviews",
            "Remove unnecessary features and services"
        ])
        
        return recommendations

class ComplianceValidator:
    """Main compliance validation framework"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.db_path = base_dir / "security" / "compliance.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
        # Initialize framework validators
        self.owasp_validator = OWASPTop10Validator(base_dir)
        
    def init_database(self):
        """Initialize compliance database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score REAL NOT NULL,
                    findings TEXT,
                    evidence TEXT,
                    recommendations TEXT,
                    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assessor TEXT DEFAULT 'automated'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework TEXT NOT NULL,
                    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    overall_score REAL,
                    total_rules INTEGER,
                    compliant_rules INTEGER,
                    non_compliant_rules INTEGER,
                    metadata TEXT
                )
            ''')
    
    async def validate_owasp_top_10(self) -> Dict[str, ComplianceResult]:
        """Validate OWASP Top 10 compliance"""
        results = {}
        
        # Validate each OWASP Top 10 category
        validators = {
            "A01": self.owasp_validator.validate_a01_access_control,
            "A02": self.owasp_validator.validate_a02_crypto_failures,
            "A03": self.owasp_validator.validate_a03_injection,
            "A05": self.owasp_validator.validate_a05_security_misconfiguration,
        }
        
        for rule_id, validator_func in validators.items():
            try:
                result = await validator_func()
                results[rule_id] = result
                self.store_compliance_result(result)
            except Exception as e:
                logging.error(f"Error validating {rule_id}: {str(e)}")
                # Create error result
                results[rule_id] = ComplianceResult(
                    rule_id=rule_id,
                    framework=ComplianceFramework.OWASP_TOP_10,
                    status=ComplianceStatus.NEEDS_REVIEW,
                    score=0.0,
                    findings=[f"Validation error: {str(e)}"],
                    evidence=[],
                    recommendations=["Manual review required"],
                    assessed_at=datetime.now()
                )
        
        return results
    
    def store_compliance_result(self, result: ComplianceResult):
        """Store compliance result in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO compliance_results 
                (rule_id, framework, status, score, findings, evidence, recommendations, assessed_at, assessor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.rule_id,
                result.framework.value,
                result.status.value,
                result.score,
                json.dumps(result.findings),
                json.dumps(result.evidence),
                json.dumps(result.recommendations),
                result.assessed_at,
                result.assessor
            ))
    
    def generate_compliance_report(self, results: Dict[str, ComplianceResult]) -> Dict:
        """Generate comprehensive compliance report"""
        total_score = sum(result.score for result in results.values())
        average_score = total_score / len(results) if results else 0
        
        status_counts = {}
        for result in results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        all_findings = []
        all_recommendations = []
        
        for result in results.values():
            all_findings.extend(result.findings)
            all_recommendations.extend(result.recommendations)
        
        report = {
            "assessment_date": datetime.now().isoformat(),
            "overall_score": round(average_score, 2),
            "total_rules": len(results),
            "status_distribution": status_counts,
            "compliance_percentage": round((status_counts.get("compliant", 0) / len(results)) * 100, 2) if results else 0,
            "summary": {
                "compliant": status_counts.get("compliant", 0),
                "partially_compliant": status_counts.get("partially_compliant", 0),
                "non_compliant": status_counts.get("non_compliant", 0),
                "needs_review": status_counts.get("needs_review", 0)
            },
            "total_findings": len(all_findings),
            "priority_recommendations": list(set(all_recommendations))[:10],
            "detailed_results": {
                rule_id: {
                    "status": result.status.value,
                    "score": result.score,
                    "findings": result.findings,
                    "evidence": result.evidence,
                    "recommendations": result.recommendations
                }
                for rule_id, result in results.items()
            }
        }
        
        return report
    
    async def run_comprehensive_compliance_assessment(self) -> Dict:
        """Run comprehensive compliance assessment"""
        assessment_results = {}
        
        # OWASP Top 10 Assessment
        owasp_results = await self.validate_owasp_top_10()
        assessment_results["OWASP_TOP_10"] = self.generate_compliance_report(owasp_results)
        
        # Store assessment history
        self.store_assessment_history("OWASP_TOP_10", assessment_results["OWASP_TOP_10"])
        
        return assessment_results
    
    def store_assessment_history(self, framework: str, report: Dict):
        """Store assessment history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO compliance_history 
                (framework, overall_score, total_rules, compliant_rules, non_compliant_rules, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                framework,
                report["overall_score"],
                report["total_rules"],
                report["summary"]["compliant"],
                report["summary"]["non_compliant"],
                json.dumps({
                    "compliance_percentage": report["compliance_percentage"],
                    "total_findings": report["total_findings"]
                })
            ))


async def main():
    """Main execution for compliance validation"""
    base_dir = Path.cwd()
    validator = ComplianceValidator(base_dir)
    
    print("Starting compliance assessment...")
    
    results = await validator.run_comprehensive_compliance_assessment()
    
    for framework, report in results.items():
        print(f"\n{framework} Compliance Assessment:")
        print(f"- Overall Score: {report['overall_score']}/100")
        print(f"- Compliance Percentage: {report['compliance_percentage']}%")
        print(f"- Total Findings: {report['total_findings']}")
        print(f"- Status: {'✅ Compliant' if report['compliance_percentage'] >= 90 else '⚠️ Needs Improvement'}")
    
    # Save results
    results_file = Path("security/compliance_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nCompliance results saved to {results_file}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())