import asyncio
import hashlib
import json
import time
from typing import List, Dict, Optional, Tuple
import asyncpg
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresRAG:
    """High-performance RAG implementation using PostgreSQL with pgvector"""
    
    def __init__(
        self,
        db_config: Dict[str, str],
        embedding_model_name: str = "all-MiniLM-L6-v2",
        llm_model_name: str = "gpt2",
        use_cache: bool = True
    ):
        self.db_config = db_config
        self.use_cache = use_cache
        self.pool = None
        
        # Initialize models
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        logger.info(f"Loading LLM model: {llm_model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
        self.llm_model = AutoModelForCausalLM.from_pretrained(llm_model_name)
        
        # Set padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    async def connect(self):
        """Create connection pool to PostgreSQL"""
        self.pool = await asyncpg.create_pool(
            host=self.db_config.get('host', 'localhost'),
            port=self.db_config.get('port', 5432),
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            min_size=10,
            max_size=20
        )
        logger.info("Connected to PostgreSQL")
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to end at a sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.8:
                    chunk = text[start:start + last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    async def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from cache if available"""
        if not self.use_cache:
            return None
        
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                UPDATE embedding_cache 
                SET hit_count = hit_count + 1, 
                    last_accessed = CURRENT_TIMESTAMP
                WHERE text_hash = $1
                RETURNING embedding
                """,
                text_hash
            )
            
            if result:
                return np.array(result['embedding'])
        
        return None
    
    async def _cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache embedding for future use"""
        if not self.use_cache:
            return
        
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO embedding_cache (text_hash, text, embedding)
                VALUES ($1, $2, $3)
                ON CONFLICT (text_hash) DO UPDATE
                SET hit_count = embedding_cache.hit_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                """,
                text_hash, text, embedding.tolist()
            )
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding with caching"""
        # Check cache first
        cached = await self._get_cached_embedding(text)
        if cached is not None:
            return cached
        
        # Generate new embedding
        embedding = self.embedding_model.encode(text)
        
        # Cache it
        await self._cache_embedding(text, embedding)
        
        return embedding
    
    async def add_documents(
        self, 
        documents: List[Dict[str, any]], 
        batch_size: int = 100
    ) -> int:
        """Add documents to the database with embeddings"""
        total_chunks = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            chunks_data = []
            
            for doc in batch:
                text = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Chunk the document
                chunks = self.chunk_text(text)
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = await self.generate_embedding(chunk)
                    
                    chunk_metadata = {
                        **metadata,
                        'chunk_index': chunk_idx,
                        'total_chunks': len(chunks),
                        'source_doc_id': doc.get('id', 'unknown')
                    }
                    
                    chunks_data.append((chunk, embedding.tolist(), json.dumps(chunk_metadata)))
            
            # Batch insert
            async with self.pool.acquire() as conn:
                await conn.executemany(
                    """
                    INSERT INTO documents (content, embedding, metadata)
                    VALUES ($1, $2, $3)
                    """,
                    chunks_data
                )
            
            total_chunks += len(chunks_data)
            logger.info(f"Added {len(chunks_data)} chunks from batch {i//batch_size + 1}")
        
        return total_chunks
    
    async def search(
        self, 
        query: str, 
        top_k: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents"""
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        # Build query with optional metadata filter
        sql_query = """
            SELECT 
                id,
                content,
                metadata,
                1 - (embedding <=> $1::vector) as similarity
            FROM documents
        """
        
        params = [query_embedding.tolist()]
        
        if metadata_filter:
            sql_query += " WHERE metadata @> $2::jsonb"
            params.append(json.dumps(metadata_filter))
        
        sql_query += """
            ORDER BY embedding <=> $1::vector
            LIMIT $%d
        """ % (len(params) + 1)
        
        params.append(top_k)
        
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql_query, *params)
        
        # Log search metrics
        search_time = int((time.time() - start_time) * 1000)
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO search_history (query, query_embedding, results_count, response_time_ms)
                VALUES ($1, $2, $3, $4)
                """,
                query, query_embedding.tolist(), len(results), search_time
            )
        
        return [
            {
                'id': r['id'],
                'content': r['content'],
                'metadata': json.loads(r['metadata']),
                'similarity': float(r['similarity'])
            }
            for r in results
        ]
    
    def generate_response(
        self, 
        query: str, 
        context: List[Dict],
        max_length: int = 200
    ) -> str:
        """Generate response using LLM with retrieved context"""
        # Combine context
        context_text = "\n\n".join([
            f"[Document {i+1}]: {doc['content']}"
            for i, doc in enumerate(context)
        ])
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question accurately and concisely.

Context:
{context_text}

Question: {query}

Answer:"""
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        with torch.no_grad():
            outputs = self.llm_model.generate(
                inputs.input_ids,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                pad_token_id=self.tokenizer.pad_token_id,
                do_sample=True
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the answer part
        answer_start = response.find("Answer:") + len("Answer:")
        if answer_start > len("Answer:") - 1:
            response = response[answer_start:].strip()
        
        return response
    
    async def query(
        self, 
        question: str, 
        top_k: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> Dict:
        """Complete RAG pipeline: search + generate"""
        # Search for relevant documents
        search_results = await self.search(question, top_k, metadata_filter)
        
        # Generate response
        response = self.generate_response(question, search_results)
        
        return {
            'question': question,
            'answer': response,
            'sources': search_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_stats(self) -> Dict:
        """Get system statistics"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM documents) as total_documents,
                    (SELECT COUNT(*) FROM search_history) as total_searches,
                    (SELECT AVG(response_time_ms) FROM search_history) as avg_response_time_ms,
                    (SELECT COUNT(*) FROM embedding_cache) as cached_embeddings
            """)
        
        return dict(stats)