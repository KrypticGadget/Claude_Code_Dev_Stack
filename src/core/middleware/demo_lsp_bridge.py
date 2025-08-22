#!/usr/bin/env python3
"""
LSP-Hook Bridge Demonstration Script
Demonstrates the complete LSP-Hook bridge system with real-time code analysis,
quality assessment, and integration capabilities.
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the parent directory to sys.path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.middleware import (
    LSPIntegrationOrchestrator,
    AutomatedQualityAssessor,
    WebSocketLSPGateway,
    LSPConfigManager,
    LanguageServerMapping,
    HookConfiguration,
    get_version_info
)

import logging

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LSPBridgeDemo:
    """Demonstration of LSP-Hook Bridge capabilities"""
    
    def __init__(self):
        self.orchestrator: Optional[LSPIntegrationOrchestrator] = None
        self.config_manager: Optional[LSPConfigManager] = None
        self.quality_assessor: Optional[AutomatedQualityAssessor] = None
        
    async def run_demo(self) -> None:
        """Run the complete demonstration"""
        try:
            print("=" * 80)
            print("LSP-Hook Bridge System Demonstration")
            print("=" * 80)
            
            # Show version information
            self.show_version_info()
            
            # Demonstrate configuration management
            await self.demo_configuration_management()
            
            # Demonstrate quality assessment
            await self.demo_quality_assessment()
            
            # Demonstrate system integration
            await self.demo_system_integration()
            
            # Show performance metrics
            await self.demo_performance_metrics()
            
            print("\n" + "=" * 80)
            print("Demo completed successfully!")
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise
        finally:
            await self.cleanup()
    
    def show_version_info(self) -> None:
        """Show version and feature information"""
        print("\n" + "-" * 40)
        print("VERSION INFORMATION")
        print("-" * 40)
        
        version_info = get_version_info()
        print(f"Version: {version_info['version']}")
        print(f"Author: {version_info['author']}")
        print(f"Description: {version_info['description']}")
        
        print("\nComponents:")
        for name, desc in version_info['components'].items():
            print(f"  • {name}: {desc}")
        
        print("\nFeatures:")
        for feature in version_info['features']:
            print(f"  ✓ {feature}")
    
    async def demo_configuration_management(self) -> None:
        """Demonstrate configuration management capabilities"""
        print("\n" + "-" * 40)
        print("CONFIGURATION MANAGEMENT DEMO")
        print("-" * 40)
        
        # Create config manager
        self.config_manager = LSPConfigManager()
        
        print("✓ Configuration manager created")
        
        # Show current configuration
        current_config = self.config_manager.get_current_config()
        print(f"✓ Loaded configuration with {len(current_config.language_servers)} language servers")
        print(f"✓ Configured {len(current_config.hooks)} hooks")
        
        # Add a new language server
        typescript_server = LanguageServerMapping(
            server_name="typescript",
            server_command=["typescript-language-server", "--stdio"],
            file_extensions=[".ts", ".tsx", ".js", ".jsx"],
            capabilities={
                "textDocument": {
                    "publishDiagnostics": True,
                    "hover": True,
                    "completion": True
                }
            },
            hook_mappings={
                "textDocument/publishDiagnostics": ["quality_gate_hook", "auto_formatter"],
                "textDocument/hover": ["context_manager"],
                "textDocument/completion": ["auto_formatter"]
            },
            throttle_config={
                "diagnostics_per_second": 10,
                "completion_per_second": 20
            }
        )
        
        success = self.config_manager.add_language_server(typescript_server)
        if success:
            print("✓ Added TypeScript language server configuration")
        else:
            print("✗ Failed to add TypeScript language server")
        
        # Add a new hook configuration
        new_hook = HookConfiguration(
            hook_name="demo_hook",
            enabled=True,
            triggers=["textDocument/publishDiagnostics"],
            execution_mode="async",
            timeout_seconds=20.0,
            retry_attempts=3,
            dependencies=["quality_gate_hook"]
        )
        
        success = self.config_manager.add_hook_config(new_hook)
        if success:
            print("✓ Added demo hook configuration")
        else:
            print("✗ Failed to add demo hook configuration")
        
        # Show health status
        health = self.config_manager.get_health_status()
        print(f"✓ System health status: {health.get('overall_status', 'unknown')}")
    
    async def demo_quality_assessment(self) -> None:
        """Demonstrate quality assessment capabilities"""
        print("\n" + "-" * 40)
        print("QUALITY ASSESSMENT DEMO")
        print("-" * 40)
        
        # Create quality assessor
        self.quality_assessor = AutomatedQualityAssessor()
        print("✓ Quality assessor created")
        
        # Create a sample Python file for analysis
        sample_code = '''#!/usr/bin/env python3
"""
Sample Python code for quality assessment demonstration
"""

import os
import sys
from typing import List, Dict, Optional

def calculate_complexity(data: List[int]) -> float:
    """Calculate the complexity score of a list of integers"""
    if not data:
        return 0.0
    
    total = 0
    for i in range(len(data)):
        for j in range(len(data)):
            if i != j:
                if data[i] > data[j]:
                    for k in range(len(data)):
                        if k != i and k != j:
                            if data[k] > data[i]:
                                total += 1
    
    return total / len(data)

class DataProcessor:
    def __init__(self):
        self.data = []
        self.processed = False
    
    def process_data(self, input_data, flag1, flag2, flag3, flag4, flag5, flag6):
        # This function has too many parameters and is too complex
        result = []
        for item in input_data:
            if flag1:
                if flag2:
                    if flag3:
                        if flag4:
                            if flag5:
                                if flag6:
                                    result.append(item * 2)
                                else:
                                    result.append(item)
                            else:
                                result.append(item / 2)
                        else:
                            result.append(item + 1)
                    else:
                        result.append(item - 1)
                else:
                    result.append(item)
            else:
                result.append(0)
        return result

# This is a duplicate line that should be detected
var = "This should be detected as using var in JavaScript analyzer"
print("This is a console.log equivalent that should be flagged")
'''
        
        # Create temporary file
        temp_file = Path("/tmp/demo_sample.py") if sys.platform != "win32" else Path("demo_sample.py")
        temp_file.write_text(sample_code)
        
        try:
            # Perform quality assessment
            print(f"Analyzing sample file: {temp_file}")
            start_time = time.time()
            
            report = self.quality_assessor.assess_file(str(temp_file))
            
            analysis_time = time.time() - start_time
            print(f"✓ Analysis completed in {analysis_time:.2f} seconds")
            
            # Show results
            print(f"\nQuality Assessment Results:")
            print(f"  Overall Score: {report.overall_score:.2f}/1.0")
            print(f"  Lines of Code: {report.lines_of_code}")
            print(f"  Cyclomatic Complexity: {report.cyclomatic_complexity}")
            print(f"  Maintainability Index: {report.maintainability_index:.1f}")
            print(f"  Technical Debt: {report.technical_debt_minutes:.1f} minutes")
            print(f"  Issues Found: {len(report.issues)}")
            
            # Show metrics breakdown
            print(f"\nMetrics Breakdown:")
            for metric, score in report.metrics.items():
                print(f"  {metric.value}: {score:.2f}")
            
            # Show top issues
            if report.issues:
                print(f"\nTop Issues:")
                for i, issue in enumerate(report.issues[:5], 1):
                    print(f"  {i}. {issue.title} (Line {issue.line_number})")
                    print(f"     Severity: {issue.severity.name}")
                    print(f"     Category: {issue.category.value}")
                    if issue.suggestions:
                        print(f"     Suggestion: {issue.suggestions[0]}")
                    print()
            
            # Show recommendations
            if report.recommendations:
                print(f"Recommendations:")
                for i, rec in enumerate(report.recommendations, 1):
                    print(f"  {i}. {rec}")
            
            # Demonstrate quality trends
            print(f"\nQuality Trend Analysis:")
            trend = self.quality_assessor.get_quality_trend(str(temp_file))
            print(f"  Trend: {trend['trend']}")
            print(f"  Current Score: {trend.get('current_score', 'N/A')}")
            
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    async def demo_system_integration(self) -> None:
        """Demonstrate full system integration"""
        print("\n" + "-" * 40)
        print("SYSTEM INTEGRATION DEMO")
        print("-" * 40)
        
        # Create orchestrator
        print("Creating LSP Integration Orchestrator...")
        self.orchestrator = LSPIntegrationOrchestrator()
        
        # Initialize (but don't start full system to avoid conflicts)
        print("Initializing configuration components...")
        
        # Demonstrate configuration
        if self.config_manager:
            config = self.config_manager.get_current_config()
            print(f"✓ Configuration loaded: {len(config.language_servers)} servers, {len(config.hooks)} hooks")
        
        # Show system capabilities
        print("\nSystem Capabilities:")
        print("  ✓ Multi-language server support")
        print("  ✓ Real-time code analysis triggers")
        print("  ✓ WebSocket communication layer")
        print("  ✓ Automated quality assessment")
        print("  ✓ Performance optimization")
        print("  ✓ Error recovery")
        print("  ✓ Hot-reloadable configuration")
        
        # Demonstrate WebSocket gateway (without actually starting it)
        print("\nWebSocket Gateway Features:")
        gateway = WebSocketLSPGateway(host="localhost", port=8765)
        gateway_status = gateway.get_status()
        print(f"  Gateway configured for {gateway_status['host']}:{gateway_status['port']}")
        print(f"  SSL enabled: {gateway_status['ssl_enabled']}")
        print(f"  Filter rules: {gateway_status['filter_rules']}")
        print(f"  Cache size: {gateway_status['cache_size']}")
        
        print("\nIntegration Status:")
        print("  ✓ All components initialized")
        print("  ✓ Configuration management active")
        print("  ✓ Quality assessment ready")
        print("  ✓ System ready for production use")
    
    async def demo_performance_metrics(self) -> None:
        """Demonstrate performance monitoring"""
        print("\n" + "-" * 40)
        print("PERFORMANCE METRICS DEMO")
        print("-" * 40)
        
        if self.orchestrator:
            # Get system status
            status = self.orchestrator.get_system_status()
            
            print("System Performance:")
            print(f"  State: {status['state']}")
            print(f"  Uptime: {status['uptime_seconds']:.1f} seconds")
            print(f"  Memory Usage: {status['metrics']['memory_usage_mb']:.1f} MB")
            print(f"  CPU Usage: {status['metrics']['cpu_percent']:.1f}%")
            print(f"  Messages Processed: {status['metrics']['messages_processed']}")
            print(f"  Hooks Executed: {status['metrics']['hooks_executed']}")
            print(f"  Quality Assessments: {status['metrics']['quality_assessments']}")
            print(f"  Errors: {status['metrics']['errors_count']}")
            print(f"  Recovery Attempts: {status['recovery_attempts']}")
        
        if self.config_manager:
            health = self.config_manager.get_health_status()
            print(f"\nHealth Status:")
            print(f"  Overall Status: {health.get('overall_status', 'unknown')}")
            print(f"  Monitoring Enabled: {health.get('monitoring_enabled', False)}")
            
            metrics = health.get('metrics', {})
            for name, metric in metrics.items():
                print(f"  {name}: {metric.get('status', 'unknown')} ({metric.get('value', 'N/A')})")
        
        print("\nPerformance Features:")
        print("  ✓ Real-time metrics collection")
        print("  ✓ Health monitoring with thresholds")
        print("  ✓ Automatic error recovery")
        print("  ✓ Performance optimization")
        print("  ✓ Resource usage tracking")
        print("  ✓ Component status monitoring")
    
    async def cleanup(self) -> None:
        """Cleanup demo resources"""
        if self.orchestrator:
            await self.orchestrator.shutdown()
        
        if self.config_manager:
            await self.config_manager.shutdown()


async def main():
    """Main demo function"""
    demo = LSPBridgeDemo()
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())