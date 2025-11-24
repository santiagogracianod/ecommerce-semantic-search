"""Configuración global de la aplicación."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings."""
    
    # Elasticsearch Configuration
    elasticsearch_url: str = "http://localhost:9200"
    index_name: str = "productos"
    
    # External API
    productos_api_url: str = "http://localhost:8000/api/v1/products"
    
    # ML Model (renombrado para evitar conflicto)
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "E-commerce Semantic Search"
    version: str = "1.0.0"
    
    # Performance
    sync_timeout: int = 30
    search_timeout: int = 5
    default_page_size: int = 10
    max_page_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": ("settings_",)
    }


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración singleton."""
    return Settings()