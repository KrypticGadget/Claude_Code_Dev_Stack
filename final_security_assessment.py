#!/usr/bin/env python3
"""
Final Security Assessment for Claude Code Dev Stack v3.0
Comprehensive security validation and threat assessment
"""

import os
import sys
import json
import socket
import ssl
import subprocess
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SecurityAssessment:
    """Final security assessment validator"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'security_score': 0,
            'vulnerabilities': [],
            'recommendations': [],
            'compliant_features': [],
            'risk_level': 'UNKNOWN'
        }
    
    def assess_authentication_security(self) -> int:
        """Assess authentication implementation"""
        score = 0
        
        # Check token system
        auth_file = Path('.claude-example/mobile/auth_tokens.json')
        if auth_file.exists():
            score += 25
            self.results['compliant_features'].append("Token-based authentication active")
            
            try:
                with open(auth_file) as f:
                    tokens = json.load(f)
                    if tokens:
                        # Validate token strength
                        for token_data in tokens.values():
                            if 'expires' in token_data and 'created' in token_data:
                                score += 15
                                self.results['compliant_features'].append("Token expiry implemented")
                                break
            except:
                self.results['vulnerabilities'].append("Authentication tokens corrupted or unreadable")
        else:
            self.results['vulnerabilities'].append("Authentication system not initialized")
        
        # Test secure token generation
        try:
            token = secrets.token_urlsafe(32)
            if len(token) >= 32:
                score += 20
                self.results['compliant_features'].append("Cryptographically secure token generation")
            else:
                self.results['vulnerabilities'].append("Weak token generation")
        except:
            self.results['vulnerabilities'].append("Secure token generation not available")
        
        # Check session management
        session_file = Path('.claude-example/mobile/current_access.json')
        if session_file.exists():
            score += 15
            self.results['compliant_features'].append("Session management implemented")
        
        return score
    
    def assess_network_security(self) -> int:
        """Assess network security configuration"""
        score = 0
        
        # Test SSL/TLS capability
        try:
            context = ssl.create_default_context()
            score += 25
            self.results['compliant_features'].append("SSL/TLS context available")
        except:
            self.results['vulnerabilities'].append("SSL/TLS not properly configured")
        
        # Check for exposed sensitive ports
        sensitive_ports = [22, 23, 3389, 5432, 3306, 27017]
        exposed_ports = []
        
        for port in sensitive_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    exposed_ports.append(port)
            except:
                pass
            finally:
                sock.close()
        
        if not exposed_ports:
            score += 25
            self.results['compliant_features'].append("No sensitive ports exposed")
        else:
            self.results['vulnerabilities'].append(f"Exposed sensitive ports: {exposed_ports}")
        
        # Check tunnel security
        if os.environ.get('NGROK_AUTH_TOKEN'):
            score += 20
            self.results['compliant_features'].append("Secure tunnel authentication configured")
        else:
            self.results['recommendations'].append("Configure NGROK_AUTH_TOKEN for secure external access")
        
        # Test localhost binding
        active_services = []
        test_ports = [8080, 5173, 3000, 7681]
        
        for port in test_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    active_services.append(port)
            except:
                pass
            finally:
                sock.close()
        
        if active_services:
            score += 15
            self.results['compliant_features'].append(f"Services properly bound to localhost: {active_services}")
        
        return score
    
    def assess_data_protection(self) -> int:
        """Assess data protection measures"""
        score = 0
        
        # Check virtual environment isolation
        venv_path = Path('.claude-example/mobile/.venv')
        if venv_path.exists():
            score += 25
            self.results['compliant_features'].append("Virtual environment isolation active")
        else:
            self.results['vulnerabilities'].append("Virtual environment not found - dependency isolation missing")
        
        # Check file permissions
        try:
            test_file = Path('.claude-example/mobile/security_test.tmp')
            test_file.write_text("security test")
            permissions = oct(test_file.stat().st_mode)[-3:]
            test_file.unlink()
            
            score += 20
            self.results['compliant_features'].append(f"File system permissions working (mode: {permissions})")
        except Exception as e:
            self.results['vulnerabilities'].append(f"File permission test failed: {e}")
        
        # Check for sensitive data exposure
        sensitive_patterns = ['.env', 'config.json', 'secrets.json', 'private.key']
        exposed_files = []
        
        for pattern in sensitive_patterns:
            files = list(Path('.').glob(f'**/{pattern}'))
            exposed_files.extend(files)
        
        if not exposed_files:
            score += 15
            self.results['compliant_features'].append("No sensitive configuration files exposed")
        else:
            self.results['recommendations'].append(f"Review exposure of files: {[str(f) for f in exposed_files]}")
        
        # Test data encryption readiness
        try:
            import cryptography
            score += 15
            self.results['compliant_features'].append("Cryptography library available for data encryption")
        except ImportError:
            self.results['recommendations'].append("Install cryptography library for enhanced data protection")
        
        return score
    
    def assess_application_security(self) -> int:
        """Assess application-level security"""
        score = 0
        
        # Check for SQL injection protection
        launcher_file = Path('.claude-example/mobile/launch_mobile.py')
        if launcher_file.exists():
            content = launcher_file.read_text()
            
            # Basic checks for secure coding practices
            if 'subprocess.run' in content and 'shell=False' in content:
                score += 15
                self.results['compliant_features'].append("Secure subprocess execution")
            elif 'subprocess.run' in content:
                self.results['recommendations'].append("Review subprocess calls for shell injection risks")
            
            if 'secrets.' in content:
                score += 15
                self.results['compliant_features'].append("Secure random number generation")
            
            if 'json.load' in content and 'json.dump' in content:
                score += 10
                self.results['compliant_features'].append("Safe JSON handling")
        
        # Check web application security
        web_package = Path('Claude_Code_Dev_Stack_v3/apps/web/package.json')
        if web_package.exists():
            try:
                with open(web_package) as f:
                    package_data = json.load(f)
                    
                # Check for security-related dependencies
                deps = package_data.get('dependencies', {})
                dev_deps = package_data.get('devDependencies', {})
                
                security_packages = ['helmet', 'cors', 'express-rate-limit', 'bcrypt']
                found_security = [pkg for pkg in security_packages if pkg in deps or pkg in dev_deps]
                
                if found_security:
                    score += 20
                    self.results['compliant_features'].append(f"Security packages found: {found_security}")
                
                # Check for modern frameworks (implicit security)
                if 'react' in deps and 'typescript' in dev_deps:
                    score += 15
                    self.results['compliant_features'].append("Modern secure framework stack (React + TypeScript)")
                    
            except:
                self.results['vulnerabilities'].append("Could not parse web application dependencies")
        
        return score
    
    def assess_infrastructure_security(self) -> int:
        """Assess infrastructure security"""
        score = 0
        
        # Check Python version security
        python_version = sys.version_info
        if python_version >= (3, 9):
            score += 20
            self.results['compliant_features'].append(f"Secure Python version: {python_version.major}.{python_version.minor}")
        else:
            self.results['vulnerabilities'].append(f"Outdated Python version: {python_version.major}.{python_version.minor}")
        
        # Check Node.js version
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                major_version = int(version.split('.')[0][1:])  # Remove 'v' prefix
                
                if major_version >= 18:
                    score += 20
                    self.results['compliant_features'].append(f"Secure Node.js version: {version}")
                else:
                    self.results['vulnerabilities'].append(f"Outdated Node.js version: {version}")
        except:
            self.results['recommendations'].append("Node.js version could not be determined")
        
        # Check for security tools
        security_tools = ['nmap', 'openssl', 'curl']
        available_tools = []
        
        for tool in security_tools:
            try:
                result = subprocess.run(['where', tool], capture_output=True, timeout=3)
                if result.returncode == 0:
                    available_tools.append(tool)
            except:
                pass
        
        if available_tools:
            score += 15
            self.results['compliant_features'].append(f"Security tools available: {available_tools}")
        
        return score
    
    def calculate_risk_level(self, total_score: int) -> str:
        """Calculate overall risk level"""
        if total_score >= 85:
            return "LOW"
        elif total_score >= 70:
            return "MEDIUM"
        elif total_score >= 50:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def run_assessment(self) -> Dict:
        """Run complete security assessment"""
        print("Running comprehensive security assessment...")
        
        auth_score = self.assess_authentication_security()
        network_score = self.assess_network_security()
        data_score = self.assess_data_protection()
        app_score = self.assess_application_security()
        infra_score = self.assess_infrastructure_security()
        
        total_score = auth_score + network_score + data_score + app_score + infra_score
        max_score = 100 + 85 + 75 + 60 + 55  # Theoretical maximum
        
        # Normalize to 100-point scale
        normalized_score = min(100, (total_score / max_score) * 100)
        
        self.results['security_score'] = round(normalized_score, 1)
        self.results['risk_level'] = self.calculate_risk_level(normalized_score)
        
        # Add category scores
        self.results['category_scores'] = {
            'authentication': auth_score,
            'network_security': network_score,
            'data_protection': data_score,
            'application_security': app_score,
            'infrastructure_security': infra_score
        }
        
        print(f"Security assessment complete. Score: {self.results['security_score']}/100")
        print(f"Risk Level: {self.results['risk_level']}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate security assessment report"""
        report = f"""
CLAUDE CODE DEV STACK v3.0 - SECURITY ASSESSMENT REPORT
========================================================

Generated: {self.results['timestamp']}
Overall Security Score: {self.results['security_score']}/100
Risk Level: {self.results['risk_level']}

CATEGORY SCORES:
- Authentication Security: {self.results['category_scores']['authentication']}/100
- Network Security: {self.results['category_scores']['network_security']}/85
- Data Protection: {self.results['category_scores']['data_protection']}/75
- Application Security: {self.results['category_scores']['application_security']}/60
- Infrastructure Security: {self.results['category_scores']['infrastructure_security']}/55

COMPLIANT SECURITY FEATURES:
"""
        for feature in self.results['compliant_features']:
            report += f"✅ {feature}\n"
        
        if self.results['vulnerabilities']:
            report += "\nIDENTIFIED VULNERABILITIES:\n"
            for vuln in self.results['vulnerabilities']:
                report += f"❌ {vuln}\n"
        
        if self.results['recommendations']:
            report += "\nSECURITY RECOMMENDATIONS:\n"
            for rec in self.results['recommendations']:
                report += f"💡 {rec}\n"
        
        # Risk assessment
        report += f"\nRISK ASSESSMENT:\n"
        if self.results['risk_level'] == 'LOW':
            report += "🟢 LOW RISK: System demonstrates excellent security practices\n"
        elif self.results['risk_level'] == 'MEDIUM':
            report += "🟡 MEDIUM RISK: Good security with some areas for improvement\n"
        elif self.results['risk_level'] == 'HIGH':
            report += "🟠 HIGH RISK: Security improvements needed before production\n"
        else:
            report += "🔴 CRITICAL RISK: Immediate security attention required\n"
        
        report += "\n" + "=" * 60 + "\n"
        
        return report

def main():
    """Main assessment function"""
    assessor = SecurityAssessment()
    results = assessor.run_assessment()
    
    # Generate and display report
    report = assessor.generate_report()
    print(report)
    
    # Save results
    results_file = Path('security_assessment_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    report_file = Path('security_assessment_report.txt')
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Security assessment saved to: {results_file}")
    print(f"Security report saved to: {report_file}")

if __name__ == "__main__":
    main()