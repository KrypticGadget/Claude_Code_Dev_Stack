#!/usr/bin/env python3
"""
Agent Metadata Database Interface
High-performance database layer for agent management and analytics
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from contextlib import asynccontextmanager, contextmanager
import time


# ========== ENUMS AND DATA CLASSES ==========

class AgentTier(Enum):
    TIER_1 = "1"
    TIER_2 = "2"  
    TIER_3 = "3"
    TIER_4 = "4"
    TIER_5 = "5"

class AgentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    DEVELOPING = "developing"

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class CommunicationType(Enum):
    DELEGATION = "delegation"
    COORDINATION = "coordination"
    HANDOFF = "handoff"
    ESCALATION = "escalation"
    CONSULTATION = "consultation"

@dataclass
class Agent:
    """Agent metadata model"""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    tier: AgentTier
    status: AgentStatus
    specializations: List[str]
    tools_available: List[str]
    supported_file_types: List[str]
    keywords: List[str]
    preferred_model: str
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime]
    version: str
    total_executions: int
    success_count: int
    avg_execution_time_ms: int

@dataclass
class ExecutionRecord:
    """Execution history record"""
    id: str
    agent_id: str
    session_id: Optional[str]
    execution_type: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    status: ExecutionStatus
    input_context: Dict[str, Any]
    output_summary: Dict[str, Any]
    error_details: Optional[str]
    tokens_used: Optional[int]
    memory_peak_mb: Optional[int]
    cpu_time_ms: Optional[int]
    user_satisfaction_rating: Optional[int]
    retry_count: int

@dataclass
class AgentRecommendation:
    """Agent recommendation with scoring"""
    agent_id: str
    keyword_match_score: float
    phase_alignment_score: float
    recent_success_score: float
    domain_expertise_score: float
    availability_score: float
    total_score: float
    context_hash: str
    context_data: Dict[str, Any]
    expires_at: datetime


# ========== DATABASE CONFIGURATION ==========

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "claude_agent_metadata"
    username: str = "claude_app"
    password: str = ""
    pool_min_size: int = 5
    pool_max_size: int = 20
    command_timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load configuration from environment variables"""
        import os
        return cls(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'claude_agent_metadata'),
            username=os.getenv('POSTGRES_USER', 'claude_app'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            pool_min_size=int(os.getenv('DB_POOL_MIN_SIZE', 5)),
            pool_max_size=int(os.getenv('DB_POOL_MAX_SIZE', 20)),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', 30))
        )


# ========== ASYNC DATABASE MANAGER ==========

class AsyncAgentMetadataDB:
    """
    High-performance async database interface for agent metadata
    Optimized for real-time agent selection and performance tracking
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=self.config.pool_min_size,
                max_size=self.config.pool_max_size,
                command_timeout=self.config.command_timeout
            )
            self.logger.info(f"Database pool initialized with {self.config.pool_min_size}-{self.config.pool_max_size} connections")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.pool.acquire() as conn:
            yield conn
    
    # ========== AGENT MANAGEMENT ==========
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """Create a new agent record"""
        query = """
        INSERT INTO agents (
            name, display_name, description, tier, status, specializations,
            tools_available, supported_file_types, keywords, preferred_model,
            configuration, version
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
        ) RETURNING id
        """
        
        async with self.get_connection() as conn:
            agent_id = await conn.fetchval(
                query,
                agent_data['name'],
                agent_data['display_name'],
                agent_data.get('description'),
                agent_data['tier'],
                agent_data.get('status', 'active'),
                agent_data.get('specializations', []),
                agent_data.get('tools_available', []),
                agent_data.get('supported_file_types', []),
                agent_data.get('keywords', []),
                agent_data.get('preferred_model', 'sonnet'),
                Json(agent_data.get('configuration', {})),
                agent_data.get('version', '1.0.0')
            )
            
        self.logger.info(f"Created agent {agent_data['name']} with ID {agent_id}")
        return str(agent_id)
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        query = """
        SELECT * FROM agents WHERE id = $1 AND status != 'deprecated'
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, uuid.UUID(agent_id))
            
        if row:
            return Agent(
                id=str(row['id']),
                name=row['name'],
                display_name=row['display_name'],
                description=row['description'],
                tier=AgentTier(row['tier']),
                status=AgentStatus(row['status']),
                specializations=row['specializations'],
                tools_available=row['tools_available'],
                supported_file_types=row['supported_file_types'],
                keywords=row['keywords'],
                preferred_model=row['preferred_model'],
                configuration=row['configuration'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                last_active_at=row['last_active_at'],
                version=row['version'],
                total_executions=row['total_executions'],
                success_count=row['success_count'],
                avg_execution_time_ms=row['avg_execution_time_ms']
            )
        return None
    
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        query = """
        SELECT * FROM agents WHERE name = $1 AND status != 'deprecated'
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, name)
            
        if row:
            return Agent(
                id=str(row['id']),
                name=row['name'],
                display_name=row['display_name'],
                description=row['description'],
                tier=AgentTier(row['tier']),
                status=AgentStatus(row['status']),
                specializations=row['specializations'],
                tools_available=row['tools_available'],
                supported_file_types=row['supported_file_types'],
                keywords=row['keywords'],
                preferred_model=row['preferred_model'],
                configuration=row['configuration'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                last_active_at=row['last_active_at'],
                version=row['version'],
                total_executions=row['total_executions'],
                success_count=row['success_count'],
                avg_execution_time_ms=row['avg_execution_time_ms']
            )
        return None
    
    async def search_agents(self, 
                           query_text: str = None,
                           specializations: List[str] = None,
                           tier: AgentTier = None,
                           limit: int = 10) -> List[Agent]:
        """Search agents with full-text search and filtering"""
        
        conditions = ["status = 'active'"]
        params = []
        param_idx = 1
        
        if query_text:
            conditions.append(f"search_vector @@ plainto_tsquery('english', ${param_idx})")
            params.append(query_text)
            param_idx += 1
            
        if specializations:
            conditions.append(f"specializations && ${param_idx}")
            params.append(specializations)
            param_idx += 1
            
        if tier:
            conditions.append(f"tier = ${param_idx}")
            params.append(tier.value)
            param_idx += 1
        
        query = f"""
        SELECT * FROM agents 
        WHERE {' AND '.join(conditions)}
        ORDER BY 
            CASE WHEN $1 IS NOT NULL THEN ts_rank(search_vector, plainto_tsquery('english', $1)) ELSE 0 END DESC,
            total_executions DESC,
            success_count DESC
        LIMIT ${param_idx}
        """
        params.append(limit)
        
        async with self.get_connection() as conn:
            if query_text:
                # Insert query_text as first parameter for ranking
                params.insert(0, query_text)
            else:
                params.insert(0, None)
            rows = await conn.fetch(query, *params)
        
        return [
            Agent(
                id=str(row['id']),
                name=row['name'],
                display_name=row['display_name'],
                description=row['description'],
                tier=AgentTier(row['tier']),
                status=AgentStatus(row['status']),
                specializations=row['specializations'],
                tools_available=row['tools_available'],
                supported_file_types=row['supported_file_types'],
                keywords=row['keywords'],
                preferred_model=row['preferred_model'],
                configuration=row['configuration'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                last_active_at=row['last_active_at'],
                version=row['version'],
                total_executions=row['total_executions'],
                success_count=row['success_count'],
                avg_execution_time_ms=row['avg_execution_time_ms']
            )
            for row in rows
        ]
    
    # ========== AGENT RECOMMENDATION ENGINE ==========
    
    async def generate_agent_recommendations(self, 
                                           context: Dict[str, Any],
                                           limit: int = 5) -> List[AgentRecommendation]:
        """Generate agent recommendations based on context"""
        
        # Create context fingerprint
        context_str = json.dumps(context, sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()
        
        # Check for existing recommendations
        query_existing = """
        SELECT * FROM v_agent_recommendations 
        WHERE context_hash = $1 
        ORDER BY total_score DESC 
        LIMIT $2
        """
        
        async with self.get_connection() as conn:
            existing = await conn.fetch(query_existing, context_hash, limit)
            
        if existing:
            return [
                AgentRecommendation(
                    agent_id=str(row['agent_id']),
                    keyword_match_score=row['keyword_match_score'],
                    phase_alignment_score=row['phase_alignment_score'],
                    recent_success_score=row['recent_success_score'],
                    domain_expertise_score=row['domain_expertise_score'],
                    availability_score=row['availability_score'],
                    total_score=row['total_score'],
                    context_hash=row['context_hash'],
                    context_data=context,
                    expires_at=row['expires_at']
                )
                for row in existing
            ]
        
        # Generate new recommendations
        return await self._calculate_agent_recommendations(context, context_hash, limit)
    
    async def _calculate_agent_recommendations(self, 
                                             context: Dict[str, Any],
                                             context_hash: str,
                                             limit: int) -> List[AgentRecommendation]:
        """Calculate agent recommendations using scoring algorithm"""
        
        # Extract context features
        keywords = context.get('keywords', [])
        phase = context.get('phase', '')
        file_types = context.get('file_types', [])
        
        # Score agents based on context
        query = """
        WITH agent_scores AS (
            SELECT 
                a.id,
                a.name,
                a.specializations,
                a.keywords,
                a.total_executions,
                a.success_count,
                a.last_active_at,
                
                -- Keyword matching score
                CASE 
                    WHEN cardinality($1::text[]) = 0 THEN 0.5
                    ELSE (
                        cardinality(a.keywords & $1::text[])::float / 
                        GREATEST(cardinality($1::text[]), 1)
                    )
                END as keyword_score,
                
                -- Phase alignment score (simplified)
                CASE 
                    WHEN $2 = '' THEN 0.5
                    WHEN a.specializations && ARRAY[$2] THEN 1.0
                    ELSE 0.3
                END as phase_score,
                
                -- Recent success score
                CASE 
                    WHEN a.total_executions = 0 THEN 0.5
                    ELSE LEAST(1.0, (a.success_count::float / a.total_executions))
                END as success_score,
                
                -- Domain expertise score
                CASE 
                    WHEN a.total_executions >= 50 THEN 1.0
                    WHEN a.total_executions >= 10 THEN 0.8
                    WHEN a.total_executions > 0 THEN 0.6
                    ELSE 0.4
                END as expertise_score,
                
                -- Availability score
                CASE 
                    WHEN a.last_active_at IS NULL THEN 1.0
                    WHEN a.last_active_at > NOW() - INTERVAL '1 hour' THEN 0.7
                    WHEN a.last_active_at > NOW() - INTERVAL '24 hours' THEN 0.9
                    ELSE 1.0
                END as availability_score
                
            FROM agents a
            WHERE a.status = 'active'
        )
        SELECT 
            id,
            keyword_score * 0.35 + 
            phase_score * 0.25 + 
            success_score * 0.20 + 
            expertise_score * 0.15 + 
            availability_score * 0.05 as total_score,
            keyword_score,
            phase_score, 
            success_score,
            expertise_score,
            availability_score
        FROM agent_scores
        ORDER BY total_score DESC
        LIMIT $3
        """
        
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, keywords, phase, limit)
            
            # Store recommendations
            if rows:
                insert_query = """
                INSERT INTO agent_recommendations (
                    agent_id, keyword_match_score, phase_alignment_score,
                    recent_success_score, domain_expertise_score, availability_score,
                    context_hash, context_data
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (agent_id, context_hash) DO UPDATE SET
                    keyword_match_score = EXCLUDED.keyword_match_score,
                    phase_alignment_score = EXCLUDED.phase_alignment_score,
                    recent_success_score = EXCLUDED.recent_success_score,
                    domain_expertise_score = EXCLUDED.domain_expertise_score,
                    availability_score = EXCLUDED.availability_score,
                    context_data = EXCLUDED.context_data,
                    created_at = NOW(),
                    expires_at = NOW() + INTERVAL '1 hour'
                """
                
                for row in rows:
                    await conn.execute(
                        insert_query,
                        uuid.UUID(str(row['id'])),
                        row['keyword_score'],
                        row['phase_score'],
                        row['success_score'],
                        row['expertise_score'],
                        row['availability_score'],
                        context_hash,
                        Json(context)
                    )
        
        return [
            AgentRecommendation(
                agent_id=str(row['id']),
                keyword_match_score=row['keyword_score'],
                phase_alignment_score=row['phase_score'],
                recent_success_score=row['success_score'],
                domain_expertise_score=row['expertise_score'],
                availability_score=row['availability_score'],
                total_score=row['total_score'],
                context_hash=context_hash,
                context_data=context,
                expires_at=datetime.now() + timedelta(hours=1)
            )
            for row in rows
        ]
    
    # ========== EXECUTION TRACKING ==========
    
    async def start_execution(self, 
                             agent_id: str,
                             execution_type: str,
                             input_context: Dict[str, Any],
                             session_id: str = None) -> str:
        """Start tracking an agent execution"""
        
        query = """
        INSERT INTO execution_history (
            agent_id, session_id, execution_type, input_context, status
        ) VALUES ($1, $2, $3, $4, 'running')
        RETURNING id
        """
        
        async with self.get_connection() as conn:
            execution_id = await conn.fetchval(
                query,
                uuid.UUID(agent_id),
                uuid.UUID(session_id) if session_id else None,
                execution_type,
                Json(input_context)
            )
        
        return str(execution_id)
    
    async def complete_execution(self,
                               execution_id: str,
                               status: ExecutionStatus,
                               output_summary: Dict[str, Any] = None,
                               error_details: str = None,
                               tokens_used: int = None,
                               user_satisfaction: int = None) -> None:
        """Complete an agent execution with results"""
        
        query = """
        UPDATE execution_history 
        SET 
            completed_at = NOW(),
            duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000,
            status = $2,
            output_summary = $3,
            error_details = $4,
            tokens_used = $5,
            user_satisfaction_rating = $6
        WHERE id = $1
        """
        
        async with self.get_connection() as conn:
            await conn.execute(
                query,
                uuid.UUID(execution_id),
                status.value,
                Json(output_summary or {}),
                error_details,
                tokens_used,
                user_satisfaction
            )
    
    # ========== PERFORMANCE ANALYTICS ==========
    
    async def get_agent_performance(self, 
                                  agent_id: str,
                                  days: int = 30) -> Dict[str, Any]:
        """Get detailed performance metrics for an agent"""
        
        query = """
        SELECT 
            COUNT(*) as total_executions,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_executions,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_executions,
            AVG(CASE WHEN duration_ms IS NOT NULL THEN duration_ms END) as avg_duration_ms,
            MIN(duration_ms) as min_duration_ms,
            MAX(duration_ms) as max_duration_ms,
            AVG(CASE WHEN tokens_used IS NOT NULL THEN tokens_used END) as avg_tokens_used,
            AVG(CASE WHEN user_satisfaction_rating IS NOT NULL THEN user_satisfaction_rating END) as avg_satisfaction,
            COUNT(DISTINCT session_id) as unique_sessions
        FROM execution_history 
        WHERE agent_id = $1 
        AND started_at >= NOW() - INTERVAL '%s days'
        """ % days
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, uuid.UUID(agent_id))
        
        return {
            'total_executions': row['total_executions'],
            'successful_executions': row['successful_executions'],
            'failed_executions': row['failed_executions'],
            'success_rate': (row['successful_executions'] / max(row['total_executions'], 1)) * 100,
            'avg_duration_ms': float(row['avg_duration_ms']) if row['avg_duration_ms'] else 0,
            'min_duration_ms': row['min_duration_ms'],
            'max_duration_ms': row['max_duration_ms'],
            'avg_tokens_used': float(row['avg_tokens_used']) if row['avg_tokens_used'] else 0,
            'avg_satisfaction': float(row['avg_satisfaction']) if row['avg_satisfaction'] else 0,
            'unique_sessions': row['unique_sessions']
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        
        async with self.get_connection() as conn:
            health_data = await conn.fetch("SELECT * FROM agent_metadata_health_check()")
        
        health_metrics = {}
        for row in health_data:
            health_metrics[row['metric_name']] = {
                'value': float(row['metric_value']),
                'status': row['status']
            }
        
        return health_metrics
    
    # ========== BULK OPERATIONS ==========
    
    async def bulk_update_agent_performance(self):
        """Bulk update agent performance statistics"""
        
        query = """
        UPDATE agents 
        SET 
            total_executions = stats.total_exec,
            success_count = stats.success_exec,
            avg_execution_time_ms = stats.avg_duration,
            last_active_at = stats.last_active,
            updated_at = NOW()
        FROM (
            SELECT 
                agent_id,
                COUNT(*) as total_exec,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as success_exec,
                AVG(duration_ms)::int as avg_duration,
                MAX(completed_at) as last_active
            FROM execution_history 
            WHERE started_at >= NOW() - INTERVAL '30 days'
            GROUP BY agent_id
        ) stats
        WHERE agents.id = stats.agent_id
        """
        
        async with self.get_connection() as conn:
            result = await conn.execute(query)
            
        return result


# ========== SYNCHRONOUS DATABASE MANAGER ==========

class AgentMetadataDB:
    """
    Synchronous database interface for simple operations
    Use AsyncAgentMetadataDB for high-performance scenarios
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Get synchronous database connection"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                cursor_factory=RealDictCursor
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def get_agent_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get agent by name (synchronous)"""
        query = """
        SELECT * FROM agents WHERE name = %s AND status != 'deprecated'
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name,))
                row = cursor.fetchone()
                
        return dict(row) if row else None
    
    def record_execution_start(self, agent_name: str, context: Dict[str, Any]) -> str:
        """Record execution start (synchronous)"""
        # Get agent ID first
        agent = self.get_agent_by_name(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")
        
        query = """
        INSERT INTO execution_history (
            agent_id, execution_type, input_context, status
        ) VALUES (%s, %s, %s, 'running')
        RETURNING id
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    agent['id'],
                    context.get('type', 'user_request'),
                    Json(context)
                ))
                execution_id = cursor.fetchone()['id']
                conn.commit()
                
        return str(execution_id)
    
    def record_execution_complete(self, execution_id: str, success: bool, **kwargs):
        """Record execution completion (synchronous)"""
        status = 'completed' if success else 'failed'
        
        query = """
        UPDATE execution_history 
        SET 
            completed_at = NOW(),
            duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000,
            status = %s,
            output_summary = %s,
            error_details = %s,
            tokens_used = %s
        WHERE id = %s
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    status,
                    Json(kwargs.get('output_summary', {})),
                    kwargs.get('error_details'),
                    kwargs.get('tokens_used'),
                    execution_id
                ))
                conn.commit()


# ========== FACTORY AND UTILITIES ==========

def create_database_manager(async_mode: bool = True) -> Union[AsyncAgentMetadataDB, AgentMetadataDB]:
    """Factory function to create database manager"""
    config = DatabaseConfig.from_env()
    
    if async_mode:
        return AsyncAgentMetadataDB(config)
    else:
        return AgentMetadataDB(config)


async def setup_sample_data(db: AsyncAgentMetadataDB):
    """Setup sample agent data for testing"""
    
    sample_agents = [
        {
            'name': 'database-architect',
            'display_name': 'Database Architecture Specialist',
            'description': 'Expert in database design, optimization, and scaling strategies',
            'tier': '3',
            'specializations': ['database-design', 'performance-optimization', 'data-modeling'],
            'tools_available': ['postgresql', 'redis', 'mongodb'],
            'keywords': ['database', 'schema', 'performance', 'optimization'],
            'preferred_model': 'opus'
        },
        {
            'name': 'backend-services',
            'display_name': 'Backend Services Developer', 
            'description': 'Develops and maintains backend APIs and services',
            'tier': '3',
            'specializations': ['api-development', 'microservices', 'rest', 'graphql'],
            'tools_available': ['fastapi', 'flask', 'django'],
            'keywords': ['backend', 'api', 'services', 'rest'],
            'preferred_model': 'sonnet'
        },
        {
            'name': 'smart-orchestrator',
            'display_name': 'Smart Agent Orchestrator',
            'description': 'Coordinates and routes requests between agents',
            'tier': '2', 
            'specializations': ['orchestration', 'routing', 'coordination'],
            'tools_available': ['orchestrator', 'router'],
            'keywords': ['orchestrator', 'routing', 'coordination'],
            'preferred_model': 'sonnet'
        }
    ]
    
    for agent_data in sample_agents:
        try:
            await db.create_agent(agent_data)
        except Exception as e:
            print(f"Agent {agent_data['name']} might already exist: {e}")


# ========== EXAMPLE USAGE ==========

async def example_usage():
    """Example usage of the agent metadata database"""
    
    # Initialize database
    db = create_database_manager(async_mode=True)
    await db.initialize()
    
    try:
        # Setup sample data
        await setup_sample_data(db)
        
        # Search for agents
        agents = await db.search_agents(
            query_text="database optimization",
            limit=3
        )
        print(f"Found {len(agents)} agents for database optimization")
        
        # Generate recommendations
        context = {
            'keywords': ['database', 'performance'],
            'phase': 'design',
            'file_types': ['sql']
        }
        
        recommendations = await db.generate_agent_recommendations(context)
        print(f"Generated {len(recommendations)} recommendations")
        
        for rec in recommendations:
            agent = await db.get_agent(rec.agent_id)
            print(f"- {agent.name}: {rec.total_score:.2f}")
        
        # Track execution
        if recommendations:
            agent_id = recommendations[0].agent_id
            execution_id = await db.start_execution(
                agent_id, 
                'user_request',
                {'query': 'optimize database schema'}
            )
            
            # Simulate completion
            await asyncio.sleep(0.1)
            await db.complete_execution(
                execution_id,
                ExecutionStatus.COMPLETED,
                {'result': 'schema optimized'},
                tokens_used=150
            )
            
            # Get performance metrics
            performance = await db.get_agent_performance(agent_id)
            print(f"Agent performance: {performance}")
        
        # System health check
        health = await db.get_system_health()
        print(f"System health: {health}")
        
    finally:
        await db.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())