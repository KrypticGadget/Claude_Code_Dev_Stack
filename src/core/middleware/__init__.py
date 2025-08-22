#!/usr/bin/env python3
"""
LSP-Hook Bridge Middleware - Complete Integration System
Robust language server protocol integration with hook system featuring:
- Real-time code analysis triggers
- IntelliSense enhancement 
- Automated code quality hooks
- Language server integration
- Performance optimization
- Error recovery
- Configuration management
"""

from .lsp_hook_bridge import (
    LSPHookBridge,
    LanguageServerConfig,
    LSPEventType,
    HookExecutionMode,
    HookExecutionContext
)

from .websocket_lsp_gateway import (
    WebSocketLSPGateway,
    MessageRouter,
    MessageFilter,
    FilterRule,
    FilterAction,
    MessagePriority,
    PerformanceOptimizer
)

from .automated_quality_hooks import (
    AutomatedQualityAssessor,
    QualityReport,
    QualityIssue,
    QualityMetric,
    SeverityLevel,
    QualityCategory,
    PythonQualityAnalyzer,
    TypeScriptQualityAnalyzer
)

from .lsp_config_manager import (
    LSPConfigManager,
    BridgeConfiguration,
    LanguageServerMapping,
    HookConfiguration,
    HealthMonitor,
    HealthMetric,
    HealthStatus,
    ConfigurationValidator
)

from .lsp_integration_orchestrator import (
    LSPIntegrationOrchestrator,
    IntegrationState,
    SystemMetrics,
    main
)

# Version information
__version__ = "1.0.0"
__author__ = "Claude Code Agents Team"
__description__ = "LSP-Hook Bridge Middleware for Real-time Code Analysis"

# Export all main classes and functions
__all__ = [
    # Core Bridge
    "LSPHookBridge",
    "LanguageServerConfig", 
    "LSPEventType",
    "HookExecutionMode",
    "HookExecutionContext",
    
    # WebSocket Gateway
    "WebSocketLSPGateway",
    "MessageRouter",
    "MessageFilter",
    "FilterRule",
    "FilterAction", 
    "MessagePriority",
    "PerformanceOptimizer",
    
    # Quality Assessment
    "AutomatedQualityAssessor",
    "QualityReport",
    "QualityIssue",
    "QualityMetric",
    "SeverityLevel",
    "QualityCategory",
    "PythonQualityAnalyzer",
    "TypeScriptQualityAnalyzer",
    
    # Configuration Management
    "LSPConfigManager",
    "BridgeConfiguration",
    "LanguageServerMapping",
    "HookConfiguration",
    "HealthMonitor",
    "HealthMetric",
    "HealthStatus",
    "ConfigurationValidator",
    
    # Main Orchestrator
    "LSPIntegrationOrchestrator",
    "IntegrationState",
    "SystemMetrics",
    "main"
]


def get_version_info() -> dict:
    """Get version and system information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "lsp_hook_bridge": "Core LSP-Hook communication bridge",
            "websocket_gateway": "Real-time WebSocket communication layer",
            "automated_quality": "Automated code quality assessment",
            "config_manager": "Dynamic configuration with hot-reload",
            "orchestrator": "Main integration system orchestrator"
        },
        "features": [
            "Real-time code analysis triggers",
            "IntelliSense enhancement",
            "Automated code quality assessment", 
            "Multi-language server support",
            "Performance optimization with caching",
            "Error recovery and health monitoring",
            "Hot-reloadable configuration",
            "WebSocket communication layer",
            "Message filtering and routing",
            "Comprehensive quality metrics"
        ]
    }


def create_default_orchestrator(config_dir: str = None) -> LSPIntegrationOrchestrator:
    """Create orchestrator with default configuration"""
    return LSPIntegrationOrchestrator(config_dir=config_dir)


def create_quality_assessor() -> AutomatedQualityAssessor:
    """Create quality assessor with default analyzers"""
    return AutomatedQualityAssessor()


def create_websocket_gateway(host: str = "localhost", port: int = 8765) -> WebSocketLSPGateway:
    """Create WebSocket gateway with default settings"""
    return WebSocketLSPGateway(host=host, port=port)


def create_lsp_bridge(config_path: str = None) -> LSPHookBridge:
    """Create LSP bridge with default configuration"""
    return LSPHookBridge(config_path=config_path)


def create_config_manager(config_dir: str = None) -> LSPConfigManager:
    """Create configuration manager"""
    return LSPConfigManager(config_dir=config_dir)


# Convenience functions for quick setup
async def quick_start(config_dir: str = None, 
                     websocket_port: int = 8765,
                     enable_quality_assessment: bool = True) -> LSPIntegrationOrchestrator:
    """Quick start the complete LSP integration system"""
    orchestrator = LSPIntegrationOrchestrator(config_dir=config_dir)
    
    # Initialize with default configuration
    success = await orchestrator.initialize()
    
    if not success:
        raise RuntimeError("Failed to initialize LSP Integration system")
    
    return orchestrator


# Example usage patterns
USAGE_EXAMPLES = {
    "basic_setup": '''
# Basic setup and start
from core.middleware import LSPIntegrationOrchestrator
import asyncio

async def main():
    orchestrator = LSPIntegrationOrchestrator()
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
    ''',
    
    "quality_assessment": '''
# Manual quality assessment
from core.middleware import AutomatedQualityAssessor

assessor = AutomatedQualityAssessor()
report = assessor.assess_file("path/to/file.py")
print(f"Quality score: {report.overall_score}")
print(f"Issues found: {len(report.issues)}")
    ''',
    
    "websocket_client": '''
# WebSocket client example
import asyncio
import websockets
import json

async def connect_to_lsp_gateway():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Send LSP request
        request = {
            "type": "lsp_request",
            "method": "textDocument/hover",
            "params": {
                "textDocument": {"uri": "file:///path/to/file.py"},
                "position": {"line": 10, "character": 5}
            }
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        print(json.loads(response))
    ''',
    
    "configuration": '''
# Configuration management
from core.middleware import LSPConfigManager, LanguageServerMapping

config_manager = LSPConfigManager()

# Add a new language server
python_server = LanguageServerMapping(
    server_name="python",
    server_command=["pylsp"],
    file_extensions=[".py"],
    capabilities={"textDocument": {"publishDiagnostics": True}},
    hook_mappings={
        "textDocument/publishDiagnostics": ["quality_gate_hook"]
    }
)

config_manager.add_language_server(python_server)
    '''
}


def get_usage_examples() -> dict:
    """Get usage examples for the middleware system"""
    return USAGE_EXAMPLES