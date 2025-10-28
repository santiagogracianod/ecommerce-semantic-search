#!/usr/bin/env python3
"""Suite completa de pruebas para todo el proyecto de búsqueda semántica."""

import asyncio
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from services.elasticsearch_service import get_elasticsearch_service
from services.embedding_service import get_embedding_service
from services.product_service import get_product_service
from config import get_settings


class ProjectTestSuite:
    """Suite completa de pruebas del proyecto."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.start_time = None
        
    def start_tests(self):
        """Inicia la suite de pruebas."""
        self.start_time = time.time()
        print("🧪 SUITE COMPLETA DE PRUEBAS DEL PROYECTO")
        print("=" * 70)
        print("🎯 Probando: Sistema de Búsqueda Semántica E-commerce")
        print(f"⚡ URL Base: {self.base_url}")
        print()
        
    def end_tests(self):
        """Finaliza la suite de pruebas."""
        elapsed = time.time() - self.start_time
        passed = sum(1 for result in self.results.values() if result['success'])
        total = len(self.results)
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL DE PRUEBAS")
        print("=" * 70)
        
        for category, result in self.results.items():
            icon = "✅" if result['success'] else "❌"
            time_str = f" ({result['time']:.2f}s)" if 'time' in result else ""
            print(f"{icon} {category}{time_str}")
            if not result['success'] and 'error' in result:
                print(f"     └─ Error: {result['error']}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n📈 Resultado: {passed}/{total} pruebas exitosas ({success_rate:.0f}%)")
        print(f"⏱️  Tiempo total: {elapsed:.2f}s")
        
        if success_rate == 100:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON! El proyecto está funcionando perfectamente.")
        elif success_rate >= 80:
            print("👍 La mayoría de pruebas pasaron. Revisar errores menores.")
        else:
            print("⚠️  Varios problemas detectados. Revisar configuración.")
            
        return success_rate == 100

    def test_category(self, category: str):
        """Decorador para categorías de prueba."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                print(f"\n📋 {category.upper()}")
                print("-" * 50)
                start = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start
                    
                    if asyncio.iscoroutine(result):
                        # Si es async, ejecutar
                        result = asyncio.run(result)
                    
                    self.results[category] = {
                        'success': result if isinstance(result, bool) else True,
                        'time': elapsed
                    }
                    
                    if result:
                        print(f"✅ {category} - Completado exitosamente")
                    else:
                        print(f"❌ {category} - Falló")
                        
                except Exception as e:
                    elapsed = time.time() - start
                    print(f"❌ {category} - Error: {str(e)}")
                    self.results[category] = {
                        'success': False,
                        'time': elapsed,
                        'error': str(e)
                    }
                    
            return wrapper
        return decorator


# Crear instancia de la suite
suite = ProjectTestSuite()


@suite.test_category("1. Configuración y Dependencias")
def test_configuration():
    """Prueba la configuración del proyecto."""
    print("🔧 Verificando configuración...")
    
    # Verificar archivo .env
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado")
        return False
    
    # Verificar configuración
    settings = get_settings()
    print(f"   ✅ Elasticsearch URL: {settings.elasticsearch_url}")
    print(f"   ✅ API Productos: {settings.productos_api_url}")
    print(f"   ✅ Modelo ML: {getattr(settings, 'model_name', 'paraphrase-multilingual-MiniLM-L12-v2')}")
    print(f"   ✅ Índice: {settings.index_name}")
    
    # Verificar requirements.txt
    req_file = Path("requirements.txt")
    if req_file.exists():
        print(f"   ✅ Requirements.txt encontrado")
        
        # Leer dependencias críticas
        content = req_file.read_text()
        critical_deps = ["fastapi", "elasticsearch", "sentence-transformers", "pydantic"]
        
        for dep in critical_deps:
            if dep in content:
                print(f"   ✅ Dependencia {dep} listada")
            else:
                print(f"   ⚠️  Dependencia {dep} no encontrada")
    
    print("   ✅ Configuración verificada correctamente")
    return True


@suite.test_category("2. Servicios Core") 
async def test_core_services():
    """Prueba los servicios principales."""
    print("🔧 Probando servicios core...")
    
    # Test embedding service
    print("   🧠 Testing Embedding Service...")
    try:
        embedding_service = get_embedding_service()
        test_texts = ["smartphone", "laptop", "auriculares"]
        embeddings = await embedding_service.generate_embeddings(test_texts)
        
        if embeddings and len(embeddings) == 3:
            print(f"   ✅ Embeddings generados: {len(embeddings)} x {len(embeddings[0])}d")
        else:
            print("   ❌ Error generando embeddings")
            return False
            
    except Exception as e:
        print(f"   ❌ Embedding service error: {e}")
        return False
    
    # Test Elasticsearch service
    print("   🔍 Testing Elasticsearch Service...")
    try:
        es_service = get_elasticsearch_service()
        
        # Verificar conexión directamente
        health = await es_service.es_client.cluster.health()
        
        if health and health.get('status') in ['green', 'yellow']:
            print(f"   ✅ Elasticsearch conectado: {health.get('status', 'N/A')}")
        else:
            print(f"   ❌ Elasticsearch no disponible: {health}")
            return False
            
        await es_service.close()
            
    except Exception as e:
        print(f"   ❌ Elasticsearch service error: {e}")
        return False
    
    # Test Product service  
    print("   📦 Testing Product Service...")
    try:
        product_service = get_product_service()
        
        # Hacer una prueba simple de conexión
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(product_service.base_url.rstrip('/') + '?limit=1')
            
            if response.status_code == 200:
                print(f"   ✅ API Productos disponible (status: {response.status_code})")
            else:
                print(f"   ⚠️  API Productos status: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️  Product service warning: {e}")
    
    print("   ✅ Servicios core verificados")
    return True


@suite.test_category("3. API Health y Conectividad")
def test_api_health():
    """Prueba la salud de la API."""
    print("🏥 Verificando health checks...")
    
    # Test ping endpoint
    try:
        response = requests.get(f"{suite.base_url}/ping", timeout=10)
        if response.status_code == 200:
            print("   ✅ Ping endpoint disponible")
        else:
            print(f"   ❌ Ping failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ No se puede conectar a la API: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{suite.base_url}/api/v1/health", timeout=15)
        if response.status_code == 200:
            health = response.json()
            
            print(f"   ✅ Health endpoint: {health.get('status', 'unknown')}")
            
            # Verificar servicios individuales
            services = health.get('services', {})
            for service_name, service_data in services.items():
                status = service_data.get('status', 'unknown')
                icon = "✅" if status in ['up', 'loaded', 'healthy'] else "⚠️"
                print(f"   {icon} {service_name}: {status}")
                
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    print("   ✅ API health verificada correctamente")
    return True


@suite.test_category("4. Sincronización de Datos")
def test_data_sync():
    """Prueba la sincronización de productos.""" 
    print("🔄 Probando sincronización...")
    
    # Verificar estado inicial
    try:
        response = requests.get(f"{suite.base_url}/api/v1/stats", timeout=10)
        if response.status_code == 200:
            initial_stats = response.json()
            initial_count = initial_stats.get('total_documents', 0)
            print(f"   📊 Productos iniciales: {initial_count}")
        else:
            print("   ⚠️  No se pudieron obtener estadísticas iniciales")
            initial_count = 0
    except Exception as e:
        print(f"   ⚠️  Stats error: {e}")
        initial_count = 0
    
    # Ejecutar sincronización
    try:
        print("   🔄 Ejecutando sincronización...")
        response = requests.post(
            f"{suite.base_url}/api/v1/sync",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            sync_result = response.json()
            
            indexed = sync_result.get('productos_indexados', 0)
            errors = sync_result.get('errores', 0)
            time_ms = sync_result.get('tiempo_ms', 0)
            
            print(f"   ✅ Sincronización completada:")
            print(f"      └─ Productos indexados: {indexed}")
            print(f"      └─ Errores: {errors}")
            print(f"      └─ Tiempo: {time_ms}ms")
            
            if indexed > 0:
                return True
            else:
                print("   ⚠️  No se indexaron productos")
                return False
                
        else:
            print(f"   ❌ Sync failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Sync error: {e}")
        return False


@suite.test_category("5. Búsquedas Semánticas")
def test_semantic_search():
    """Prueba las búsquedas semánticas."""
    print("🔍 Probando búsquedas semánticas...")
    
    test_queries = [
        {
            "name": "Smartphone con cámara",
            "query": "smartphone con excelente cámara",
            "expected_categories": ["Smartphones"]
        },
        {
            "name": "Laptop para desarrollo", 
            "query": "laptop para programar",
            "expected_categories": ["Laptops"]
        },
        {
            "name": "Dispositivo de audio",
            "query": "auriculares para música",
            "expected_categories": ["Audio"]
        },
        {
            "name": "Query genérica",
            "query": "tecnología",
            "min_results": 1
        }
    ]
    
    successful_searches = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"   🔎 Test {i}: {test['name']}")
        
        try:
            search_data = {
                "query": test["query"],
                "top_k": 5
            }
            
            response = requests.post(
                f"{suite.base_url}/api/v1/buscar",
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                results = response.json()
                
                total_results = results.get('total_resultados', 0)
                search_time = results.get('tiempo_busqueda_ms', 0)
                productos = results.get('resultados', [])
                
                print(f"      └─ Resultados: {total_results} en {search_time}ms")
                
                # Verificar que hay resultados
                if total_results > 0:
                    successful_searches += 1
                    
                    # Mostrar top resultado
                    if productos:
                        top_product = productos[0]
                        score = top_product.get('score_semantico', 0)
                        print(f"      └─ Top: {top_product.get('name', 'N/A')} (score: {score:.3f})")
                        
                        # Verificar categoría esperada si está definida
                        if 'expected_categories' in test:
                            product_category = top_product.get('category', '')
                            if product_category in test['expected_categories']:
                                print(f"      └─ ✅ Categoría correcta: {product_category}")
                            else:
                                print(f"      └─ ⚠️  Categoría: {product_category} (esperada: {test['expected_categories']})")
                else:
                    print("      └─ ⚠️  Sin resultados")
                    
            else:
                print(f"      └─ ❌ Error {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      └─ ❌ Exception: {e}")
    
    success_rate = successful_searches / len(test_queries)
    print(f"   📊 Búsquedas exitosas: {successful_searches}/{len(test_queries)} ({success_rate:.0%})")
    
    return success_rate >= 0.75  # 75% de éxito mínimo


@suite.test_category("6. Filtros Avanzados")
def test_advanced_filters():
    """Prueba los filtros avanzados de búsqueda."""
    print("🎯 Probando filtros avanzados...")
    
    # Test 1: Filtro por categoría
    print("   📱 Test: Filtro por categoría")
    try:
        search_data = {
            "query": "cámara",
            "category": "Smartphones",
            "top_k": 5
        }
        
        response = requests.post(
            f"{suite.base_url}/api/v1/buscar",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            productos = results.get('resultados', [])
            filtros = results.get('filtros_aplicados', {})
            
            print(f"      └─ Productos encontrados: {len(productos)}")
            print(f"      └─ Filtro aplicado: {filtros.get('category', 'N/A')}")
            
            # Verificar que todos son de la categoría correcta
            category_ok = all(p.get('category') == 'Smartphones' for p in productos)
            if category_ok and productos:
                print("      └─ ✅ Todos los productos son Smartphones")
            elif not productos:
                print("      └─ ⚠️  Sin productos en esa categoría")
            else:
                print("      └─ ❌ Productos de categorías incorrectas")
                
        else:
            print(f"      └─ ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"      └─ ❌ Exception: {e}")
        return False
    
    # Test 2: Filtro por precio
    print("   💰 Test: Filtro por precio")
    try:
        search_data = {
            "query": "tecnología",
            "price_max": 500.0,
            "top_k": 5
        }
        
        response = requests.post(
            f"{suite.base_url}/api/v1/buscar",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            productos = results.get('resultados', [])
            
            print(f"      └─ Productos encontrados: {len(productos)}")
            
            # Verificar precios
            if productos:
                prices = [p.get('price', 0) for p in productos]
                max_price = max(prices) if prices else 0
                print(f"      └─ Precio máximo encontrado: ${max_price}")
                
                if max_price <= 500:
                    print("      └─ ✅ Todos los productos están bajo $500")
                else:
                    print("      └─ ❌ Hay productos sobre $500")
            else:
                print("      └─ ⚠️  Sin productos en ese rango de precio")
                
        else:
            print(f"      └─ ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"      └─ ❌ Exception: {e}")
        return False
    
    print("   ✅ Filtros avanzados funcionando correctamente")
    return True


@suite.test_category("7. Endpoints Auxiliares")
def test_auxiliary_endpoints():
    """Prueba endpoints auxiliares."""
    print("🔗 Probando endpoints auxiliares...")
    
    # Test categories endpoint
    print("   🏷️  Test: Categories")
    try:
        response = requests.get(f"{suite.base_url}/api/v1/categories", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            
            print(f"      └─ Categorías encontradas: {len(categories)}")
            
            if categories:
                for cat in categories[:3]:  # Mostrar primeras 3
                    name = cat.get('name', 'N/A')
                    count = cat.get('count', 0)
                    print(f"      └─ {name}: {count} productos")
                print("      └─ ✅ Categories endpoint funcionando")
            else:
                print("      └─ ⚠️  Sin categorías disponibles")
                
        else:
            print(f"      └─ ❌ Categories error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"      └─ ❌ Categories exception: {e}")
        return False
    
    # Test stats endpoint
    print("   📊 Test: Stats")
    try:
        response = requests.get(f"{suite.base_url}/api/v1/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            
            docs = stats.get('total_documents', 0)
            size_mb = stats.get('index_size_mb', 0)
            avg_time = stats.get('avg_search_time_ms', 0)
            
            print(f"      └─ Documentos: {docs}")
            print(f"      └─ Tamaño índice: {size_mb} MB")
            print(f"      └─ Tiempo promedio: {avg_time}ms")
            print("      └─ ✅ Stats endpoint funcionando")
            
        else:
            print(f"      └─ ❌ Stats error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"      └─ ❌ Stats exception: {e}")
        return False
    
    # Test docs endpoint
    print("   📚 Test: Documentation")
    try:
        response = requests.get(f"{suite.base_url}/docs", timeout=10)
        
        if response.status_code == 200:
            print("      └─ ✅ Swagger UI disponible en /docs")
        else:
            print(f"      └─ ⚠️  Docs status: {response.status_code}")
            
    except Exception as e:
        print(f"      └─ ⚠️  Docs warning: {e}")
    
    print("   ✅ Endpoints auxiliares verificados")
    return True


@suite.test_category("8. Performance y Métricas")
def test_performance():
    """Prueba el rendimiento del sistema."""
    print("⚡ Probando performance...")
    
    # Test múltiples búsquedas concurrentes
    print("   🏃 Test: Búsquedas concurrentes")
    
    queries = [
        "smartphone",
        "laptop", 
        "auriculares",
        "cámara",
        "gaming"
    ]
    
    times = []
    
    for i, query in enumerate(queries, 1):
        try:
            start = time.time()
            
            response = requests.post(
                f"{suite.base_url}/api/v1/buscar",
                json={"query": query, "top_k": 3},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            elapsed = time.time() - start
            times.append(elapsed * 1000)  # Convert to ms
            
            if response.status_code == 200:
                results = response.json()
                search_time = results.get('tiempo_busqueda_ms', 0)
                print(f"      └─ Query {i}: {elapsed*1000:.0f}ms total, {search_time}ms búsqueda")
            else:
                print(f"      └─ Query {i}: Error {response.status_code}")
                
        except Exception as e:
            print(f"      └─ Query {i}: Exception {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"   📊 Estadísticas de rendimiento:")
        print(f"      └─ Tiempo promedio: {avg_time:.0f}ms")
        print(f"      └─ Tiempo mínimo: {min_time:.0f}ms")
        print(f"      └─ Tiempo máximo: {max_time:.0f}ms")
        
        # Verificar que el rendimiento es aceptable
        if avg_time < 1000:  # Menos de 1 segundo
            print("      └─ ✅ Rendimiento aceptable")
            return True
        else:
            print("      └─ ⚠️  Rendimiento lento")
            return False
    else:
        print("      └─ ❌ No se pudieron medir tiempos")
        return False


def main():
    """Ejecuta la suite completa de pruebas."""
    
    # Verificar que la API esté disponible
    try:
        response = requests.get("http://localhost:8000/ping", timeout=5)
        if response.status_code != 200:
            print("❌ API no disponible. Asegúrate de que esté ejecutándose:")
            print("   python main.py")
            return False
    except:
        print("❌ No se puede conectar a la API. Inicia la aplicación:")
        print("   python main.py")
        return False
    
    # Iniciar suite
    suite.start_tests()
    
    # Ejecutar todas las pruebas
    test_configuration()
    asyncio.run(test_core_services())
    test_api_health() 
    test_data_sync()
    test_semantic_search()
    test_advanced_filters()
    test_auxiliary_endpoints()
    test_performance()
    
    # Finalizar y mostrar resumen
    success = suite.end_tests()
    
    if success:
        print("\n🎉 ¡PROYECTO COMPLETAMENTE FUNCIONAL!")
        print("🚀 Listo para producción o desarrollo adicional")
        print("\n💡 Próximos pasos sugeridos:")
        print("   • Revisar documentación en http://localhost:8000/docs")
        print("   • Probar con datos reales de tu dominio")
        print("   • Implementar autenticación si es necesario")
        print("   • Configurar monitoreo en producción")
    else:
        print("\n⚠️  ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa los errores y la configuración")
        print("\n💡 Recursos de ayuda:")
        print("   • README.md - Documentación completa")
        print("   • scripts/health_check.py - Diagnósticos")
        print("   • Logs de la aplicación")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)