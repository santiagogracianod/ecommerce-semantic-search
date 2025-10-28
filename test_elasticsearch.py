"""Script específico para probar la conexión y funcionalidad de Elasticsearch."""
import asyncio
import json
from datetime import datetime

from services.elasticsearch_service import get_elasticsearch_service
from services.embedding_service import get_embedding_service
from models.schemas import Product
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_basic_connection():
    """Prueba la conexión básica con Elasticsearch."""
    print("🔌 Probando conexión básica...")
    
    es_service = get_elasticsearch_service()
    
    try:
        health = await es_service.check_connection()
        print(f"Estado: {health['status']}")
        print(f"Salud del cluster: {health.get('cluster_health', 'unknown')}")
        print(f"Nodos: {health.get('number_of_nodes', 0)}")
        
        return health["status"] == "up"
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await es_service.close()


async def test_index_operations():
    """Prueba las operaciones básicas del índice."""
    print("\n📋 Probando operaciones del índice...")
    
    es_service = get_elasticsearch_service()
    
    try:
        # Crear índice
        print("Creando índice...")
        success = await es_service.create_index()
        if success:
            print("✅ Índice creado/verificado")
        else:
            print("❌ Error creando índice")
            return False
        
        # Verificar estadísticas
        print("Obteniendo estadísticas...")
        stats = await es_service.get_index_stats()
        print(f"Productos: {stats.get('total_productos', 0)}")
        print(f"Tamaño: {stats.get('index_size_mb', 0)} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await es_service.close()


async def test_product_indexing():
    """Prueba indexar un producto de ejemplo."""
    print("\n📦 Probando indexación de producto...")
    
    es_service = get_elasticsearch_service()
    embedding_service = get_embedding_service()
    
    try:
        # Crear producto de prueba
        test_product = Product(
            id="test-product-123",
            name="iPhone 15 Pro Test",
            description="Smartphone de prueba con excelente cámara y rendimiento",
            price="999.99",
            category="Smartphones",
            stock=10,
            image_url="https://example.com/iphone.jpg",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print(f"Producto de prueba: {test_product.name}")
        
        # Indexar producto
        success = await es_service.index_product(test_product)
        
        if success:
            print("✅ Producto indexado correctamente")
            
            # Verificar que se puede recuperar
            stats = await es_service.get_index_stats()
            print(f"Total productos después de indexar: {stats.get('total_productos', 0)}")
            
            return True
        else:
            print("❌ Error indexando producto")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await es_service.close()


async def test_semantic_search():
    """Prueba una búsqueda semántica básica."""
    print("\n🔍 Probando búsqueda semántica...")
    
    es_service = get_elasticsearch_service()
    
    try:
        from models.schemas import SearchRequest
        
        # Crear request de búsqueda
        search_request = SearchRequest(
            query="smartphone con buena cámara",
            top_k=5
        )
        
        print(f"Consulta: '{search_request.query}'")
        
        # Ejecutar búsqueda
        results = await es_service.search_products(search_request)
        
        print(f"Resultados encontrados: {results['total_resultados']}")
        print(f"Tiempo de búsqueda: {results['tiempo_busqueda_ms']}ms")
        
        # Mostrar resultados
        if results['resultados']:
            print("\nPrimeros resultados:")
            for i, product in enumerate(results['resultados'][:3]):
                print(f"  {i+1}. {product.name} (score: {product.score_semantico:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await es_service.close()


async def run_full_test():
    """Ejecuta todas las pruebas de Elasticsearch."""
    print("🧪 PRUEBAS COMPLETAS DE ELASTICSEARCH")
    print("=" * 50)
    
    start_time = datetime.now()
    
    tests = [
        ("Conexión Básica", test_basic_connection()),
        ("Operaciones de Índice", test_index_operations()),
        ("Indexación de Producto", test_product_indexing()),
        ("Búsqueda Semántica", test_semantic_search())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = await test_coro
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {status} - {test_name}")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Tiempo total: {elapsed:.2f}s")
    print(f"📈 Pruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TODAS LAS PRUEBAS PASARON")
        print("✨ Elasticsearch está funcionando correctamente")
    else:
        print(f"\n⚠️  {total - passed} PRUEBAS FALLARON")
        print("🔧 Revisa la configuración de Elasticsearch")
    
    return passed == total


async def main():
    """Función principal."""
    success = await run_full_test()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)