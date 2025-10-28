"""Esquemas y modelos Pydantic para el API."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


# Modelos base del producto
class Product(BaseModel):
    """Modelo de producto."""
    id: str
    name: str
    description: str
    price: Union[str, float] 
    image_url: str
    category: str
    stock: int
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]

    @validator('price')
    def validate_price(cls, v):
        """Valida y convierte el precio a float."""
        if isinstance(v, str):
            return float(v)
        return v

    @validator('created_at', 'updated_at')
    def validate_dates(cls, v):
        """Valida y convierte las fechas."""
        if isinstance(v, str):
            # Intenta parsear la fecha ISO
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class ProductWithScore(Product):
    """Producto con score de relevancia para resultados de búsqueda."""
    score_semantico: float = Field(..., description="Score de similaridad semántica")
    relevancia: str = Field(..., description="Nivel de relevancia: alta, media, baja")

    @validator('relevancia')
    def validate_relevancia(cls, v, values):
        """Asigna nivel de relevancia basado en el score."""
        score = values.get('score_semantico', 0)
        if score >= 0.8:
            return "alta"
        elif score >= 0.6:
            return "media"
        else:
            return "baja"


# Request models
class SearchRequest(BaseModel):
    """Request para búsqueda semántica."""
    query: str = Field(..., description="Consulta de búsqueda")
    top_k: int = Field(5, ge=1, le=50, description="Número máximo de resultados")
    category: Optional[str] = Field(None, description="Filtro por categoría")
    price_min: Optional[float] = Field(None, ge=0, description="Precio mínimo")
    price_max: Optional[float] = Field(None, gt=0, description="Precio máximo") 
    include_out_of_stock: bool = Field(False, description="Incluir productos sin stock")

    @validator('price_max')
    def validate_price_range(cls, v, values):
        """Valida que price_max > price_min."""
        price_min = values.get('price_min')
        if price_min is not None and v is not None and v <= price_min:
            raise ValueError('price_max debe ser mayor que price_min')
        return v


class SyncRequest(BaseModel):
    """Request para sincronización de productos."""
    force_reindex: bool = Field(False, description="Forzar reindexación completa")


# Response models
class SearchFilters(BaseModel):
    """Filtros aplicados en la búsqueda."""
    category: Optional[str] = None
    price_range: Optional[Dict[str, Optional[float]]] = None
    in_stock_only: bool = True


class SearchResponse(BaseModel):
    """Response de búsqueda semántica."""
    query: str
    total_resultados: int
    tiempo_busqueda_ms: int
    filtros_aplicados: SearchFilters
    resultados: List[ProductWithScore]


class SyncResponse(BaseModel):
    """Response de sincronización."""
    message: str
    productos_indexados: int
    tiempo_ms: int
    errores: int


class ServiceStatus(BaseModel):
    """Estado de un servicio."""
    status: str = Field(..., description="Estado: up, down, degraded")
    response_time_ms: Optional[int] = None
    cluster_health: Optional[str] = None
    model: Optional[str] = None


class IndexStats(BaseModel):
    """Estadísticas del índice."""
    total_productos: int
    last_sync: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Response del health check."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, ServiceStatus]
    index_stats: IndexStats


class CategoryInfo(BaseModel):
    """Información de una categoría."""
    name: str
    count: int


class CategoriesResponse(BaseModel):
    """Response de categorías disponibles."""
    categories: List[CategoryInfo]


class SearchTerm(BaseModel):
    """Término de búsqueda más usado."""
    term: str
    count: int


class StatsResponse(BaseModel):
    """Response de estadísticas."""
    index_size_mb: float
    total_documents: int
    avg_search_time_ms: int
    last_24h_searches: int
    most_searched_terms: List[SearchTerm]


# Modelos internos para Elasticsearch
class ProductDocument(BaseModel):
    """Documento de producto para indexar en Elasticsearch."""
    id: str
    name: str
    description: str
    category: str
    price: float
    stock: int
    image_url: str
    embedding: List[float]  # Vector de embedding
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_product(cls, product: Product, embedding: List[float]) -> "ProductDocument":
        """Crea un documento desde un Product y su embedding."""
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            category=product.category,
            price=float(product.price),
            stock=product.stock,
            image_url=product.image_url,
            embedding=embedding,
            created_at=product.created_at,
            updated_at=product.updated_at
        )


# Error responses
class ErrorResponse(BaseModel):
    """Response de error estándar."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)