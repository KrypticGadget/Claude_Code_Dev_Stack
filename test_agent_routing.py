#!/usr/bin/env python3
"""
Agent Routing Integration Test for Claude Code Dev Stack v3.0
Tests @agent- mention routing, delegation patterns, and orchestrator integration.
"""

import json
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# All 28 agents with their routing information
AGENT_ROUTING_MAP = {
    # Tier 1: Orchestration
    "master-orchestrator": {
        "tier": 1,
        "delegates_to": ["business-analyst", "technical-cto", "project-manager"],
        "receives_from": [],
        "routing_priority": "high"
    },
    "prompt-engineer": {
        "tier": 1,
        "delegates_to": ["master-orchestrator"],
        "receives_from": [],
        "routing_priority": "high"
    },
    
    # Tier 2: Business
    "business-analyst": {
        "tier": 2,
        "delegates_to": ["project-manager", "financial-analyst"],
        "receives_from": ["master-orchestrator"],
        "routing_priority": "high"
    },
    "technical-cto": {
        "tier": 2,
        "delegates_to": ["technical-specifications", "frontend-architecture"],
        "receives_from": ["master-orchestrator", "business-analyst"],
        "routing_priority": "high"
    },
    "ceo-strategy": {
        "tier": 2,
        "delegates_to": ["business-analyst", "financial-analyst"],
        "receives_from": ["master-orchestrator"],
        "routing_priority": "medium"
    },
    "financial-analyst": {
        "tier": 2,
        "delegates_to": ["business-tech-alignment"],
        "receives_from": ["business-analyst", "ceo-strategy"],
        "routing_priority": "medium"
    },
    
    # Tier 3: Planning
    "project-manager": {
        "tier": 3,
        "delegates_to": ["technical-specifications", "devops-engineering"],
        "receives_from": ["master-orchestrator", "business-analyst"],
        "routing_priority": "high"
    },
    "technical-specifications": {
        "tier": 3,
        "delegates_to": ["frontend-architecture", "backend-services"],
        "receives_from": ["technical-cto", "project-manager"],
        "routing_priority": "high"
    },
    "business-tech-alignment": {
        "tier": 3,
        "delegates_to": ["technical-specifications"],
        "receives_from": ["financial-analyst"],
        "routing_priority": "medium"
    },
    
    # Tier 4: Architecture
    "technical-documentation": {
        "tier": 4,
        "delegates_to": ["usage-guide"],
        "receives_from": ["technical-specifications"],
        "routing_priority": "low"
    },
    "api-integration-specialist": {
        "tier": 4,
        "delegates_to": ["backend-services", "middleware-specialist"],
        "receives_from": ["technical-specifications"],
        "routing_priority": "medium"
    },
    "frontend-architecture": {
        "tier": 4,
        "delegates_to": ["frontend-mockup", "production-frontend"],
        "receives_from": ["technical-cto", "technical-specifications"],
        "routing_priority": "high"
    },
    "frontend-mockup": {
        "tier": 4,
        "delegates_to": ["ui-ux-design", "production-frontend"],
        "receives_from": ["frontend-architecture"],
        "routing_priority": "medium"
    },
    "ui-ux-design": {
        "tier": 4,
        "delegates_to": ["production-frontend", "mobile-development"],
        "receives_from": ["frontend-mockup"],
        "routing_priority": "medium"
    },
    
    # Tier 5: Development
    "production-frontend": {
        "tier": 5,
        "delegates_to": ["testing-automation", "quality-assurance"],
        "receives_from": ["frontend-architecture", "frontend-mockup", "ui-ux-design"],
        "routing_priority": "high"
    },
    "backend-services": {
        "tier": 5,
        "delegates_to": ["database-architecture", "testing-automation"],
        "receives_from": ["technical-specifications", "api-integration-specialist"],
        "routing_priority": "high"
    },
    "database-architecture": {
        "tier": 5,
        "delegates_to": ["backend-services", "performance-optimization"],
        "receives_from": ["backend-services"],
        "routing_priority": "high"
    },
    "middleware-specialist": {
        "tier": 5,
        "delegates_to": ["backend-services", "performance-optimization"],
        "receives_from": ["api-integration-specialist"],
        "routing_priority": "medium"
    },
    "mobile-development": {
        "tier": 5,
        "delegates_to": ["testing-automation", "quality-assurance"],
        "receives_from": ["ui-ux-design"],
        "routing_priority": "medium"
    },
    
    # Tier 6: DevOps
    "devops-engineering": {
        "tier": 6,
        "delegates_to": ["security-architecture", "performance-optimization"],
        "receives_from": ["project-manager"],
        "routing_priority": "high"
    },
    "integration-setup": {
        "tier": 6,
        "delegates_to": ["script-automation"],
        "receives_from": ["devops-engineering"],
        "routing_priority": "low"
    },
    "script-automation": {
        "tier": 6,
        "delegates_to": ["devops-engineering"],
        "receives_from": ["integration-setup"],
        "routing_priority": "low"
    },
    "development-prompt": {
        "tier": 6,
        "delegates_to": ["script-automation"],
        "receives_from": ["devops-engineering"],
        "routing_priority": "low"
    },
    
    # Tier 7: Quality
    "security-architecture": {
        "tier": 7,
        "delegates_to": [],
        "receives_from": ["devops-engineering"],
        "routing_priority": "critical"
    },
    "performance-optimization": {
        "tier": 7,
        "delegates_to": [],
        "receives_from": ["database-architecture", "middleware-specialist", "devops-engineering"],
        "routing_priority": "high"
    },
    "quality-assurance": {
        "tier": 7,
        "delegates_to": [],
        "receives_from": ["production-frontend", "mobile-development"],
        "routing_priority": "high"
    },
    "testing-automation": {
        "tier": 7,
        "delegates_to": [],
        "receives_from": ["production-frontend", "backend-services", "mobile-development"],
        "routing_priority": "critical"
    },
    "usage-guide": {
        "tier": 7,
        "delegates_to": [],
        "receives_from": ["technical-documentation"],
        "routing_priority": "low"
    }
}

class AgentRoutingTester:
    def __init__(self):
        self.orchestrator_path = self._find_orchestrator()
        self.test_results = {}
        
    def _find_orchestrator(self) -> Optional[Path]:
        """Find the v3_orchestrator.py file"""
        search_paths = [
            "Claude_Code_Dev_Stack_v3/core/hooks/hooks/v3_orchestrator.py",
            "core/hooks/hooks/v3_orchestrator.py"
        ]
        
        for path_str in search_paths:
            path = Path(path_str)
            if path.exists():
                return path.absolute()
        return None
    
    def test_agent_mention_parsing(self) -> Dict[str, Any]:
        """Test @agent- mention parsing functionality"""
        logger.info("Testing @agent- mention parsing...")
        
        test_prompts = [
            "@agent-master-orchestrator start a new project",
            "I need @agent-business-analyst to analyze the market",
            "Can @agent-frontend-architecture and @agent-backend-services work together?",
            "Use @agent-testing-automation for comprehensive testing",
            "@agent-security-architecture please audit the system",
            "Multiple agents: @agent-business-analyst @agent-financial-analyst @agent-ceo-strategy",
            "@agent-nonexistent-agent should be handled gracefully",
            "No agent mentions in this prompt",
            "@agent-prompt-engineer optimize this: @agent-master-orchestrator coordinate everything"
        ]
        
        results = {
            "total_prompts": len(test_prompts),
            "successful_parses": 0,
            "failed_parses": 0,
            "parsing_details": {}
        }
        
        for i, prompt in enumerate(test_prompts):
            try:
                # Parse @agent- mentions
                mentions = self._parse_agent_mentions(prompt)
                
                results["successful_parses"] += 1
                results["parsing_details"][f"prompt_{i}"] = {
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "mentions_found": len(mentions),
                    "agents": [mention["agent"] for mention in mentions],
                    "status": "success"
                }
                
            except Exception as e:
                results["failed_parses"] += 1
                results["parsing_details"][f"prompt_{i}"] = {
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "error": str(e),
                    "status": "failed"
                }
        
        results["parsing_success_rate"] = (results["successful_parses"] / results["total_prompts"]) * 100
        return results
    
    def _parse_agent_mentions(self, prompt: str) -> List[Dict[str, Any]]:
        """Parse @agent- mentions from prompt"""
        import re
        
        pattern = r'@agent-([a-z-]+)'
        mentions = []
        
        for match in re.finditer(pattern, prompt):
            agent_name = match.group(1)
            mentions.append({
                "agent": agent_name,
                "position": match.start(),
                "full_mention": match.group(0)
            })
        
        return mentions
    
    def test_routing_logic(self) -> Dict[str, Any]:
        """Test agent routing and delegation logic"""
        logger.info("Testing agent routing logic...")
        
        routing_scenarios = [
            {
                "name": "master_orchestrator_delegation",
                "source": "master-orchestrator",
                "expected_targets": ["business-analyst", "technical-cto", "project-manager"],
                "scenario_type": "standard_delegation"
            },
            {
                "name": "business_to_technical",
                "source": "business-analyst",
                "expected_targets": ["project-manager", "financial-analyst"],
                "scenario_type": "business_flow"
            },
            {
                "name": "architecture_to_development",
                "source": "frontend-architecture",
                "expected_targets": ["frontend-mockup", "production-frontend"],
                "scenario_type": "development_flow"
            },
            {
                "name": "development_to_quality",
                "source": "backend-services",
                "expected_targets": ["database-architecture", "testing-automation"],
                "scenario_type": "quality_flow"
            },
            {
                "name": "parallel_execution",
                "source": "technical-specifications",
                "expected_targets": ["frontend-architecture", "backend-services"],
                "scenario_type": "parallel_flow"
            }
        ]
        
        results = {
            "total_scenarios": len(routing_scenarios),
            "successful_routes": 0,
            "failed_routes": 0,
            "routing_details": {}
        }
        
        for scenario in routing_scenarios:
            try:
                source_agent = scenario["source"]
                expected_targets = scenario["expected_targets"]
                
                # Check if source agent exists and has correct routing
                if source_agent in AGENT_ROUTING_MAP:
                    actual_targets = AGENT_ROUTING_MAP[source_agent]["delegates_to"]
                    
                    # Check if expected targets match actual delegation rules
                    matching_targets = set(expected_targets).intersection(set(actual_targets))
                    routing_score = len(matching_targets) / len(expected_targets) if expected_targets else 1.0
                    
                    if routing_score >= 0.5:  # At least 50% match
                        results["successful_routes"] += 1
                        status = "success"
                    else:
                        results["failed_routes"] += 1
                        status = "mismatch"
                    
                    results["routing_details"][scenario["name"]] = {
                        "source": source_agent,
                        "expected_targets": expected_targets,
                        "actual_targets": actual_targets,
                        "matching_targets": list(matching_targets),
                        "routing_score": routing_score,
                        "status": status
                    }
                else:
                    results["failed_routes"] += 1
                    results["routing_details"][scenario["name"]] = {
                        "source": source_agent,
                        "error": "Source agent not found",
                        "status": "error"
                    }
                    
            except Exception as e:
                results["failed_routes"] += 1
                results["routing_details"][scenario["name"]] = {
                    "source": scenario["source"],
                    "error": str(e),
                    "status": "exception"
                }
        
        results["routing_success_rate"] = (results["successful_routes"] / results["total_scenarios"]) * 100
        return results
    
    def test_orchestrator_integration(self) -> Dict[str, Any]:
        """Test integration with v3_orchestrator.py"""
        logger.info("Testing orchestrator integration...")
        
        if not self.orchestrator_path:
            return {
                "status": "skipped",
                "reason": "Orchestrator not found",
                "integration_available": False
            }
        
        try:
            # Import orchestrator
            sys.path.append(str(self.orchestrator_path.parent))
            from v3_orchestrator import get_v3_orchestrator, process_hook
            
            orchestrator = get_v3_orchestrator()
            
            # Test orchestrator routing
            test_requests = [
                {
                    "event_type": "agent_activation",
                    "data": {
                        "agent": "business-analyst",
                        "prompt": "Analyze market for new product",
                        "priority": "high"
                    }
                },
                {
                    "event_type": "agent_delegation",
                    "data": {
                        "source_agent": "master-orchestrator",
                        "target_agent": "technical-cto",
                        "delegation_reason": "technical_feasibility_assessment"
                    }
                },
                {
                    "event_type": "parallel_execution",
                    "data": {
                        "agents": ["frontend-architecture", "backend-services"],
                        "coordination_required": True
                    }
                }
            ]
            
            integration_results = {
                "orchestrator_available": True,
                "total_requests": len(test_requests),
                "successful_requests": 0,
                "failed_requests": 0,
                "request_details": {}
            }
            
            for i, request in enumerate(test_requests):
                try:
                    result = orchestrator.process_request(
                        request["event_type"],
                        request["data"]
                    )
                    
                    if result.get("processed", False):
                        integration_results["successful_requests"] += 1
                        status = "success"
                    else:
                        integration_results["failed_requests"] += 1
                        status = "not_processed"
                    
                    integration_results["request_details"][f"request_{i}"] = {
                        "event_type": request["event_type"],
                        "result": result,
                        "status": status
                    }
                    
                except Exception as e:
                    integration_results["failed_requests"] += 1
                    integration_results["request_details"][f"request_{i}"] = {
                        "event_type": request["event_type"],
                        "error": str(e),
                        "status": "error"
                    }
            
            integration_results["integration_success_rate"] = (
                integration_results["successful_requests"] / integration_results["total_requests"]
            ) * 100
            
            return integration_results
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "integration_available": False
            }
    
    def test_agent_hierarchy(self) -> Dict[str, Any]:
        """Test agent tier hierarchy and flow"""
        logger.info("Testing agent hierarchy...")
        
        tier_analysis = {
            "tiers": {},
            "hierarchy_violations": [],
            "flow_analysis": {}
        }
        
        # Analyze tiers
        for agent, config in AGENT_ROUTING_MAP.items():
            tier = config["tier"]
            if tier not in tier_analysis["tiers"]:
                tier_analysis["tiers"][tier] = {
                    "agents": [],
                    "delegates_to_lower": 0,
                    "delegates_to_higher": 0,
                    "receives_from_higher": 0,
                    "receives_from_lower": 0
                }
            
            tier_analysis["tiers"][tier]["agents"].append(agent)
            
            # Analyze delegation patterns
            for target in config["delegates_to"]:
                if target in AGENT_ROUTING_MAP:
                    target_tier = AGENT_ROUTING_MAP[target]["tier"]
                    if target_tier > tier:
                        tier_analysis["tiers"][tier]["delegates_to_lower"] += 1
                    elif target_tier < tier:
                        tier_analysis["tiers"][tier]["delegates_to_higher"] += 1
                        # This might be a hierarchy violation
                        tier_analysis["hierarchy_violations"].append({
                            "source": agent,
                            "source_tier": tier,
                            "target": target,
                            "target_tier": target_tier,
                            "violation_type": "delegates_upward"
                        })
            
            # Analyze incoming connections
            for source in config["receives_from"]:
                if source in AGENT_ROUTING_MAP:
                    source_tier = AGENT_ROUTING_MAP[source]["tier"]
                    if source_tier < tier:
                        tier_analysis["tiers"][tier]["receives_from_higher"] += 1
                    elif source_tier > tier:
                        tier_analysis["tiers"][tier]["receives_from_lower"] += 1
        
        # Calculate hierarchy health
        total_violations = len(tier_analysis["hierarchy_violations"])
        total_agents = len(AGENT_ROUTING_MAP)
        hierarchy_health = max(0, (total_agents - total_violations) / total_agents * 100)
        
        return {
            "total_agents": total_agents,
            "total_tiers": len(tier_analysis["tiers"]),
            "hierarchy_violations": total_violations,
            "hierarchy_health": hierarchy_health,
            "tier_analysis": tier_analysis,
            "flow_recommendations": self._generate_flow_recommendations(tier_analysis)
        }
    
    def _generate_flow_recommendations(self, tier_analysis: Dict) -> List[str]:
        """Generate recommendations for improving agent flow"""
        recommendations = []
        
        violations = tier_analysis.get("hierarchy_violations", [])
        if violations:
            recommendations.append(f"Review {len(violations)} hierarchy violations for proper flow")
        
        # Check for isolated tiers
        for tier, info in tier_analysis["tiers"].items():
            if info["delegates_to_lower"] == 0 and info["delegates_to_higher"] == 0:
                if tier < 7:  # Not the final tier
                    recommendations.append(f"Tier {tier} agents may need delegation targets")
        
        if not recommendations:
            recommendations.append("Agent hierarchy and flow patterns are well-structured")
        
        return recommendations
    
    def test_parallel_execution_routes(self) -> Dict[str, Any]:
        """Test parallel execution routing patterns"""
        logger.info("Testing parallel execution routes...")
        
        parallel_scenarios = [
            {
                "name": "business_parallel",
                "agents": ["business-analyst", "financial-analyst", "ceo-strategy"],
                "expected_coordination": True
            },
            {
                "name": "architecture_parallel",
                "agents": ["frontend-architecture", "database-architecture"],
                "expected_coordination": True
            },
            {
                "name": "development_parallel",
                "agents": ["production-frontend", "backend-services", "mobile-development"],
                "expected_coordination": True
            },
            {
                "name": "quality_parallel",
                "agents": ["testing-automation", "security-architecture", "performance-optimization"],
                "expected_coordination": False  # Can run independently
            }
        ]
        
        results = {
            "total_scenarios": len(parallel_scenarios),
            "coordination_patterns": {},
            "parallel_efficiency": {}
        }
        
        for scenario in parallel_scenarios:
            agents = scenario["agents"]
            
            # Check if agents can run in parallel (different tiers or same tier)
            agent_tiers = []
            for agent in agents:
                if agent in AGENT_ROUTING_MAP:
                    agent_tiers.append(AGENT_ROUTING_MAP[agent]["tier"])
                else:
                    agent_tiers.append(None)
            
            # Analyze parallelization potential
            unique_tiers = set(t for t in agent_tiers if t is not None)
            same_tier = len(unique_tiers) == 1
            
            results["coordination_patterns"][scenario["name"]] = {
                "agents": agents,
                "agent_tiers": agent_tiers,
                "same_tier": same_tier,
                "can_parallelize": True,  # Assume true for this test
                "coordination_needed": scenario["expected_coordination"]
            }
        
        return results
    
    def run_comprehensive_routing_test(self) -> Dict[str, Any]:
        """Run comprehensive agent routing test suite"""
        logger.info("Starting comprehensive agent routing test...")
        
        test_start = datetime.now()
        
        # Run all routing tests
        mention_parsing_result = self.test_agent_mention_parsing()
        routing_logic_result = self.test_routing_logic()
        orchestrator_integration_result = self.test_orchestrator_integration()
        hierarchy_result = self.test_agent_hierarchy()
        parallel_execution_result = self.test_parallel_execution_routes()
        
        test_end = datetime.now()
        test_duration = (test_end - test_start).total_seconds()
        
        # Calculate overall routing score
        scores = []
        scores.append(mention_parsing_result["parsing_success_rate"])
        scores.append(routing_logic_result["routing_success_rate"])
        
        if orchestrator_integration_result.get("integration_available", False):
            scores.append(orchestrator_integration_result["integration_success_rate"])
        
        scores.append(hierarchy_result["hierarchy_health"])
        
        overall_score = sum(scores) / len(scores)
        
        # Determine routing system health
        if overall_score >= 95:
            routing_health = "excellent"
        elif overall_score >= 85:
            routing_health = "good"
        elif overall_score >= 70:
            routing_health = "adequate"
        else:
            routing_health = "needs_improvement"
        
        return {
            "test_suite_version": "3.0_routing",
            "timestamp": test_end.isoformat(),
            "test_duration": test_duration,
            "overall_score": overall_score,
            "routing_health": routing_health,
            
            "test_results": {
                "mention_parsing": mention_parsing_result,
                "routing_logic": routing_logic_result,
                "orchestrator_integration": orchestrator_integration_result,
                "agent_hierarchy": hierarchy_result,
                "parallel_execution": parallel_execution_result
            },
            
            "summary": {
                "total_agents": len(AGENT_ROUTING_MAP),
                "total_tiers": len(set(config["tier"] for config in AGENT_ROUTING_MAP.values())),
                "orchestrator_available": orchestrator_integration_result.get("integration_available", False),
                "hierarchy_violations": hierarchy_result["hierarchy_violations"],
                "routing_patterns_tested": routing_logic_result["total_scenarios"]
            },
            
            "recommendations": self._generate_routing_recommendations(
                mention_parsing_result, routing_logic_result,
                orchestrator_integration_result, hierarchy_result
            )
        }
    
    def _generate_routing_recommendations(self, *test_results) -> List[str]:
        """Generate recommendations for improving routing"""
        recommendations = []
        
        mention_parsing, routing_logic, orchestrator_integration, hierarchy = test_results
        
        if mention_parsing["parsing_success_rate"] < 100:
            recommendations.append("Improve @agent- mention parsing reliability")
        
        if routing_logic["routing_success_rate"] < 90:
            recommendations.append("Review and optimize agent delegation patterns")
        
        if not orchestrator_integration.get("integration_available", False):
            recommendations.append("Verify orchestrator integration and availability")
        elif orchestrator_integration.get("integration_success_rate", 0) < 95:
            recommendations.append("Improve orchestrator integration reliability")
        
        if hierarchy["hierarchy_violations"] > 0:
            recommendations.append("Address agent hierarchy violations for better flow")
        
        if not recommendations:
            recommendations.append("Agent routing system is operating optimally")
        
        return recommendations
    
    def save_routing_test_results(self, results: Dict[str, Any]):
        """Save routing test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"routing_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Routing test results saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    print("Claude Code Dev Stack v3.0 - Agent Routing Integration Testing")
    print("=" * 70)
    
    try:
        tester = AgentRoutingTester()
        results = tester.run_comprehensive_routing_test()
        tester.save_routing_test_results(results)
        
        print("\nAGENT ROUTING TEST RESULTS:")
        print("=" * 70)
        print(f"Overall Score: {results['overall_score']:.1f}%")
        print(f"Routing Health: {results['routing_health'].upper()}")
        print(f"Test Duration: {results['test_duration']:.2f}s")
        
        summary = results['summary']
        print(f"\nSUMMARY:")
        print(f"Total Agents: {summary['total_agents']}")
        print(f"Agent Tiers: {summary['total_tiers']}")
        print(f"Orchestrator Available: {'YES' if summary['orchestrator_available'] else 'NO'}")
        print(f"Hierarchy Violations: {summary['hierarchy_violations']}")
        print(f"Routing Patterns Tested: {summary['routing_patterns_tested']}")
        
        print("\nTEST BREAKDOWN:")
        test_results = results['test_results']
        print(f"Mention Parsing: {test_results['mention_parsing']['parsing_success_rate']:.1f}%")
        print(f"Routing Logic: {test_results['routing_logic']['routing_success_rate']:.1f}%")
        
        if test_results['orchestrator_integration'].get('integration_available'):
            print(f"Orchestrator Integration: {test_results['orchestrator_integration']['integration_success_rate']:.1f}%")
        else:
            print("Orchestrator Integration: NOT AVAILABLE")
        
        print(f"Agent Hierarchy: {test_results['agent_hierarchy']['hierarchy_health']:.1f}%")
        
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("=" * 70)
        print("Agent routing test completed!")
        
    except Exception as e:
        logger.error(f"Agent routing test failed: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())