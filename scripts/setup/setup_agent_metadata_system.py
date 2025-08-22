#!/usr/bin/env python3
"""
Agent Metadata System Setup and Demo Script
Comprehensive setup, initialization, and demonstration of the agent metadata database system
"""

import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import subprocess
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import our database components
try:
    from core.database import (
        create_database_manager,
        create_agent_selector,
        create_performance_monitor,
        create_migration_manager,
        create_backup_manager,
        DatabaseConfig,
        AgentTier,
        ExecutionStatus
    )
except ImportError as e:
    print(f"Failed to import database components: {e}")
    print("Make sure you have installed required dependencies:")
    print("pip install asyncpg psycopg2-binary")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentMetadataSystemSetup:
    """Complete setup and initialization of the agent metadata system"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or str(Path.home() / ".claude" / "database_config.json")
        self.config = self._load_or_create_config()
        
        # System components (will be initialized)
        self.db = None
        self.selector = None
        self.monitor = None
        self.migration_manager = None
        self.backup_manager = None
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load existing config or create default configuration"""
        
        config_path = Path(self.config_file)
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        else:
            # Create default configuration
            config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "claude_agent_metadata",
                    "username": "claude_app",
                    "password": "",
                    "pool_min_size": 5,
                    "pool_max_size": 20
                },
                "monitoring": {
                    "collection_interval_seconds": 30,
                    "metrics_retention_hours": 24,
                    "alert_thresholds": {
                        "response_time_ms": {"warning": 5000, "critical": 10000},
                        "error_rate_percent": {"warning": 10, "critical": 25},
                        "success_rate_percent": {"warning": 85, "critical": 70}
                    }
                },
                "backup": {
                    "auto_backup_enabled": True,
                    "backup_schedule": "daily",
                    "retention_days": 30,
                    "compression_enabled": True
                },
                "agent_selection": {
                    "cache_duration_minutes": 15,
                    "recommendation_weights": {
                        "keyword_match": 0.25,
                        "phase_alignment": 0.20,
                        "recent_success": 0.15,
                        "domain_expertise": 0.15,
                        "availability": 0.10,
                        "collaboration": 0.10,
                        "user_preference": 0.05
                    }
                }
            }
            
            # Save default config
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Created default configuration at {config_path}")
        
        return config
    
    async def check_database_connection(self) -> bool:
        """Check if database is accessible and properly configured"""
        
        try:
            # Create database manager
            db_config = DatabaseConfig(
                host=self.config["database"]["host"],
                port=self.config["database"]["port"],
                database=self.config["database"]["database"],
                username=self.config["database"]["username"],
                password=self.config["database"]["password"]
            )
            
            db = create_database_manager(async_mode=True)
            db.config = db_config
            await db.initialize()
            
            # Test connection
            async with db.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                if result == 1:
                    logger.info("Database connection successful")
                    await db.close()
                    return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
        
        return False
    
    async def setup_database_schema(self) -> bool:
        """Setup database schema using SQL file"""
        
        try:
            # Path to schema file
            schema_file = project_root / "config" / "postgres" / "agent_metadata_schema.sql"
            
            if not schema_file.exists():
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            # Execute schema using psql
            cmd = [
                "psql",
                f"--host={self.config['database']['host']}",
                f"--port={self.config['database']['port']}",
                f"--username={self.config['database']['username']}",
                f"--dbname={self.config['database']['database']}",
                "--no-password",
                "-f", str(schema_file)
            ]
            
            env = os.environ.copy()
            if self.config["database"]["password"]:
                env["PGPASSWORD"] = self.config["database"]["password"]
            
            logger.info("Executing database schema setup...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Database schema setup completed successfully")
                return True
            else:
                logger.error(f"Schema setup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup database schema: {e}")
            return False
    
    async def initialize_system_components(self) -> bool:
        """Initialize all system components"""
        
        try:
            # Initialize database manager
            logger.info("Initializing database manager...")
            self.db = create_database_manager(async_mode=True)
            await self.db.initialize()
            
            # Initialize agent selector
            logger.info("Initializing agent selector...")
            self.selector = await create_agent_selector()
            
            # Initialize performance monitor
            logger.info("Initializing performance monitor...")
            self.monitor = await create_performance_monitor()
            
            # Initialize migration manager
            logger.info("Initializing migration manager...")
            self.migration_manager = await create_migration_manager()
            
            # Initialize backup manager
            logger.info("Initializing backup manager...")
            self.backup_manager = create_backup_manager()
            
            logger.info("All system components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system components: {e}")
            return False
    
    async def populate_sample_data(self) -> bool:
        """Populate database with sample agent data"""
        
        try:
            logger.info("Populating sample agent data...")
            
            # Sample agents based on the existing V3.6.9 system
            sample_agents = [
                {
                    'name': 'database-architect',
                    'display_name': 'Database Architecture Specialist',
                    'description': 'Expert in database design, optimization, and scaling strategies',
                    'tier': '3',
                    'specializations': ['database-design', 'performance-optimization', 'data-modeling', 'sql', 'nosql'],
                    'tools_available': ['postgresql', 'redis', 'mongodb', 'elasticsearch'],
                    'keywords': ['database', 'schema', 'performance', 'optimization', 'postgres', 'sql'],
                    'preferred_model': 'opus'
                },
                {
                    'name': 'backend-services',
                    'display_name': 'Backend Services Developer',
                    'description': 'Develops and maintains backend APIs and services',
                    'tier': '3',
                    'specializations': ['api-development', 'microservices', 'rest', 'graphql'],
                    'tools_available': ['fastapi', 'flask', 'django', 'express'],
                    'keywords': ['backend', 'api', 'services', 'rest', 'graphql'],
                    'preferred_model': 'sonnet'
                },
                {
                    'name': 'frontend-architecture',
                    'display_name': 'Frontend Architecture Specialist',
                    'description': 'Expert in frontend architecture and modern web frameworks',
                    'tier': '3',
                    'specializations': ['frontend-architecture', 'react', 'vue', 'angular', 'typescript'],
                    'tools_available': ['react', 'vue', 'angular', 'webpack', 'vite'],
                    'keywords': ['frontend', 'react', 'vue', 'typescript', 'components'],
                    'preferred_model': 'sonnet'
                },
                {
                    'name': 'testing-automation',
                    'display_name': 'Testing & Automation Specialist',
                    'description': 'Comprehensive testing strategies and automation frameworks',
                    'tier': '3',
                    'specializations': ['testing', 'automation', 'unit-testing', 'integration-testing', 'e2e'],
                    'tools_available': ['pytest', 'jest', 'selenium', 'playwright'],
                    'keywords': ['testing', 'automation', 'unit', 'integration', 'e2e'],
                    'preferred_model': 'sonnet'
                },
                {
                    'name': 'smart-orchestrator',
                    'display_name': 'Smart Agent Orchestrator',
                    'description': 'Coordinates and routes requests between agents intelligently',
                    'tier': '2',
                    'specializations': ['orchestration', 'routing', 'coordination', 'workflow'],
                    'tools_available': ['orchestrator', 'router', 'workflow-engine'],
                    'keywords': ['orchestrator', 'routing', 'coordination', 'workflow'],
                    'preferred_model': 'sonnet'
                },
                {
                    'name': 'performance-optimization',
                    'display_name': 'Performance Optimization Specialist',
                    'description': 'Expert in application and system performance optimization',
                    'tier': '3',
                    'specializations': ['performance', 'optimization', 'profiling', 'caching'],
                    'tools_available': ['profiler', 'cache', 'cdn', 'monitoring'],
                    'keywords': ['performance', 'optimization', 'speed', 'caching', 'profiling'],
                    'preferred_model': 'opus'
                },
                {
                    'name': 'security-architecture',
                    'display_name': 'Security Architecture Specialist',
                    'description': 'Security design, threat modeling, and vulnerability assessment',
                    'tier': '3',
                    'specializations': ['security', 'authentication', 'authorization', 'encryption'],
                    'tools_available': ['auth', 'encryption', 'scanner', 'firewall'],
                    'keywords': ['security', 'auth', 'encryption', 'vulnerability', 'threat'],
                    'preferred_model': 'opus'
                },
                {
                    'name': 'devops-engineer',
                    'display_name': 'DevOps Engineering Specialist',
                    'description': 'Infrastructure, deployment, and CI/CD pipeline expert',
                    'tier': '3',
                    'specializations': ['devops', 'deployment', 'ci-cd', 'infrastructure', 'containers'],
                    'tools_available': ['docker', 'kubernetes', 'terraform', 'jenkins'],
                    'keywords': ['devops', 'deployment', 'docker', 'kubernetes', 'ci-cd'],
                    'preferred_model': 'sonnet'
                }
            ]
            
            # Create agents
            for agent_data in sample_agents:
                try:
                    agent_id = await self.db.create_agent(agent_data)
                    logger.info(f"Created agent: {agent_data['name']} (ID: {agent_id})")
                except Exception as e:
                    logger.warning(f"Agent {agent_data['name']} might already exist: {e}")
            
            # Create some sample execution history
            await self._create_sample_executions()
            
            logger.info("Sample data population completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to populate sample data: {e}")
            return False
    
    async def _create_sample_executions(self):
        """Create sample execution history for demo purposes"""
        
        try:
            # Get all agents
            agents = await self.db.search_agents(limit=20)
            
            if not agents:
                logger.warning("No agents found for creating sample executions")
                return
            
            # Create sample executions for the last 7 days
            import random
            
            for days_ago in range(7):
                base_time = datetime.now() - timedelta(days=days_ago)
                
                # Create 5-15 executions per day
                execution_count = random.randint(5, 15)
                
                for _ in range(execution_count):
                    agent = random.choice(agents)
                    
                    # Random execution time within the day
                    execution_time = base_time.replace(
                        hour=random.randint(0, 23),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    
                    # Sample contexts
                    contexts = [
                        {'type': 'user_request', 'query': 'optimize database performance'},
                        {'type': 'user_request', 'query': 'create REST API endpoint'},
                        {'type': 'user_request', 'query': 'fix frontend component bug'},
                        {'type': 'user_request', 'query': 'setup CI/CD pipeline'},
                        {'type': 'user_request', 'query': 'implement authentication'},
                        {'type': 'delegation', 'from_agent': 'smart-orchestrator'},
                        {'type': 'auto_trigger', 'trigger': 'performance_alert'}
                    ]
                    
                    context = random.choice(contexts)
                    
                    # Start execution
                    execution_id = await self.db.start_execution(
                        agent.id,
                        context['type'],
                        context
                    )
                    
                    # Complete execution with random results
                    success_rate = 0.85  # 85% success rate
                    status = ExecutionStatus.COMPLETED if random.random() < success_rate else ExecutionStatus.FAILED
                    
                    duration_ms = random.randint(1000, 30000)  # 1-30 seconds
                    tokens_used = random.randint(50, 500)
                    
                    await self.db.complete_execution(
                        execution_id,
                        status,
                        output_summary={'result': 'Sample execution result'},
                        tokens_used=tokens_used
                    )
            
            logger.info("Sample execution history created")
            
        except Exception as e:
            logger.error(f"Failed to create sample executions: {e}")
    
    async def run_system_tests(self) -> bool:
        """Run comprehensive system tests"""
        
        try:
            logger.info("Running system tests...")
            
            # Test 1: Agent selection
            logger.info("Testing agent selection...")
            best_agent = await self.selector.select_best_agent(
                "I need help optimizing a PostgreSQL database for better query performance"
            )
            
            if best_agent:
                logger.info(f"✓ Agent selection works - selected: {best_agent.agent_name} (score: {best_agent.total_score:.2f})")
            else:
                logger.warning("✗ Agent selection returned no results")
                return False
            
            # Test 2: Performance monitoring
            logger.info("Testing performance monitoring...")
            await self.monitor.start_monitoring()
            
            # Wait for some metrics to be collected
            await asyncio.sleep(2)
            
            health_report = await self.monitor.get_system_health_report()
            logger.info(f"✓ Performance monitoring works - health score: {health_report.overall_health_score}")
            
            await self.monitor.stop_monitoring()
            
            # Test 3: Database queries
            logger.info("Testing database queries...")
            system_health = await self.db.get_system_health()
            logger.info(f"✓ Database queries work - found {len(system_health)} health metrics")
            
            # Test 4: Migration system
            logger.info("Testing migration system...")
            pending_migrations = await self.migration_manager.get_pending_migrations()
            logger.info(f"✓ Migration system works - {len(pending_migrations)} pending migrations")
            
            # Test 5: Backup system
            logger.info("Testing backup system...")
            backups = self.backup_manager.list_backups()
            logger.info(f"✓ Backup system works - {len(backups)} existing backups")
            
            logger.info("All system tests passed!")
            return True
            
        except Exception as e:
            logger.error(f"System tests failed: {e}")
            return False
    
    async def run_demonstration(self):
        """Run a comprehensive demonstration of system capabilities"""
        
        logger.info("=" * 60)
        logger.info("AGENT METADATA SYSTEM DEMONSTRATION")
        logger.info("=" * 60)
        
        # Demo 1: Agent Selection
        print("\n1. INTELLIGENT AGENT SELECTION")
        print("-" * 40)
        
        test_queries = [
            "Create a REST API for user authentication with PostgreSQL backend",
            "Optimize React component performance and fix memory leaks",
            "Setup automated testing pipeline with Jest and Playwright",
            "Design database schema for e-commerce application"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            recommendations = await self.selector.get_top_recommendations(query, count=3)
            
            if recommendations:
                print("Top recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec.agent_name} (Score: {rec.total_score:.2f})")
                    print(f"     Reasoning: {', '.join(rec.reasoning[:2])}")
            else:
                print("  No recommendations found")
        
        # Demo 2: System Health
        print("\n\n2. SYSTEM HEALTH AND PERFORMANCE")
        print("-" * 40)
        
        health_report = await self.monitor.get_system_health_report()
        print(f"Overall Health Score: {health_report.overall_health_score:.1f}/100")
        print(f"Active Agents: {health_report.active_agents}/{health_report.total_agents}")
        print(f"24h Executions: {health_report.total_executions_24h}")
        print(f"Average Success Rate: {health_report.avg_success_rate:.1f}%")
        
        # Show top performing agents
        print("\nTop Performing Agents:")
        for agent in health_report.agent_health[:5]:
            print(f"  • {agent.agent_name}: {agent.health_score:.1f} health score")
            print(f"    Success Rate: {agent.success_rate_24h:.1f}% | Executions: {agent.total_executions_24h}")
        
        # Demo 3: Performance Analytics
        print("\n\n3. PERFORMANCE ANALYTICS")
        print("-" * 40)
        
        # Get performance trends
        trends = await self.monitor.get_performance_trends(hours=24)
        print("Performance Trends (24h):")
        for trend in trends:
            direction_icon = "↑" if trend.trend_direction == "up" else "↓" if trend.trend_direction == "down" else "→"
            print(f"  {direction_icon} {trend.metric_name}: {trend.trend_direction} ({trend.trend_percentage:+.1f}%)")
        
        # Demo 4: Database Statistics
        print("\n\n4. DATABASE STATISTICS")
        print("-" * 40)
        
        system_health = await self.db.get_system_health()
        print("System Metrics:")
        for metric_name, metric_data in system_health.items():
            status_icon = "✓" if metric_data['status'] == 'OK' else "⚠"
            print(f"  {status_icon} {metric_name}: {metric_data['value']}")
        
        # Demo 5: Collaboration Network
        print("\n\n5. AGENT COLLABORATION")
        print("-" * 40)
        
        dashboard = DashboardQueries(self.db)
        collaborations = await dashboard.get_collaboration_network()
        
        if collaborations:
            print("Agent Collaboration Network:")
            for collab in collaborations[:5]:
                success_rate = (collab['successful_handoffs'] / collab['total_handoffs']) * 100
                print(f"  {collab['from_agent']} → {collab['to_agent']}")
                print(f"    Handoffs: {collab['total_handoffs']} | Success: {success_rate:.1f}%")
        else:
            print("No collaboration data available yet")
        
        print("\n" + "=" * 60)
        logger.info("Demonstration completed successfully!")
    
    async def cleanup_resources(self):
        """Clean up all system resources"""
        
        try:
            if self.monitor:
                await self.monitor.stop_monitoring()
                await self.monitor.db.close()
            
            if self.db:
                await self.db.close()
            
            if self.migration_manager:
                await self.migration_manager.db.close()
            
            logger.info("All resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# ========== MAIN SETUP FUNCTION ==========

async def main():
    """Main setup and demonstration function"""
    
    print("🚀 Agent Metadata System Setup")
    print("=" * 50)
    
    setup = AgentMetadataSystemSetup()
    
    try:
        # Step 1: Check database connection
        print("\n1. Checking database connection...")
        if not await setup.check_database_connection():
            print("❌ Database connection failed!")
            print("\nPlease ensure:")
            print("- PostgreSQL is running")
            print("- Database exists and is accessible")
            print("- Connection parameters are correct")
            return False
        print("✅ Database connection successful")
        
        # Step 2: Setup database schema
        print("\n2. Setting up database schema...")
        if not await setup.setup_database_schema():
            print("❌ Schema setup failed!")
            return False
        print("✅ Database schema setup complete")
        
        # Step 3: Initialize system components
        print("\n3. Initializing system components...")
        if not await setup.initialize_system_components():
            print("❌ Component initialization failed!")
            return False
        print("✅ All components initialized")
        
        # Step 4: Populate sample data
        print("\n4. Populating sample data...")
        if not await setup.populate_sample_data():
            print("❌ Sample data population failed!")
            return False
        print("✅ Sample data populated")
        
        # Step 5: Run system tests
        print("\n5. Running system tests...")
        if not await setup.run_system_tests():
            print("❌ System tests failed!")
            return False
        print("✅ All system tests passed")
        
        # Step 6: Run demonstration
        print("\n6. Running system demonstration...")
        await setup.run_demonstration()
        
        print("\n🎉 Agent Metadata System setup completed successfully!")
        print("\nThe system is now ready for use. You can:")
        print("- Query agents using the selection engine")
        print("- Monitor performance in real-time") 
        print("- Track execution history and analytics")
        print("- Manage migrations and backups")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        print(f"\n❌ Setup failed: {e}")
        return False
    finally:
        await setup.cleanup_resources()


if __name__ == "__main__":
    # Run the setup
    success = asyncio.run(main())
    sys.exit(0 if success else 1)