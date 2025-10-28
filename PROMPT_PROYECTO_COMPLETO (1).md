# 🚀 Prompt Completo: Sistema de Búsqueda Semántica E-commerce

## 📋 Descripción del Proyecto

Crear un sistema de búsqueda semántica para productos de e-commerce que permita encontrar productos por significado (no solo palabras exactas) usando Elasticsearch, FastAPI y modelos de embeddings multilingües.

**Ejemplo**: Buscar "teléfono con buena cámara" debe encontrar "iPhone 15 Pro Max" aunque la descripción no contenga exactamente esas palabras.

## 🎯 Objetivos

1. **API REST** completa con FastAPI
2. **Búsqueda semántica** usando embeddings y Elasticsearch
3. **Sincronización automática** desde microservicio existente
4. **DevContainer** configurado para desarrollo inmediato
5. **Documentación interactiva** con Swagger/OpenAPI

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI        │───▶│  Elasticsearch  │
│   (opcional)    │    │   (Búsquedas)    │    │   (Índice +     │
└─────────────────┘    └──────────────────┘    │   Embeddings)   │
                              │                 └─────────────────┘
                              ▼
                       ┌──────────────────┐
                       │  Microservicio   │
                       │   Productos      │
                       │   (Existente)    │
                       └──────────────────┘
```

## 🔌 API Existente (Productos)

**URL**: `https://scaling-umbrella-vj7gqw4v65qcww5g-8000.app.github.dev/api/v1/products`

**Estructura de Producto**:

```json
{
  "id": "88d7984b-a03c-413c-960f-e73291",
  "name": "iPhone 15 Pro Max",
  "description": "El iPhone más avanzado con chip A17 Pro, cámara de 48MP con zoom óptico 5x, pantalla Super Retina XDR de 6.7 pulgadas, batería de larga duración y resistencia al agua IP68.",
  "price": "1199.99",
  "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab",
  "category": "Smartphones",
  "stock": 25,
  "created_at": "2025-09-15T03:42:47.3640767",
  "updated_at": "2025-09-15T03:42:47.3640767"
}
```

**Endpoints disponibles**:

- `GET /api/v1/products?skip=0&limit=100` - Listar productos (paginado)
- `GET /api/v1/products/{id}` - Obtener producto específico

## 🛠️ Stack Tecnológico

### Backend

- **FastAPI** 0.109+ (API REST + docs automática)
- **Elasticsearch** 7.17+ (motor de búsqueda + vectores)
- **sentence-transformers** (embeddings multilingües)
- **Pydantic** (validación de datos)

### Desarrollo

- **DevContainer** con VS Code
- **Docker Compose** (orquestación)
- **GitHub Codespaces** compatible

### ML/AI

- **Modelo**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensiones**: 384 (embeddings)
- **Similitud**: Coseno

## 📁 Estructura del Proyecto

```
ecommerce-semantic-search/
├── .devcontainer/
│   ├── devcontainer.json       # Configuración VS Code
│   ├── docker-compose.yml      # Elasticsearch + App
│   ├── Dockerfile              # Imagen Python
│   ├── setup.sh                # Script inicial
│   └── start-services.sh       # Inicio automático ES
├── api/
│   ├── __init__.py
│   └── routes.py               # Endpoints FastAPI
├── models/
│   ├── __init__.py
│   └── schemas.py              # Modelos Pydantic
├── services/
│   ├── __init__.py
│   ├── elasticsearch_service.py # Cliente ES + búsquedas
│   ├── embedding_service.py     # Generación embeddings
│   └── product_service.py       # Sincronización productos
├── utils/
│   ├── __init__.py
│   └── logger.py               # Logging configurado
├── scripts/
│   ├── health_check.py         # Verificación servicios
│   └── setup_index.py          # Crear índice inicial
├── tests/
│   ├── __init__.py
│   └── test_api.py             # Tests básicos
├── .env                        # Variables entorno
├── .env.example               # Template configuración
├── config.py                  # Configuración global
├── main.py                    # Aplicación principal
├── requirements.txt           # Dependencias Python
├── README.md                  # Documentación
└── test_elasticsearch.py      # Pruebas ES específicas
```

## 🔧 Configuración Técnica

### 1. Mapping Elasticsearch

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "name": { "type": "text", "analyzer": "spanish" },
      "description": { "type": "text", "analyzer": "spanish" },
      "category": { "type": "keyword" },
      "price": { "type": "float" },
      "stock": { "type": "integer" },
      "image_url": { "type": "keyword" },
      "embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "spanish": {
          "tokenizer": "standard",
          "filter": ["lowercase", "spanish_stemmer"]
        }
      },
      "filter": {
        "spanish_stemmer": {
          "type": "stemmer",
          "language": "spanish"
        }
      }
    }
  }
}
```

### 2. DevContainer Configuration

```json
{
  "name": "E-commerce Semantic Search",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.12"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-azuretools.azure-dev",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "github.copilot",
        "github.copilot-chat",
        "ms-azuretools.vscode-docker",
        "esbenp.prettier-vscode"
      ],
      "settings": {
        "python.pythonPath": "/usr/local/bin/python",
        "python.formatting.provider": "black",
        "editor.formatOnSave": true
      }
    }
  },
  "forwardPorts": [8000, 9200, 5601],

  "remoteUser": "vscode"
}
```

## 🌐 API Endpoints Requeridos

### 1. **POST** `/api/v1/sync`

Sincroniza productos desde la API externa hacia Elasticsearch.

**Request**: `{}`
**Response**:

```json
{
  "message": "Sincronización completada",
  "productos_indexados": 156,
  "tiempo_ms": 12450,
  "errores": 0
}
```

### 2. **POST** `/api/v1/buscar`

Búsqueda semántica principal.

**Request**:

```json
{
  "query": "smartphone con buena cámara para fotografía",
  "top_k": 5,
  "category": "Smartphones", // opcional
  "price_min": 200, // opcional
  "price_max": 1500, // opcional
  "include_out_of_stock": false // opcional, default false
}
```

**Response**:

```json
{
  "query": "smartphone con buena cámara para fotografía",
  "total_resultados": 3,
  "tiempo_busqueda_ms": 45,
  "filtros_aplicados": {
    "category": "Smartphones",
    "price_range": { "min": 200, "max": 1500 },
    "in_stock_only": true
  },
  "resultados": [
    {
      "id": "88d7984b-a03c-413c-960f-e73291",
      "name": "iPhone 15 Pro Max",
      "description": "El iPhone más avanzado con chip A17 Pro...",
      "price": 1199.99,
      "category": "Smartphones",
      "stock": 25,
      "image_url": "https://images.unsplash.com/...",
      "score_semantico": 0.924,
      "relevancia": "alta"
    }
  ]
}
```

### 3. **GET** `/api/v1/health`

Health check del sistema.

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-05T10:30:00Z",
  "services": {
    "elasticsearch": { "status": "up", "cluster_health": "green" },
    "productos_api": { "status": "up", "response_time_ms": 234 },
    "embedding_model": {
      "status": "loaded",
      "model": "paraphrase-multilingual-MiniLM-L12-v2"
    }
  },
  "index_stats": {
    "total_productos": 156,
    "last_sync": "2025-10-05T10:15:00Z"
  }
}
```

### 4. **GET** `/api/v1/categories`

Lista categorías disponibles.

**Response**:

```json
{
  "categories": [
    { "name": "Smartphones", "count": 45 },
    { "name": "Laptops", "count": 23 },
    { "name": "Tablets", "count": 18 }
  ]
}
```

### 5. **GET** `/api/v1/stats`

Estadísticas del índice y uso.

**Response**:

```json
{
  "index_size_mb": 12.5,
  "total_documents": 156,
  "avg_search_time_ms": 34,
  "last_24h_searches": 247,
  "most_searched_terms": [
    { "term": "iphone", "count": 45 },
    { "term": "laptop gaming", "count": 23 }
  ]
}
```

## 📦 Dependencies (requirements.txt)

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Search & ML
elasticsearch==8.11.0
sentence-transformers==2.3.1

# HTTP & Data
requests==2.31.0
httpx==0.25.2
pydantic==2.5.0

# Utils
python-dotenv==1.0.0
python-multipart==0.0.6

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

## 🔐 Environment Variables (.env)

```env
# Elasticsearch Configuration
# Se cambia por la URL del codespace o donde este desplegado
ELASTICSEARCH_URL=https://animated-space-parakeet-7j4rpwq9p76hpjx6-9200.app.github.dev
INDEX_NAME=productos

# External API
PRODUCTOS_API_URL=https://scaling-umbrella-vj7gqw4v65qcw5g-8000.app.github.dev/api/v1/products

# ML Model
MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=E-commerce Semantic Search
VERSION=1.0.0

# Performance
SYNC_TIMEOUT=30
SEARCH_TIMEOUT=5
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
```

## 🧪 Casos de Uso para Testing

### Búsquedas Semánticas Esperadas:

1. **"teléfono con buena cámara"** → encuentra iPhones, Samsung Galaxy con especificaciones de cámara
2. **"laptop para programar"** → encuentra MacBooks, ThinkPads, laptops con buenas specs
3. **"dispositivo para entretenimiento"** → tablets, smart TVs, consolas
4. **"regalo tecnológico económico"** → productos tech bajo cierto precio
5. **"equipo profesional de fotografía"** → cámaras DSLR, lentes, accesorios

### Filtros Combinados:

1. Buscar "gaming" en categoría "Laptops" con precio máximo $2000
2. Buscar "apple" solo productos en stock
3. Buscar por rango de precio específico + categoría

## 🚀 Comandos de Inicio Rápido

```bash
# 1. Clonar/crear proyecto
git clone <repo> && cd ecommerce-semantic-search

# 2. Abrir en VS Code con DevContainer
code .
# → "Reopen in Container" cuando aparezca el popup

# 3. Verificar servicios (automático con postStartCommand)
python scripts/health_check.py

# 4. Crear índice inicial
python scripts/setup_index.py

# 5. Sincronizar productos
curl -X POST http://localhost:8000/api/v1/sync

# 6. Probar búsqueda
curl -X POST http://localhost:8000/api/v1/buscar \
  -H "Content-Type: application/json" \
  -d '{"query": "smartphone cámara", "top_k": 3}'

# 7. Ver documentación interactiva
# http://localhost:8000/docs
```

## 🎯 Criterios de Éxito

### Funcionales:

- ✅ Sincronización completa de productos (>150 items)
- ✅ Búsquedas semánticas relevantes (score > 0.7 para queries obvios)
- ✅ Filtros funcionando correctamente
- ✅ Tiempo de respuesta < 100ms para búsquedas
- ✅ Health checks reportando estado correcto

### Técnicos:

- ✅ DevContainer funciona en GitHub Codespaces
- ✅ Elasticsearch auto-start configurado
- ✅ API documentada en /docs
- ✅ Tests básicos pasando
- ✅ Logs informativos y structured

## 💡 Tips de Implementación

### 1. **Generación de Embeddings**:

```python
# Combinar name + description para mejor contexto semántico
text_for_embedding = f"{product['name']}. {product['description']}"
embedding = model.encode(text_for_embedding)
```

### 2. **Búsqueda Híbrida**:

```python
# Combinar búsqueda semántica + texto tradicional
query = {
  "query": {
    "bool": {
      "should": [
        {"knn": {"embedding": {"vector": query_embedding, "k": top_k}}},
        {"multi_match": {"query": text_query, "fields": ["name^2", "description"]}}
      ]
    }
  }
}
```

### 3. **Manejo de Errores Robusto**:

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def sync_products():
    # Lógica con reintentos automáticos
```

### 4. **Logging Structured**:

```python
logger.info("Búsqueda realizada", extra={
    "query": query_text,
    "results_count": len(results),
    "search_time_ms": elapsed_ms,
    "filters": filters_applied
})
```

---

## 🎉 Resultado Final Esperado

Un sistema completo de búsqueda semántica que:

1. **Funciona inmediatamente** al abrir en GitHub Codespaces
2. **Encuentra productos relevantes** por significado, no solo keywords
3. **Está bien documentado** con Swagger UI interactivo
4. **Es escalable** y fácil de mantener
5. **Incluye monitoreo** y health checks

**¡Listo para ser usado en producción o como base para extensiones más avanzadas!** 🚀
