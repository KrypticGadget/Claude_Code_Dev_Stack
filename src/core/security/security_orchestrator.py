#!/usr/bin/env python3
"""
Security Orchestrator for Claude Code V3.6.9
Main security management and coordination system
"""

import asyncio
import json
import logging
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml

# Import security modules
from audit_framework import SecurityAuditFramework
from penetration_testing import PenetrationTestSuite
from compliance_validator import ComplianceValidator
from security_monitor import SecurityMonitor

class SecurityOrchestrator:
    """Main security orchestration system"""
    
    def __init__(self, base_directory: str = None):
        self.base_dir = Path(base_directory) if base_directory else Path.cwd()
        self.security_dir = self.base_dir / "security"
        self.security_dir.mkdir(exist_ok=True)
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize security components
        self.audit_framework = SecurityAuditFramework(str(self.base_dir))
        self.pentest_suite = PenetrationTestSuite()
        self.compliance_validator = ComplianceValidator(self.base_dir)
        self.security_monitor = None  # Initialized when monitoring starts
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Security Orchestrator initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.security_dir / "security_orchestrator.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    async def run_full_security_assessment(self) -> Dict[str, Any]:
        """Run comprehensive security assessment"""
        self.logger.info("Starting comprehensive security assessment")
        assessment_start = datetime.now()
        
        assessment_results = {
            "assessment_id": f"security_assessment_{int(time.time())}",
            "start_time": assessment_start.isoformat(),
            "components": {},
            "summary": {},
            "recommendations": [],
            "risk_score": 0,
            "status": "in_progress"
        }
        
        try:
            # 1. Security Audit
            self.logger.info("Running security audit framework")
            audit_results = await self.audit_framework.run_comprehensive_audit()
            assessment_results["components"]["security_audit"] = audit_results
            
            # 2. Compliance Validation
            self.logger.info("Running compliance validation")
            compliance_results = await self.compliance_validator.run_comprehensive_compliance_assessment()
            assessment_results["components"]["compliance_validation"] = compliance_results
            
            # 3. Penetration Testing (if target available)
            if self.should_run_pentest():
                self.logger.info("Running penetration testing")
                pentest_results = await self.run_penetration_tests()
                assessment_results["components"]["penetration_testing"] = pentest_results
            
            # 4. Generate overall assessment
            assessment_end = datetime.now()
            assessment_results["end_time"] = assessment_end.isoformat()
            assessment_results["duration_seconds"] = (assessment_end - assessment_start).total_seconds()
            
            # Calculate overall scores and recommendations
            assessment_results["summary"] = self.generate_assessment_summary(assessment_results["components"])
            assessment_results["recommendations"] = self.generate_consolidated_recommendations(assessment_results["components"])
            assessment_results["risk_score"] = self.calculate_overall_risk_score(assessment_results["components"])
            assessment_results["status"] = "completed"
            
            # Save assessment results
            await self.save_assessment_results(assessment_results)
            
            # Generate reports
            await self.generate_assessment_reports(assessment_results)
            
            self.logger.info(f"Security assessment completed in {assessment_results['duration_seconds']:.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Security assessment failed: {str(e)}")
            assessment_results["status"] = "failed"
            assessment_results["error"] = str(e)
            assessment_results["end_time"] = datetime.now().isoformat()
        
        return assessment_results
    
    def should_run_pentest(self) -> bool:
        """Determine if penetration testing should be run"""
        # Check if there are running web services to test
        web_configs = list(self.base_dir.rglob("*docker-compose*.yml")) + \
                     list(self.base_dir.rglob("nginx.conf")) + \
                     list(self.base_dir.rglob("server.py")) + \
                     list(self.base_dir.rglob("app.py"))
        
        return len(web_configs) > 0
    
    async def run_penetration_tests(self) -> Dict[str, Any]:
        """Run penetration testing suite"""
        # Default targets for local testing
        target_host = "127.0.0.1"
        target_url = "http://127.0.0.1:8080"
        
        # Try to detect running services
        detected_targets = await self.detect_running_services()
        if detected_targets:
            target_url = detected_targets.get("web_url", target_url)
            target_host = detected_targets.get("host", target_host)
        
        return await self.pentest_suite.run_comprehensive_pentest(
            target_host=target_host,
            target_url=target_url
        )
    
    async def detect_running_services(self) -> Dict[str, str]:
        """Detect running web services for testing"""
        detected = {}
        
        try:
            import socket
            import aiohttp
            
            # Check common web service ports
            common_ports = [3000, 8000, 8080, 8443, 9000]
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    # Port is open, try to determine if it's HTTP
                    try:
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                            async with session.get(f"http://127.0.0.1:{port}") as response:
                                if response.status < 500:  # Assume it's a web service
                                    detected["web_url"] = f"http://127.0.0.1:{port}"
                                    detected["host"] = "127.0.0.1"
                                    break
                    except:
                        continue
        
        except ImportError:
            pass  # aiohttp not available
        except Exception as e:
            self.logger.warning(f"Error detecting services: {str(e)}")
        
        return detected
    
    def generate_assessment_summary(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment summary"""
        summary = {
            "total_findings": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "compliance_score": 0,
            "security_score": 0,
            "components_assessed": list(components.keys()),
            "overall_status": "unknown"
        }
        
        # Process security audit results
        if "security_audit" in components:
            audit_summary = components["security_audit"].get("summary", {})
            summary["total_findings"] += audit_summary.get("total_findings", 0)
            summary["critical_issues"] += audit_summary.get("severity_distribution", {}).get("critical", 0)
            summary["high_issues"] += audit_summary.get("severity_distribution", {}).get("high", 0)
            summary["medium_issues"] += audit_summary.get("severity_distribution", {}).get("medium", 0)
            summary["low_issues"] += audit_summary.get("severity_distribution", {}).get("low", 0)
            summary["security_score"] = max(0, 100 - audit_summary.get("risk_score", 0))
        
        # Process compliance validation results
        if "compliance_validation" in components:
            compliance_data = components["compliance_validation"]
            owasp_compliance = compliance_data.get("OWASP_TOP_10", {})
            summary["compliance_score"] = owasp_compliance.get("overall_score", 0)
        
        # Process penetration testing results
        if "penetration_testing" in components:
            pentest_data = components["penetration_testing"]
            pentest_summary = pentest_data.get("summary", {})
            summary["total_findings"] += pentest_summary.get("vulnerabilities_found", 0)
            
            # Add pentest severity distribution to totals
            severity_dist = pentest_summary.get("severity_distribution", {})
            summary["critical_issues"] += severity_dist.get("critical", 0)
            summary["high_issues"] += severity_dist.get("high", 0)
            summary["medium_issues"] += severity_dist.get("medium", 0)
            summary["low_issues"] += severity_dist.get("low", 0)
        
        # Determine overall status
        if summary["critical_issues"] > 0:
            summary["overall_status"] = "critical"
        elif summary["high_issues"] > 5:
            summary["overall_status"] = "high_risk"
        elif summary["compliance_score"] < 70:
            summary["overall_status"] = "non_compliant"
        elif summary["security_score"] < 70:
            summary["overall_status"] = "needs_improvement"
        else:
            summary["overall_status"] = "acceptable"
        
        return summary
    
    def generate_consolidated_recommendations(self, components: Dict[str, Any]) -> List[str]:
        """Generate consolidated security recommendations"""
        recommendations = []
        
        # Collect recommendations from all components
        all_recommendations = []
        
        if "security_audit" in components:
            all_recommendations.extend(components["security_audit"].get("recommendations", []))
        
        if "compliance_validation" in components:
            for framework, data in components["compliance_validation"].items():
                all_recommendations.extend(data.get("priority_recommendations", []))
        
        if "penetration_testing" in components:
            all_recommendations.extend(components["penetration_testing"].get("recommendations", []))
        
        # Deduplicate and prioritize recommendations
        unique_recommendations = list(set(all_recommendations))
        
        # Priority keywords for sorting
        priority_keywords = [
            "critical", "urgent", "immediately", "fix", "patch",
            "update", "upgrade", "remove", "disable", "block"
        ]
        
        # Sort recommendations by priority
        prioritized = []
        standard = []
        
        for rec in unique_recommendations:
            if any(keyword in rec.lower() for keyword in priority_keywords):
                prioritized.append(rec)
            else:
                standard.append(rec)
        
        # Combine prioritized and standard recommendations
        recommendations = prioritized + standard
        
        # Add general security recommendations if not already present
        general_recommendations = [
            "Implement regular security testing in CI/CD pipeline",
            "Establish security monitoring and alerting",
            "Conduct regular security training for development team",
            "Implement Web Application Firewall (WAF)",
            "Establish incident response procedures",
            "Regular security architecture reviews",
            "Implement security metrics and KPIs",
            "Regular backup and disaster recovery testing"
        ]
        
        for gen_rec in general_recommendations:
            if not any(gen_rec.lower() in rec.lower() for rec in recommendations):
                recommendations.append(gen_rec)
        
        return recommendations[:15]  # Limit to top 15 recommendations
    
    def calculate_overall_risk_score(self, components: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-100, higher is more risk)"""
        risk_score = 0
        component_count = 0
        
        # Security audit risk score
        if "security_audit" in components:
            audit_risk = components["security_audit"].get("summary", {}).get("risk_score", 0)
            risk_score += audit_risk
            component_count += 1
        
        # Compliance risk score (inverse of compliance score)
        if "compliance_validation" in components:
            compliance_data = components["compliance_validation"]
            owasp_compliance = compliance_data.get("OWASP_TOP_10", {})
            compliance_score = owasp_compliance.get("overall_score", 100)
            compliance_risk = max(0, 100 - compliance_score)
            risk_score += compliance_risk
            component_count += 1
        
        # Penetration testing risk score
        if "penetration_testing" in components:
            pentest_data = components["penetration_testing"]
            pentest_risk = pentest_data.get("summary", {}).get("risk_score", 0)
            risk_score += pentest_risk
            component_count += 1
        
        # Calculate average risk score
        overall_risk = risk_score / component_count if component_count > 0 else 0
        
        return min(100, overall_risk)
    
    async def save_assessment_results(self, assessment_results: Dict[str, Any]):
        """Save assessment results to file"""
        results_file = self.security_dir / f"assessment_{assessment_results['assessment_id']}.json"
        
        # Convert any datetime objects to strings for JSON serialization
        json_results = json.loads(json.dumps(assessment_results, default=str))
        
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        self.logger.info(f"Assessment results saved to {results_file}")
    
    async def generate_assessment_reports(self, assessment_results: Dict[str, Any]):
        """Generate assessment reports"""
        reports_dir = self.security_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Executive Summary Report
        exec_summary = self.generate_executive_summary_report(assessment_results)
        exec_file = reports_dir / f"executive_summary_{timestamp}.md"
        with open(exec_file, 'w') as f:
            f.write(exec_summary)
        
        # Technical Report
        tech_report = self.generate_technical_report(assessment_results)
        tech_file = reports_dir / f"technical_report_{timestamp}.md"
        with open(tech_file, 'w') as f:
            f.write(tech_report)
        
        # Risk Assessment Report
        risk_report = self.generate_risk_assessment_report(assessment_results)
        risk_file = reports_dir / f"risk_assessment_{timestamp}.md"
        with open(risk_file, 'w') as f:
            f.write(risk_report)
        
        self.logger.info(f"Assessment reports generated in {reports_dir}")
    
    def generate_executive_summary_report(self, assessment_results: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        summary = assessment_results.get("summary", {})
        
        report = f"""# Security Assessment Executive Summary

## Assessment Overview
- **Assessment ID**: {assessment_results['assessment_id']}
- **Date**: {assessment_results['start_time']}
- **Duration**: {assessment_results.get('duration_seconds', 0):.2f} seconds
- **Components Assessed**: {', '.join(summary.get('components_assessed', []))}

## Executive Summary
The comprehensive security assessment of Claude Code v3.6.9 has been completed. This assessment included vulnerability scanning, compliance validation, and penetration testing.

## Key Findings
- **Overall Risk Score**: {assessment_results.get('risk_score', 0):.1f}/100
- **Total Security Issues**: {summary.get('total_findings', 0)}
- **Critical Issues**: {summary.get('critical_issues', 0)}
- **High Severity Issues**: {summary.get('high_issues', 0)}
- **Compliance Score**: {summary.get('compliance_score', 0):.1f}%

## Risk Assessment
**Overall Status**: {summary.get('overall_status', 'Unknown').upper()}

{self._get_status_description(summary.get('overall_status', 'unknown'))}

## Priority Actions Required
"""
        
        # Add top 5 recommendations
        for i, rec in enumerate(assessment_results.get('recommendations', [])[:5], 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
## Compliance Status
- **OWASP Top 10 Compliance**: {summary.get('compliance_score', 0):.1f}%
- **Security Controls**: {"Adequate" if summary.get('compliance_score', 0) >= 80 else "Needs Improvement"}

## Next Steps
1. Address all critical and high-severity vulnerabilities immediately
2. Implement recommended security controls
3. Establish regular security testing schedule
4. Review and update security policies
5. Conduct security awareness training

---
*This report was generated by Claude Code Security Assessment Framework*
"""
        
        return report
    
    def generate_technical_report(self, assessment_results: Dict[str, Any]) -> str:
        """Generate technical report"""
        summary = assessment_results.get("summary", {})
        components = assessment_results.get("components", {})
        
        report = f"""# Technical Security Assessment Report

## Assessment Details
- **Assessment ID**: {assessment_results['assessment_id']}
- **Start Time**: {assessment_results['start_time']}
- **End Time**: {assessment_results.get('end_time', 'N/A')}
- **Duration**: {assessment_results.get('duration_seconds', 0):.2f} seconds

## Assessment Methodology
This comprehensive security assessment included:
1. **Static Application Security Testing (SAST)** - Code vulnerability analysis
2. **Compliance Validation** - OWASP Top 10 and other framework compliance
3. **Penetration Testing** - Simulated attack scenarios (if applicable)
4. **Configuration Security Review** - Infrastructure and deployment security

## Detailed Findings by Component

"""
        
        # Security Audit Results
        if "security_audit" in components:
            audit_data = components["security_audit"]
            audit_summary = audit_data.get("summary", {})
            
            report += f"""### Security Audit Results
- **Total Vulnerabilities**: {audit_summary.get('total_findings', 0)}
- **Files Scanned**: {audit_summary.get('affected_file_count', 0)}
- **Risk Score**: {audit_summary.get('risk_score', 0)}/100

#### Severity Distribution
- Critical: {audit_summary.get('severity_distribution', {}).get('critical', 0)}
- High: {audit_summary.get('severity_distribution', {}).get('high', 0)}
- Medium: {audit_summary.get('severity_distribution', {}).get('medium', 0)}
- Low: {audit_summary.get('severity_distribution', {}).get('low', 0)}

"""
        
        # Compliance Results
        if "compliance_validation" in components:
            compliance_data = components["compliance_validation"]
            
            report += "### Compliance Assessment Results\n\n"
            
            for framework, framework_data in compliance_data.items():
                report += f"""#### {framework}
- **Overall Score**: {framework_data.get('overall_score', 0):.1f}/100
- **Compliance Percentage**: {framework_data.get('compliance_percentage', 0):.1f}%
- **Total Rules**: {framework_data.get('total_rules', 0)}
- **Compliant**: {framework_data.get('summary', {}).get('compliant', 0)}
- **Non-Compliant**: {framework_data.get('summary', {}).get('non_compliant', 0)}

"""
        
        # Penetration Testing Results
        if "penetration_testing" in components:
            pentest_data = components["penetration_testing"]
            pentest_summary = pentest_data.get("summary", {})
            
            report += f"""### Penetration Testing Results
- **Total Tests**: {pentest_summary.get('total_tests', 0)}
- **Vulnerabilities Found**: {pentest_summary.get('vulnerabilities_found', 0)}
- **Risk Score**: {pentest_summary.get('risk_score', 0)}

#### Test Distribution
"""
            
            for test_name, test_data in pentest_summary.get('test_distribution', {}).items():
                report += f"- **{test_name}**: {test_data.get('vulnerable', 0)}/{test_data.get('total', 0)} vulnerable\n"
        
        # Recommendations
        report += f"""
## Technical Recommendations

### Immediate Actions (Critical/High Priority)
"""
        
        critical_recs = [rec for rec in assessment_results.get('recommendations', []) 
                        if any(word in rec.lower() for word in ['critical', 'urgent', 'immediately'])]
        
        for rec in critical_recs[:5]:
            report += f"- {rec}\n"
        
        report += f"""
### Medium-Term Improvements
"""
        
        other_recs = [rec for rec in assessment_results.get('recommendations', []) 
                     if rec not in critical_recs]
        
        for rec in other_recs[:10]:
            report += f"- {rec}\n"
        
        report += """
## Implementation Timeline
1. **Week 1**: Address all critical security vulnerabilities
2. **Week 2-3**: Implement high-priority security controls
3. **Month 1**: Complete compliance remediation
4. **Ongoing**: Regular security testing and monitoring

---
*Detailed technical findings available in component-specific reports*
"""
        
        return report
    
    def generate_risk_assessment_report(self, assessment_results: Dict[str, Any]) -> str:
        """Generate risk assessment report"""
        summary = assessment_results.get("summary", {})
        risk_score = assessment_results.get("risk_score", 0)
        
        report = f"""# Security Risk Assessment Report

## Risk Overview
- **Overall Risk Score**: {risk_score:.1f}/100
- **Risk Level**: {self._get_risk_level(risk_score)}
- **Assessment Date**: {assessment_results['start_time']}

## Risk Analysis

### Threat Landscape
Based on the security assessment, the following risk areas have been identified:

#### High-Risk Areas
"""
        
        if summary.get('critical_issues', 0) > 0:
            report += f"- **Critical Security Vulnerabilities**: {summary['critical_issues']} critical issues identified\n"
        
        if summary.get('compliance_score', 100) < 70:
            report += f"- **Compliance Gaps**: {summary['compliance_score']:.1f}% compliance score indicates significant gaps\n"
        
        if summary.get('high_issues', 0) > 5:
            report += f"- **High Severity Vulnerabilities**: {summary['high_issues']} high-severity issues require attention\n"
        
        report += f"""
#### Medium-Risk Areas
- **Configuration Security**: Review required for security configurations
- **Dependency Management**: Regular updates and vulnerability monitoring needed
- **Access Controls**: Implementation and review of authorization mechanisms

### Risk Impact Assessment

#### Business Impact
- **Confidentiality Risk**: {self._assess_confidentiality_risk(summary)}
- **Integrity Risk**: {self._assess_integrity_risk(summary)}
- **Availability Risk**: {self._assess_availability_risk(summary)}

#### Technical Impact
- **System Security**: {self._assess_system_security(summary)}
- **Data Protection**: {self._assess_data_protection(summary)}
- **Network Security**: {self._assess_network_security(summary)}

### Risk Mitigation Strategy

#### Immediate Actions (0-30 days)
"""
        
        immediate_actions = [
            rec for rec in assessment_results.get('recommendations', [])[:5]
        ]
        
        for action in immediate_actions:
            report += f"- {action}\n"
        
        report += f"""
#### Short-term Actions (1-3 months)
- Implement comprehensive security monitoring
- Establish security incident response procedures
- Regular security training for development team
- Security architecture review and improvements

#### Long-term Actions (3-12 months)
- Mature security operations capabilities
- Advanced threat detection and response
- Comprehensive security metrics and reporting
- Regular third-party security assessments

### Risk Monitoring and Review
- **Monthly**: Security metrics review and reporting
- **Quarterly**: Risk assessment updates and trend analysis
- **Annually**: Comprehensive security assessment and strategy review

---
*Risk assessment based on industry standards and best practices*
"""
        
        return report
    
    def _get_status_description(self, status: str) -> str:
        """Get description for overall status"""
        descriptions = {
            "critical": "IMMEDIATE ACTION REQUIRED: Critical security vulnerabilities pose significant risk to the organization.",
            "high_risk": "HIGH PRIORITY: Multiple high-severity issues require prompt remediation.",
            "non_compliant": "COMPLIANCE GAPS: Security controls do not meet required compliance standards.",
            "needs_improvement": "IMPROVEMENT NEEDED: Security posture requires enhancement to meet best practices.",
            "acceptable": "ACCEPTABLE: Security posture meets basic requirements but monitoring should continue.",
            "unknown": "UNKNOWN: Unable to determine security status - manual review required."
        }
        return descriptions.get(status, descriptions["unknown"])
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level description"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _assess_confidentiality_risk(self, summary: Dict) -> str:
        """Assess confidentiality risk level"""
        if summary.get('critical_issues', 0) > 0:
            return "HIGH - Critical vulnerabilities may expose sensitive data"
        elif summary.get('high_issues', 0) > 3:
            return "MEDIUM - Multiple vulnerabilities pose data exposure risk"
        else:
            return "LOW - Basic data protection controls in place"
    
    def _assess_integrity_risk(self, summary: Dict) -> str:
        """Assess integrity risk level"""
        if summary.get('critical_issues', 0) > 0:
            return "HIGH - Critical vulnerabilities may allow data manipulation"
        elif summary.get('compliance_score', 100) < 70:
            return "MEDIUM - Compliance gaps may affect data integrity"
        else:
            return "LOW - Adequate integrity controls identified"
    
    def _assess_availability_risk(self, summary: Dict) -> str:
        """Assess availability risk level"""
        if summary.get('critical_issues', 0) > 2:
            return "HIGH - Multiple critical issues may impact service availability"
        elif summary.get('high_issues', 0) > 5:
            return "MEDIUM - Security issues may affect system stability"
        else:
            return "LOW - Basic availability protections in place"
    
    def _assess_system_security(self, summary: Dict) -> str:
        """Assess system security level"""
        security_score = summary.get('security_score', 0)
        if security_score < 50:
            return "POOR - Significant security improvements required"
        elif security_score < 70:
            return "FAIR - Security controls need enhancement"
        elif security_score < 85:
            return "GOOD - Adequate security with room for improvement"
        else:
            return "EXCELLENT - Strong security posture"
    
    def _assess_data_protection(self, summary: Dict) -> str:
        """Assess data protection level"""
        compliance_score = summary.get('compliance_score', 0)
        if compliance_score < 60:
            return "INADEQUATE - Data protection controls insufficient"
        elif compliance_score < 80:
            return "FAIR - Basic data protection with gaps"
        else:
            return "GOOD - Adequate data protection controls"
    
    def _assess_network_security(self, summary: Dict) -> str:
        """Assess network security level"""
        if summary.get('critical_issues', 0) > 0:
            return "POOR - Critical network security issues identified"
        elif summary.get('high_issues', 0) > 2:
            return "FAIR - Network security improvements needed"
        else:
            return "GOOD - Basic network security controls in place"
    
    async def start_continuous_monitoring(self):
        """Start continuous security monitoring"""
        self.logger.info("Starting continuous security monitoring")
        
        # Initialize security monitor if not already done
        if not self.security_monitor:
            monitor_config = self.security_dir / "monitor_config.yaml"
            if monitor_config.exists():
                self.security_monitor = SecurityMonitor(str(monitor_config))
            else:
                self.security_monitor = SecurityMonitor()
        
        # Start monitoring
        await self.security_monitor.start_monitoring()
    
    def stop_continuous_monitoring(self):
        """Stop continuous security monitoring"""
        if self.security_monitor:
            self.security_monitor.stop_monitoring()
            self.logger.info("Continuous security monitoring stopped")
    
    async def run_quick_security_scan(self) -> Dict[str, Any]:
        """Run quick security scan (subset of full assessment)"""
        self.logger.info("Running quick security scan")
        
        # Run only the most critical checks
        quick_results = {
            "scan_type": "quick",
            "start_time": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # Quick vulnerability scan
            quick_audit = await self.audit_framework.run_static_analysis()
            quick_results["components"]["vulnerability_scan"] = {
                "findings": quick_audit,
                "total_findings": len(quick_audit)
            }
            
            # Quick compliance check (OWASP A01, A02, A03 only)
            quick_compliance = await self.compliance_validator.validate_owasp_top_10()
            top_3_results = {k: v for k, v in quick_compliance.items() if k in ["A01", "A02", "A03"]}
            quick_results["components"]["compliance_check"] = top_3_results
            
            quick_results["end_time"] = datetime.now().isoformat()
            quick_results["status"] = "completed"
            
        except Exception as e:
            self.logger.error(f"Quick scan failed: {str(e)}")
            quick_results["status"] = "failed"
            quick_results["error"] = str(e)
        
        return quick_results


async def main():
    """Main CLI interface for security orchestrator"""
    parser = argparse.ArgumentParser(description="Claude Code Security Orchestrator")
    parser.add_argument("command", choices=[
        "full-assessment", "quick-scan", "monitor", "pentest", "compliance"
    ], help="Security operation to perform")
    parser.add_argument("--directory", "-d", help="Base directory to assess", default=".")
    parser.add_argument("--output", "-o", help="Output directory for reports")
    parser.add_argument("--config", "-c", help="Configuration file")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = SecurityOrchestrator(args.directory)
    
    try:
        if args.command == "full-assessment":
            print("🔒 Running comprehensive security assessment...")
            results = await orchestrator.run_full_security_assessment()
            
            print(f"\n✅ Security Assessment Completed!")
            print(f"📊 Assessment ID: {results['assessment_id']}")
            print(f"📈 Risk Score: {results.get('risk_score', 0):.1f}/100")
            print(f"🔍 Total Findings: {results.get('summary', {}).get('total_findings', 0)}")
            print(f"❗ Critical Issues: {results.get('summary', {}).get('critical_issues', 0)}")
            print(f"⚠️  High Issues: {results.get('summary', {}).get('high_issues', 0)}")
            print(f"📋 Status: {results.get('summary', {}).get('overall_status', 'Unknown').upper()}")
            
            # Exit with appropriate code
            if results.get('summary', {}).get('critical_issues', 0) > 0:
                sys.exit(2)  # Critical issues
            elif results.get('summary', {}).get('high_issues', 0) > 5:
                sys.exit(1)  # High issues
            else:
                sys.exit(0)  # Success
        
        elif args.command == "quick-scan":
            print("🔍 Running quick security scan...")
            results = await orchestrator.run_quick_security_scan()
            
            findings_count = results.get('components', {}).get('vulnerability_scan', {}).get('total_findings', 0)
            print(f"\n✅ Quick scan completed!")
            print(f"🔍 Findings: {findings_count}")
            
            sys.exit(1 if findings_count > 0 else 0)
        
        elif args.command == "monitor":
            print("👁️  Starting continuous security monitoring...")
            print("Press Ctrl+C to stop monitoring")
            
            try:
                await orchestrator.start_continuous_monitoring()
            except KeyboardInterrupt:
                print("\n🛑 Stopping security monitoring...")
                orchestrator.stop_continuous_monitoring()
        
        elif args.command == "pentest":
            print("🎯 Running penetration testing...")
            results = await orchestrator.run_penetration_tests()
            
            vulns_found = results.get('vulnerabilities_found', 0)
            print(f"\n✅ Penetration testing completed!")
            print(f"🎯 Vulnerabilities found: {vulns_found}")
            
            sys.exit(1 if vulns_found > 0 else 0)
        
        elif args.command == "compliance":
            print("📋 Running compliance validation...")
            results = await orchestrator.compliance_validator.run_comprehensive_compliance_assessment()
            
            for framework, data in results.items():
                compliance_pct = data.get('compliance_percentage', 0)
                print(f"📋 {framework}: {compliance_pct:.1f}% compliant")
            
            # Exit based on lowest compliance score
            min_compliance = min(data.get('compliance_percentage', 100) for data in results.values())
            sys.exit(0 if min_compliance >= 80 else 1)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())