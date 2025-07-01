import asyncio
import time
import random
import string
from postgres_rag import PostgresRAG
import matplotlib.pyplot as plt
import numpy as np

class RAGBenchmark:
    """Benchmark the RAG system performance"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.results = {
            'embedding_times': [],
            'search_times': [],
            'generation_times': [],
            'documents_count': [],
            'cache_hit_rates': []
        }
    
    def generate_random_document(self, length=500):
        """Generate random document for testing"""
        words = ['database', 'PostgreSQL', 'vector', 'search', 'embedding', 
                'machine', 'learning', 'data', 'science', 'algorithm',
                'performance', 'optimization', 'query', 'index', 'storage']
        
        doc_words = []
        for _ in range(length // 10):
            doc_words.append(random.choice(words))
        
        return ' '.join(doc_words)
    
    async def run_benchmarks(self):
        """Run complete benchmark suite"""
        rag = PostgresRAG(self.db_config)
        await rag.connect()
        
        print("Starting RAG System Benchmarks...")
        print("=" * 50)
        
        # Test 1: Document insertion performance
        await self.benchmark_document_insertion(rag)
        
        # Test 2: Search performance with varying document counts
        await self.benchmark_search_scaling(rag)
        
        # Test 3: Cache effectiveness
        await self.benchmark_cache_performance(rag)
        
        # Test 4: Concurrent query handling
        await self.benchmark_concurrent_queries(rag)
        
        await rag.close()
        
        # Generate report
        self.generate_report()
    
    async def benchmark_document_insertion(self, rag):
        """Benchmark document insertion speed"""
        print("\n1. Document Insertion Benchmark")
        print("-" * 30)
        
        batch_sizes = [10, 50, 100, 500]
        
        for batch_size in batch_sizes:
            documents = [
                {
                    'content': self.generate_random_document(),
                    'metadata': {'batch': batch_size, 'test': 'insertion'}
                }
                for _ in range(batch_size)
            ]
            
            start_time = time.time()
            chunks = await rag.add_documents(documents)
            elapsed = time.time() - start_time
            
            docs_per_second = batch_size / elapsed
            print(f"Batch size: {batch_size}, Time: {elapsed:.2f}s, Docs/sec: {docs_per_second:.2f}")
    
    async def benchmark_search_scaling(self, rag):
        """Benchmark search performance with increasing documents"""
        print("\n2. Search Scaling Benchmark")
        print("-" * 30)
        
        # Add documents progressively
        doc_counts = [100, 500, 1000, 5000]
        queries = ["database performance", "vector search", "machine learning"]
        
        for count in doc_counts:
            # Add more documents
            new_docs = [
                {
                    'content': self.generate_random_document(),
                    'metadata': {'test': 'scaling', 'count': count}
                }
                for _ in range(count - len(self.results['documents_count']) * 100 if self.results['documents_count'] else count)
            ]
            
            if new_docs:
                await rag.add_documents(new_docs)
            
            # Run search benchmarks
            search_times = []
            for query in queries:
                start_time = time.time()
                results = await rag.search(query, top_k=10)
                search_times.append(time.time() - start_time)
            
            avg_search_time = np.mean(search_times)
            self.results['documents_count'].append(count)
            self.results['search_times'].append(avg_search_time)
            
            print(f"Documents: {count}, Avg search time: {avg_search_time*1000:.2f}ms")
    
    async def benchmark_cache_performance(self, rag):
        """Benchmark embedding cache effectiveness"""
        print("\n3. Cache Performance Benchmark")
        print("-" * 30)
        
        test_texts = [self.generate_random_document() for _ in range(20)]
        
        # First pass - no cache
        no_cache_times = []
        for text in test_texts:
            start_time = time.time()
            await rag.generate_embedding(text)
            no_cache_times.append(time.time() - start_time)
        
        # Second pass - with cache
        cache_times = []
        for text in test_texts:
            start_time = time.time()
            await rag.generate_embedding(text)
            cache_times.append(time.time() - start_time)
        
        avg_no_cache = np.mean(no_cache_times)
        avg_cache = np.mean(cache_times)
        speedup = avg_no_cache / avg_cache
        
        print(f"No cache avg: {avg_no_cache*1000:.2f}ms")
        print(f"With cache avg: {avg_cache*1000:.2f}ms")
        print(f"Cache speedup: {speedup:.2f}x")
    
    async def benchmark_concurrent_queries(self, rag):
        """Benchmark concurrent query handling"""
        print("\n4. Concurrent Query Benchmark")
        print("-" * 30)
        
        queries = [
            "What is PostgreSQL?",
            "How does vector search work?",
            "Explain machine learning",
            "Database optimization techniques",
            "RAG system architecture"
        ]
        
        concurrent_counts = [1, 5, 10, 20]
        
        for count in concurrent_counts:
            tasks = []
            start_time = time.time()
            
            for _ in range(count):
                query = random.choice(queries)
                tasks.append(rag.query(query, top_k=3))
            
            await asyncio.gather(*tasks)
            elapsed = time.time() - start_time
            qps = count / elapsed
            
            print(f"Concurrent queries: {count}, Time: {elapsed:.2f}s, QPS: {qps:.2f}")
    
    def generate_report(self):
        """Generate benchmark report with visualizations"""
        print("\n" + "=" * 50)
        print("Benchmark Complete!")
        
        # Create plots if we have data
        if self.results['documents_count'] and self.results['search_times']:
            plt.figure(figsize=(10, 6))
            plt.plot(self.results['documents_count'], 
                    [t*1000 for t in self.results['search_times']], 
                    'b-o')
            plt.xlabel('Number of Documents')
            plt.ylabel('Search Time (ms)')
            plt.title('Search Performance vs Document Count')
            plt.grid(True)
            plt.savefig('search_scaling.png')
            print("Saved search scaling plot to search_scaling.png")

async def main():
    """Run benchmarks"""
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'raguser',
        'password': 'ragpass',
        'database': 'ragdb'
    }
    
    benchmark = RAGBenchmark(db_config)
    await benchmark.run_benchmarks()

if __name__ == "__main__":
    asyncio.run(main())