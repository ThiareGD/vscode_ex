from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import asyncio
import os
from datetime import datetime
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

from postgres_rag import PostgresRAG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
query_counter = Counter('rag_queries_total', 'Total number of RAG queries')
query_duration = Histogram('rag_query_duration_seconds', 'RAG query duration')
document_counter = Counter('rag_documents_added_total', 'Total documents added')

# Initialize FastAPI app
app = FastAPI(
    title="PostgreSQL RAG API",
    description="High-performance RAG system using PostgreSQL with pgvector",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG instance
rag_system = None

# Pydantic models
class Document(BaseModel):
    content: str = Field(..., description="Document content")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")
    id: Optional[str] = Field(None, description="Document ID")

class DocumentBatch(BaseModel):
    documents: List[Document] = Field(..., description="List of documents to add")

class Query(BaseModel):
    question: str = Field(..., description="Question to ask")
    top_k: int = Field(5, description="Number of documents to retrieve")
    metadata_filter: Optional[Dict] = Field(None, description="Metadata filter for search")

class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results to return")
    metadata_filter: Optional[Dict] = Field(None, description="Metadata filter")

# API endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'user': os.getenv('DB_USER', 'raguser'),
        'password': os.getenv('DB_PASSWORD', 'ragpass'),
        'database': os.getenv('DB_NAME', 'ragdb')
    }
    
    rag_system = PostgresRAG(
        db_config=db_config,
        embedding_model_name=os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
        llm_model_name=os.getenv('LLM_MODEL', 'gpt2'),
        use_cache=True
    )
    
    await rag_system.connect()
    logger.info("RAG system initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if rag_system:
        await rag_system.close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PostgreSQL RAG API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = await rag_system.get_stats()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/documents")
async def add_documents(
    batch: DocumentBatch,
    background_tasks: BackgroundTasks
):
    """Add documents to the RAG system"""
    try:
        document_counter.inc(len(batch.documents))
        
        # Convert to format expected by RAG system
        docs = [doc.dict() for doc in batch.documents]
        
        # Add documents
        chunks_added = await rag_system.add_documents(docs)
        
        return {
            "status": "success",
            "documents_processed": len(batch.documents),
            "chunks_created": chunks_added,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documents(search: SearchQuery):
    """Search for similar documents"""
    try:
        results = await rag_system.search(
            query=search.query,
            top_k=search.top_k,
            metadata_filter=search.metadata_filter
        )
        
        return {
            "query": search.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_rag(query: Query):
    """Query the RAG system and get generated response"""
    try:
        query_counter.inc()
        
        with query_duration.time():
            result = await rag_system.query(
                question=query.question,
                top_k=query.top_k,
                metadata_filter=query.metadata_filter
            )
        
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics():
    """Get system statistics"""
    try:
        stats = await rag_system.get_stats()
        return {
            "database_stats": stats,
            "api_stats": {
                "total_queries": query_counter._value.get(),
                "total_documents_added": document_counter._value.get()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Example usage endpoint
@app.post("/example")
async def example_usage():
    """Example of how to use the RAG system"""
    # Add sample documents
    sample_docs = [
        {
            "content": "PostgreSQL is a powerful, open source object-relational database system. It has more than 35 years of active development and a proven architecture.",
            "metadata": {"category": "database", "source": "documentation"}
        },
        {
            "content": "pgvector is an open-source vector similarity search extension for PostgreSQL. It supports exact and approximate nearest neighbor search.",
            "metadata": {"category": "extension", "source": "github"}
        },
        {
            "content": "RAG (Retrieval-Augmented Generation) combines information retrieval with text generation to provide more accurate and contextual responses.",
            "metadata": {"category": "ai", "source": "research"}
        }
    ]
    
    # Add documents
    batch = DocumentBatch(documents=[Document(**doc) for doc in sample_docs])
    await add_documents(batch, BackgroundTasks())
    
    # Query the system
    result = await query_rag(Query(
        question="What is pgvector and how does it relate to PostgreSQL?",
        top_k=3
    ))
    
    return {
        "message": "Example completed successfully",
        "sample_result": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)