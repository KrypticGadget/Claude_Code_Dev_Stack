#!/usr/bin/env python3
"""
Parallel Execution Engine - V3.0 Concurrent Agent Execution
Manages parallel execution of multiple agents with coordination
"""

import json
import os
import sys
import time
import threading
import queue
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class ParallelExecutionEngine:
    """
    Manages parallel execution of agents with smart coordination
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.execution_log = self.home_dir / "parallel_execution.log"
        self.max_workers = self.get_optimal_workers()
        
        # Execution tracking
        self.active_executions = {}
        self.execution_results = {}
        self.execution_queue = queue.Queue()
        
        # Coordination locks
        self.resource_locks = {
            "database": threading.Lock(),
            "filesystem": threading.Lock(),
            "network": threading.Lock(),
            "git": threading.Lock()
        }
        
        # Agent dependencies
        self.dependencies = {
            "master-orchestrator": [],
            "prompt-engineer": [],
            "business-analyst": ["prompt-engineer"],
            "technical-cto": ["business-analyst"],
            "frontend-architecture": ["technical-specifications"],
            "backend-services": ["technical-specifications", "database-architecture"],
            "production-frontend": ["frontend-architecture", "frontend-mockup"],
            "testing-automation": ["backend-services", "production-frontend"],
            "deployment": ["testing-automation", "security-architecture"]
        }
    
    def get_optimal_workers(self) -> int:
        """Determine optimal number of parallel workers"""
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            # Use 75% of CPU cores, minimum 2, maximum 8
            return max(2, min(8, int(cpu_count * 0.75)))
        except:
            return 4  # Default
    
    def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent"""
        start_time = time.time()
        
        try:
            # Record execution start
            self.active_executions[agent_name] = {
                "started": datetime.now().isoformat(),
                "status": "running",
                "context": context
            }
            
            # Simulate agent execution (replace with actual agent call)
            result = self.run_agent_task(agent_name, context)
            
            # Record success
            execution_time = (time.time() - start_time) * 1000
            self.execution_results[agent_name] = {
                "status": "success",
                "result": result,
                "execution_time_ms": execution_time,
                "completed": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "agent": agent_name,
                "result": result,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            # Record failure
            self.execution_results[agent_name] = {
                "status": "failed",
                "error": str(e),
                "completed": datetime.now().isoformat()
            }
            
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }
        
        finally:
            # Clean up active execution
            if agent_name in self.active_executions:
                del self.active_executions[agent_name]
    
    def run_agent_task(self, agent_name: str, context: Dict[str, Any]) -> Any:
        """Run the actual agent task"""
        # This would normally call the actual agent
        # For now, simulate with a command
        agent_script = self.home_dir / "agents" / f"{agent_name}.py"
        
        if agent_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(agent_script), json.dumps(context)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout) if result.stdout else {}
                else:
                    raise Exception(f"Agent failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                raise Exception("Agent execution timeout")
            except Exception as e:
                raise Exception(f"Agent execution error: {e}")
        else:
            # Simulate agent execution
            time.sleep(0.5)  # Simulate work
            return {
                "agent": agent_name,
                "status": "simulated",
                "context_received": context
            }
    
    def execute_parallel_group(self, agents: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a group of agents in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all agents for parallel execution
            futures = {
                executor.submit(self.execute_agent, agent, context): agent
                for agent in agents
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Log successful execution
                    self.log_execution(agent, "success", result.get("execution_time_ms", 0))
                    
                except Exception as e:
                    results.append({
                        "success": False,
                        "agent": agent,
                        "error": str(e)
                    })
                    
                    # Log failed execution
                    self.log_execution(agent, "failed", 0, str(e))
        
        return results
    
    def execute_with_dependencies(self, agents: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents respecting dependencies"""
        execution_plan = self.create_execution_plan(agents)
        all_results = {}
        
        for phase in execution_plan:
            print(f"Executing phase {phase['phase']}: {phase['agents']}")
            
            # Execute agents in this phase in parallel
            phase_results = self.execute_parallel_group(phase['agents'], context)
            
            # Store results
            for result in phase_results:
                all_results[result['agent']] = result
            
            # Update context with phase results for next phase
            context['previous_phase_results'] = phase_results
        
        return {
            "execution_plan": execution_plan,
            "results": all_results,
            "summary": self.create_execution_summary(all_results)
        }
    
    def create_execution_plan(self, agents: List[str]) -> List[Dict[str, Any]]:
        """Create execution plan with dependency resolution"""
        # Build dependency graph
        graph = {}
        for agent in agents:
            deps = self.dependencies.get(agent, [])
            graph[agent] = [d for d in deps if d in agents]
        
        # Topological sort to determine execution order
        visited = set()
        stack = []
        
        def visit(agent):
            if agent in visited:
                return
            visited.add(agent)
            for dep in graph.get(agent, []):
                visit(dep)
            stack.append(agent)
        
        for agent in agents:
            visit(agent)
        
        # Group agents that can run in parallel
        phases = []
        while stack:
            # Find all agents with no remaining dependencies
            ready = []
            for agent in stack[:]:
                deps = graph.get(agent, [])
                if all(d not in stack for d in deps):
                    ready.append(agent)
                    stack.remove(agent)
            
            if ready:
                phases.append({
                    "phase": len(phases) + 1,
                    "agents": ready,
                    "parallel": True
                })
        
        return phases
    
    def acquire_resource_lock(self, resource: str) -> bool:
        """Acquire a resource lock for exclusive access"""
        if resource in self.resource_locks:
            return self.resource_locks[resource].acquire(timeout=5)
        return True
    
    def release_resource_lock(self, resource: str):
        """Release a resource lock"""
        if resource in self.resource_locks:
            self.resource_locks[resource].release()
    
    def execute_with_resource_management(self, agent: str, context: Dict[str, Any], resources: List[str]) -> Dict[str, Any]:
        """Execute agent with resource lock management"""
        acquired_locks = []
        
        try:
            # Acquire all needed resource locks
            for resource in resources:
                if self.acquire_resource_lock(resource):
                    acquired_locks.append(resource)
                else:
                    raise Exception(f"Could not acquire {resource} lock")
            
            # Execute agent with exclusive resource access
            result = self.execute_agent(agent, context)
            
            return result
            
        finally:
            # Release all acquired locks
            for resource in acquired_locks:
                self.release_resource_lock(resource)
    
    def create_execution_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of execution results"""
        successful = sum(1 for r in results.values() if r.get("success", False))
        failed = len(results) - successful
        
        total_time = sum(
            r.get("execution_time_ms", 0) 
            for r in results.values() 
            if r.get("success", False)
        )
        
        return {
            "total_agents": len(results),
            "successful": successful,
            "failed": failed,
            "total_execution_time_ms": total_time,
            "average_time_ms": total_time / successful if successful > 0 else 0,
            "parallel_efficiency": self.calculate_efficiency(results)
        }
    
    def calculate_efficiency(self, results: Dict[str, Any]) -> float:
        """Calculate parallel execution efficiency"""
        if not results:
            return 0.0
        
        # Calculate what sequential time would have been
        sequential_time = sum(
            r.get("execution_time_ms", 0) 
            for r in results.values()
        )
        
        # Actual parallel time (simplified - would need phases)
        parallel_time = max(
            r.get("execution_time_ms", 0) 
            for r in results.values()
        ) if results else 0
        
        if parallel_time == 0:
            return 0.0
        
        return (sequential_time / parallel_time) / len(results) * 100
    
    def log_execution(self, agent: str, status: str, time_ms: float, error: str = None):
        """Log execution details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "status": status,
            "execution_time_ms": time_ms
        }
        
        if error:
            log_entry["error"] = error
        
        # Append to log file
        try:
            with open(self.execution_log, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return {
            "active_executions": list(self.active_executions.keys()),
            "completed_executions": len(self.execution_results),
            "max_workers": self.max_workers,
            "resource_locks": {
                name: lock.locked() 
                for name, lock in self.resource_locks.items()
            }
        }

def main():
    """Main execution demonstration"""
    engine = ParallelExecutionEngine()
    
    # Example: Execute multiple agents
    agents = [
        "prompt-engineer",
        "business-analyst", 
        "technical-cto",
        "frontend-architecture",
        "backend-services",
        "testing-automation"
    ]
    
    context = {
        "request": "Build a web application",
        "phase": "design"
    }
    
    print("Starting parallel execution...")
    print(f"Max workers: {engine.max_workers}")
    
    # Execute with dependencies
    results = engine.execute_with_dependencies(agents, context)
    
    # Display results
    print("\nExecution Summary:")
    print(json.dumps(results["summary"], indent=2))
    
    print("\nExecution Plan:")
    for phase in results["execution_plan"]:
        print(f"  Phase {phase['phase']}: {', '.join(phase['agents'])}")

if __name__ == "__main__":
    main()