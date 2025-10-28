"""Script para probar el sistema con productos de muestra."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.elasticsearch_service import get_elasticsearch_service
from models.schemas import Product, SearchRequest
from utils.logger import get_logger

logger = get_logger(__name__)


def create_sample_products():
    """Crea productos de muestra para testing."""
    products = [
        Product(
            id="sample-iphone-15-pro",
            name="iPhone 15 Pro Max",
            description="El iPhone más avanzado con chip A17 Pro, cámara de 48MP con zoom óptico 5x, pantalla Super Retina XDR de 6.7 pulgadas, batería de larga duración y resistencia al agua IP68. Perfecto para fotografía profesional y videografía.",
            price=1199.99,
            image_url="https://images.unsplash.com/photo-1592750475338-74b7b21085ab",
            category="Smartphones",
            stock=15,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-samsung-s24-ultra",
            name="Samsung Galaxy S24 Ultra",
            description="Smartphone premium con S Pen integrado, cámara de 200MP con zoom espacial 100x, pantalla Dynamic AMOLED 2X de 6.8 pulgadas, procesador Snapdragon 8 Gen 3. Ideal para productividad y creatividad.",
            price=1299.99,
            image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf",
            category="Smartphones", 
            stock=8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-macbook-air-m3",
            name="MacBook Air M3",
            description="Laptop ultraligera con chip Apple M3, pantalla Liquid Retina de 13.6 pulgadas, hasta 18 horas de batería, 8GB RAM y 256GB SSD. Perfecta para programadores, diseñadores y estudiantes. Silenciosa sin ventiladores.",
            price=1099.99,
            image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
            category="Laptops",
            stock=12,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-dell-xps-15",
            name="Dell XPS 15 Gaming",
            description="Laptop de alto rendimiento con Intel Core i7, NVIDIA RTX 4060, 16GB RAM DDR5, SSD 512GB, pantalla 4K OLED de 15.6 pulgadas. Ideal para gaming, desarrollo de software y edición de video profesional.",
            price=1899.99,
            image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853",
            category="Laptops",
            stock=6,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-ipad-pro-12",
            name="iPad Pro 12.9 pulgadas",
            description="Tablet profesional con chip M2, pantalla Liquid Retina XDR mini-LED, Apple Pencil compatible, Magic Keyboard compatible. Perfecto para diseño gráfico, toma de notas y entretenimiento multimedia.",
            price=999.99,
            image_url="https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0",
            category="Tablets",
            stock=10,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-canon-eos-r5",
            name="Cámara Canon EOS R5",
            description="Cámara mirrorless profesional de 45MP con grabación de video 8K, estabilización de imagen en el cuerpo, enfoque automático Dual Pixel CMOS AF II. Equipo profesional para fotografía y videografía de alta gama.",
            price=3899.99,
            image_url="https://images.unsplash.com/photo-1606983340126-99ab4feaa64a",
            category="Cámaras",
            stock=4,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-airpods-pro-2",
            name="Apple AirPods Pro 2da Gen",
            description="Audífonos inalámbricos con cancelación activa de ruido adaptativa, audio espacial personalizado, hasta 6 horas de reproducción, estuche MagSafe. Perfectos para música, llamadas y entretenimiento.",
            price=249.99,
            image_url="https://images.unsplash.com/photo-1606983340126-99ab4feaa64a",
            category="Audio",
            stock=25,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Product(
            id="sample-nintendo-switch",
            name="Nintendo Switch OLED",
            description="Consola de videojuegos híbrida con pantalla OLED de 7 pulgadas, 64GB almacenamiento interno, controles Joy-Con, dock para TV. Ideal para gaming familiar, entretenimiento y juegos exclusivos de Nintendo.",
            price=349.99,
            image_url="https://images.unsplash.com/photo-1606144042614-b2417e99c4e3",
            category="Gaming",
            stock=18,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    return products


async def index_sample_products():
    """Indexa los productos de muestra en Elasticsearch."""
    print("📦 Indexando productos de muestra...")
    
    es_service = get_elasticsearch_service()
    
    try:
        # Crear productos de muestra
        products = create_sample_products()
        
        print(f"Creando {len(products)} productos de muestra...")
        
        # Indexar en lotes
        result = await es_service.index_products_batch(products)
        
        print(f"✅ Productos indexados: {result['indexed']}")
        if result['errors'] > 0:
            print(f"⚠️  Errores: {result['errors']}")
        
        return result['indexed'] > 0
        
    except Exception as e:
        print(f"❌ Error indexando productos: {str(e)}")
        return False
    finally:
        await es_service.close()


async def test_semantic_searches():
    """Prueba búsquedas semánticas con diferentes queries."""
    print("\n🔍 Probando búsquedas semánticas...")
    
    es_service = get_elasticsearch_service()
    
    test_queries = [
        "teléfono con buena cámara",
        "laptop para programar", 
        "dispositivo para entretenimiento",
        "equipo profesional fotografía",
        "regalo tecnológico económico",
        "gaming portátil"
    ]
    
    try:
        for query in test_queries:
            print(f"\n📋 Buscar: '{query}'")
            
            search_request = SearchRequest(query=query, top_k=3)
            results = await es_service.search_products(search_request)
            
            print(f"   └─ Resultados: {results['total_resultados']} en {results['tiempo_busqueda_ms']}ms")
            
            for i, product in enumerate(results['resultados'][:2], 1):
                score = product.score_semantico
                print(f"   └─ {i}. {product.name} (score: {score:.3f}, {product.relevancia})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en búsquedas: {str(e)}")
        return False
    finally:
        await es_service.close()


async def test_filtered_searches():
    """Prueba búsquedas con filtros."""
    print("\n🎯 Probando búsquedas con filtros...")
    
    es_service = get_elasticsearch_service()
    
    try:
        # Búsqueda por categoría
        print("\n📱 Búsqueda en categoría 'Smartphones':")
        search_request = SearchRequest(
            query="cámara",
            category="Smartphones",
            top_k=5
        )
        results = await es_service.search_products(search_request)
        print(f"   └─ Resultados: {results['total_resultados']}")
        for product in results['resultados']:
            print(f"   └─ {product.name} (${product.price})")
        
        # Búsqueda por rango de precio
        print("\n💰 Búsqueda con precio máximo $500:")
        search_request = SearchRequest(
            query="entretenimiento",
            price_max=500.0,
            top_k=5
        )
        results = await es_service.search_products(search_request)
        print(f"   └─ Resultados: {results['total_resultados']}")
        for product in results['resultados']:
            print(f"   └─ {product.name} (${product.price})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en búsquedas filtradas: {str(e)}")
        return False
    finally:
        await es_service.close()


async def test_categories():
    """Prueba obtener categorías disponibles."""
    print("\n🏷️  Obteniendo categorías disponibles...")
    
    es_service = get_elasticsearch_service()
    
    try:
        categories = await es_service.get_categories()
        
        print(f"✅ Categorías encontradas: {len(categories)}")
        for cat in categories:
            print(f"   └─ {cat.name}: {cat.count} productos")
        
        return len(categories) > 0
        
    except Exception as e:
        print(f"❌ Error obteniendo categorías: {str(e)}")
        return False
    finally:
        await es_service.close()


async def main():
    """Ejecuta todas las pruebas."""
    print("🧪 DEMO COMPLETA DEL SISTEMA DE BÚSQUEDA SEMÁNTICA")
    print("=" * 60)
    
    # Indexar productos de muestra
    indexed = await index_sample_products()
    if not indexed:
        print("❌ No se pudieron indexar los productos")
        return False
    
    # Probar búsquedas semánticas
    searches_ok = await test_semantic_searches()
    
    # Probar búsquedas con filtros
    filters_ok = await test_filtered_searches()
    
    # Probar categorías
    categories_ok = await test_categories()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LA DEMO")
    
    tests = [
        ("Indexación de productos", indexed),
        ("Búsquedas semánticas", searches_ok),
        ("Filtros y rangos", filters_ok), 
        ("Categorías", categories_ok)
    ]
    
    for test_name, success in tests:
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}")
    
    all_passed = all(success for _, success in tests)
    
    if all_passed:
        print("\n🎉 DEMO COMPLETADA EXITOSAMENTE")
        print("✨ El sistema de búsqueda semántica está funcionando perfectamente")
        print("\n💡 Prueba más búsquedas en: http://localhost:8000/docs")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)