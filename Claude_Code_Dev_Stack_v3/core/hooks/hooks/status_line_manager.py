#!/usr/bin/env python3
"""
Status Line Manager - V3.0 Core Intelligence Hub
Real-time context awareness for Claude Code Dev Stack
"""

import json
import os
import sys
import time
import subprocess
import sqlite3
import threading
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

class StatusLineManager:
    """
    Central intelligence hub for Claude Code V3.0
    Tracks model, git, phase, agents, tokens, and performance
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.status_file = self.home_dir / "status.json"
        self.db_path = self.home_dir / "status_history.db"
        self.update_interval = 0.1  # 100ms updates
        
        # Ensure directories exist
        self.home_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Current status
        self.status = {
            "model": self.get_current_model(),
            "git": self.get_git_context(),
            "phase": self.get_current_phase(),
            "agents": self.get_active_agents(),
            "tokens": self.get_token_usage(),
            "performance": self.get_performance_metrics(),
            "chat_health": self.get_chat_health(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Start background updater
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def init_database(self):
        """Initialize SQLite database for status history"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT,
                git_branch TEXT,
                git_status TEXT,
                phase TEXT,
                active_agents TEXT,
                token_count INTEGER,
                token_percentage REAL,
                performance_score REAL,
                chat_depth INTEGER
            )
        """)
        conn.commit()
        conn.close()
    
    def get_current_model(self) -> str:
        """Detect current Claude model"""
        model_file = self.home_dir / "current_model"
        if model_file.exists():
            return model_file.read_text().strip()
        
        # Default based on environment
        if os.environ.get("ANTHROPIC_MODEL"):
            return os.environ["ANTHROPIC_MODEL"]
        return "claude-3-opus-20240229"  # Default
    
    def get_git_context(self) -> Dict[str, str]:
        """Get current git status and branch"""
        try:
            # Get current branch
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=1
            ).stdout.strip()
            
            # Get status
            status_output = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=1
            ).stdout.strip()
            
            status = "clean" if not status_output else f"{len(status_output.splitlines())} changes"
            
            # Check if ahead/behind
            upstream = subprocess.run(
                ["git", "status", "-sb"],
                capture_output=True, text=True, timeout=1
            ).stdout.strip()
            
            ahead_behind = ""
            if "ahead" in upstream:
                ahead_behind = "ahead"
            if "behind" in upstream:
                ahead_behind = "behind" if not ahead_behind else "diverged"
            
            return {
                "branch": branch or "no-repo",
                "status": status,
                "sync": ahead_behind or "synced"
            }
        except:
            return {"branch": "no-repo", "status": "unknown", "sync": "unknown"}
    
    def get_current_phase(self) -> str:
        """Detect current development phase"""
        phase_file = self.home_dir / "current_phase"
        if phase_file.exists():
            return phase_file.read_text().strip()
        
        # Auto-detect based on context
        git = self.get_git_context()
        if git["branch"] == "main":
            return "production"
        elif "feature" in git["branch"]:
            return "implementation"
        elif "test" in git["branch"]:
            return "testing"
        elif "fix" in git["branch"]:
            return "debugging"
        return "exploration"
    
    def get_active_agents(self) -> list:
        """Get list of currently active agents"""
        agents_file = self.home_dir / "active_agents.json"
        if agents_file.exists():
            try:
                return json.loads(agents_file.read_text())
            except:
                pass
        return []
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get current token usage and limits"""
        token_file = self.home_dir / "token_usage.json"
        if token_file.exists():
            try:
                data = json.loads(token_file.read_text())
                return {
                    "current": data.get("current", 0),
                    "limit": data.get("limit", 100000),
                    "percentage": (data.get("current", 0) / data.get("limit", 100000)) * 100
                }
            except:
                pass
        return {"current": 0, "limit": 100000, "percentage": 0}
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get system performance metrics"""
        return {
            "response_time_ms": self.measure_response_time(),
            "cpu_usage": self.get_cpu_usage(),
            "memory_mb": self.get_memory_usage(),
            "api_latency_ms": self.get_api_latency()
        }
    
    def get_chat_health(self) -> Dict[str, Any]:
        """Assess current chat/conversation health"""
        tokens = self.get_token_usage()
        
        # Determine health status
        if tokens["percentage"] < 70:
            health = "good"
        elif tokens["percentage"] < 85:
            health = "warning"
        else:
            health = "critical"
        
        # Get conversation depth
        depth_file = self.home_dir / "conversation_depth"
        depth = 1
        if depth_file.exists():
            try:
                depth = int(depth_file.read_text().strip())
            except:
                pass
        
        return {
            "status": health,
            "token_pressure": tokens["percentage"],
            "conversation_depth": depth,
            "recommendation": self.get_recommendation(health, tokens["percentage"], depth)
        }
    
    def get_recommendation(self, health: str, token_percentage: float, depth: int) -> str:
        """Get context management recommendation"""
        if health == "critical":
            return "Immediate handoff recommended - generate documentation"
        elif health == "warning":
            if depth > 15:
                return "Consider starting new chat with handoff"
            else:
                return "Consider using /compact command"
        elif token_percentage > 60 and depth > 20:
            return "Deep conversation - consider phase transition"
        return "Context healthy"
    
    def measure_response_time(self) -> float:
        """Measure system response time"""
        start = time.time()
        # Simple filesystem operation as proxy
        Path.home().exists()
        return (time.time() - start) * 1000
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["wmic", "cpu", "get", "loadpercentage", "/value"],
                    capture_output=True, text=True, timeout=1
                )
                for line in result.stdout.split("\n"):
                    if "LoadPercentage" in line:
                        return float(line.split("=")[1])
        except:
            pass
        return 0.0
    
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def get_api_latency(self) -> float:
        """Get API latency from last request"""
        latency_file = self.home_dir / "api_latency"
        if latency_file.exists():
            try:
                return float(latency_file.read_text().strip())
            except:
                pass
        return 0.0
    
    def update_status(self):
        """Update all status information"""
        self.status = {
            "model": self.get_current_model(),
            "git": self.get_git_context(),
            "phase": self.get_current_phase(),
            "agents": self.get_active_agents(),
            "tokens": self.get_token_usage(),
            "performance": self.get_performance_metrics(),
            "chat_health": self.get_chat_health(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        self.status_file.write_text(json.dumps(self.status, indent=2))
        
        # Log to database
        self.log_to_database()
    
    def log_to_database(self):
        """Log current status to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO status_history (
                    timestamp, model, git_branch, git_status, phase,
                    active_agents, token_count, token_percentage,
                    performance_score, chat_depth
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.status["timestamp"],
                self.status["model"],
                self.status["git"]["branch"],
                self.status["git"]["status"],
                self.status["phase"],
                json.dumps(self.status["agents"]),
                self.status["tokens"]["current"],
                self.status["tokens"]["percentage"],
                self.status["performance"]["response_time_ms"],
                self.status["chat_health"]["conversation_depth"]
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database logging error: {e}", file=sys.stderr)
    
    def _update_loop(self):
        """Background thread to update status"""
        while self.running:
            try:
                self.update_status()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Status update error: {e}", file=sys.stderr)
                time.sleep(1)
    
    def get_status_line(self) -> str:
        """Get formatted status line for display"""
        git = self.status["git"]
        tokens = self.status["tokens"]
        health = self.status["chat_health"]
        
        # Format: Model | Branch | Phase | Agents | Tokens | Health (no emojis for Windows compatibility)
        return (
            f"[{self.status['model'].split('-')[-1]}] "
            f"git:{git['branch']} "
            f"({git['status']}) "
            f"| {self.status['phase']} "
            f"| {len(self.status['agents'])} agents "
            f"| {tokens['percentage']:.1f}% tokens "
            f"| {health['status']}"
        )
    
    def shutdown(self):
        """Gracefully shutdown the status manager"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=1)

def main():
    """Main entry point for status line display"""
    manager = StatusLineManager()
    
    try:
        # Output status line
        print(manager.get_status_line())
        
        # If verbose mode, output full JSON
        if "--json" in sys.argv:
            print(json.dumps(manager.status, indent=2))
        
        # If monitoring mode, continuous updates
        if "--monitor" in sys.argv:
            while True:
                print(f"\r{manager.get_status_line()}", end="", flush=True)
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        manager.shutdown()

if __name__ == "__main__":
    main()