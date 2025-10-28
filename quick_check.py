#!/usr/bin/env python3
"""Script de verificación rápida para desarrollo diario."""

import requests
import json
import sys
import time
from typing import Dict, Any


def quick_check() -> bool:
    """Verificación rápida del sistema."""
    base_url = "http://localhost:8000"
    
    print("⚡ VERIFICACIÓN RÁPIDA DEL PROYECTO")
    print("=" * 50)
    
    # 1. Ping básico
    print("1️⃣ Conectividad...")
    try:
        response = requests.get(f"{base_url}/ping", timeout=5)
        if response.status_code == 200:
            print("   ✅ API disponible")
        else:
            print(f"   ❌ API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ No conecta: {e}")
        print("\n💡 Solución: Ejecuta 'python main.py'")
        return False
    
    # 2. Health check
    print("2️⃣ Servicios...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            status = health.get('status', 'unknown')
            
            if status == 'healthy':
                print("   ✅ Todos los servicios operativos")
            else:
                print(f"   ⚠️  Estado: {status}")
                
            # Mostrar servicios individuales
            services = health.get('services', {})
            for name, data in services.items():
                service_status = data.get('status', 'unknown')
                icon = "✅" if service_status in ['up', 'loaded', 'healthy'] else "⚠️"
                print(f"      {icon} {name}: {service_status}")
                
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health error: {e}")
        return False
    
    # 3. Datos indexados
    print("3️⃣ Datos...")
    try:
        response = requests.get(f"{base_url}/api/v1/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            docs = stats.get('total_documents', 0)
            size_mb = stats.get('index_size_mb', 0)
            
            if docs > 0:
                print(f"   ✅ {docs} productos indexados ({size_mb} MB)")
            else:
                print("   ⚠️  Sin productos - Ejecuta sincronización")
                print("      curl -X POST http://localhost:8000/api/v1/sync")
                
        else:
            print(f"   ❌ Stats error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # 4. Búsqueda rápida
    print("4️⃣ Búsqueda...")
    try:
        search_data = {"query": "smartphone", "top_k": 1}
        
        start = time.time()
        response = requests.post(
            f"{base_url}/api/v1/buscar",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            results = response.json()
            total = results.get('total_resultados', 0)
            search_time = results.get('tiempo_busqueda_ms', 0)
            
            print(f"   ✅ Búsqueda OK: {total} resultados en {search_time}ms (total: {elapsed*1000:.0f}ms)")
            
            if results.get('resultados'):
                top_product = results['resultados'][0]
                score = top_product.get('score_semantico', 0)
                print(f"      └─ Top: {top_product.get('name', 'N/A')} (score: {score:.3f})")
        else:
            print(f"   ❌ Search error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Search error: {e}")
        return False
    
    print("\n✅ VERIFICACIÓN COMPLETA - Sistema funcionando")
    print(f"📚 Docs: {base_url}/docs")
    return True


def demo_search():
    """Demo interactivo de búsqueda."""
    base_url = "http://localhost:8000"
    
    print("\n🎮 DEMO INTERACTIVO DE BÚSQUEDA")
    print("=" * 50)
    print("Escribe consultas para probar el sistema (o 'exit' para salir)")
    
    while True:
        try:
            query = input("\n🔍 Buscar: ").strip()
            
            if query.lower() == 'exit':
                break
            elif not query:
                continue
                
            # Ejecutar búsqueda
            start = time.time()
            
            response = requests.post(
                f"{base_url}/api/v1/buscar",
                json={"query": query, "top_k": 3},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            elapsed = time.time() - start
            
            if response.status_code == 200:
                results = response.json()
                
                total = results.get('total_resultados', 0)
                search_time = results.get('tiempo_busqueda_ms', 0)
                productos = results.get('resultados', [])
                
                print(f"\n📊 {total} resultados en {search_time}ms (total: {elapsed*1000:.0f}ms)")
                
                if productos:
                    for i, product in enumerate(productos, 1):
                        name = product.get('name', 'N/A')
                        category = product.get('category', 'N/A')
                        price = product.get('price', 0)
                        score = product.get('score_semantico', 0)
                        relevancia = product.get('relevancia', 'N/A')
                        
                        print(f"{i}. {name}")
                        print(f"   └─ {category} - ${price} - Score: {score:.3f} ({relevancia})")
                else:
                    print("Sin resultados")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def show_project_info():
    """Muestra información del proyecto."""
    print("\n📋 INFORMACIÓN DEL PROYECTO")
    print("=" * 50)
    
    print("🎯 E-commerce Semantic Search")
    print("📚 Búsqueda semántica para productos e-commerce")
    print()
    
    print("🔗 URLs Importantes:")
    print("   • API Base: http://localhost:8000")
    print("   • Documentación: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("   • Health: http://localhost:8000/api/v1/health")
    print()
    
    print("🛠️ Comandos Útiles:")
    print("   • Iniciar: python main.py")
    print("   • Sincronizar: curl -X POST http://localhost:8000/api/v1/sync")
    print("   • Health: python scripts/health_check.py")
    print("   • Setup índice: python scripts/setup_index.py")
    print()
    
    print("🧪 Scripts de Testing:")
    print("   • Completo: python test_complete_project.py")
    print("   • Rápido: python quick_check.py")
    print("   • Embeddings: python test_embeddings.py")
    print("   • API: python test_api_embeddings.py")


def main():
    """Función principal."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "demo":
            if quick_check():
                demo_search()
            return
        elif command == "info":
            show_project_info()
            return
        elif command == "--help" or command == "help":
            print("📚 USO: python quick_check.py [comando]")
            print()
            print("Comandos disponibles:")
            print("   (sin args) - Verificación rápida")
            print("   demo      - Demo interactivo de búsqueda")
            print("   info      - Información del proyecto")
            print("   help      - Esta ayuda")
            return
    
    # Verificación por defecto
    success = quick_check()
    
    if success:
        print("\n💡 Opciones:")
        print("   python quick_check.py demo  # Demo interactivo")
        print("   python quick_check.py info  # Info del proyecto")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)