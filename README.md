# 🚀 E-commerce Semantic Search

Sistema de búsqueda semántica para productos de e-commerce que permite encontrar productos por significado (no solo palabras exactas) usando **Elasticsearch**, **FastAPI** y modelos de **embeddings multilingües**.

**Ejemplo**: Buscar "teléfono con buena cámara" encuentra "iPhone 15 Pro Max" aunque la descripción no contenga exactamente esas palabras.

## ✨ Características

- **🔍 Búsqueda Semántica**: Encuentra productos por significado, no solo palabras exactas
- **⚡ API REST Completa**: FastAPI con documentación automática
- **🔄 Sincronización Automática**: Indexación desde microservicio existente
- **📊 Métricas y Monitoreo**: Health checks y estadísticas de uso
- **🌐 Multilingüe**: Soporta búsquedas en español
- **🎯 Filtros Avanzados**: Por categoría, precio y stock

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cliente       │───▶│   FastAPI        │───▶│  Elasticsearch  │
│   (Web/Mobile)  │    │   (Búsquedas)    │    │   (Índice +     │
└─────────────────┘    └──────────────────┘    │   Embeddings)   │
                              │                 └─────────────────┘
                              ▼
                       ┌──────────────────┐
                       │  Microservicio   │
                       │   Productos      │
                       │   (Externo)      │
                       └──────────────────┘
```

## 🛠️ Stack Tecnológico

- **FastAPI** 0.109+ - API REST + documentación automática
- **Elasticsearch** 8.11+ - Motor de búsqueda + vectores semánticos
- **sentence-transformers** - Embeddings multilingües
- **Pydantic** - Validación de datos
- **Python** 3.12+

## 🚀 Inicio Rápido

### 1. Configuración

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus URLs de Elasticsearch y API de productos
```

### 2. Configurar Elasticsearch

```bash
# Crear índice con mapping correcto
python scripts/setup_index.py

# Verificar conexión
python scripts/health_check.py --quick
```

### 3. Sincronizar Productos

```bash
# Iniciar la aplicación
python main.py

# En otra terminal, sincronizar productos
curl -X POST http://localhost:8000/api/v1/sync
```

### 4. Probar Búsquedas

```bash
# Búsqueda básica
curl -X POST http://localhost:8000/api/v1/buscar \
  -H "Content-Type: application/json" \
  -d '{"query": "smartphone cámara", "top_k": 3}'

# Ver documentación interactiva
# http://localhost:8000/docs
```

## 📋 API Endpoints

### Búsqueda Semántica

- **POST** `/api/v1/buscar` - Búsqueda semántica principal
- **GET** `/api/v1/categories` - Lista categorías disponibles

### Sincronización

- **POST** `/api/v1/sync` - Sincroniza productos desde API externa

### Monitoreo

- **GET** `/api/v1/health` - Estado completo del sistema
- **GET** `/api/v1/stats` - Estadísticas de uso

### Documentación

- **GET** `/docs` - Swagger UI interactivo
- **GET** `/redoc` - Documentación ReDoc

## 🔍 Ejemplos de Uso

### Búsqueda Semántica

```json
POST /api/v1/buscar
{
  "query": "laptop para programar",
  "top_k": 5,
  "category": "Laptops",
  "price_max": 2000,
  "include_out_of_stock": false
}
```

**Response:**

```json
{
  "query": "laptop para programar",
  "total_resultados": 3,
  "tiempo_busqueda_ms": 45,
  "filtros_aplicados": {
    "category": "Laptops",
    "price_range": { "max": 2000 },
    "in_stock_only": true
  },
  "resultados": [
    {
      "id": "laptop-123",
      "name": "MacBook Pro M3",
      "description": "Potente laptop para desarrollo...",
      "price": 1899.99,
      "score_semantico": 0.924,
      "relevancia": "alta"
    }
  ]
}
```

### Casos de Uso Avanzados

**Búsquedas que funcionan bien:**

- "teléfono con buena cámara" → encuentra iPhones, Samsung Galaxy
- "dispositivo para entretenimiento" → tablets, smart TVs, consolas
- "regalo tecnológico económico" → productos tech bajo cierto precio
- "equipo profesional fotografía" → cámaras DSLR, lentes, accesorios

## 🔧 Scripts Utilitarios

```bash
# Verificación completa de salud
python scripts/health_check.py

# Verificación rápida
python scripts/health_check.py --quick

# Configurar índice Elasticsearch
python scripts/setup_index.py

# Resetear índice (¡cuidado!)
python scripts/setup_index.py --reset

# Pruebas específicas de Elasticsearch
python test_elasticsearch.py
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con verbose
pytest -v

# Tests específicos
pytest tests/test_api.py
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Elasticsearch
ELASTICSEARCH_URL=https://your-es-instance.com
INDEX_NAME=productos

# API Externa
PRODUCTOS_API_URL=https://your-api.com/api/v1/products

# Modelo ML
MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Performance
SYNC_TIMEOUT=30
SEARCH_TIMEOUT=5
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
```

### Mapping de Elasticsearch

El sistema configura automáticamente un mapping optimizado con:

- **Analizador español** para texto
- **Vectores densos (384 dim)** para embeddings
- **Similaridad coseno** para búsqueda semántica
- **Campos de filtros** optimizados

## 🚨 Troubleshooting

### Problemas Comunes

**1. Error conectando con Elasticsearch**

```bash
python scripts/health_check.py
# Verificar URL en .env
```

**2. Modelo de embeddings no carga**

```bash
# Verificar conexión a internet
# El modelo se descarga automáticamente la primera vez
```

**3. API de productos no responde**

```bash
# Verificar URL en .env
curl -X GET "https://your-api.com/api/v1/products?limit=1"
```

**4. Búsquedas sin resultados**

```bash
# Verificar que hay productos indexados
curl -X GET http://localhost:8000/api/v1/stats
```

### Logs y Debug

```bash
# Ver logs detallados
LOG_LEVEL=DEBUG python main.py

# Health check con detalles
python scripts/health_check.py
```

## 🔄 Desarrollo

### Estructura del Proyecto

```
ecommerce-semantic-search/
├── api/routes.py              # Endpoints FastAPI
├── models/schemas.py          # Modelos Pydantic
├── services/                  # Lógica de negocio
│   ├── elasticsearch_service.py
│   ├── embedding_service.py
│   └── product_service.py
├── scripts/                   # Utilidades
│   ├── setup_index.py
│   └── health_check.py
├── tests/test_api.py         # Tests básicos
├── utils/logger.py           # Sistema de logging
├── config.py                 # Configuración
└── main.py                   # Aplicación principal
```

### Agregar Nuevas Características

**Nuevos filtros de búsqueda:**

1. Agregar campos al `SearchRequest` en `models/schemas.py`
2. Implementar lógica en `elasticsearch_service.py`
3. Actualizar documentación

**Nuevos endpoints:**

1. Agregar ruta en `api/routes.py`
2. Crear tests en `tests/`
3. Actualizar este README

## 📊 Performance

- **Tiempo de búsqueda**: < 100ms (típico 45ms)
- **Sincronización**: ~150 productos/segundo
- **Memoria**: ~500MB (con modelo cargado)
- **Embeddings**: 384 dimensiones, similaridad coseno

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 🎉 Estado del Proyecto

✅ **Listo para Producción**

- Búsqueda semántica funcionando
- API completa documentada
- Health checks implementados
- Tests básicos incluidos
- Scripts de utilidad listos

**¡El sistema está listo para ser usado o extendido según tus necesidades!** 🚀
