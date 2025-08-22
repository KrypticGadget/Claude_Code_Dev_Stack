-- Claude Code Agent Metadata System - Production Schema
-- Comprehensive database design for agent hierarchy, performance, and collaboration tracking
-- Optimized for fast agent selection and real-time monitoring

-- ========== EXTENSIONS AND SETUP ==========
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";         -- For text similarity searches
CREATE EXTENSION IF NOT EXISTS "btree_gin";       -- For composite indexes
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- For query performance tracking
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE; -- For time-series data (if available)

-- ========== CUSTOM TYPES ==========
DO $$ BEGIN
    CREATE TYPE agent_tier AS ENUM ('1', '2', '3', '4', '5');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE agent_status AS ENUM ('active', 'inactive', 'maintenance', 'deprecated', 'developing');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'timeout', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE communication_type AS ENUM ('delegation', 'coordination', 'handoff', 'escalation', 'consultation');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ========== CORE AGENT METADATA ==========

-- Main agent registry with hierarchy and capabilities
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    tier agent_tier NOT NULL,
    status agent_status DEFAULT 'active',
    
    -- Capability and specialization data
    specializations TEXT[] DEFAULT '{}',
    tools_available TEXT[] DEFAULT '{}',
    supported_file_types TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    
    -- Model and configuration
    preferred_model VARCHAR(50) DEFAULT 'sonnet',
    configuration JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE,
    version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Performance tracking fields
    total_executions BIGINT DEFAULT 0,
    success_count BIGINT DEFAULT 0,
    avg_execution_time_ms INTEGER DEFAULT 0,
    
    -- Search optimization
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', 
            name || ' ' || display_name || ' ' || 
            COALESCE(description, '') || ' ' ||
            array_to_string(specializations, ' ') || ' ' ||
            array_to_string(keywords, ' ')
        )
    ) STORED
);

-- ========== HIERARCHY AND RELATIONSHIPS ==========

-- Agent hierarchy and reporting relationships
CREATE TABLE IF NOT EXISTS agent_hierarchy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    parent_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- 'reports_to', 'delegates_to', 'coordinates_with'
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(agent_id, parent_agent_id, relationship_type)
);

-- Team assignments and role-based groupings
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    team_type VARCHAR(50) NOT NULL, -- 'analysis', 'design', 'implementation', 'quality', 'management'
    lead_agent_id UUID REFERENCES agents(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS team_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    role VARCHAR(100), -- 'lead', 'member', 'consultant', 'backup'
    priority INTEGER DEFAULT 1,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(team_id, agent_id)
);

-- ========== PERFORMANCE TRACKING ==========

-- Detailed execution history with time-series optimization
CREATE TABLE IF NOT EXISTS execution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id),
    session_id UUID, -- Groups related executions
    execution_type VARCHAR(50) NOT NULL, -- 'user_request', 'delegation', 'auto_trigger'
    
    -- Performance metrics
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    status execution_status DEFAULT 'pending',
    
    -- Context and input/output
    input_context JSONB DEFAULT '{}',
    output_summary JSONB DEFAULT '{}',
    error_details TEXT,
    
    -- Resource usage
    tokens_used INTEGER,
    memory_peak_mb INTEGER,
    cpu_time_ms INTEGER,
    
    -- Quality metrics
    user_satisfaction_rating INTEGER CHECK (user_satisfaction_rating BETWEEN 1 AND 5),
    retry_count INTEGER DEFAULT 0,
    
    -- Indexing for time-series queries
    day_bucket DATE GENERATED ALWAYS AS (DATE(started_at)) STORED
);

-- Performance aggregations for fast lookups
CREATE TABLE IF NOT EXISTS agent_performance_daily (
    agent_id UUID NOT NULL REFERENCES agents(id),
    date DATE NOT NULL,
    
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms FLOAT,
    total_tokens_used BIGINT DEFAULT 0,
    avg_satisfaction FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (agent_id, date)
);

-- ========== COMMUNICATION AND COLLABORATION ==========

-- Agent communication patterns and handoffs
CREATE TABLE IF NOT EXISTS agent_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_agent_id UUID NOT NULL REFERENCES agents(id),
    to_agent_id UUID NOT NULL REFERENCES agents(id),
    communication_type communication_type NOT NULL,
    
    -- Context and data passed
    context_data JSONB DEFAULT '{}',
    handoff_reason VARCHAR(200),
    success BOOLEAN,
    response_time_ms INTEGER,
    
    -- Timing
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Reference to related execution
    execution_id UUID REFERENCES execution_history(id)
);

-- Agent collaboration effectiveness tracking
CREATE TABLE IF NOT EXISTS collaboration_patterns (
    from_agent_id UUID NOT NULL REFERENCES agents(id),
    to_agent_id UUID NOT NULL REFERENCES agents(id),
    
    -- Aggregated metrics
    total_handoffs INTEGER DEFAULT 0,
    successful_handoffs INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT,
    last_collaboration TIMESTAMP WITH TIME ZONE,
    
    -- Effectiveness scoring
    collaboration_score FLOAT DEFAULT 0.0,
    
    PRIMARY KEY (from_agent_id, to_agent_id)
);

-- ========== CONFIGURATION AND CUSTOMIZATION ==========

-- Agent-specific configurations and settings
CREATE TABLE IF NOT EXISTS agent_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    config_type VARCHAR(50) NOT NULL, -- 'system', 'user', 'performance', 'integration'
    config_name VARCHAR(100) NOT NULL,
    config_value JSONB NOT NULL,
    
    -- Versioning and lifecycle
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(agent_id, config_type, config_name, version)
);

-- Dynamic agent capabilities based on context
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    capability_name VARCHAR(100) NOT NULL,
    capability_description TEXT,
    proficiency_level INTEGER CHECK (proficiency_level BETWEEN 1 AND 5),
    
    -- Context where this capability applies
    applicable_contexts TEXT[] DEFAULT '{}',
    required_tools TEXT[] DEFAULT '{}',
    
    -- Performance tracking for this capability
    usage_count BIGINT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(agent_id, capability_name)
);

-- ========== AUDIT AND COMPLIANCE ==========

-- Complete audit trail for all agent activities
CREATE TABLE IF NOT EXISTS agent_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    user_id VARCHAR(100), -- External user identifier
    
    -- Action details
    action_type VARCHAR(50) NOT NULL, -- 'created', 'updated', 'executed', 'delegated', 'failed'
    table_name VARCHAR(50),
    record_id UUID,
    
    -- Change tracking
    old_values JSONB,
    new_values JSONB,
    change_reason TEXT,
    
    -- Context and metadata
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    request_id UUID,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========== RECOMMENDATION ENGINE DATA ==========

-- Agent selection patterns for machine learning
CREATE TABLE IF NOT EXISTS agent_selection_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Context fingerprint
    request_keywords TEXT[] DEFAULT '{}',
    file_types TEXT[] DEFAULT '{}',
    project_phase VARCHAR(50),
    time_of_day INTEGER, -- Hour of day (0-23)
    day_of_week INTEGER, -- 1-7
    
    -- Selection result
    selected_agent_id UUID NOT NULL REFERENCES agents(id),
    selection_reason VARCHAR(200),
    confidence_score FLOAT,
    
    -- Outcome tracking
    execution_success BOOLEAN,
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    duration_ms INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent recommendation scoring
CREATE TABLE IF NOT EXISTS agent_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id),
    
    -- Context-based scoring
    keyword_match_score FLOAT DEFAULT 0.0,
    phase_alignment_score FLOAT DEFAULT 0.0,
    recent_success_score FLOAT DEFAULT 0.0,
    domain_expertise_score FLOAT DEFAULT 0.0,
    availability_score FLOAT DEFAULT 1.0,
    
    -- Overall recommendation
    total_score FLOAT GENERATED ALWAYS AS (
        keyword_match_score * 0.35 + 
        phase_alignment_score * 0.25 + 
        recent_success_score * 0.20 + 
        domain_expertise_score * 0.15 + 
        availability_score * 0.05
    ) STORED,
    
    -- Context this recommendation applies to
    context_hash VARCHAR(64) NOT NULL, -- MD5 of normalized context
    context_data JSONB DEFAULT '{}',
    
    -- Lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 hour'),
    
    UNIQUE(agent_id, context_hash)
);

-- ========== INDEXES FOR PERFORMANCE ==========

-- Agent search and selection indexes
CREATE INDEX IF NOT EXISTS idx_agents_search ON agents USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_agents_tier_status ON agents(tier, status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_agents_specializations ON agents USING GIN(specializations);
CREATE INDEX IF NOT EXISTS idx_agents_keywords ON agents USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_agents_last_active ON agents(last_active_at DESC) WHERE status = 'active';

-- Hierarchy and team indexes
CREATE INDEX IF NOT EXISTS idx_hierarchy_agent ON agent_hierarchy(agent_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_hierarchy_parent ON agent_hierarchy(parent_agent_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_team_memberships_agent ON team_memberships(agent_id) WHERE left_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_team_memberships_team ON team_memberships(team_id) WHERE left_at IS NULL;

-- Performance tracking indexes
CREATE INDEX IF NOT EXISTS idx_execution_history_agent_time ON execution_history(agent_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_execution_history_day_bucket ON execution_history(day_bucket, agent_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_session ON execution_history(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_execution_history_status ON execution_history(status, started_at) WHERE status IN ('running', 'pending');

-- Communication pattern indexes
CREATE INDEX IF NOT EXISTS idx_communications_from_agent ON agent_communications(from_agent_id, initiated_at DESC);
CREATE INDEX IF NOT EXISTS idx_communications_to_agent ON agent_communications(to_agent_id, initiated_at DESC);
CREATE INDEX IF NOT EXISTS idx_communications_type ON agent_communications(communication_type, initiated_at DESC);

-- Recommendation engine indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON agent_recommendations(total_score DESC) WHERE expires_at > NOW();
CREATE INDEX IF NOT EXISTS idx_recommendations_context ON agent_recommendations(context_hash) WHERE expires_at > NOW();
CREATE INDEX IF NOT EXISTS idx_selection_patterns_keywords ON agent_selection_patterns USING GIN(request_keywords);

-- Audit and compliance indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_agent_time ON agent_audit_log(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_time ON agent_audit_log(action_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_session ON agent_audit_log(session_id) WHERE session_id IS NOT NULL;

-- Configuration indexes
CREATE INDEX IF NOT EXISTS idx_agent_configs_active ON agent_configurations(agent_id, config_type) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_agent_capabilities_context ON agent_capabilities USING GIN(applicable_contexts);

-- ========== TRIGGERS FOR AUTOMATION ==========

-- Update agent statistics on execution completion
CREATE OR REPLACE FUNCTION update_agent_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE agents 
        SET 
            total_executions = total_executions + 1,
            success_count = success_count + 1,
            last_active_at = NEW.completed_at,
            avg_execution_time_ms = (
                (avg_execution_time_ms * (total_executions - 1) + COALESCE(NEW.duration_ms, 0)) / 
                GREATEST(total_executions, 1)
            )
        WHERE id = NEW.agent_id;
        
        -- Update daily aggregations
        INSERT INTO agent_performance_daily (agent_id, date, execution_count, success_count, avg_duration_ms, total_tokens_used)
        VALUES (
            NEW.agent_id, 
            DATE(NEW.started_at), 
            1, 
            1, 
            NEW.duration_ms,
            COALESCE(NEW.tokens_used, 0)
        )
        ON CONFLICT (agent_id, date) 
        DO UPDATE SET
            execution_count = agent_performance_daily.execution_count + 1,
            success_count = agent_performance_daily.success_count + 1,
            avg_duration_ms = (
                (agent_performance_daily.avg_duration_ms * agent_performance_daily.execution_count + COALESCE(NEW.duration_ms, 0)) /
                (agent_performance_daily.execution_count + 1)
            ),
            total_tokens_used = agent_performance_daily.total_tokens_used + COALESCE(NEW.tokens_used, 0),
            updated_at = NOW();
            
    ELSIF NEW.status = 'failed' AND OLD.status != 'failed' THEN
        UPDATE agents 
        SET 
            total_executions = total_executions + 1,
            last_active_at = COALESCE(NEW.completed_at, NEW.started_at)
        WHERE id = NEW.agent_id;
        
        -- Update daily aggregations for failures
        INSERT INTO agent_performance_daily (agent_id, date, execution_count, failure_count)
        VALUES (NEW.agent_id, DATE(NEW.started_at), 1, 1)
        ON CONFLICT (agent_id, date) 
        DO UPDATE SET
            execution_count = agent_performance_daily.execution_count + 1,
            failure_count = agent_performance_daily.failure_count + 1,
            updated_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_agent_stats
    AFTER UPDATE ON execution_history
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_stats();

-- Update collaboration patterns
CREATE OR REPLACE FUNCTION update_collaboration_patterns()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO collaboration_patterns (from_agent_id, to_agent_id, total_handoffs, successful_handoffs, avg_response_time_ms, last_collaboration)
    VALUES (
        NEW.from_agent_id, 
        NEW.to_agent_id, 
        1, 
        CASE WHEN NEW.success THEN 1 ELSE 0 END,
        NEW.response_time_ms,
        NEW.completed_at
    )
    ON CONFLICT (from_agent_id, to_agent_id)
    DO UPDATE SET
        total_handoffs = collaboration_patterns.total_handoffs + 1,
        successful_handoffs = collaboration_patterns.successful_handoffs + CASE WHEN NEW.success THEN 1 ELSE 0 END,
        avg_response_time_ms = (
            (collaboration_patterns.avg_response_time_ms * collaboration_patterns.total_handoffs + COALESCE(NEW.response_time_ms, 0)) /
            (collaboration_patterns.total_handoffs + 1)
        ),
        last_collaboration = NEW.completed_at,
        collaboration_score = (
            collaboration_patterns.successful_handoffs::FLOAT / 
            GREATEST(collaboration_patterns.total_handoffs, 1) * 100
        );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_collaboration_patterns
    AFTER INSERT ON agent_communications
    FOR EACH ROW
    EXECUTE FUNCTION update_collaboration_patterns();

-- Auto-expire old recommendations
CREATE OR REPLACE FUNCTION cleanup_expired_recommendations()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM agent_recommendations WHERE expires_at < NOW();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_cleanup_recommendations
    AFTER INSERT ON agent_recommendations
    FOR EACH STATEMENT
    EXECUTE FUNCTION cleanup_expired_recommendations();

-- ========== VIEWS FOR COMMON QUERIES ==========

-- Active agents with current performance
CREATE OR REPLACE VIEW v_active_agents AS
SELECT 
    a.id,
    a.name,
    a.display_name,
    a.tier,
    a.specializations,
    a.total_executions,
    a.success_count,
    CASE 
        WHEN a.total_executions > 0 THEN (a.success_count::FLOAT / a.total_executions * 100)
        ELSE 0 
    END as success_rate,
    a.avg_execution_time_ms,
    a.last_active_at,
    EXTRACT(EPOCH FROM (NOW() - a.last_active_at))/3600 as hours_since_last_active
FROM agents a
WHERE a.status = 'active'
ORDER BY a.tier, a.success_count DESC;

-- Agent hierarchy with performance
CREATE OR REPLACE VIEW v_agent_hierarchy_performance AS
SELECT 
    a.id as agent_id,
    a.name as agent_name,
    a.tier,
    p.name as parent_name,
    p.tier as parent_tier,
    h.relationship_type,
    a.total_executions,
    CASE 
        WHEN a.total_executions > 0 THEN (a.success_count::FLOAT / a.total_executions * 100)
        ELSE 0 
    END as success_rate
FROM agents a
LEFT JOIN agent_hierarchy h ON a.id = h.agent_id AND h.is_active = true
LEFT JOIN agents p ON h.parent_agent_id = p.id
WHERE a.status = 'active'
ORDER BY a.tier, a.name;

-- Real-time agent recommendations
CREATE OR REPLACE VIEW v_agent_recommendations AS
SELECT 
    r.agent_id,
    a.name,
    a.display_name,
    r.total_score,
    r.keyword_match_score,
    r.phase_alignment_score,
    r.recent_success_score,
    r.domain_expertise_score,
    r.availability_score,
    r.context_hash,
    r.expires_at
FROM agent_recommendations r
JOIN agents a ON r.agent_id = a.id
WHERE r.expires_at > NOW() AND a.status = 'active'
ORDER BY r.total_score DESC;

-- Team effectiveness
CREATE OR REPLACE VIEW v_team_effectiveness AS
SELECT 
    t.name as team_name,
    t.team_type,
    COUNT(tm.agent_id) as team_size,
    AVG(a.success_count::FLOAT / GREATEST(a.total_executions, 1) * 100) as avg_success_rate,
    AVG(a.avg_execution_time_ms) as avg_execution_time,
    MAX(a.last_active_at) as last_team_activity
FROM teams t
JOIN team_memberships tm ON t.id = tm.team_id AND tm.left_at IS NULL
JOIN agents a ON tm.agent_id = a.id AND a.status = 'active'
GROUP BY t.id, t.name, t.team_type
ORDER BY avg_success_rate DESC;

-- ========== INITIAL DATA ==========

-- Insert sample configuration (to be replaced with actual agent data)
INSERT INTO agents (name, display_name, description, tier, specializations, keywords) VALUES
('database-architect', 'Database Architecture Specialist', 'Expert in database design, optimization, and scaling strategies', '3', 
 ARRAY['database-design', 'performance-optimization', 'data-modeling', 'sql', 'nosql'], 
 ARRAY['database', 'schema', 'performance', 'optimization', 'postgres', 'sql']),
('backend-services', 'Backend Services Developer', 'Develops and maintains backend APIs and services', '3',
 ARRAY['api-development', 'microservices', 'rest', 'graphql'], 
 ARRAY['backend', 'api', 'services', 'rest', 'graphql']),
('smart-orchestrator', 'Smart Agent Orchestrator', 'Coordinates and routes requests between agents', '2',
 ARRAY['orchestration', 'routing', 'coordination'], 
 ARRAY['orchestrator', 'routing', 'coordination', 'agents'])
ON CONFLICT (name) DO NOTHING;

-- Set up basic hierarchy
INSERT INTO agent_hierarchy (agent_id, parent_agent_id, relationship_type) 
SELECT 
    a1.id, 
    a2.id, 
    'reports_to'
FROM agents a1, agents a2 
WHERE a1.name = 'database-architect' AND a2.name = 'smart-orchestrator'
ON CONFLICT DO NOTHING;

-- Create default teams
INSERT INTO teams (name, team_type, description) VALUES
('design-team', 'design', 'Architecture and design specialists'),
('implementation-team', 'implementation', 'Backend and frontend developers'),
('quality-team', 'quality', 'Testing and quality assurance specialists')
ON CONFLICT (name) DO NOTHING;

-- Grant permissions for application user
-- Note: Replace 'claude_app' with your actual application database user
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'claude_app') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO claude_app;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO claude_app;
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO claude_app;
    END IF;
END
$$;

-- Create indexes for time-series data if TimescaleDB is available
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('execution_history', 'started_at', if_not_exists => TRUE);
        PERFORM create_hypertable('agent_audit_log', 'created_at', if_not_exists => TRUE);
    END IF;
EXCEPTION
    WHEN others THEN
        -- TimescaleDB not available, continue with regular tables
        NULL;
END
$$;

-- Performance monitoring setup
CREATE OR REPLACE FUNCTION agent_metadata_health_check()
RETURNS TABLE(
    metric_name TEXT,
    metric_value NUMERIC,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'total_agents'::TEXT, COUNT(*)::NUMERIC, 'OK'::TEXT FROM agents WHERE status = 'active'
    UNION ALL
    SELECT 'total_executions_today'::TEXT, COUNT(*)::NUMERIC, 'OK'::TEXT FROM execution_history WHERE started_at >= CURRENT_DATE
    UNION ALL
    SELECT 'avg_success_rate'::TEXT, 
           ROUND(AVG(success_count::FLOAT / GREATEST(total_executions, 1) * 100), 2), 
           CASE WHEN AVG(success_count::FLOAT / GREATEST(total_executions, 1) * 100) >= 80 THEN 'OK' ELSE 'WARNING' END
    FROM agents WHERE status = 'active' AND total_executions > 0
    UNION ALL
    SELECT 'active_recommendations'::TEXT, COUNT(*)::NUMERIC, 'OK'::TEXT FROM agent_recommendations WHERE expires_at > NOW();
END;
$$ LANGUAGE plpgsql;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_versions (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_versions (version, description) VALUES 
('1.0.0', 'Initial agent metadata schema with comprehensive tracking and optimization')
ON CONFLICT (version) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Agent Metadata System schema created successfully!';
    RAISE NOTICE 'Schema version: 1.0.0';
    RAISE NOTICE 'Tables created: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%agent%' OR table_name LIKE '%execution%' OR table_name = 'teams');
    RAISE NOTICE 'Run agent_metadata_health_check() to verify system health';
END
$$;