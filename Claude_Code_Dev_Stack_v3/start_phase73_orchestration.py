#!/usr/bin/env python3
"""
PHASE 7.3 Orchestration System Startup Script
Complete initialization and testing of the unified MCP service orchestration layer.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add paths for imports
sys.path.append(str(Path(__file__).parent / "core" / "orchestration"))
sys.path.append(str(Path(__file__).parent / "core" / "hooks" / "hooks"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('phase73_orchestration.log')
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main orchestration system demonstration"""
    logger.info("🚀 Starting PHASE 7.3 Orchestration System")
    
    try:
        # Import orchestration components
        from core.orchestration import (
            start_orchestration_system,
            get_orchestration_status,
            route_service_request,
            start_gateway_server,
            get_service_types
        )
        
        # Import v3 orchestrator
        from v3_orchestrator import get_v3_orchestrator
        
        logger.info("✅ Successfully imported all orchestration components")
        
        # 1. Start the unified orchestration system
        logger.info("🔧 Initializing orchestration system...")
        success = await start_orchestration_system()
        
        if not success:
            logger.error("❌ Failed to start orchestration system")
            return False
        
        logger.info("✅ Orchestration system started successfully")
        
        # 2. Get and display system status
        logger.info("📊 Getting system status...")
        status = await get_orchestration_status()
        
        print("\n" + "="*80)
        print("PHASE 7.3 ORCHESTRATION SYSTEM STATUS")
        print("="*80)
        print(f"System Running: {status['system']['running']}")
        print(f"Version: {status['system']['version']}")
        print(f"Components Initialized: {status['system']['initialized']}")
        
        if status['components']:
            print("\nComponent Status:")
            for component, comp_status in status['components'].items():
                if isinstance(comp_status, dict):
                    comp_running = comp_status.get('running', comp_status.get('available', False))
                    print(f"  {component}: {'✅' if comp_running else '❌'}")
                else:
                    print(f"  {component}: {'✅' if comp_status else '❌'}")
        
        if status['services']:
            print(f"\nServices Available: {len(status['services'])}")
            for service_type, service_info in status['services'].items():
                if isinstance(service_info, dict):
                    total = service_info.get('total_instances', 0)
                    healthy = service_info.get('healthy_instances', 0)
                    print(f"  {service_type}: {healthy}/{total} healthy")
        
        # 3. Test v3 orchestrator integration
        logger.info("🔗 Testing v3 orchestrator integration...")
        v3_orch = get_v3_orchestrator()
        
        if v3_orch:
            print(f"\nv3 Orchestrator Integration: ✅")
            print(f"PHASE 7.3 Enabled: {getattr(v3_orch, 'phase73_initialized', False)}")
            
            # Test MCP service routing through v3
            test_service = v3_orch.route_mcp_service("playwright", {"test": True})
            if test_service:
                print(f"MCP Service Routing: ✅ ({test_service.get('name', 'Unknown')})")
            else:
                print(f"MCP Service Routing: ❌ (No services available)")
        else:
            print(f"\nv3 Orchestrator Integration: ❌")
        
        # 4. Test service routing
        logger.info("🔀 Testing service routing...")
        print(f"\nAvailable Service Types: {get_service_types()}")
        
        # Test each service type
        for service_type in ["playwright", "github", "websearch"]:
            service_info = await route_service_request(
                service_type, 
                {"test_request": True, "session_id": "test_session"}
            )
            
            if service_info:
                print(f"  {service_type}: ✅ -> {service_info.get('url', 'N/A')}")
            else:
                print(f"  {service_type}: ❌ (No instances available)")
        
        # 5. Demonstrate load balancing
        logger.info("⚖️ Testing load balancing...")
        print("\nLoad Balancing Test (5 requests to playwright):")
        
        for i in range(5):
            service_info = await route_service_request("playwright", {"request_id": i})
            if service_info:
                print(f"  Request {i+1}: {service_info.get('name', 'Unknown')} ({service_info.get('id', 'N/A')[:8]})")
            else:
                print(f"  Request {i+1}: No service available")
            await asyncio.sleep(0.1)  # Small delay
        
        # 6. Test event processing through v3 orchestrator
        logger.info("📨 Testing event processing...")
        if v3_orch:
            print("\nEvent Processing Test:")
            
            # Test different event types
            test_events = [
                ("user_prompt", {"prompt": "Take a screenshot of github.com"}),
                ("mcp_request", {"service_type": "github", "action": "list_repos"}),
                ("agent_activation", {"agent_type": "frontend"}),
                ("user_prompt", {"prompt": "Search for Python tutorials"})
            ]
            
            for event_type, data in test_events:
                result = v3_orch.process_request(event_type, data)
                phase73_result = result.get("phase73_orchestration", {})
                
                service_routed = phase73_result.get("service_routed", False)
                service_info = phase73_result.get("service_info", {})
                
                print(f"  {event_type}: {'✅' if service_routed else '❌'}", end="")
                if service_routed and service_info:
                    print(f" -> {service_info.get('type', 'unknown')} service")
                else:
                    print()
        
        # 7. Final status check
        logger.info("📈 Final system metrics...")
        final_status = await get_orchestration_status()
        metrics = final_status.get('metrics', {})
        
        print(f"\nFinal Metrics:")
        print(f"  Events Processed: {metrics.get('events_processed', 0)}")
        print(f"  Services Routed: {metrics.get('service_routes', 0)}")
        print(f"  Load Balance Decisions: {metrics.get('load_balance_decisions', 0)}")
        print(f"  Integration Cycles: {metrics.get('coordination_cycles', 0)}")
        
        print("\n" + "="*80)
        print("🎉 PHASE 7.3 ORCHESTRATION SYSTEM DEMONSTRATION COMPLETE")
        print("="*80)
        
        # 8. Optional: Start the gateway server
        print(f"\n🌐 To start the REST API gateway, run:")
        print(f"   python -m core.orchestration.orchestration_gateway --port 8000")
        print(f"   Then visit: http://localhost:8000/dashboard")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        print(f"\n❌ Failed to import orchestration components: {e}")
        print("Make sure all PHASE 7.3 components are properly installed.")
        return False
    
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        print(f"\n❌ System error: {e}")
        return False


async def quick_demo():
    """Quick demonstration without full testing"""
    logger.info("🚀 Quick PHASE 7.3 Demo")
    
    try:
        from core.orchestration import quick_start, get_orchestration_status
        
        # Quick start the system
        success = await quick_start(enable_gateway=False)
        
        if success:
            status = await get_orchestration_status()
            print(f"✅ PHASE 7.3 System Running")
            print(f"   Components: {len([c for c, s in status.get('components', {}).items() if s])}")
            print(f"   Services: {len(status.get('services', {}))}")
            print(f"   Status: {status['system']['running']}")
        else:
            print(f"❌ Failed to start PHASE 7.3 system")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")


def start_gateway_only():
    """Start only the API gateway"""
    try:
        from core.orchestration.orchestration_gateway import app
        import uvicorn
        
        print("🌐 Starting PHASE 7.3 API Gateway...")
        print("   Dashboard: http://localhost:8000/dashboard")
        print("   API Docs: http://localhost:8000/docs")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except ImportError:
        print("❌ Gateway not available - install required dependencies")
    except Exception as e:
        print(f"❌ Gateway error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PHASE 7.3 Orchestration System")
    parser.add_argument("--mode", choices=["full", "quick", "gateway"], default="full",
                       help="Demo mode: full=complete demo, quick=basic check, gateway=API only")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if args.mode == "full":
        print("🚀 Starting Full PHASE 7.3 Orchestration Demonstration")
        print("This will test all components and integrations...")
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    
    elif args.mode == "quick":
        print("⚡ Quick PHASE 7.3 System Check")
        asyncio.run(quick_demo())
    
    elif args.mode == "gateway":
        print("🌐 Starting API Gateway Only")
        start_gateway_only()
    
    else:
        parser.print_help()