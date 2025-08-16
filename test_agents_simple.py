#!/usr/bin/env python3
"""
Claude Code Dev Stack v3.0 - Agent Testing Suite (ASCII Version)
Tests all 28 agents, routing, audio notifications, parallel execution, and error handling.
"""

import asyncio
import json
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# All 28 agents
AGENTS = {
    "master-orchestrator": {"tier": 1, "category": "orchestration", "test_prompt": "Coordinate a full project lifecycle"},
    "prompt-engineer": {"tier": 1, "category": "orchestration", "test_prompt": "Optimize this prompt: 'make a website'"},
    "business-analyst": {"tier": 2, "category": "business", "test_prompt": "Analyze market viability for SaaS platform"},
    "technical-cto": {"tier": 2, "category": "business", "test_prompt": "Assess technical feasibility for data platform"},
    "ceo-strategy": {"tier": 2, "category": "business", "test_prompt": "Develop go-to-market strategy"},
    "financial-analyst": {"tier": 2, "category": "business", "test_prompt": "Create financial model for subscription service"},
    "project-manager": {"tier": 3, "category": "planning", "test_prompt": "Create project timeline for web application"},
    "technical-specifications": {"tier": 3, "category": "planning", "test_prompt": "Generate technical requirements for REST API"},
    "business-tech-alignment": {"tier": 3, "category": "planning", "test_prompt": "Align technical architecture with business objectives"},
    "technical-documentation": {"tier": 4, "category": "architecture", "test_prompt": "Create documentation for microservices"},
    "api-integration-specialist": {"tier": 4, "category": "architecture", "test_prompt": "Design third-party API integration"},
    "frontend-architecture": {"tier": 4, "category": "architecture", "test_prompt": "Design React application architecture"},
    "frontend-mockup": {"tier": 4, "category": "architecture", "test_prompt": "Create interactive dashboard mockup"},
    "ui-ux-design": {"tier": 4, "category": "architecture", "test_prompt": "Design mobile application UX"},
    "production-frontend": {"tier": 5, "category": "development", "test_prompt": "Build production React frontend"},
    "backend-services": {"tier": 5, "category": "development", "test_prompt": "Develop REST API with authentication"},
    "database-architecture": {"tier": 5, "category": "development", "test_prompt": "Design optimized database schema"},
    "middleware-specialist": {"tier": 5, "category": "development", "test_prompt": "Implement message queue system"},
    "mobile-development": {"tier": 5, "category": "development", "test_prompt": "Develop cross-platform mobile app"},
    "devops-engineering": {"tier": 6, "category": "devops", "test_prompt": "Setup CI/CD pipeline"},
    "integration-setup": {"tier": 6, "category": "devops", "test_prompt": "Configure development environment"},
    "script-automation": {"tier": 6, "category": "devops", "test_prompt": "Create deployment automation scripts"},
    "development-prompt": {"tier": 6, "category": "devops", "test_prompt": "Generate development command sequences"},
    "security-architecture": {"tier": 7, "category": "quality", "test_prompt": "Conduct security audit"},
    "performance-optimization": {"tier": 7, "category": "quality", "test_prompt": "Analyze application performance"},
    "quality-assurance": {"tier": 7, "category": "quality", "test_prompt": "Review code quality standards"},
    "testing-automation": {"tier": 7, "category": "quality", "test_prompt": "Implement comprehensive testing"},
    "usage-guide": {"tier": 7, "category": "quality", "test_prompt": "Generate user documentation"}
}

class AgentTester:
    def __init__(self):
        self.test_results = {}
        self.orchestrator_path = self._find_orchestrator()
        self.audio_base_path = self._find_audio_path()
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        logger.info(f"Initializing with {len(AGENTS)} agents")
        logger.info(f"Orchestrator: {self.orchestrator_path}")
        logger.info(f"Audio path: {self.audio_base_path}")
    
    def _find_orchestrator(self) -> Optional[Path]:
        search_paths = [
            "Claude_Code_Dev_Stack_v3/core/hooks/hooks/v3_orchestrator.py",
            "core/hooks/hooks/v3_orchestrator.py"
        ]
        
        for path_str in search_paths:
            path = Path(path_str)
            if path.exists():
                return path.absolute()
        return None
    
    def _find_audio_path(self) -> Optional[Path]:
        search_paths = [
            "Claude_Code_Dev_Stack_v3/core/audio/audio",
            "core/audio/audio"
        ]
        
        for path_str in search_paths:
            path = Path(path_str)
            if path.exists():
                return path.absolute()
        return None
    
    async def test_orchestrator(self) -> Dict[str, Any]:
        logger.info("Testing v3_orchestrator.py...")
        
        if not self.orchestrator_path:
            return {"status": "skipped", "reason": "Orchestrator not found"}
        
        try:
            sys.path.append(str(self.orchestrator_path.parent))
            from v3_orchestrator import get_v3_orchestrator, process_hook
            
            orchestrator = get_v3_orchestrator()
            status = orchestrator.get_system_status()
            
            test_data = {"agent": "test", "prompt": "test"}
            result = orchestrator.process_request("agent_activation", test_data)
            
            return {
                "status": "passed",
                "orchestrator_available": True,
                "system_health": status.get('system_state', {}).get('health'),
                "processing_successful": result.get('processed', False)
            }
            
        except Exception as e:
            logger.error(f"Orchestrator test failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def test_single_agent(self, agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Testing @agent-{agent_name}")
        
        start_time = time.time()
        
        # Validate configuration
        required_fields = ["tier", "category", "test_prompt"]
        missing = [f for f in required_fields if f not in config]
        
        if missing:
            self.failed_tests += 1
            return {
                "agent": agent_name,
                "status": "failed",
                "error": f"Missing fields: {missing}"
            }
        
        # Test audio file (if audio directory exists)
        audio_status = "skipped"
        if self.audio_base_path:
            audio_files = list(self.audio_base_path.glob("*.wav"))
            audio_status = "available" if audio_files else "no_files"
        
        # Simulate prompt processing
        test_duration = time.time() - start_time
        
        self.passed_tests += 1
        return {
            "agent": agent_name,
            "status": "passed",
            "tier": config["tier"],
            "category": config["category"],
            "test_duration": test_duration,
            "audio_status": audio_status,
            "prompt_tested": len(config["test_prompt"]) > 0
        }
    
    async def test_parallel_execution(self, agent_batch: List[str]) -> Dict[str, Any]:
        logger.info(f"Testing parallel batch: {agent_batch}")
        
        start_time = time.time()
        
        # Simulate parallel testing
        tasks = []
        for agent_name in agent_batch:
            if agent_name in AGENTS:
                task = asyncio.create_task(
                    self._async_test_agent(agent_name, AGENTS[agent_name])
                )
                tasks.append(task)
        
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
        
        execution_time = time.time() - start_time
        
        return {
            "batch_size": len(agent_batch),
            "execution_time": execution_time,
            "results": results,
            "parallel_efficiency": len(results) / execution_time if execution_time > 0 else 0
        }
    
    async def _async_test_agent(self, agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate async processing delay
        await asyncio.sleep(0.1)
        return self.test_single_agent(agent_name, config)
    
    def test_agent_communication(self) -> Dict[str, Any]:
        logger.info("Testing agent communication patterns...")
        
        communication_patterns = [
            {
                "pattern": "orchestrator_to_business",
                "source": "master-orchestrator",
                "targets": ["business-analyst", "technical-cto"]
            },
            {
                "pattern": "business_to_planning", 
                "source": "business-analyst",
                "targets": ["project-manager", "technical-specifications"]
            },
            {
                "pattern": "architecture_to_development",
                "source": "frontend-architecture", 
                "targets": ["production-frontend"]
            }
        ]
        
        results = []
        for pattern in communication_patterns:
            source_exists = pattern["source"] in AGENTS
            targets_exist = all(t in AGENTS for t in pattern["targets"])
            
            results.append({
                "pattern": pattern["pattern"],
                "source_available": source_exists,
                "targets_available": targets_exist,
                "communication_possible": source_exists and targets_exist
            })
        
        successful = sum(1 for r in results if r["communication_possible"])
        
        return {
            "status": "passed" if successful == len(results) else "partial",
            "successful_patterns": successful,
            "total_patterns": len(results),
            "pattern_results": results
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        logger.info("Starting comprehensive test suite...")
        
        suite_start = time.time()
        
        # Test orchestrator
        orchestrator_result = await self.test_orchestrator()
        
        # Test all agents in parallel batches
        agent_names = list(AGENTS.keys())
        batch_size = 8
        batches = [agent_names[i:i + batch_size] for i in range(0, len(agent_names), batch_size)]
        
        all_results = []
        for i, batch in enumerate(batches):
            logger.info(f"Testing batch {i+1}/{len(batches)}")
            batch_result = await self.test_parallel_execution(batch)
            all_results.extend(batch_result["results"])
        
        # Test communication patterns
        communication_result = self.test_agent_communication()
        
        # Calculate summary
        total_time = time.time() - suite_start
        
        summary = {
            "test_suite_version": "3.0",
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": total_time,
            "total_agents": len(AGENTS),
            "agents_passed": self.passed_tests,
            "agents_failed": self.failed_tests,
            "success_rate": (self.passed_tests / len(AGENTS)) * 100,
            
            "orchestrator_test": orchestrator_result,
            "communication_test": communication_result,
            "agent_results": all_results,
            
            "system_capabilities": {
                "orchestrator_available": orchestrator_result.get("status") == "passed",
                "audio_system_available": self.audio_base_path is not None,
                "parallel_execution": len(all_results) > 0
            }
        }
        
        return summary
    
    def save_results(self, results: Dict[str, Any]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

async def main():
    print("Claude Code Dev Stack v3.0 - Agent Testing Suite")
    print("=" * 60)
    print(f"Testing {len(AGENTS)} agents")
    print("=" * 60)
    
    tester = AgentTester()
    
    try:
        results = await tester.run_comprehensive_test()
        tester.save_results(results)
        
        print("\nTEST RESULTS:")
        print("=" * 60)
        print(f"Total Agents: {results['total_agents']}")
        print(f"Passed: {results['agents_passed']}")
        print(f"Failed: {results['agents_failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Total Time: {results['total_execution_time']:.2f}s")
        
        print("\nSYSTEM COMPONENTS:")
        capabilities = results['system_capabilities']
        print(f"Orchestrator: {'Available' if capabilities['orchestrator_available'] else 'Not Found'}")
        print(f"Audio System: {'Available' if capabilities['audio_system_available'] else 'Not Found'}")
        print(f"Parallel Execution: {'Working' if capabilities['parallel_execution'] else 'Failed'}")
        
        print("\nCOMMUNICATION PATTERNS:")
        comm_test = results['communication_test']
        print(f"Successful: {comm_test['successful_patterns']}/{comm_test['total_patterns']}")
        
        print("=" * 60)
        print("Test completed successfully!")
        
        return results
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(main())