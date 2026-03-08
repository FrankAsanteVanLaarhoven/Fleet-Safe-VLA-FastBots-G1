-- IronCloud-AI Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create projects table
CREATE TABLE IF NOT EXISTS archon_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    github_repo VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pinned BOOLEAN DEFAULT FALSE,
    docs JSONB DEFAULT '[]',
    features JSONB DEFAULT '[]',
    data JSONB DEFAULT '[]'
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS archon_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo',
    assignee VARCHAR(100) DEFAULT 'User',
    task_order INTEGER DEFAULT 0,
    feature VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archived BOOLEAN DEFAULT FALSE,
    sources JSONB DEFAULT '[]',
    code_examples JSONB DEFAULT '[]'
);

-- Create knowledge sources table
CREATE TABLE IF NOT EXISTS knowledge_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    url TEXT,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON archon_projects(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON archon_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON archon_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON archon_tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_type ON knowledge_sources(type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at DESC);

-- Insert sample data
INSERT INTO archon_projects (title, description, github_repo) VALUES
('IronCloud-AI Platform', 'World-leading agentic RAG and military-grade web intelligence platform', 'https://github.com/ironcloud/ai-platform'),
('DataMinerAI Platform', 'Comprehensive AI-powered data mining and analytics platform', 'https://github.com/dataminerai/platform'),
('Universal Web Crawler', 'Advanced web crawling and data extraction platform', 'https://github.com/dataminerai/web-crawler')
ON CONFLICT DO NOTHING;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON archon_projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON archon_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_sources_updated_at BEFORE UPDATE ON knowledge_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
