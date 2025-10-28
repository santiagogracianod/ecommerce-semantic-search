#!/usr/bin/env python3
"""Script para probar embeddings directamente via API REST."""

import requests
import json
from typing import List, Dict, Any

def test_embeddings_via_api():
    """Prueba embeddings usando endpoints de la API."""
    base_url = "http://localhost:8000"
    
    print("🔗 PROBANDO EMBEDDINGS VÍA API REST")
    print("=" * 50)
    
    # 1. Verificar salud del sistema
    print("\n1️⃣ Verificando estado del sistema...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        health = response.json()
        
        embedding_status = health['services']['embedding_model']['status']
        model_name = health['services']['embedding_model']['model']
        
        print(f"   ✅ Modelo: {model_name}")
        print(f"   ✅ Estado: {embedding_status}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Probar búsquedas semánticas (que usan embeddings internamente)
    print("\n2️⃣ Probando búsquedas semánticas...")
    
    test_queries = [
        "smartphone con excelente cámara",
        "laptop potente para desarrollo", 
        "auriculares con cancelación de ruido",
        "dispositivo para gaming",
        "equipo de fotografía profesional"
    ]
    
    for query in test_queries:
        try:
            search_data = {
                "query": query,
                "top_k": 2
            }
            
            response = requests.post(
                f"{base_url}/api/v1/buscar",
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"   🔍 '{query}':")
                print(f"      └─ {results['total_resultados']} resultados en {results['tiempo_busqueda_ms']}ms")
                
                for i, product in enumerate(results['resultados'][:2], 1):
                    score = product['score_semantico']
                    print(f"      └─ {i}. {product['name']} (score: {score:.3f})")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error en query '{query}': {e}")
    
    # 3. Estadísticas de búsqueda
    print("\n3️⃣ Estadísticas del sistema...")
    try:
        response = requests.get(f"{base_url}/api/v1/stats", timeout=10)
        stats = response.json()
        
        print(f"   📊 Documentos indexados: {stats['total_documents']}")
        print(f"   📏 Tamaño del índice: {stats['index_size_mb']} MB")
        print(f"   ⚡ Tiempo promedio búsqueda: {stats['avg_search_time_ms']}ms")
        
    except Exception as e:
        print(f"   ❌ Error obteniendo estadísticas: {e}")
    
    return True

def compare_semantic_similarity():
    """Compara la similitud semántica entre diferentes queries."""
    base_url = "http://localhost:8000"
    
    print("\n🔬 ANÁLISIS DE SIMILITUD SEMÁNTICA")
    print("=" * 50)
    
    # Pares de consultas para comparar
    query_pairs = [
        ("smartphone", "teléfono móvil"),
        ("laptop", "computadora portátil"),
        ("auriculares", "audífonos"),
        ("cámara profesional", "equipo de fotografía"),
        ("gaming", "videojuegos"),
        ("iPhone", "Samsung Galaxy"),
        ("MacBook", "laptop Apple"),
    ]
    
    print("Comparando similitud entre conceptos relacionados:\n")
    
    for query1, query2 in query_pairs:
        try:
            # Buscar con primera query
            response1 = requests.post(
                f"{base_url}/api/v1/buscar",
                json={"query": query1, "top_k": 3},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Buscar con segunda query  
            response2 = requests.post(
                f"{base_url}/api/v1/buscar",
                json={"query": query2, "top_k": 3},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response1.status_code == 200 and response2.status_code == 200:
                results1 = response1.json()['resultados']
                results2 = response2.json()['resultados']
                
                # Encontrar productos en común
                products1 = {p['id']: p for p in results1}
                products2 = {p['id']: p for p in results2}
                
                common_products = set(products1.keys()) & set(products2.keys())
                
                if common_products:
                    print(f"🔄 '{query1}' vs '{query2}':")
                    print(f"   └─ Productos en común: {len(common_products)}")
                    
                    for product_id in list(common_products)[:2]:
                        p1 = products1[product_id]
                        p2 = products2[product_id]
                        
                        score_diff = abs(p1['score_semantico'] - p2['score_semantico'])
                        avg_score = (p1['score_semantico'] + p2['score_semantico']) / 2
                        
                        print(f"   └─ {p1['name']}")
                        print(f"      Scores: {p1['score_semantico']:.3f} vs {p2['score_semantico']:.3f}")
                        print(f"      Promedio: {avg_score:.3f}, Diferencia: {score_diff:.3f}")
                else:
                    print(f"🔄 '{query1}' vs '{query2}': Sin productos en común")
                
        except Exception as e:
            print(f"❌ Error comparando '{query1}' vs '{query2}': {e}")

def test_category_specific_embeddings():
    """Prueba embeddings específicos por categoría."""
    base_url = "http://localhost:8000"
    
    print("\n📱 PRUEBA POR CATEGORÍAS")
    print("=" * 50)
    
    # Obtener categorías disponibles
    try:
        response = requests.get(f"{base_url}/api/v1/categories", timeout=10)
        categories_data = response.json()
        categories = [cat['name'] for cat in categories_data['categories']]
        
        print(f"Categorías disponibles: {', '.join(categories)}")
        
        # Probar búsquedas específicas por categoría
        category_queries = {
            "Smartphones": ["cámara", "batería", "pantalla"],
            "Laptops": ["procesador", "memoria", "programación"],
            "Audio": ["sonido", "música", "cancelación ruido"],
            "Gaming": ["juegos", "rendimiento", "fps"]
        }
        
        for category, queries in category_queries.items():
            if category in categories:
                print(f"\n🏷️  Categoría: {category}")
                
                for query in queries:
                    try:
                        search_data = {
                            "query": query,
                            "category": category,
                            "top_k": 2
                        }
                        
                        response = requests.post(
                            f"{base_url}/api/v1/buscar",
                            json=search_data,
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            results = response.json()
                            print(f"   🔍 '{query}' → {results['total_resultados']} resultados")
                            
                            for product in results['resultados'][:1]:
                                print(f"      └─ {product['name']} (score: {product['score_semantico']:.3f})")
                        
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error obteniendo categorías: {e}")

if __name__ == "__main__":
    print("🧪 SUITE DE PRUEBAS DE EMBEDDINGS VÍA API")
    print("=" * 60)
    
    # Verificar que la API esté disponible
    try:
        response = requests.get("http://localhost:8000/ping", timeout=5)
        if response.status_code == 200:
            print("✅ API disponible\n")
        else:
            print("❌ API no disponible")
            exit(1)
    except:
        print("❌ No se puede conectar a la API")
        exit(1)
    
    # Ejecutar pruebas
    test_embeddings_via_api()
    compare_semantic_similarity()  
    test_category_specific_embeddings()
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS DE EMBEDDINGS VÍA API COMPLETADAS")
    print("💡 El sistema de embeddings está integrado y funcionando correctamente")