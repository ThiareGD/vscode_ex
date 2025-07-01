# Prompt para Implementar RAG con PostgreSQL

## 🎯 Objetivo
Quiero que me ayudes a construir un sistema RAG (Retrieval-Augmented Generation) de alto rendimiento usando únicamente PostgreSQL como base de datos vectorial.

## 📋 Instrucciones Detalladas

### 1. Configuración Inicial
- Configura un entorno PostgreSQL con Docker
- Instala y configura la extensión pgvector
- Crea la estructura de base de datos necesaria para almacenar documentos y sus embeddings

### 2. Preparación de Datos
- Implementa un sistema para dividir documentos largos en chunks manejables
- Cada chunk debe tener un tamaño óptimo (aproximadamente 500-1000 caracteres)
- Mantén metadatos sobre el documento origen de cada chunk

### 3. Generación de Embeddings
- Usa el modelo 'all-MiniLM-L6-v2' de sentence-transformers
- Genera embeddings para cada chunk de documento
- Implementa un sistema de batch processing para documentos grandes

### 4. Almacenamiento en PostgreSQL
```sql
-- Crea una tabla con la siguiente estructura:
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),  -- dimensión depende del modelo
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crea índice para búsqueda vectorial eficiente
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
```

### 5. Sistema de Búsqueda
Implementa una función que:
- Reciba una consulta del usuario
- Convierta la consulta en embedding
- Busque los K documentos más similares usando similitud coseno
- Retorne los documentos con su score de relevancia

### 6. Integración con LLM
- Toma los documentos recuperados como contexto
- Construye un prompt que incluya:
  - El contexto recuperado
  - La pregunta del usuario
  - Instrucciones para generar respuesta basada en el contexto
- Usa un modelo de lenguaje (GPT-2, LLaMA, o similar) para generar la respuesta

### 7. Optimizaciones Requeridas
- Implementa caché de embeddings frecuentes
- Usa connection pooling para PostgreSQL
- Implementa búsqueda asíncrona para múltiples consultas
- Añade logging y métricas de rendimiento

## 💻 Código Base Esperado

```python
class PostgresRAG:
    def __init__(self, db_config, embedding_model, llm_model):
        # Inicializar conexiones y modelos
        pass
    
    def add_documents(self, documents):
        # Procesar y almacenar documentos con embeddings
        pass
    
    def search(self, query, top_k=5):
        # Buscar documentos relevantes
        pass
    
    def generate_response(self, query):
        # Pipeline completo: búsqueda + generación
        pass
```

## 📊 Métricas a Implementar
- Tiempo de respuesta de búsqueda vectorial
- Relevancia de documentos recuperados
- Calidad de respuestas generadas
- Uso de memoria y CPU

## 🔧 Configuración Adicional
- Docker Compose para levantar PostgreSQL + pgvector
- Scripts de inicialización de base de datos
- API REST para exponer el servicio
- Tests unitarios y de integración

## 📝 Entregables Esperados
1. Código Python completo y funcional
2. Scripts SQL para setup de base de datos
3. Dockerfile y docker-compose.yml
4. README con instrucciones de instalación
5. Ejemplos de uso y casos de prueba
6. Benchmarks de rendimiento

## ⚠️ Consideraciones Importantes
- El sistema debe manejar al menos 1 millón de documentos
- Latencia de búsqueda < 100ms
- Soporte para actualización incremental de documentos
- Manejo de errores robusto
- Logs estructurados para debugging

---

**Nota**: Asegúrate de que toda la implementación use SOLO PostgreSQL como base de datos, sin dependencias de bases de datos vectoriales externas como Pinecone, Weaviate, etc.