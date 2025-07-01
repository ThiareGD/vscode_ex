# PostgreSQL RAG System

A high-performance Retrieval-Augmented Generation (RAG) system built using only PostgreSQL with pgvector extension.

## Features

- 🚀 High-performance vector search using pgvector
- 📝 Automatic document chunking with overlap
- 🧠 Embedding generation with sentence-transformers
- 💾 Intelligent caching system for embeddings
- 🔍 Metadata filtering for targeted search
- 📊 Built-in analytics and metrics
- 🔌 REST API with FastAPI
- 🐳 Docker support for easy deployment

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│  FastAPI     │────▶│  PostgresRAG    │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │   PostgreSQL    │
                                         │   + pgvector    │
                                         └─────────────────┘
```

## Quick Start

### 1. Clone the repository
```bash
cd rag-postgresql
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start PostgreSQL with Docker
```bash
docker-compose up -d
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the API server
```bash
python api.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Add Documents
```bash
POST /documents
Content-Type: application/json

{
  "documents": [
    {
      "content": "Your document text here",
      "metadata": {
        "source": "web",
        "category": "tutorial"
      }
    }
  ]
}
```

### Search Documents
```bash
POST /search
Content-Type: application/json

{
  "query": "How to use pgvector?",
  "top_k": 5,
  "metadata_filter": {
    "category": "tutorial"
  }
}
```

### Query with Generation
```bash
POST /query
Content-Type: application/json

{
  "question": "What is pgvector?",
  "top_k": 3
}
```

### Get Statistics
```bash
GET /stats
```

### Prometheus Metrics
```bash
GET /metrics
```

## Example Usage

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Add documents
docs = {
    "documents": [
        {
            "content": "PostgreSQL is a powerful database system.",
            "metadata": {"type": "intro"}
        }
    ]
}
response = requests.post(f"{base_url}/documents", json=docs)

# Query the system
query = {
    "question": "Tell me about PostgreSQL",
    "top_k": 3
}
response = requests.post(f"{base_url}/query", json=query)
print(response.json())
```

## Performance Optimization

1. **Embedding Cache**: Frequently used embeddings are cached
2. **Connection Pooling**: Async connection pool for PostgreSQL
3. **Batch Processing**: Documents are processed in batches
4. **Vector Indexing**: IVFFlat index for fast similarity search

## Configuration

### Database Schema
- `documents`: Main table for storing content and embeddings
- `embedding_cache`: Cache table for frequent embeddings
- `search_history`: Analytics for search queries

### Model Selection
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **LLM Model**: `gpt2` (can be replaced with any Hugging Face model)

## Testing

Run the test example:
```bash
curl -X POST http://localhost:8000/example
```

## Monitoring

- Prometheus metrics available at `/metrics`
- Database statistics at `/stats`
- Health check at `/health`

## Requirements

- PostgreSQL 15+ with pgvector extension
- Python 3.8+
- 4GB+ RAM recommended
- GPU optional (for faster embedding generation)

## License

MIT License