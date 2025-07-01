# Tutorial Detallado: Cómo Funcionan Docker, PostgreSQL y Búsqueda Vectorial

## 📚 Tabla de Contenidos
1. [¿Qué es Docker y cómo funciona?](#docker)
2. [¿Qué es Docker Compose?](#docker-compose)
3. [PostgreSQL y pgvector explicados](#postgresql-pgvector)
4. [¿Qué son los vectores y embeddings?](#vectores-embeddings)
5. [Búsqueda vectorial: conceptos y funcionamiento](#busqueda-vectorial)
6. [Explicación línea por línea](#linea-por-linea)

---

## 🐳 1. ¿Qué es Docker y cómo funciona? <a id="docker"></a>

### Conceptos Fundamentales

**Docker** es una plataforma de containerización que permite empaquetar aplicaciones y sus dependencias en contenedores portables.

### ¿Qué problema resuelve Docker?

Imagina que tienes una aplicación que funciona perfectamente en tu computadora, pero cuando la llevas a otro servidor, no funciona. Docker resuelve el problema de "en mi máquina sí funciona".

### Componentes principales:

```
┌─────────────────────────────────────────────┐
│              Tu Sistema Operativo           │
├─────────────────────────────────────────────┤
│                 Docker Engine               │
├─────────────┬─────────────┬────────────────┤
│ Contenedor 1│ Contenedor 2│ Contenedor 3   │
│ PostgreSQL  │ Node.js App │ Redis Cache    │
│ + pgvector  │             │                │
└─────────────┴─────────────┴────────────────┘
```

### ¿Cómo funciona internamente?

1. **Namespaces**: Aíslan los procesos
   ```bash
   # Cada contenedor tiene su propio:
   - PID namespace (procesos)
   - Network namespace (red)
   - Mount namespace (sistema de archivos)
   ```

2. **Cgroups**: Limitan recursos
   ```bash
   # Controlan:
   - CPU usage
   - Memory
   - Disk I/O
   ```

3. **Union File System**: Capas de archivos
   ```
   Capa 4: Tu aplicación
   Capa 3: Dependencias Python
   Capa 2: PostgreSQL
   Capa 1: Sistema base Linux
   ```

### Comandos Docker explicados:

```bash
# sudo docker pull imagen:tag
# ¿Qué hace? Descarga una imagen del Docker Hub
# Proceso interno:
# 1. Contacta registry.docker.com
# 2. Busca la imagen 'pgvector/pgvector:pg17'
# 3. Descarga cada capa de la imagen
# 4. Las almacena en /var/lib/docker/

sudo docker pull pgvector/pgvector:pg17

# sudo docker run [opciones] imagen
# ¿Qué hace? Crea y ejecuta un contenedor
# Proceso interno:
# 1. Crea un nuevo namespace
# 2. Configura cgroups para recursos
# 3. Monta el filesystem de la imagen
# 4. Ejecuta el proceso principal

sudo docker run -d \
  --name postgres_vectorial \     # Nombre del contenedor
  -e POSTGRES_PASSWORD=secreto \  # Variable de entorno
  -p 5432:5432 \                 # Mapeo de puertos host:contenedor
  -v ./data:/var/lib/postgresql/data \ # Volumen para persistencia
  pgvector/pgvector:pg17
```

---

## 🎼 2. ¿Qué es Docker Compose? <a id="docker-compose"></a>

Docker Compose es una herramienta para definir y ejecutar aplicaciones multi-contenedor.

### ¿Por qué Docker Compose?

En lugar de ejecutar múltiples comandos `docker run`, defines todo en un archivo YAML:

```yaml
version: '3.8'  # Versión de la especificación de Compose

services:       # Define los contenedores
  postgres:     # Nombre del servicio
    image: pgvector/pgvector:pg17
```

### Explicación detallada del docker-compose.yml:

```yaml
version: '3.8'
# ¿Qué hace? Define qué versión de la sintaxis de Compose usar
# Cada versión soporta diferentes características

services:
  postgres:
    # IMAGEN BASE
    image: pgvector/pgvector:pg17
    # ¿Qué hace? Especifica qué imagen usar
    # pgvector/pgvector: repositorio en Docker Hub
    # :pg17: tag específico (PostgreSQL 17)
    
    # NOMBRE DEL CONTENEDOR
    container_name: postgres_vectorial
    # ¿Por qué? Sin esto, Docker genera nombres aleatorios
    # como "project_postgres_1"
    
    # POLÍTICA DE REINICIO
    restart: always
    # Opciones:
    # - no: nunca reiniciar
    # - on-failure: solo si falla
    # - always: siempre reiniciar
    # - unless-stopped: reiniciar excepto si se detiene manualmente
    
    # VARIABLES DE ENTORNO
    environment:
      POSTGRES_USER: usuario_vector
      POSTGRES_PASSWORD: contraseña_segura
      POSTGRES_DB: base_vectorial
    # ¿Qué hacen? PostgreSQL las lee al iniciar:
    # 1. Crea usuario 'usuario_vector'
    # 2. Asigna la contraseña
    # 3. Crea base de datos 'base_vectorial'
    
    # MAPEO DE PUERTOS
    ports:
      - "5432:5432"
    # Formato: "puerto_host:puerto_contenedor"
    # ¿Qué hace? Expone el puerto 5432 del contenedor
    # en el puerto 5432 de tu máquina
    
    # VOLÚMENES
    volumes:
      - ./data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/01-init.sql
    # ¿Qué hacen?
    # 1. ./data se mapea a donde PostgreSQL guarda datos
    #    Esto hace que los datos persistan
    # 2. Scripts en /docker-entrypoint-initdb.d/ se ejecutan
    #    automáticamente al crear la base de datos
    
    # HEALTHCHECK
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U usuario_vector -d base_vectorial"]
      interval: 10s
      timeout: 5s
      retries: 5
    # ¿Qué hace? Verifica que PostgreSQL esté funcionando
    # - test: comando para verificar salud
    # - interval: cada cuánto verificar
    # - timeout: cuánto esperar respuesta
    # - retries: intentos antes de marcar como unhealthy
```

### ¿Qué pasa cuando ejecutas docker-compose up?

```bash
sudo docker-compose up -d
# Proceso paso a paso:

# 1. Lee docker-compose.yml
# 2. Crea una red bridge para los servicios
# 3. Para cada servicio:
#    a. Descarga imagen si no existe
#    b. Crea contenedor con configuración
#    c. Conecta a la red
#    d. Monta volúmenes
#    e. Aplica variables de entorno
#    f. Inicia el contenedor
# 4. El flag -d lo ejecuta en background
```

---

## 🐘 3. PostgreSQL y pgvector explicados <a id="postgresql-pgvector"></a>

### ¿Qué es PostgreSQL?

PostgreSQL es un sistema de gestión de bases de datos relacional y objeto-relacional (ORDBMS).

### Arquitectura de PostgreSQL:

```
┌─────────────────────────────────────┐
│         Aplicación Cliente          │
└────────────────┬────────────────────┘
                 │ SQL
┌────────────────┴────────────────────┐
│          Postmaster Process         │ ← Proceso principal
├─────────────────────────────────────┤
│         Backend Processes           │ ← Un proceso por conexión
├─────────────────────────────────────┤
│         Shared Memory               │
│  ┌─────────┐ ┌─────────┐ ┌───────┐│
│  │ Buffer  │ │  WAL    │ │ Lock  ││
│  │  Cache  │ │ Buffer  │ │ Table ││
│  └─────────┘ └─────────┘ └───────┘│
├─────────────────────────────────────┤
│          Disk Storage               │
│  ┌─────────┐ ┌─────────┐ ┌───────┐│
│  │  Data   │ │  WAL    │ │Config ││
│  │  Files  │ │  Logs   │ │ Files ││
│  └─────────┘ └─────────┘ └───────┘│
└─────────────────────────────────────┘
```

### ¿Qué es pgvector?

pgvector es una extensión que añade el tipo de dato `vector` a PostgreSQL y operaciones de similitud.

### ¿Cómo funciona pgvector internamente?

```sql
-- Cuando creas una columna vector:
CREATE TABLE productos (
    embedding vector(384)
);

-- pgvector:
-- 1. Registra un nuevo tipo de dato 'vector'
-- 2. Implementa operadores de distancia:
--    - <-> : Distancia euclidiana
--    - <=> : Distancia coseno
--    - <#> : Producto interno negativo
-- 3. Añade funciones de indexación especializadas
```

### Índices en pgvector:

```sql
-- IVFFlat (Inverted File Flat)
CREATE INDEX ON productos 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ¿Qué hace lists = 100?
-- Divide el espacio vectorial en 100 clusters
-- Proceso de búsqueda:
-- 1. Encuentra clusters más cercanos a la consulta
-- 2. Busca solo dentro de esos clusters
-- 3. Más lists = más precisión pero más lento
```

---

## 📊 4. ¿Qué son los vectores y embeddings? <a id="vectores-embeddings"></a>

### Conceptos Fundamentales

Un **vector** es una representación numérica multidimensional. Un **embedding** es un vector que representa el significado semántico de algo (texto, imagen, etc.).

### Ejemplo visual:

```
Texto: "laptop gaming"
         ↓
   Modelo de IA
         ↓
Vector: [0.23, -0.45, 0.67, ..., 0.12]  (384 números)

¿Por qué 384 dimensiones?
- Cada dimensión captura una característica
- Dimensión 1: podría representar "tecnología"
- Dimensión 2: podría representar "entretenimiento"
- ... y así sucesivamente
```

### ¿Cómo se generan los embeddings?

```python
# Proceso simplificado:
texto = "laptop gaming"

# 1. Tokenización
tokens = ["laptop", "gaming"]

# 2. Conversión a números
token_ids = [15496, 8723]  # IDs del vocabulario

# 3. Pasar por red neuronal
# La red neuronal (como BERT) procesa los tokens
# y produce un vector de 384 dimensiones

# 4. Resultado
embedding = [0.23, -0.45, 0.67, ..., 0.12]
```

### Propiedades importantes:

```
Textos similares → Vectores cercanos

"laptop gaming" → [0.23, -0.45, 0.67, ...]
"notebook gamer" → [0.25, -0.43, 0.65, ...]
"cafetera" → [0.89, 0.12, -0.34, ...]

La distancia entre los primeros dos es pequeña
La distancia con "cafetera" es grande
```

---

## 🔍 5. Búsqueda vectorial: conceptos y funcionamiento <a id="busqueda-vectorial"></a>

### ¿Qué es la búsqueda vectorial?

Es encontrar los vectores más similares a un vector de consulta.

### Métricas de distancia:

```python
# 1. Distancia Euclidiana (L2)
# Como medir la distancia en línea recta
distancia = sqrt(sum((a[i] - b[i])^2 for i in range(len(a))))

# 2. Similitud Coseno
# Mide el ángulo entre vectores
# 1 = idénticos, 0 = perpendiculares, -1 = opuestos
similitud = dot_product(a, b) / (norm(a) * norm(b))

# 3. Producto Interno
# Útil cuando los vectores están normalizados
producto = sum(a[i] * b[i] for i in range(len(a)))
```

### Proceso de búsqueda paso a paso:

```sql
-- Consulta: "computadora para juegos"
-- 1. Generar embedding de la consulta
consulta_embedding = [0.24, -0.44, 0.66, ...]

-- 2. PostgreSQL ejecuta:
SELECT * FROM productos
ORDER BY embedding <=> consulta_embedding
LIMIT 5;

-- 3. Proceso interno:
-- Para cada producto:
--   a. Calcula distancia coseno
--   b. Ordena por distancia
--   c. Retorna los 5 más cercanos
```

### Optimización con índices IVFFlat:

```
Sin índice: O(n) - busca en todos los productos
Con índice: O(√n) - busca solo en clusters relevantes

Ejemplo con 1 millón de productos:
- Sin índice: 1,000,000 comparaciones
- Con índice (100 lists): ~10,000 comparaciones
```

---

## 📝 6. Explicación línea por línea <a id="linea-por-linea"></a>

### Script SQL detallado:

```sql
-- CREAR EXTENSIÓN
CREATE EXTENSION IF NOT EXISTS vector;
-- ¿Qué hace?
-- 1. Verifica si pgvector está instalado
-- 2. Si no existe, lo activa
-- 3. Registra nuevos tipos de datos y operadores

-- CREAR TABLA
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    -- SERIAL: 
    -- - Crea una secuencia automática
    -- - Incrementa en 1 cada vez
    -- PRIMARY KEY:
    -- - Garantiza unicidad
    -- - Crea índice automático
    
    embedding vector(384)
    -- vector(384):
    -- - Tipo de dato de pgvector
    -- - Array de 384 floats
    -- - Ocupa 384 * 4 bytes = 1,536 bytes por registro
);

-- CREAR ÍNDICE IVFFLAT
CREATE INDEX idx_productos_embedding ON productos 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
-- Proceso de creación:
-- 1. Escanea todos los embeddings existentes
-- 2. Usa k-means para crear 100 centroides
-- 3. Asigna cada vector al centroide más cercano
-- 4. Guarda la estructura en disco

-- FUNCIÓN DE BÚSQUEDA
CREATE OR REPLACE FUNCTION buscar_productos_similares(
    consulta_embedding vector(384),
    limite INTEGER DEFAULT 5
)
RETURNS TABLE (...) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.nombre,
        1 - (p.embedding <=> consulta_embedding) AS similitud
        -- ¿Por qué "1 -"?
        -- <=> retorna distancia coseno (0 a 2)
        -- 0 = idénticos
        -- 2 = opuestos
        -- Convertimos a similitud (1 a -1)
    FROM productos p
    WHERE p.embedding IS NOT NULL
    ORDER BY p.embedding <=> consulta_embedding
    -- ORDER BY usa el índice automáticamente
    LIMIT limite;
END;
$$ LANGUAGE plpgsql;
-- plpgsql: Lenguaje procedural de PostgreSQL
-- Permite loops, condiciones, variables
```

### Proceso completo de una búsqueda:

```python
# 1. Usuario busca: "laptop para gaming"

# 2. Python genera embedding
embedding = modelo.encode("laptop para gaming")
# → [0.24, -0.44, 0.66, ..., 0.15]

# 3. Envía consulta a PostgreSQL
cursor.execute("""
    SELECT * FROM buscar_productos_similares(%s, 5)
""", (embedding.tolist(),))

# 4. PostgreSQL:
#    a. Recibe el vector
#    b. Usa el índice IVFFlat:
#       - Calcula distancia a 100 centroides
#       - Selecciona los 10 más cercanos
#       - Busca solo en esos clusters
#    c. Calcula distancia exacta
#    d. Ordena y retorna top 5

# 5. Python recibe resultados y los muestra
```

### ¿Por qué es rápido?

```
Búsqueda tradicional SQL:
SELECT * FROM productos WHERE descripcion LIKE '%gaming%'
- Busca coincidencia exacta de texto
- No entiende sinónimos
- O(n) complejidad

Búsqueda vectorial:
SELECT * FROM productos ORDER BY embedding <=> query
- Busca por significado
- Encuentra "computadora gamer" cuando buscas "laptop gaming"
- O(√n) con índice
```

## 🎯 Conclusión

Este sistema combina:
- **Docker**: Para portabilidad y aislamiento
- **PostgreSQL**: Para almacenamiento confiable
- **pgvector**: Para capacidades de búsqueda vectorial
- **Embeddings**: Para representar significado semántico

El resultado es un sistema que puede encontrar productos similares basándose en el significado, no solo en coincidencias exactas de texto.