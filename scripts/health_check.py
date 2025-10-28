"""Script para verificar el estado de todos los servicios."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.elasticsearch_service import get_elasticsearch_service
from services.product_service import get_product_service  
from services.embedding_service import get_embedding_service
from utils.logger import get_logger

logger = get_logger(__name__)


def print_status(service_name: str, status: dict, details: bool = False):
    """Imprime el estado de un servicio de forma legible."""
    status_icon = "✅" if status.get("status") == "up" or status.get("status") == "loaded" else "❌"
    print(f"{status_icon} {service_name}: {status.get('status', 'unknown')}")
    
    if details:
        for key, value in status.items():
            if key != "status":
                print(f"   └─ {key}: {value}")


async def check_elasticsearch():
    """Verifica el estado de Elasticsearch."""
    print("\n🔍 Verificando Elasticsearch...")
    
    es_service = get_elasticsearch_service()
    
    try:
        # Verificar conexión básica
        health = await es_service.check_connection()
        print_status("Conexión", health, details=True)
        
        if health["status"] == "up":
            # Verificar índice
            try:
                stats = await es_service.get_index_stats()
                print(f"   └─ Productos indexados: {stats.get('total_productos', 0)}")
                print(f"   └─ Tamaño del índice: {stats.get('index_size_mb', 0)} MB")
            except Exception as e:
                print(f"   └─ ⚠️  Error obteniendo estadísticas: {str(e)}")
        
        return health["status"] == "up"
        
    except Exception as e:
        print(f"❌ Error verificando Elasticsearch: {str(e)}")
        return False
    finally:
        await es_service.close()


async def check_products_api():
    """Verifica el estado de la API de productos."""
    print("\n🛍️  Verificando API de productos...")
    
    product_service = get_product_service()
    
    try:
        health = await product_service.check_api_health()
        print_status("API Productos", health, details=True)
        
        if health["status"] == "up":
            # Verificar que podemos obtener productos
            try:
                products = await product_service.get_products(skip=0, limit=1)
                print(f"   └─ Productos disponibles: ✅ (sample: {len(products)})")
            except Exception as e:
                print(f"   └─ ⚠️  Error obteniendo productos: {str(e)}")
        
        return health["status"] == "up"
        
    except Exception as e:
        print(f"❌ Error verificando API de productos: {str(e)}")
        return False


async def check_embedding_model():
    """Verifica el estado del modelo de embeddings."""
    print("\n🧠 Verificando modelo de embeddings...")
    
    embedding_service = get_embedding_service()
    
    try:
        # Intentar cargar el modelo y generar un embedding de prueba
        model_info = await embedding_service.get_model_info()
        print_status("Modelo", {"status": "loaded"}, details=False)
        
        for key, value in model_info.items():
            print(f"   └─ {key}: {value}")
        
        # Prueba de embedding
        test_embedding = await embedding_service.generate_embedding("test")
        print(f"   └─ Prueba de embedding: ✅ (dimensión: {len(test_embedding)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando modelo de embeddings: {str(e)}")
        print("   └─ Esto puede deberse a falta de internet para descargar el modelo")
        return False


async def comprehensive_health_check():
    """Ejecuta una verificación completa de salud."""
    print("🏥 VERIFICACIÓN COMPLETA DE SALUD DEL SISTEMA")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # Verificar todos los servicios
    es_ok = await check_elasticsearch()
    api_ok = await check_products_api()  
    model_ok = await check_embedding_model()
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE ESTADO")
    
    services_status = [
        ("Elasticsearch", es_ok),
        ("API de Productos", api_ok),
        ("Modelo de Embeddings", model_ok)
    ]
    
    all_ok = True
    for service, status in services_status:
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
        if not status:
            all_ok = False
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Tiempo de verificación: {elapsed:.2f}s")
    
    if all_ok:
        print("\n🎉 TODOS LOS SERVICIOS ESTÁN FUNCIONANDO CORRECTAMENTE")
        print("✨ El sistema está listo para ser usado")
        return True
    else:
        print("\n⚠️  ALGUNOS SERVICIOS TIENEN PROBLEMAS")
        print("🔧 Revisa los errores anteriores y configura los servicios necesarios")
        return False


async def quick_health_check():
    """Verificación rápida básica."""
    print("🚀 Verificación rápida...")
    
    try:
        es_service = get_elasticsearch_service()
        es_health = await es_service.check_connection()
        await es_service.close()
        
        product_service = get_product_service()
        api_health = await product_service.check_api_health()
        
        if es_health["status"] == "up" and api_health["status"] == "up":
            print("✅ Servicios básicos funcionando")
            return True
        else:
            print("❌ Problemas con servicios básicos")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {str(e)}")
        return False


def main():
    """Función principal del script."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = asyncio.run(quick_health_check())
    else:
        success = asyncio.run(comprehensive_health_check())
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()