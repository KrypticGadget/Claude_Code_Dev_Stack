-- Context Preservation System Database Schema
-- PostgreSQL schema for robust context management

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create context storage schema
CREATE SCHEMA IF NOT EXISTS context_system;

-- Main context storage table
CREATE TABLE IF NOT EXISTS context_system.contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_key VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    agent_id VARCHAR(255),
    parent_context_id UUID REFERENCES context_system.contexts(id) ON DELETE SET NULL,
    
    -- Content and metadata
    context_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    
    -- Versioning
    version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Storage optimization
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_compressed BOOLEAN DEFAULT FALSE,
    content_size INTEGER DEFAULT 0,
    content_hash VARCHAR(64),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Access tracking
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT unique_current_context UNIQUE(context_key, is_current) DEFERRABLE INITIALLY DEFERRED
);

-- Context versions table for history tracking
CREATE TABLE IF NOT EXISTS context_system.context_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_id UUID NOT NULL REFERENCES context_system.contexts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    
    -- Version data
    context_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    content_size INTEGER DEFAULT 0,
    content_hash VARCHAR(64),
    
    -- Change tracking
    change_type VARCHAR(50) DEFAULT 'update',
    change_summary TEXT,
    changed_by VARCHAR(255),
    change_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(context_id, version)
);

-- Context relationships table
CREATE TABLE IF NOT EXISTS context_system.context_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_context_id UUID NOT NULL REFERENCES context_system.contexts(id) ON DELETE CASCADE,
    child_context_id UUID NOT NULL REFERENCES context_system.contexts(id) ON DELETE CASCADE,
    
    -- Relationship details
    relationship_type VARCHAR(50) NOT NULL,
    relationship_strength DECIMAL(3,2) DEFAULT 1.0,
    relationship_metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(parent_context_id, child_context_id, relationship_type),
    CHECK (parent_context_id != child_context_id),
    CHECK (relationship_strength >= 0.0 AND relationship_strength <= 1.0)
);

-- Full-text search table
CREATE TABLE IF NOT EXISTS context_system.context_search (
    context_id UUID PRIMARY KEY REFERENCES context_system.contexts(id) ON DELETE CASCADE,
    search_vector TSVECTOR,
    search_content TEXT,
    content_hash VARCHAR(64) UNIQUE,
    language VARCHAR(10) DEFAULT 'english',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Session management table
CREATE TABLE IF NOT EXISTS context_system.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    agent_id VARCHAR(255),
    
    -- Session metadata
    session_data JSONB DEFAULT '{}',
    session_tags TEXT[] DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Access logs table for analytics
CREATE TABLE IF NOT EXISTS context_system.access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_id UUID REFERENCES context_system.contexts(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    agent_id VARCHAR(255),
    
    -- Access details
    operation VARCHAR(50) NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    response_time_ms INTEGER,
    error_message TEXT,
    
    -- Request metadata
    request_metadata JSONB DEFAULT '{}',
    client_info JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS context_system.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    
    -- Dimensions
    session_id VARCHAR(255),
    agent_id VARCHAR(255),
    operation VARCHAR(50),
    
    -- Metadata
    tags JSONB DEFAULT '{}',
    
    -- Timestamps
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for optimal performance

-- Primary indexes on contexts table
CREATE INDEX IF NOT EXISTS idx_contexts_key ON context_system.contexts(context_key);
CREATE INDEX IF NOT EXISTS idx_contexts_session_agent ON context_system.contexts(session_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_contexts_parent ON context_system.contexts(parent_context_id);
CREATE INDEX IF NOT EXISTS idx_contexts_expires ON context_system.contexts(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contexts_current ON context_system.contexts(context_key, is_current) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_contexts_tags ON context_system.contexts USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_contexts_metadata ON context_system.contexts USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_contexts_created ON context_system.contexts(created_at);
CREATE INDEX IF NOT EXISTS idx_contexts_accessed ON context_system.contexts(last_accessed_at);

-- Indexes on context_versions table
CREATE INDEX IF NOT EXISTS idx_versions_context_id ON context_system.context_versions(context_id, version);
CREATE INDEX IF NOT EXISTS idx_versions_created ON context_system.context_versions(created_at);
CREATE INDEX IF NOT EXISTS idx_versions_changed_by ON context_system.context_versions(changed_by);

-- Indexes on relationships table
CREATE INDEX IF NOT EXISTS idx_relationships_parent ON context_system.context_relationships(parent_context_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child ON context_system.context_relationships(child_context_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON context_system.context_relationships(relationship_type);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_search_vector ON context_system.context_search USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_search_content_hash ON context_system.context_search(content_hash);

-- Session indexes
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON context_system.sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_agent_id ON context_system.sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON context_system.sessions(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON context_system.sessions(expires_at) WHERE expires_at IS NOT NULL;

-- Access logs indexes for analytics
CREATE INDEX IF NOT EXISTS idx_access_logs_context ON context_system.access_logs(context_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_session_agent ON context_system.access_logs(session_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_operation ON context_system.access_logs(operation);
CREATE INDEX IF NOT EXISTS idx_access_logs_created ON context_system.access_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_access_logs_success ON context_system.access_logs(success);

-- Performance metrics indexes
CREATE INDEX IF NOT EXISTS idx_metrics_name_recorded ON context_system.performance_metrics(metric_name, recorded_at);
CREATE INDEX IF NOT EXISTS idx_metrics_session_agent ON context_system.performance_metrics(session_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_metrics_operation ON context_system.performance_metrics(operation);

-- Create triggers for automatic timestamp updates

-- Update timestamps on context updates
CREATE OR REPLACE FUNCTION context_system.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contexts_update_timestamp
    BEFORE UPDATE ON context_system.contexts
    FOR EACH ROW
    EXECUTE FUNCTION context_system.update_updated_at();

CREATE TRIGGER relationships_update_timestamp
    BEFORE UPDATE ON context_system.context_relationships
    FOR EACH ROW
    EXECUTE FUNCTION context_system.update_updated_at();

CREATE TRIGGER sessions_update_timestamp
    BEFORE UPDATE ON context_system.sessions
    FOR EACH ROW
    EXECUTE FUNCTION context_system.update_updated_at();

-- Trigger to update search vector when context changes
CREATE OR REPLACE FUNCTION context_system.update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO context_system.context_search (
        context_id, 
        search_vector, 
        search_content,
        content_hash
    ) VALUES (
        NEW.id,
        to_tsvector('english', 
            COALESCE(NEW.context_key, '') || ' ' ||
            COALESCE(NEW.context_data::text, '') || ' ' ||
            COALESCE(NEW.metadata::text, '') || ' ' ||
            COALESCE(array_to_string(NEW.tags, ' '), '')
        ),
        NEW.context_key || ' ' || NEW.context_data::text,
        NEW.content_hash
    ) ON CONFLICT (context_id) DO UPDATE SET
        search_vector = to_tsvector('english', 
            COALESCE(NEW.context_key, '') || ' ' ||
            COALESCE(NEW.context_data::text, '') || ' ' ||
            COALESCE(NEW.metadata::text, '') || ' ' ||
            COALESCE(array_to_string(NEW.tags, ' '), '')
        ),
        search_content = NEW.context_key || ' ' || NEW.context_data::text,
        content_hash = NEW.content_hash,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contexts_update_search
    AFTER INSERT OR UPDATE ON context_system.contexts
    FOR EACH ROW
    EXECUTE FUNCTION context_system.update_search_vector();

-- Trigger to log access
CREATE OR REPLACE FUNCTION context_system.log_context_access()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if access_count actually changed (indicating a read operation)
    IF NEW.access_count > OLD.access_count THEN
        INSERT INTO context_system.access_logs (
            context_id,
            session_id,
            agent_id,
            operation,
            success,
            client_info
        ) VALUES (
            NEW.id,
            NEW.session_id,
            COALESCE(NEW.last_accessed_by, NEW.agent_id),
            'read',
            TRUE,
            jsonb_build_object('access_count', NEW.access_count)
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contexts_log_access
    AFTER UPDATE ON context_system.contexts
    FOR EACH ROW
    WHEN (NEW.access_count > OLD.access_count)
    EXECUTE FUNCTION context_system.log_context_access();

-- Create views for common queries

-- Active contexts view
CREATE OR REPLACE VIEW context_system.active_contexts AS
SELECT 
    c.*,
    s.search_content,
    CASE 
        WHEN c.expires_at IS NULL THEN TRUE
        WHEN c.expires_at > NOW() THEN TRUE
        ELSE FALSE
    END AS is_active
FROM context_system.contexts c
LEFT JOIN context_system.context_search s ON c.id = s.context_id
WHERE c.is_current = TRUE
    AND (c.expires_at IS NULL OR c.expires_at > NOW());

-- Context with relationships view
CREATE OR REPLACE VIEW context_system.contexts_with_relationships AS
SELECT 
    c.*,
    COALESCE(
        json_agg(
            json_build_object(
                'type', r.relationship_type,
                'child_id', r.child_context_id,
                'strength', r.relationship_strength
            )
        ) FILTER (WHERE r.id IS NOT NULL),
        '[]'::json
    ) AS relationships
FROM context_system.contexts c
LEFT JOIN context_system.context_relationships r ON c.id = r.parent_context_id
WHERE c.is_current = TRUE
GROUP BY c.id;

-- Session summary view
CREATE OR REPLACE VIEW context_system.session_summary AS
SELECT 
    s.session_id,
    s.agent_id,
    s.is_active,
    s.created_at as session_started,
    s.last_activity_at,
    COUNT(c.id) as context_count,
    SUM(c.access_count) as total_accesses,
    MAX(c.last_accessed_at) as last_context_access
FROM context_system.sessions s
LEFT JOIN context_system.contexts c ON s.session_id = c.session_id
GROUP BY s.session_id, s.agent_id, s.is_active, s.created_at, s.last_activity_at;

-- Analytics view for context usage
CREATE OR REPLACE VIEW context_system.context_analytics AS
SELECT 
    c.agent_id,
    c.session_id,
    DATE(c.created_at) as date,
    COUNT(*) as contexts_created,
    SUM(c.access_count) as total_accesses,
    AVG(c.access_count) as avg_accesses_per_context,
    COUNT(*) FILTER (WHERE c.expires_at IS NOT NULL AND c.expires_at > NOW()) as active_contexts,
    COUNT(*) FILTER (WHERE c.expires_at IS NOT NULL AND c.expires_at <= NOW()) as expired_contexts
FROM context_system.contexts c
GROUP BY c.agent_id, c.session_id, DATE(c.created_at)
ORDER BY date DESC;

-- Create stored procedures for common operations

-- Procedure to clean up expired contexts
CREATE OR REPLACE FUNCTION context_system.cleanup_expired_contexts()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete expired contexts
    WITH deleted AS (
        DELETE FROM context_system.contexts 
        WHERE expires_at IS NOT NULL 
            AND expires_at <= NOW()
            AND is_current = TRUE
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    -- Clean up orphaned search entries
    DELETE FROM context_system.context_search 
    WHERE context_id NOT IN (SELECT id FROM context_system.contexts);
    
    -- Log the cleanup
    INSERT INTO context_system.access_logs (
        context_id,
        operation,
        success,
        request_metadata
    ) VALUES (
        NULL,
        'cleanup',
        TRUE,
        jsonb_build_object('deleted_count', deleted_count, 'timestamp', NOW())
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Procedure to archive old context versions
CREATE OR REPLACE FUNCTION context_system.archive_old_versions(max_versions INTEGER DEFAULT 10)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    WITH versions_to_delete AS (
        SELECT cv.id
        FROM context_system.context_versions cv
        WHERE cv.version NOT IN (
            SELECT version 
            FROM context_system.context_versions cv2 
            WHERE cv2.context_id = cv.context_id
            ORDER BY version DESC 
            LIMIT max_versions
        )
    ),
    deleted AS (
        DELETE FROM context_system.context_versions 
        WHERE id IN (SELECT id FROM versions_to_delete)
        RETURNING id
    )
    SELECT COUNT(*) INTO archived_count FROM deleted;
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Procedure to get context statistics
CREATE OR REPLACE FUNCTION context_system.get_context_stats(
    session_filter VARCHAR DEFAULT NULL,
    agent_filter VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    total_contexts BIGINT,
    active_contexts BIGINT,
    expired_contexts BIGINT,
    total_versions BIGINT,
    total_accesses BIGINT,
    unique_sessions BIGINT,
    unique_agents BIGINT,
    avg_accesses_per_context NUMERIC,
    storage_size_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_contexts,
        COUNT(*) FILTER (WHERE c.expires_at IS NULL OR c.expires_at > NOW()) as active_contexts,
        COUNT(*) FILTER (WHERE c.expires_at IS NOT NULL AND c.expires_at <= NOW()) as expired_contexts,
        (SELECT COUNT(*) FROM context_system.context_versions WHERE context_id = ANY(ARRAY_AGG(c.id))) as total_versions,
        SUM(c.access_count) as total_accesses,
        COUNT(DISTINCT c.session_id) FILTER (WHERE c.session_id IS NOT NULL) as unique_sessions,
        COUNT(DISTINCT c.agent_id) FILTER (WHERE c.agent_id IS NOT NULL) as unique_agents,
        AVG(c.access_count) as avg_accesses_per_context,
        ROUND(SUM(c.content_size)::NUMERIC / 1024 / 1024, 2) as storage_size_mb
    FROM context_system.contexts c
    WHERE (session_filter IS NULL OR c.session_id = session_filter)
        AND (agent_filter IS NULL OR c.agent_id = agent_filter)
        AND c.is_current = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your security requirements)
GRANT USAGE ON SCHEMA context_system TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA context_system TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA context_system TO PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA context_system TO PUBLIC;

-- Create a scheduled job to clean up expired contexts (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-expired-contexts', '0 */1 * * *', 'SELECT context_system.cleanup_expired_contexts();');
-- SELECT cron.schedule('archive-old-versions', '0 2 * * *', 'SELECT context_system.archive_old_versions(10);');