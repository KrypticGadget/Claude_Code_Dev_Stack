-- Claude Code Dev Stack V3.6.9 - Development Database Initialization
-- Simplified setup for development and testing

-- Create test databases
CREATE DATABASE claude_dev_test;
CREATE DATABASE claude_test_integration;
CREATE DATABASE claude_test_e2e;

-- Create test users
CREATE USER claude_test WITH ENCRYPTED PASSWORD 'claude_test_pass';
CREATE USER claude_integration WITH ENCRYPTED PASSWORD 'claude_integration_pass';
CREATE USER claude_e2e WITH ENCRYPTED PASSWORD 'claude_e2e_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE claude_dev_test TO claude_test;
GRANT ALL PRIVILEGES ON DATABASE claude_test_integration TO claude_integration;
GRANT ALL PRIVILEGES ON DATABASE claude_test_e2e TO claude_e2e;

-- Connect to test database
\c claude_dev_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create simple test tables
CREATE TABLE IF NOT EXISTS test_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS test_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES test_agents(id),
    title VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS test_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert test data
INSERT INTO test_agents (name, status, data) VALUES
('test-agent-1', 'active', '{"type": "test", "tier": 1}'),
('test-agent-2', 'active', '{"type": "test", "tier": 2}'),
('test-agent-3', 'inactive', '{"type": "test", "tier": 3}');

INSERT INTO test_tasks (agent_id, title, status, data) 
SELECT id, 'Test Task ' || name, 'completed', '{"test": true}' 
FROM test_agents WHERE status = 'active';

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO claude_test;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO claude_test;

-- Setup integration test database
\c claude_test_integration;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create integration test tables
CREATE TABLE IF NOT EXISTS integration_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite VARCHAR(100) NOT NULL,
    test_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO claude_integration;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO claude_integration;

-- Setup E2E test database
\c claude_test_e2e;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create E2E test tables
CREATE TABLE IF NOT EXISTS e2e_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL,
    browser VARCHAR(50),
    viewport VARCHAR(50),
    test_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS e2e_screenshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES e2e_sessions(id),
    test_step VARCHAR(100),
    screenshot_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO claude_e2e;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO claude_e2e;