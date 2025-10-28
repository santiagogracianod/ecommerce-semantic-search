"""Servicio para generar embeddings semánticos."""
import asyncio
from typing import List, Union
import numpy as np

from sentence_transformers import SentenceTransformer
from config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EmbeddingService:
    """Servicio para generar embeddings usando sentence-transformers."""
    
    def __init__(self):
        """Inicializa el servicio de embeddings."""
        self.model = None
        self._loading = False
        self._load_lock = asyncio.Lock()
    
    async def _load_model(self) -> None:
        """Carga el modelo de embeddings de forma lazy."""
        if self.model is not None:
            return
            
        async with self._load_lock:
            # Double-check locking pattern
            if self.model is not None:
                return
                
            if self._loading:
                # Esperar hasta que termine de cargar
                while self._loading:
                    await asyncio.sleep(0.1)
                return
                
            self._loading = True
            
            try:
                logger.info(f"Cargando modelo de embeddings: {settings.embedding_model_name}")
                
                # Ejecutar en thread pool para no bloquear el event loop
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None, 
                    lambda: SentenceTransformer(settings.embedding_model_name)
                )
                
                logger.info(
                    "Modelo cargado exitosamente",
                    extra={
                        "model_name": settings.embedding_model_name,
                        "embedding_dimension": self.model.get_sentence_embedding_dimension()
                    }
                )
                
            except Exception as e:
                logger.error(f"Error cargando modelo: {str(e)}")
                raise
            finally:
                self._loading = False
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Genera embedding para un texto único."""
        await self._load_model()
        
        try:
            # Ejecutar en thread pool para no bloquear
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(text, convert_to_tensor=False)
            )
            
            # Convertir a lista de floats
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            logger.debug(f"Embedding generado para texto de {len(text)} caracteres")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para múltiples textos de forma batch."""
        await self._load_model()
        
        if not texts:
            return []
            
        try:
            logger.info(f"Generando embeddings para {len(texts)} textos")
            
            # Ejecutar en thread pool para no bloquear
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_tensor=False, batch_size=32)
            )
            
            # Convertir a lista de listas de floats
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            logger.info(f"Embeddings generados exitosamente para {len(texts)} textos")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generando embeddings batch: {str(e)}")
            raise
    
    def prepare_product_text(self, name: str, description: str) -> str:
        """Prepara el texto del producto para generar embedding."""
        # Combinar nombre y descripción para mejor contexto semántico
        combined_text = f"{name}. {description}"
        
        # Limpiar y normalizar el texto
        combined_text = combined_text.strip()
        
        # Limitar longitud para evitar textos muy largos
        max_length = 512  # Límite común para modelos de transformers
        if len(combined_text) > max_length:
            combined_text = combined_text[:max_length-3] + "..."
            
        return combined_text
    
    async def get_model_info(self) -> dict:
        """Obtiene información sobre el modelo cargado."""
        await self._load_model()
        
        return {
            "model_name": settings.embedding_model_name,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown'),
            "is_loaded": self.model is not None
        }


# Singleton global
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Obtiene la instancia singleton del servicio de embeddings."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service