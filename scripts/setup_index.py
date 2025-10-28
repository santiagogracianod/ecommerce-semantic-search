"""Script para configurar el índice de Elasticsearch."""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.elasticsearch_service import get_elasticsearch_service
from utils.logger import get_logger

logger = get_logger(__name__)


async def setup_index():
    """Configura el índice de Elasticsearch con el mapping correcto."""
    logger.info("Iniciando configuración del índice de Elasticsearch")
    
    es_service = get_elasticsearch_service()
    
    try:
        # Verificar conexión
        logger.info("Verificando conexión con Elasticsearch...")
        health = await es_service.check_connection()
        
        if health["status"] != "up":
            logger.error("No se puede conectar con Elasticsearch")
            logger.error(f"Estado: {health}")
            return False
        
        logger.info(f"Conexión exitosa. Estado del cluster: {health.get('cluster_health', 'unknown')}")
        
        # Crear índice
        logger.info("Creando índice con mapping configurado...")
        success = await es_service.create_index()
        
        if success:
            logger.info("✅ Índice configurado exitosamente")
            
            # Mostrar información del índice
            stats = await es_service.get_index_stats()
            logger.info(f"Estadísticas del índice: {stats}")
            
            return True
        else:
            logger.error("❌ Error configurando el índice")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error configurando índice: {str(e)}")
        return False
    
    finally:
        await es_service.close()


async def reset_index():
    """Elimina y recrea el índice (¡CUIDADO: borra todos los datos!)."""
    logger.warning("🔥 ELIMINANDO ÍNDICE COMPLETO - Se perderán todos los datos")
    
    es_service = get_elasticsearch_service()
    
    try:
        # Eliminar índice existente
        deleted = await es_service.delete_index()
        if deleted:
            logger.info("Índice eliminado")
        
        # Crear nuevo índice
        created = await es_service.create_index()
        if created:
            logger.info("✅ Nuevo índice creado")
            return True
        else:
            logger.error("❌ Error creando nuevo índice")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error reseteando índice: {str(e)}")
        return False
    
    finally:
        await es_service.close()


def main():
    """Función principal del script."""
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("⚠️  ATENCIÓN: Vas a ELIMINAR todos los datos del índice")
        confirmation = input("¿Estás seguro? Escribe 'SI' para confirmar: ")
        
        if confirmation == "SI":
            success = asyncio.run(reset_index())
        else:
            print("Operación cancelada")
            return
    else:
        success = asyncio.run(setup_index())
    
    if success:
        print("\n🎉 Configuración completada exitosamente")
        print("Puedes proceder con la sincronización de productos")
    else:
        print("\n💥 Error en la configuración")
        sys.exit(1)


if __name__ == "__main__":
    main()