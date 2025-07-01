# Tutorial: Docker + PostgreSQL 17 + pgvector para Búsqueda Vectorial

## 📋 Requisitos Previos

- Docker instalado en tu sistema
- Docker Compose instalado
- Permisos sudo para ejecutar comandos Docker

## 🚀 Paso 1: Crear la Estructura del Proyecto

```bash
# Crear directorio del proyecto
mkdir tutorial-pgvector
cd tutorial-pgvector

# Crear estructura de carpetas
mkdir scripts
mkdir data
```

## 📝 Paso 2: Crear docker-compose.yml

Crea un archivo `docker-compose.yml` con el siguiente contenido:

```yaml
version: '3.8'

services:
  postgres:
    # Imagen oficial de PostgreSQL 17 con pgvector
    image: pgvector/pgvector:pg17
    container_name: postgres_vectorial
    restart: always
    environment:
      # Variables de entorno para PostgreSQL
      POSTGRES_USER: usuario_vector
      POSTGRES_PASSWORD: contraseña_segura
      POSTGRES_DB: base_vectorial
      # Configuración adicional
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=es_ES.UTF-8"
    ports:
      # Puerto expuesto: host:container
      - "5432:5432"
    volumes:
      # Persistencia de datos
      - ./data:/var/lib/postgresql/data
      # Scripts de inicialización
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./scripts/datos_ejemplo.sql:/docker-entrypoint-initdb.d/02-datos.sql
    healthcheck:
      # Verificación de salud del contenedor
      test: ["CMD-SHELL", "pg_isready -U usuario_vector -d base_vectorial"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Servicio adicional para administración (opcional)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin_vectorial
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@ejemplo.com
      PGADMIN_DEFAULT_PASSWORD: admin123
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - "8080:80"
    depends_on:
      - postgres
```

## 🗄️ Paso 3: Crear Script de Inicialización

Crea el archivo `scripts/init.sql`:

```sql
-- Habilitar la extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Crear tabla de productos con embeddings
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(100),
    precio DECIMAL(10, 2),
    embedding vector(384), -- Vector de 384 dimensiones
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice para búsqueda vectorial eficiente
CREATE INDEX idx_productos_embedding ON productos 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Tabla para almacenar búsquedas (analytics)
CREATE TABLE IF NOT EXISTS historial_busquedas (
    id SERIAL PRIMARY KEY,
    consulta TEXT NOT NULL,
    embedding_consulta vector(384),
    resultados_encontrados INTEGER,
    fecha_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Función para buscar productos similares
CREATE OR REPLACE FUNCTION buscar_productos_similares(
    consulta_embedding vector(384),
    limite INTEGER DEFAULT 5
)
RETURNS TABLE (
    id INTEGER,
    nombre VARCHAR,
    descripcion TEXT,
    categoria VARCHAR,
    precio DECIMAL,
    similitud FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.nombre,
        p.descripcion,
        p.categoria,
        p.precio,
        1 - (p.embedding <=> consulta_embedding) AS similitud
    FROM productos p
    WHERE p.embedding IS NOT NULL
    ORDER BY p.embedding <=> consulta_embedding
    LIMIT limite;
END;
$$ LANGUAGE plpgsql;

-- Vista para estadísticas
CREATE VIEW estadisticas_productos AS
SELECT 
    categoria,
    COUNT(*) as total_productos,
    AVG(precio) as precio_promedio,
    MIN(precio) as precio_minimo,
    MAX(precio) as precio_maximo
FROM productos
GROUP BY categoria;
```

## 📊 Paso 4: Crear Datos de Ejemplo

Crea el archivo `scripts/datos_ejemplo.sql`:

```sql
-- Insertar productos de ejemplo con embeddings simulados
-- Nota: En producción, estos embeddings serían generados por un modelo ML

-- Función auxiliar para generar embeddings aleatorios (solo para demostración)
CREATE OR REPLACE FUNCTION generar_embedding_aleatorio()
RETURNS vector(384) AS $$
DECLARE
    embedding FLOAT[];
    i INTEGER;
BEGIN
    embedding := ARRAY[]::FLOAT[];
    FOR i IN 1..384 LOOP
        embedding := array_append(embedding, random()::FLOAT);
    END LOOP;
    RETURN embedding::vector(384);
END;
$$ LANGUAGE plpgsql;

-- Insertar productos de electrónica
INSERT INTO productos (nombre, descripcion, categoria, precio, embedding) VALUES
('Laptop Gaming Pro', 'Laptop de alta gama con RTX 4090 y procesador Intel i9', 'Electrónica', 2499.99, generar_embedding_aleatorio()),
('Mouse Inalámbrico', 'Mouse ergonómico con sensor de alta precisión', 'Electrónica', 49.99, generar_embedding_aleatorio()),
('Teclado Mecánico RGB', 'Teclado mecánico con switches Cherry MX', 'Electrónica', 129.99, generar_embedding_aleatorio()),
('Monitor 4K 32"', 'Monitor IPS con resolución 4K y 144Hz', 'Electrónica', 599.99, generar_embedding_aleatorio()),
('Auriculares Bluetooth', 'Auriculares con cancelación de ruido activa', 'Electrónica', 199.99, generar_embedding_aleatorio());

-- Insertar productos de ropa
INSERT INTO productos (nombre, descripcion, categoria, precio, embedding) VALUES
('Camiseta Deportiva', 'Camiseta transpirable para running', 'Ropa', 29.99, generar_embedding_aleatorio()),
('Jeans Clásicos', 'Jeans de corte recto color azul', 'Ropa', 59.99, generar_embedding_aleatorio()),
('Zapatillas Running', 'Zapatillas ligeras con amortiguación', 'Ropa', 89.99, generar_embedding_aleatorio()),
('Chaqueta Impermeable', 'Chaqueta resistente al agua para outdoor', 'Ropa', 149.99, generar_embedding_aleatorio()),
('Gorra Deportiva', 'Gorra ajustable con protección UV', 'Ropa', 19.99, generar_embedding_aleatorio());

-- Insertar productos de hogar
INSERT INTO productos (nombre, descripcion, categoria, precio, embedding) VALUES
('Cafetera Espresso', 'Cafetera automática con molinillo integrado', 'Hogar', 399.99, generar_embedding_aleatorio()),
('Robot Aspirador', 'Robot aspirador con mapeo inteligente', 'Hogar', 299.99, generar_embedding_aleatorio()),
('Lámpara LED Smart', 'Lámpara inteligente con control por app', 'Hogar', 79.99, generar_embedding_aleatorio()),
('Purificador de Aire', 'Purificador con filtro HEPA', 'Hogar', 199.99, generar_embedding_aleatorio()),
('Termostato Inteligente', 'Termostato WiFi programable', 'Hogar', 149.99, generar_embedding_aleatorio());
```

## 🐳 Paso 5: Comandos Docker con sudo

### Iniciar los contenedores:

```bash
# Construir e iniciar los servicios
sudo docker-compose up -d

# Ver los logs
sudo docker-compose logs -f postgres

# Verificar que los contenedores estén ejecutándose
sudo docker ps

# Ver información detallada del contenedor
sudo docker inspect postgres_vectorial
```

### Comandos útiles de administración:

```bash
# Detener los servicios
sudo docker-compose stop

# Iniciar servicios detenidos
sudo docker-compose start

# Reiniciar servicios
sudo docker-compose restart

# Eliminar contenedores (mantiene los datos)
sudo docker-compose down

# Eliminar contenedores Y volúmenes (CUIDADO: borra todos los datos)
sudo docker-compose down -v

# Ver uso de recursos
sudo docker stats postgres_vectorial

# Ejecutar comandos dentro del contenedor
sudo docker exec -it postgres_vectorial bash

# Acceder a PostgreSQL directamente
sudo docker exec -it postgres_vectorial psql -U usuario_vector -d base_vectorial
```

## 🔍 Paso 6: Realizar Búsquedas Vectoriales

### Conectarse a la base de datos:

```bash
# Opción 1: Usando docker exec
sudo docker exec -it postgres_vectorial psql -U usuario_vector -d base_vectorial

# Opción 2: Usando psql local (si está instalado)
psql -h localhost -p 5432 -U usuario_vector -d base_vectorial
```

### Ejemplos de búsquedas vectoriales:

```sql
-- Ver todos los productos
SELECT id, nombre, categoria, precio FROM productos;

-- Buscar productos similares a uno existente
WITH producto_referencia AS (
    SELECT embedding FROM productos WHERE id = 1
)
SELECT 
    p.nombre,
    p.categoria,
    p.precio,
    1 - (p.embedding <=> pr.embedding) AS similitud
FROM productos p, producto_referencia pr
WHERE p.id != 1
ORDER BY p.embedding <=> pr.embedding
LIMIT 5;

-- Usar la función de búsqueda creada
SELECT * FROM buscar_productos_similares(
    (SELECT embedding FROM productos WHERE id = 3),
    10
);

-- Búsqueda por categoría con similitud
SELECT 
    nombre,
    descripcion,
    precio,
    1 - (embedding <=> (SELECT embedding FROM productos WHERE id = 1)) as similitud
FROM productos
WHERE categoria = 'Electrónica'
ORDER BY embedding <=> (SELECT embedding FROM productos WHERE id = 1)
LIMIT 3;

-- Ver estadísticas por categoría
SELECT * FROM estadisticas_productos;
```

## 🐍 Paso 7: Script Python para Búsqueda Vectorial

Crea un archivo `busqueda_vectorial.py`:

```python
import psycopg2
import numpy as np
from psycopg2.extras import RealDictCursor

# Configuración de conexión
config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'base_vectorial',
    'user': 'usuario_vector',
    'password': 'contraseña_segura'
}

def conectar_db():
    """Conectar a PostgreSQL"""
    return psycopg2.connect(**config)

def buscar_productos_similares(producto_id, limite=5):
    """Buscar productos similares usando búsqueda vectorial"""
    
    with conectar_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Obtener embedding del producto de referencia
            cur.execute("""
                SELECT embedding::text FROM productos WHERE id = %s
            """, (producto_id,))
            
            resultado = cur.fetchone()
            if not resultado:
                print(f"Producto {producto_id} no encontrado")
                return
            
            # Buscar productos similares
            cur.execute("""
                SELECT 
                    p.id,
                    p.nombre,
                    p.descripcion,
                    p.categoria,
                    p.precio,
                    1 - (p.embedding <=> %s::vector) AS similitud
                FROM productos p
                WHERE p.id != %s
                ORDER BY p.embedding <=> %s::vector
                LIMIT %s
            """, (resultado['embedding'], producto_id, resultado['embedding'], limite))
            
            productos_similares = cur.fetchall()
            
            print(f"\nProductos similares al ID {producto_id}:")
            print("-" * 60)
            
            for prod in productos_similares:
                print(f"ID: {prod['id']}")
                print(f"Nombre: {prod['nombre']}")
                print(f"Categoría: {prod['categoria']}")
                print(f"Precio: ${prod['precio']}")
                print(f"Similitud: {prod['similitud']:.4f}")
                print("-" * 60)

def listar_productos():
    """Listar todos los productos"""
    with conectar_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, nombre, categoria, precio 
                FROM productos 
                ORDER BY categoria, nombre
            """)
            
            productos = cur.fetchall()
            
            print("\nLista de Productos:")
            print("-" * 60)
            
            categoria_actual = None
            for prod in productos:
                if prod['categoria'] != categoria_actual:
                    categoria_actual = prod['categoria']
                    print(f"\n[{categoria_actual}]")
                
                print(f"  ID: {prod['id']:2d} | {prod['nombre']:30s} | ${prod['precio']:7.2f}")

if __name__ == "__main__":
    print("=== BÚSQUEDA VECTORIAL CON POSTGRESQL ===")
    
    # Listar productos disponibles
    listar_productos()
    
    # Buscar productos similares
    producto_id = int(input("\nIngrese el ID del producto para buscar similares: "))
    buscar_productos_similares(producto_id, limite=5)
```

## 📚 Paso 8: Instalar Dependencias Python

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows

# Instalar dependencias
pip install psycopg2-binary numpy
```

## 🎯 Paso 9: Probar el Sistema

```bash
# Ejecutar el script Python
python busqueda_vectorial.py

# O acceder a pgAdmin en el navegador
# http://localhost:8080
# Usuario: admin@ejemplo.com
# Contraseña: admin123
```

## 🔧 Resolución de Problemas Comunes

### Permisos de Docker:

```bash
# Si tienes problemas con permisos, añadir tu usuario al grupo docker
sudo usermod -aG docker $USER
# Luego cerrar sesión y volver a entrar

# O ejecutar todos los comandos con sudo como se muestra en el tutorial
```

### Puerto ocupado:

```bash
# Verificar qué está usando el puerto 5432
sudo lsof -i :5432

# Cambiar el puerto en docker-compose.yml si es necesario
# Por ejemplo: "5433:5432"
```

### Limpiar todo y empezar de nuevo:

```bash
# Detener y eliminar todo
sudo docker-compose down -v
sudo rm -rf data/

# Volver a iniciar
sudo docker-compose up -d
```

## 🎉 Conclusión

¡Felicidades! Ahora tienes un sistema completo de búsqueda vectorial funcionando con:

- ✅ PostgreSQL 17 oficial
- ✅ Extensión pgvector para búsquedas vectoriales
- ✅ Datos de ejemplo listos para usar
- ✅ Funciones SQL para búsqueda de similitud
- ✅ Interface de administración con pgAdmin
- ✅ Script Python para interactuar con el sistema

Este sistema es la base para construir aplicaciones más complejas como:
- Sistemas de recomendación
- Búsqueda semántica
- RAG (Retrieval-Augmented Generation)
- Análisis de similitud de documentos

---

**Nota**: Los embeddings en este tutorial son aleatorios para demostración. En producción, deberías usar un modelo de ML real como Sentence-Transformers para generar embeddings significativos.