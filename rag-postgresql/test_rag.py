import pytest
import asyncio
import asyncpg
from postgres_rag import PostgresRAG
import numpy as np
import time

# Test configuration
TEST_DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'raguser',
    'password': 'ragpass',
    'database': 'ragdb'
}

@pytest.fixture
async def rag_system():
    """Create RAG system for testing"""
    rag = PostgresRAG(
        db_config=TEST_DB_CONFIG,
        embedding_model_name='all-MiniLM-L6-v2',
        llm_model_name='gpt2',
        use_cache=True
    )
    await rag.connect()
    yield rag
    await rag.close()

@pytest.fixture
async def clean_database():
    """Clean database before tests"""
    conn = await asyncpg.connect(**TEST_DB_CONFIG)
    await conn.execute("DELETE FROM documents")
    await conn.execute("DELETE FROM embedding_cache")
    await conn.execute("DELETE FROM search_history")
    await conn.close()

@pytest.mark.asyncio
async def test_chunk_text(rag_system):
    """Test text chunking functionality"""
    text = "This is a test. " * 100
    chunks = rag_system.chunk_text(text, chunk_size=100, overlap=20)
    
    assert len(chunks) > 1
    assert all(len(chunk) <= 200 for chunk in chunks)
    
@pytest.mark.asyncio
async def test_embedding_generation(rag_system):
    """Test embedding generation"""
    text = "This is a test document"
    embedding = await rag_system.generate_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == 384  # all-MiniLM-L6-v2 dimension

@pytest.mark.asyncio
async def test_embedding_cache(rag_system, clean_database):
    """Test embedding caching"""
    text = "This text should be cached"
    
    # First call - generate embedding
    start_time = time.time()
    embedding1 = await rag_system.generate_embedding(text)
    first_call_time = time.time() - start_time
    
    # Second call - should be cached
    start_time = time.time()
    embedding2 = await rag_system.generate_embedding(text)
    cached_call_time = time.time() - start_time
    
    assert np.array_equal(embedding1, embedding2)
    assert cached_call_time < first_call_time

@pytest.mark.asyncio
async def test_add_documents(rag_system, clean_database):
    """Test adding documents"""
    documents = [
        {
            'content': 'PostgreSQL is a powerful database system.',
            'metadata': {'category': 'database'}
        },
        {
            'content': 'Python is a versatile programming language.',
            'metadata': {'category': 'programming'}
        }
    ]
    
    chunks_added = await rag_system.add_documents(documents)
    assert chunks_added >= 2

@pytest.mark.asyncio
async def test_search(rag_system, clean_database):
    """Test document search"""
    # Add test documents
    documents = [
        {
            'content': 'PostgreSQL is an advanced open-source relational database.',
            'metadata': {'topic': 'database'}
        },
        {
            'content': 'Machine learning enables computers to learn from data.',
            'metadata': {'topic': 'ai'}
        },
        {
            'content': 'Python is great for data science and web development.',
            'metadata': {'topic': 'programming'}
        }
    ]
    
    await rag_system.add_documents(documents)
    
    # Search for database-related content
    results = await rag_system.search("Tell me about PostgreSQL", top_k=2)
    
    assert len(results) > 0
    assert results[0]['similarity'] > 0.5
    assert 'PostgreSQL' in results[0]['content']

@pytest.mark.asyncio
async def test_metadata_filter(rag_system, clean_database):
    """Test search with metadata filtering"""
    documents = [
        {
            'content': 'Advanced PostgreSQL features.',
            'metadata': {'category': 'database', 'level': 'advanced'}
        },
        {
            'content': 'Basic PostgreSQL tutorial.',
            'metadata': {'category': 'database', 'level': 'beginner'}
        },
        {
            'content': 'Python programming basics.',
            'metadata': {'category': 'programming', 'level': 'beginner'}
        }
    ]
    
    await rag_system.add_documents(documents)
    
    # Search with filter
    results = await rag_system.search(
        "PostgreSQL",
        top_k=5,
        metadata_filter={'level': 'beginner'}
    )
    
    assert len(results) == 1
    assert results[0]['metadata']['level'] == 'beginner'

@pytest.mark.asyncio
async def test_generate_response(rag_system):
    """Test response generation"""
    context = [
        {
            'content': 'PostgreSQL is a powerful, open-source relational database.',
            'metadata': {},
            'similarity': 0.9
        }
    ]
    
    response = rag_system.generate_response(
        "What is PostgreSQL?",
        context,
        max_length=100
    )
    
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_full_query_pipeline(rag_system, clean_database):
    """Test complete RAG pipeline"""
    # Add documents
    documents = [
        {
            'content': 'RAG combines retrieval and generation for better AI responses.',
            'metadata': {'source': 'tutorial'}
        },
        {
            'content': 'PostgreSQL with pgvector enables efficient vector search.',
            'metadata': {'source': 'documentation'}
        }
    ]
    
    await rag_system.add_documents(documents)
    
    # Query the system
    result = await rag_system.query("What is RAG?", top_k=2)
    
    assert 'question' in result
    assert 'answer' in result
    assert 'sources' in result
    assert len(result['sources']) > 0

@pytest.mark.asyncio
async def test_get_stats(rag_system, clean_database):
    """Test statistics retrieval"""
    # Add some data
    await rag_system.add_documents([
        {'content': 'Test document', 'metadata': {}}
    ])
    
    await rag_system.search("test query")
    
    stats = await rag_system.get_stats()
    
    assert 'total_documents' in stats
    assert 'total_searches' in stats
    assert stats['total_documents'] > 0
    assert stats['total_searches'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])