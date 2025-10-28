"""Servicio para operaciones con Elasticsearch."""
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, ConnectionError as ESConnectionError

from config import get_settings
from models.schemas import (
    Product, ProductDocument, ProductWithScore, SearchRequest, 
    CategoryInfo, SearchFilters
)
from services.embedding_service import get_embedding_service
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ElasticsearchService:
    """Servicio para operaciones con Elasticsearch."""
    
    def __init__(self):
        """Inicializa el cliente de Elasticsearch."""
        self.es_client = AsyncElasticsearch(
            hosts=[settings.elasticsearch_url],
            request_timeout=settings.search_timeout,
        )
        self.index_name = settings.index_name
        self.embedding_service = get_embedding_service()
    
    async def close(self):
        """Cierra la conexión con Elasticsearch."""
        await self.es_client.close()
    
    async def check_connection(self) -> dict:
        """Verifica la conexión y estado del cluster."""
        try:
            # Verificar conectividad básica
            health = await self.es_client.cluster.health()
            
            return {
                "status": "up",
                "cluster_health": health.get("status", "unknown"),
                "number_of_nodes": health.get("number_of_nodes", 0)
            }
            
        except Exception as e:
            logger.error(f"Error verificando conexión ES: {str(e)}")
            return {
                "status": "down",
                "error": str(e)
            }
    
    async def create_index(self) -> bool:
        """Crea el índice con el mapping correcto."""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text", 
                        "analyzer": "spanish",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {
                        "type": "text", 
                        "analyzer": "spanish"
                    },
                    "category": {"type": "keyword"},
                    "price": {"type": "float"},
                    "stock": {"type": "integer"},
                    "image_url": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
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
        
        try:
            # Verificar si el índice ya existe
            exists = await self.es_client.indices.exists(index=self.index_name)
            
            if exists:
                logger.info(f"Índice {self.index_name} ya existe")
                return True
            
            # Crear el índice
            logger.info(f"Creando índice {self.index_name}")
            await self.es_client.indices.create(
                index=self.index_name,
                body=mapping
            )
            
            logger.info(f"Índice {self.index_name} creado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando índice: {str(e)}")
            return False
    
    async def delete_index(self) -> bool:
        """Elimina el índice completo."""
        try:
            exists = await self.es_client.indices.exists(index=self.index_name)
            if not exists:
                return True
                
            await self.es_client.indices.delete(index=self.index_name)
            logger.info(f"Índice {self.index_name} eliminado")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando índice: {str(e)}")
            return False
    
    async def index_product(self, product: Product) -> bool:
        """Indexa un producto individual."""
        try:
            # Generar embedding
            text_for_embedding = self.embedding_service.prepare_product_text(
                product.name, product.description
            )
            embedding = await self.embedding_service.generate_embedding(text_for_embedding)
            
            # Crear documento
            doc = ProductDocument.from_product(product, embedding)
            
            # Indexar
            await self.es_client.index(
                index=self.index_name,
                id=product.id,
                body=doc.dict()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexando producto {product.id}: {str(e)}")
            return False
    
    async def index_products_batch(self, products: List[Product]) -> Dict[str, int]:
        """Indexa múltiples productos usando bulk API."""
        if not products:
            return {"indexed": 0, "errors": 0}
        
        logger.info(f"Preparando indexación batch de {len(products)} productos")
        
        try:
            # Generar embeddings para todos los productos
            texts = [
                self.embedding_service.prepare_product_text(p.name, p.description)
                for p in products
            ]
            
            embeddings = await self.embedding_service.generate_embeddings(texts)
            
            # Preparar bulk operations
            bulk_body = []
            
            for product, embedding in zip(products, embeddings):
                # Action header
                bulk_body.append({
                    "index": {
                        "_index": self.index_name,
                        "_id": product.id
                    }
                })
                
                # Document body
                doc = ProductDocument.from_product(product, embedding)
                bulk_body.append(doc.dict())
            
            # Ejecutar bulk operation
            response = await self.es_client.bulk(body=bulk_body)
            
            # Procesar resultados
            indexed = 0
            errors = 0
            
            for item in response["items"]:
                if "index" in item:
                    if item["index"].get("status") in [200, 201]:
                        indexed += 1
                    else:
                        errors += 1
                        logger.warning(f"Error indexando: {item}")
            
            logger.info(f"Indexación batch completada: {indexed} indexados, {errors} errores")
            
            # Refresh index para búsquedas inmediatas
            await self.es_client.indices.refresh(index=self.index_name)
            
            return {"indexed": indexed, "errors": errors}
            
        except Exception as e:
            logger.error(f"Error en indexación batch: {str(e)}")
            raise
    
    async def search_products(self, search_request: SearchRequest) -> Dict[str, Any]:
        """Realiza búsqueda semántica de productos."""
        start_time = datetime.now()
        
        try:
            # Generar embedding para la consulta
            query_embedding = await self.embedding_service.generate_embedding(search_request.query)
            
            # Construir query de Elasticsearch (búsqueda híbrida)
            query = {
                "bool": {
                    "should": [
                        # Búsqueda semántica usando embeddings
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                    "params": {"query_vector": query_embedding}
                                }
                            }
                        },
                        # Búsqueda textual tradicional (menor peso)
                        {
                            "multi_match": {
                                "query": search_request.query,
                                "fields": ["name^2", "description"],
                                "fuzziness": "AUTO",
                                "boost": 0.3
                            }
                        }
                    ]
                }
            }
            
            # Aplicar filtros
            filters = []
            
            if search_request.category:
                filters.append({"term": {"category": search_request.category}})
            
            if search_request.price_min is not None:
                filters.append({"range": {"price": {"gte": search_request.price_min}}})
                
            if search_request.price_max is not None:
                filters.append({"range": {"price": {"lte": search_request.price_max}}})
            
            if not search_request.include_out_of_stock:
                filters.append({"range": {"stock": {"gt": 0}}})
            
            if filters:
                query = {
                    "bool": {
                        "must": [query],
                        "filter": filters
                    }
                }
            
            # Ejecutar búsqueda
            response = await self.es_client.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": search_request.top_k,
                    "_source": {
                        "excludes": ["embedding"]  # No devolver el vector embedding
                    }
                }
            )
            
            # Procesar resultados
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                score = hit["_score"]
                
                # Normalizar score (el script_score puede dar valores altos)
                normalized_score = min(max(score / 2.0, 0.0), 1.0)
                
                product_with_score = ProductWithScore(
                    **source,
                    score_semantico=normalized_score,
                    relevancia=""  # Se calculará automáticamente en el validator
                )
                results.append(product_with_score)
            
            # Calcular tiempo de búsqueda
            search_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Preparar información de filtros aplicados
            filters_applied = SearchFilters(
                category=search_request.category,
                price_range={
                    "min": search_request.price_min,
                    "max": search_request.price_max
                } if search_request.price_min is not None or search_request.price_max is not None else None,
                in_stock_only=not search_request.include_out_of_stock
            )
            
            logger.info(
                f"Búsqueda completada",
                extra={
                    "query": search_request.query,
                    "results_count": len(results),
                    "total_hits": response["hits"]["total"]["value"],
                    "search_time_ms": search_time
                }
            )
            
            return {
                "query": search_request.query,
                "total_resultados": response["hits"]["total"]["value"],
                "tiempo_busqueda_ms": search_time,
                "filtros_aplicados": filters_applied,
                "resultados": results
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            raise
    
    async def get_categories(self) -> List[CategoryInfo]:
        """Obtiene las categorías disponibles con conteos."""
        try:
            response = await self.es_client.search(
                index=self.index_name,
                body={
                    "size": 0,
                    "aggs": {
                        "categories": {
                            "terms": {
                                "field": "category",
                                "size": 100
                            }
                        }
                    }
                }
            )
            
            categories = []
            buckets = response["aggregations"]["categories"]["buckets"]
            
            for bucket in buckets:
                categories.append(CategoryInfo(
                    name=bucket["key"],
                    count=bucket["doc_count"]
                ))
            
            return categories
            
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {str(e)}")
            return []
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice."""
        try:
            # Estadísticas básicas del índice
            stats = await self.es_client.indices.stats(index=self.index_name)
            index_stats = stats["indices"][self.index_name]
            
            # Conteo de documentos
            count_response = await self.es_client.count(index=self.index_name)
            
            return {
                "total_productos": count_response["count"],
                "index_size_mb": round(
                    index_stats["total"]["store"]["size_in_bytes"] / (1024 * 1024), 2
                ),
                "last_sync": None  # Esto se puede almacenar en un documento especial
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {
                "total_productos": 0,
                "index_size_mb": 0.0,
                "last_sync": None
            }


# Singleton global
_elasticsearch_service = None


def get_elasticsearch_service() -> ElasticsearchService:
    """Obtiene la instancia singleton del servicio de Elasticsearch."""
    global _elasticsearch_service
    if _elasticsearch_service is None:
        _elasticsearch_service = ElasticsearchService()
    return _elasticsearch_service