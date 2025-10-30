-- HaaS Platform - Database Initialization Script
-- SQL script to initialize PostgreSQL database with basic setup

-- Create extensions if needed
CREATE EXTENSION
IF NOT EXISTS "uuid-ossp";
-- Note: PostGIS not available in pgvector image, removed
CREATE EXTENSION
IF NOT EXISTS "vector";

-- Create basic tables structure (will be managed by Alembic migrations)
-- This is just for initial setup

-- Create logs table for application logging
CREATE TABLE
IF NOT EXISTS app_logs
(
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR
(20) NOT NULL,
    logger VARCHAR
(100) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR
(100),
    function VARCHAR
(100),
    line_number INTEGER,
    extra_data JSONB
);

-- Create index for performance
CREATE INDEX
IF NOT EXISTS idx_app_logs_timestamp ON app_logs
(timestamp);
CREATE INDEX
IF NOT EXISTS idx_app_logs_level ON app_logs
(level);

-- Create application settings table
CREATE TABLE
IF NOT EXISTS app_settings
(
    key VARCHAR
(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO app_settings
    (key, value, description)
VALUES
    ('app_version', '1.0.0', 'Application version'),
    ('maintenance_mode', 'false', 'Maintenance mode flag'),
    ('max_file_upload_size', '52428800', 'Maximum file upload size in bytes')
ON CONFLICT
(key) DO NOTHING;

-- Create vector embeddings tables for semantic search
-- ANEEL documents embeddings
CREATE TABLE
IF NOT EXISTS aneel_document_embeddings
(
    id SERIAL PRIMARY KEY,
    document_id VARCHAR
(100) NOT NULL,
    document_type VARCHAR
(50) NOT NULL, -- 'regulatory', 'technical', 'guideline'
    title TEXT NOT NULL,
    content TEXT,
    embedding vector
(1536), -- OpenAI text-embedding-ada-002 dimension
    metadata JSONB,
    source_url TEXT,
    created_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE
(document_id, document_type)
);

-- Project embeddings for similarity search
CREATE TABLE
IF NOT EXISTS project_embeddings
(
    id SERIAL PRIMARY KEY,
    project_id VARCHAR
(100) NOT NULL,
    ceg VARCHAR
(50),
    embedding vector
(1536
), -- OpenAI text-embedding-ada-002 dimension
    project_data JSONB, -- Complete project information
    similarity_score FLOAT,
    created_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE
(project_id)
);

-- Regulatory compliance embeddings
CREATE TABLE
IF NOT EXISTS regulatory_embeddings
(
    id SERIAL PRIMARY KEY,
    regulation_id VARCHAR
(100) NOT NULL,
    regulation_type VARCHAR
(50) NOT NULL, -- 'aneel_resolution', 'technical_standard', 'legal_requirement'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector
(1536),
    applicability_rules JSONB, -- Rules for when this regulation applies
    compliance_checks JSONB, -- Automated compliance checks
    effective_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE
(regulation_id)
);

-- Create vector indexes for performance
CREATE INDEX
IF NOT EXISTS idx_aneel_docs_embedding ON aneel_document_embeddings USING ivfflat
(embedding vector_cosine_ops)
WITH
(lists = 100);

CREATE INDEX
IF NOT EXISTS idx_project_embedding ON project_embeddings USING ivfflat
(embedding vector_cosine_ops)
WITH
(lists = 100);

CREATE INDEX
IF NOT EXISTS idx_regulatory_embedding ON regulatory_embeddings USING ivfflat
(embedding vector_cosine_ops)
WITH
(lists = 100);

-- Create regular indexes for metadata queries
CREATE INDEX
IF NOT EXISTS idx_aneel_docs_type ON aneel_document_embeddings
(document_type);
CREATE INDEX
IF NOT EXISTS idx_aneel_docs_metadata ON aneel_document_embeddings USING gin
(metadata);
CREATE INDEX
IF NOT EXISTS idx_project_ceg ON project_embeddings
(ceg);
CREATE INDEX
IF NOT EXISTS idx_regulatory_type ON regulatory_embeddings
(regulation_type);
CREATE INDEX
IF NOT EXISTS idx_regulatory_applicability ON regulatory_embeddings USING gin
(applicability_rules);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column
()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for app_settings
CREATE TRIGGER update_app_settings_updated_at 
    BEFORE
UPDATE ON app_settings 
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

-- Create triggers for vector tables
CREATE TRIGGER update_aneel_docs_updated_at 
    BEFORE
UPDATE ON aneel_document_embeddings 
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

CREATE TRIGGER update_project_embeddings_updated_at 
    BEFORE
UPDATE ON project_embeddings 
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

CREATE TRIGGER update_regulatory_updated_at 
    BEFORE
UPDATE ON regulatory_embeddings 
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO haas_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO haas_user;

-- Create Huginn database
CREATE DATABASE huginn_production
    WITH 
    OWNER = haas_user
ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Grant permissions on Huginn database
GRANT ALL PRIVILEGES ON DATABASE huginn_production TO haas_user;