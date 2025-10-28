"""Servicio para interactuar con la API de productos externa."""
import asyncio
from typing import List, Optional
from datetime import datetime

import httpx
from config import get_settings
from models.schemas import Product
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ProductService:
    """Servicio para obtener productos de la API externa."""
    
    def __init__(self):
        """Inicializa el servicio de productos."""
        self.base_url = settings.productos_api_url.rstrip('/')
        self.timeout = settings.sync_timeout
        
    async def get_products(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        timeout: Optional[int] = None
    ) -> List[Product]:
        """Obtiene productos de la API externa con paginación."""
        if timeout is None:
            timeout = self.timeout
            
        url = f"{self.base_url}/?skip={skip}&limit={limit}"
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info(f"Obteniendo productos: skip={skip}, limit={limit}")
                
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                
                # Validar y convertir a modelos Product
                products = []
                for item in data:
                    try:
                        product = Product(**item)
                        products.append(product)
                    except Exception as e:
                        logger.warning(f"Error parseando producto {item.get('id', 'unknown')}: {str(e)}")
                        continue
                
                logger.info(f"Productos obtenidos exitosamente: {len(products)}")
                return products
                
        except httpx.TimeoutException:
            logger.error(f"Timeout obteniendo productos desde {url}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP {e.response.status_code} obteniendo productos: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado obteniendo productos: {str(e)}")
            raise
    
    async def get_all_products(self, batch_size: int = 100) -> List[Product]:
        """Obtiene todos los productos usando paginación automática."""
        all_products = []
        skip = 0
        
        logger.info("Iniciando obtención de todos los productos")
        
        while True:
            try:
                batch = await self.get_products(skip=skip, limit=batch_size)
                
                if not batch:
                    # No hay más productos
                    break
                    
                all_products.extend(batch)
                skip += len(batch)
                
                # Si obtuvimos menos productos que el límite, hemos llegado al final
                if len(batch) < batch_size:
                    break
                    
                logger.info(f"Productos obtenidos hasta ahora: {len(all_products)}")
                
                # Pequeña pausa para no sobrecargar la API
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error obteniendo batch en skip={skip}: {str(e)}")
                # Intentar continuar con el siguiente batch o fallar completamente
                if len(all_products) == 0:
                    # Si no hemos obtenido nada aún, fallar
                    raise
                else:
                    # Si ya tenemos algunos productos, log el error pero continuar
                    logger.warning(f"Continuando con {len(all_products)} productos obtenidos")
                    break
        
        logger.info(f"Obtención completa: {len(all_products)} productos totales")
        return all_products
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Obtiene un producto específico por ID."""
        url = f"{self.base_url}/{product_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                data = response.json()
                
                return Product(**data)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error HTTP obteniendo producto {product_id}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
            raise
    
    async def check_api_health(self) -> dict:
        """Verifica el estado de la API de productos."""
        start_time = datetime.now()
        
        try:
            # Intentar obtener un pequeño batch para verificar conectividad
            await self.get_products(skip=0, limit=1, timeout=5)
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "up",
                "response_time_ms": int(elapsed)
            }
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "down",
                "response_time_ms": int(elapsed),
                "error": str(e)
            }


# Singleton global  
_product_service = None


def get_product_service() -> ProductService:
    """Obtiene la instancia singleton del servicio de productos."""
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service