"""Tests básicos para la API."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test del endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_ping_endpoint():
    """Test del endpoint ping."""
    response = client.get("/ping")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@patch('services.elasticsearch_service.get_elasticsearch_service')
@patch('services.product_service.get_product_service')
@patch('services.embedding_service.get_embedding_service')
def test_health_endpoint(mock_embedding, mock_product, mock_es):
    """Test del endpoint de health check."""
    # Configurar mocks
    mock_es_service = AsyncMock()
    mock_es_service.check_connection.return_value = {"status": "up", "cluster_health": "green"}
    mock_es_service.get_index_stats.return_value = {"total_productos": 100, "index_size_mb": 10.5}
    mock_es.return_value = mock_es_service
    
    mock_product_service = AsyncMock()
    mock_product_service.check_api_health.return_value = {"status": "up", "response_time_ms": 150}
    mock_product.return_value = mock_product_service
    
    mock_embedding_service = AsyncMock()
    mock_embedding_service.get_model_info.return_value = {
        "model_name": "test-model",
        "embedding_dimension": 384
    }
    mock_embedding.return_value = mock_embedding_service
    
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "services" in data
    assert "index_stats" in data


def test_search_endpoint_validation():
    """Test de validación del endpoint de búsqueda."""
    # Test con query vacío
    response = client.post("/api/v1/buscar", json={})
    assert response.status_code == 422  # Validation error
    
    # Test con query válido pero sin servicios
    response = client.post("/api/v1/buscar", json={
        "query": "smartphone",
        "top_k": 5
    })
    # Debería fallar por falta de servicios, pero la validación debe pasar
    assert response.status_code in [500, 503]  # Error de servicio, no de validación


def test_categories_endpoint():
    """Test del endpoint de categorías."""
    response = client.get("/api/v1/categories")
    # Sin servicios configurados, debería dar error de servidor
    assert response.status_code in [500, 503]


def test_stats_endpoint():
    """Test del endpoint de estadísticas."""
    response = client.get("/api/v1/stats")
    # Sin servicios configurados, debería dar error de servidor
    assert response.status_code in [500, 503]


class TestSearchRequestValidation:
    """Tests de validación para SearchRequest."""
    
    def test_valid_search_request(self):
        """Test con request válido."""
        from models.schemas import SearchRequest
        
        request = SearchRequest(
            query="smartphone",
            top_k=10,
            category="Electronics",
            price_min=100.0,
            price_max=500.0
        )
        
        assert request.query == "smartphone"
        assert request.top_k == 10
        assert request.category == "Electronics"
    
    def test_invalid_price_range(self):
        """Test con rango de precios inválido."""
        from models.schemas import SearchRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SearchRequest(
                query="smartphone",
                price_min=500.0,
                price_max=100.0  # price_max < price_min
            )
    
    def test_top_k_validation(self):
        """Test de validación del parámetro top_k."""
        from models.schemas import SearchRequest
        from pydantic import ValidationError
        
        # top_k muy grande
        with pytest.raises(ValidationError):
            SearchRequest(query="test", top_k=100)
        
        # top_k negativo  
        with pytest.raises(ValidationError):
            SearchRequest(query="test", top_k=-1)


class TestProductModel:
    """Tests para el modelo Product."""
    
    def test_product_creation(self):
        """Test de creación de producto."""
        from models.schemas import Product
        from datetime import datetime
        
        product_data = {
            "id": "test-123",
            "name": "Test Product",
            "description": "Test description",
            "price": "99.99",
            "image_url": "https://example.com/image.jpg",
            "category": "Test Category",
            "stock": 10,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
        
        product = Product(**product_data)
        
        assert product.id == "test-123"
        assert product.name == "Test Product"
        assert isinstance(product.price, (int, float))
        assert isinstance(product.created_at, datetime)
    
    def test_price_conversion(self):
        """Test de conversión automática de precio."""
        from models.schemas import Product
        
        # Precio como string
        product_data = {
            "id": "test-123",
            "name": "Test Product", 
            "description": "Test description",
            "price": "123.45",
            "image_url": "https://example.com/image.jpg",
            "category": "Test Category",
            "stock": 10,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
        
        product = Product(**product_data)
        assert product.price == 123.45
        assert isinstance(product.price, float)