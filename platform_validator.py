#!/usr/bin/env python3
"""
Cross-Platform Validation for Claude Code Dev Stack v3.0
Security Architecture Assessment
"""

import os
import sys
import json
import platform
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class PlatformValidator:
    """Cross-platform compatibility validator"""
    
    def __init__(self):
        self.results = {
            'platform': platform.uname()._asdict(),
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
    def safe_print(self, text: str):
        """Safe printing for Windows compatibility"""
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', 'replace').decode('ascii')
            print(safe_text)
    
    def test_windows_compatibility(self) -> Dict:
        """Test Windows 10/11 compatibility"""
        results = {'score': 0, 'issues': [], 'features': []}
        
        if platform.system() == 'Windows':
            results['score'] += 25
            results['features'].append("Windows platform detected")
            
            # Test PowerShell
            try:
                subprocess.run(['powershell', '-Command', 'Get-Host'], 
                             capture_output=True, check=True, timeout=5)
                results['score'] += 25
                results['features'].append("PowerShell available")
            except:
                results['issues'].append("PowerShell not accessible")
            
            # Test Python venv
            try:
                subprocess.run([sys.executable, '-m', 'venv', '--help'], 
                             capture_output=True, check=True, timeout=5)
                results['score'] += 25
                results['features'].append("Python venv available")
            except:
                results['issues'].append("Python venv not available")
            
            # Test file permissions
            try:
                test_file = Path.home() / 'claude_test.tmp'
                test_file.write_text("test")
                test_file.unlink()
                results['score'] += 25
                results['features'].append("File system writable")
            except:
                results['issues'].append("Limited file permissions")
        else:
            results['issues'].append("Not running on Windows")
            
        return results
    
    def test_linux_compatibility(self) -> Dict:
        """Test Linux compatibility"""
        results = {'score': 0, 'issues': [], 'features': []}
        
        if platform.system() == 'Linux':
            results['score'] += 30
            results['features'].append("Native Linux environment")
            
            # Test bash
            try:
                subprocess.run(['bash', '--version'], 
                             capture_output=True, check=True, timeout=5)
                results['score'] += 35
                results['features'].append("Bash shell available")
            except:
                results['issues'].append("Bash not available")
            
            # Test common tools
            tools = ['curl', 'git', 'python3']
            available = 0
            for tool in tools:
                try:
                    subprocess.run(['which', tool], 
                                 capture_output=True, check=True, timeout=3)
                    available += 1
                except:
                    results['issues'].append(f"{tool} not found")
            
            results['score'] += (available / len(tools)) * 35
            
        elif platform.system() == 'Windows':
            # Test WSL
            try:
                subprocess.run(['wsl', '--version'], 
                             capture_output=True, check=True, timeout=5)
                results['score'] += 50
                results['features'].append("WSL available")
            except:
                results['issues'].append("WSL not available")
        else:
            results['issues'].append("Limited Linux compatibility")
            
        return results
    
    def test_mobile_access(self) -> Dict:
        """Test mobile access capabilities"""
        results = {'score': 0, 'issues': [], 'features': []}
        
        # Check mobile launcher
        mobile_launcher = Path('.claude-example/mobile/launch_mobile.py')
        if mobile_launcher.exists():
            results['score'] += 30
            results['features'].append("Mobile launcher found")
            
            # Check for QR code support
            try:
                import qrcode
                results['score'] += 25
                results['features'].append("QR code generation available")
            except ImportError:
                results['issues'].append("QR code library not installed")
            
            # Check tunnel support
            if os.environ.get('NGROK_AUTH_TOKEN'):
                results['score'] += 25
                results['features'].append("NGROK token configured")
            else:
                results['issues'].append("NGROK token not set")
            
            # Check web app
            web_app = Path('Claude_Code_Dev_Stack_v3/apps/web/package.json')
            if web_app.exists():
                results['score'] += 20
                results['features'].append("Web app available")
            else:
                results['issues'].append("Web app not found")
        else:
            results['issues'].append("Mobile launcher not found")
            
        return results
    
    def test_web_browser_access(self) -> Dict:
        """Test web browser compatibility"""
        results = {'score': 0, 'issues': [], 'features': []}
        
        # Check for running web services
        try:
            import requests
            ports = [8080, 5173, 3000]
            accessible = 0
            
            for port in ports:
                try:
                    response = requests.get(f'http://localhost:{port}', timeout=2)
                    if response.status_code in [200, 401, 403]:
                        accessible += 1
                        results['features'].append(f"Service on port {port}")
                except:
                    continue
            
            results['score'] += (accessible / len(ports)) * 40
            
            # Check PWA support
            manifest = Path('Claude_Code_Dev_Stack_v3/apps/web/public/manifest.json')
            if manifest.exists():
                results['score'] += 30
                results['features'].append("PWA manifest available")
            
            # Check for modern web features
            package_json = Path('Claude_Code_Dev_Stack_v3/apps/web/package.json')
            if package_json.exists():
                results['score'] += 30
                results['features'].append("Modern web stack")
            
        except ImportError:
            results['issues'].append("Requests library not available")
            
        return results
    
    def test_security_features(self) -> Dict:
        """Test security implementations"""
        results = {'score': 0, 'issues': [], 'features': []}
        
        # Check authentication system
        auth_file = Path('.claude-example/mobile/auth_tokens.json')
        if auth_file.exists():
            results['score'] += 30
            results['features'].append("Authentication system active")
        else:
            results['issues'].append("Authentication not initialized")
        
        # Check secure token generation
        try:
            import secrets
            token = secrets.token_urlsafe(32)
            if len(token) >= 32:
                results['score'] += 25
                results['features'].append("Secure token generation")
        except:
            results['issues'].append("Secure tokens not available")
        
        # Check SSL support
        try:
            import ssl
            results['score'] += 25
            results['features'].append("SSL/TLS support")
        except:
            results['issues'].append("SSL support limited")
        
        # Check virtual environment isolation
        if Path('.claude-example/mobile/.venv').exists():
            results['score'] += 20
            results['features'].append("Virtual environment isolation")
        
        return results
    
    def run_comprehensive_validation(self):
        """Run all validation tests"""
        self.safe_print("Starting Cross-Platform Validation...")
        self.safe_print("=" * 60)
        
        tests = {
            'windows': self.test_windows_compatibility,
            'linux': self.test_linux_compatibility,
            'mobile': self.test_mobile_access,
            'web_browser': self.test_web_browser_access,
            'security': self.test_security_features
        }
        
        total_score = 0
        
        for test_name, test_func in tests.items():
            self.safe_print(f"\nTesting {test_name.replace('_', ' ').title()}...")
            result = test_func()
            self.results['tests'][test_name] = result
            total_score += result['score']
            
            self.safe_print(f"Score: {result['score']:.1f}/100")
            
            for feature in result['features']:
                self.safe_print(f"  + {feature}")
            
            for issue in result['issues']:
                self.safe_print(f"  - {issue}")
        
        overall_score = total_score / len(tests)
        self.results['overall_score'] = overall_score
        
        self.safe_print("\n" + "=" * 60)
        self.safe_print("VALIDATION SUMMARY")
        self.safe_print("=" * 60)
        
        for test_name, result in self.results['tests'].items():
            self.safe_print(f"{test_name.replace('_', ' ').title()}: {result['score']:.1f}/100")
        
        self.safe_print(f"\nOverall Score: {overall_score:.1f}/100")
        
        if overall_score >= 80:
            self.safe_print("Status: EXCELLENT - Highly compatible")
        elif overall_score >= 60:
            self.safe_print("Status: GOOD - Generally compatible")
        elif overall_score >= 40:
            self.safe_print("Status: FAIR - Some issues")
        else:
            self.safe_print("Status: POOR - Significant issues")
        
        # Save results
        results_file = Path('validation_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        self.safe_print(f"\nDetailed results saved to: {results_file}")
        
        return self.results

def main():
    """Main validation function"""
    validator = PlatformValidator()
    results = validator.run_comprehensive_validation()
    
    # Generate specific recommendations
    validator.safe_print("\n" + "=" * 60)
    validator.safe_print("RECOMMENDATIONS")
    validator.safe_print("=" * 60)
    
    # Windows recommendations
    if platform.system() == 'Windows':
        windows_score = results['tests']['windows']['score']
        if windows_score < 80:
            validator.safe_print("Windows:")
            validator.safe_print("  - Ensure PowerShell is available")
            validator.safe_print("  - Check Python venv module installation")
            validator.safe_print("  - Verify file system permissions")
    
    # Mobile recommendations
    mobile_score = results['tests']['mobile']['score']
    if mobile_score < 80:
        validator.safe_print("Mobile Access:")
        validator.safe_print("  - Install QR code library: pip install qrcode[pil]")
        validator.safe_print("  - Set NGROK_AUTH_TOKEN environment variable")
        validator.safe_print("  - Ensure mobile launcher is accessible")
    
    # Security recommendations
    security_score = results['tests']['security']['score']
    if security_score < 80:
        validator.safe_print("Security:")
        validator.safe_print("  - Initialize authentication system")
        validator.safe_print("  - Ensure SSL/TLS support is available")
        validator.safe_print("  - Set up virtual environment isolation")
    
    validator.safe_print("\n" + "=" * 60)
    
    return results

if __name__ == "__main__":
    main()