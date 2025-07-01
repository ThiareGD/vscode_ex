-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384), -- Dimension for all-MiniLM-L6-v2
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient search
CREATE INDEX idx_documents_embedding ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index on metadata for filtering
CREATE INDEX idx_documents_metadata ON documents USING GIN (metadata);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE
    ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create search history table for analytics
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    query_embedding vector(384),
    results_count INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create cache table for frequent queries
CREATE TABLE IF NOT EXISTS embedding_cache (
    id SERIAL PRIMARY KEY,
    text_hash VARCHAR(64) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    hit_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_hash ON embedding_cache(text_hash);
CREATE INDEX idx_cache_accessed ON embedding_cache(last_accessed);