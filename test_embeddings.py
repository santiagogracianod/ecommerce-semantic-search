#!/usr/bin/env python3
"""Script para probar el sistema de embeddings y similitud semántica."""

import asyncio
import sys
from pathlib import Path
import numpy as np
from typing import List, Tuple

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from services.embedding_service import get_embedding_service
from utils.logger import get_logger

logger = get_logger(__name__)


def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calcula la similitud coseno entre dos embeddings."""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Similitud coseno
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


async def test_basic_embeddings():
    """Prueba básica de generación de embeddings."""
    print("🧠 PRUEBA 1: Generación Básica de Embeddings")
    print("=" * 50)
    
    embedding_service = get_embedding_service()
    
    # Textos de prueba
    texts = [
        "smartphone con buena cámara",
        "teléfono móvil con fotografía excelente", 
        "laptop para programar",
        "computadora portátil para desarrolladores",
        "auriculares inalámbricos",
        "pizza italiana deliciosa"  # texto no relacionado
    ]
    
    print("📝 Generando embeddings para textos de prueba...")
    
    try:
        # Generar embeddings
        embeddings = await embedding_service.generate_embeddings(texts)
        
        print(f"✅ Embeddings generados exitosamente")
        print(f"📊 Cantidad: {len(embeddings)}")
        print(f"📏 Dimensiones: {len(embeddings[0]) if embeddings else 0}")
        
        # Mostrar estadísticas
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            norm = np.linalg.norm(embedding)
            mean_val = np.mean(embedding)
            std_val = np.std(embedding)
            
            print(f"\n{i+1}. '{text[:40]}...'")
            print(f"   └─ Norma: {norm:.4f}, Media: {mean_val:.4f}, Std: {std_val:.4f}")
        
        return embeddings, texts
        
    except Exception as e:
        print(f"❌ Error generando embeddings: {str(e)}")
        return None, None


async def test_semantic_similarity(embeddings: List[List[float]], texts: List[str]):
    """Prueba la similitud semántica entre textos."""
    print("\n🔍 PRUEBA 2: Similitud Semántica")
    print("=" * 50)
    
    if not embeddings or not texts:
        print("❌ No hay embeddings para probar")
        return
    
    print("📊 Matriz de similitud coseno:")
    print()
    
    # Crear matriz de similitud
    n = len(texts)
    similarities = []
    
    # Header
    print("Texto".ljust(25), end="")
    for i in range(n):
        print(f"{i+1:>6}", end="")
    print()
    print("-" * (25 + 6 * n))
    
    # Calcular y mostrar similitudes
    for i in range(n):
        row_similarities = []
        
        # Mostrar nombre del texto
        text_short = texts[i][:22] + "..." if len(texts[i]) > 22 else texts[i]
        print(f"{i+1}. {text_short}".ljust(25), end="")
        
        for j in range(n):
            similarity = calculate_similarity(embeddings[i], embeddings[j])
            row_similarities.append(similarity)
            
            # Color coding para similitud
            if similarity > 0.8:
                color_code = "🟢"  # Verde - muy similar
            elif similarity > 0.6:
                color_code = "🟡"  # Amarillo - similar
            elif similarity > 0.3:
                color_code = "🟠"  # Naranja - poco similar
            else:
                color_code = "🔴"  # Rojo - no similar
                
            print(f"{similarity:>5.2f}{'🔥' if i==j else color_code[0]}", end="")
        
        similarities.append(row_similarities)
        print()
    
    # Encontrar pares más similares (excluyendo autoreferencias)
    print(f"\n🎯 Pares más similares:")
    similar_pairs = []
    
    for i in range(n):
        for j in range(i+1, n):
            sim = similarities[i][j]
            similar_pairs.append((sim, i, j))
    
    # Ordenar por similitud
    similar_pairs.sort(reverse=True)
    
    for sim, i, j in similar_pairs[:3]:
        print(f"   └─ {sim:.3f}: '{texts[i][:30]}...' ↔ '{texts[j][:30]}...'")


async def test_product_embeddings():
    """Prueba embeddings con descripciones de productos reales."""
    print("\n📱 PRUEBA 3: Embeddings de Productos")
    print("=" * 50)
    
    embedding_service = get_embedding_service()
    
    # Productos de ejemplo
    productos = [
        {
            "name": "iPhone 15 Pro Max",
            "description": "Smartphone premium con chip A17 Pro, cámara de 48MP con zoom óptico 5x, pantalla Super Retina XDR de 6.7 pulgadas"
        },
        {
            "name": "Samsung Galaxy S24 Ultra", 
            "description": "Teléfono Android con S Pen, cámara de 200MP, pantalla Dynamic AMOLED de 6.8 pulgadas, procesador Snapdragon"
        },
        {
            "name": "MacBook Pro M3",
            "description": "Laptop profesional con chip Apple M3, pantalla Liquid Retina, ideal para desarrolladores y creativos"
        },
        {
            "name": "Canon EOS R5",
            "description": "Cámara mirrorless profesional de 45MP, grabación 8K, estabilización en cuerpo, enfoque automático"
        }
    ]
    
    # Preparar textos para embeddings
    product_texts = []
    for producto in productos:
        # Combinar nombre y descripción
        combined_text = f"{producto['name']} {producto['description']}"
        product_texts.append(combined_text)
    
    print("🔄 Generando embeddings para productos...")
    
    try:
        product_embeddings = await embedding_service.generate_embeddings(product_texts)
        
        print(f"✅ Embeddings de productos generados: {len(product_embeddings)}")
        
        # Queries de prueba
        queries = [
            "teléfono con cámara profesional",
            "smartphone para fotografía",
            "laptop para programación", 
            "computadora para desarrolladores",
            "cámara para video profesional",
            "equipo de fotografía avanzado"
        ]
        
        print(f"\n🔍 Probando {len(queries)} consultas...")
        
        query_embeddings = await embedding_service.generate_embeddings(queries)
        
        # Calcular similitudes
        print(f"\n📊 RESULTADOS DE BÚSQUEDA:")
        print("-" * 60)
        
        for i, query in enumerate(queries):
            print(f"\n🔎 Query: '{query}'")
            
            # Calcular similitud con cada producto
            query_similarities = []
            for j, producto in enumerate(productos):
                similarity = calculate_similarity(query_embeddings[i], product_embeddings[j])
                query_similarities.append((similarity, j, producto))
            
            # Ordenar por similitud
            query_similarities.sort(reverse=True)
            
            # Mostrar top 3
            for rank, (sim, idx, producto) in enumerate(query_similarities[:3], 1):
                relevancia = "🟢 Alta" if sim > 0.7 else "🟡 Media" if sim > 0.5 else "🔴 Baja"
                print(f"   {rank}. {sim:.3f} {relevancia} - {producto['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en embeddings de productos: {str(e)}")
        return False


async def test_multilingual_embeddings():
    """Prueba capacidades multilingües del modelo."""
    print("\n🌍 PRUEBA 4: Capacidades Multilingües")
    print("=" * 50)
    
    embedding_service = get_embedding_service()
    
    # Textos en diferentes idiomas con el mismo significado
    multilingual_texts = [
        # Español
        "teléfono inteligente con cámara excelente",
        # Inglés  
        "smartphone with excellent camera",
        # Francés
        "téléphone intelligent avec excellente caméra",
        # Italiano
        "smartphone con eccellente fotocamera",
        # Portugués
        "smartphone com excelente câmera"
    ]
    
    languages = ["🇪🇸 Español", "🇺🇸 Inglés", "🇫🇷 Francés", "🇮🇹 Italiano", "🇧🇷 Portugués"]
    
    print("🌐 Generando embeddings multilingües...")
    
    try:
        multi_embeddings = await embedding_service.generate_embeddings(multilingual_texts)
        
        print(f"✅ Embeddings multilingües generados: {len(multi_embeddings)}")
        
        # Calcular similitudes entre idiomas
        print(f"\n📊 Similitud entre idiomas (mismo concepto):")
        print("-" * 55)
        
        for i in range(len(multilingual_texts)):
            for j in range(i+1, len(multilingual_texts)):
                similarity = calculate_similarity(multi_embeddings[i], multi_embeddings[j])
                
                status = "🟢 Excelente" if similarity > 0.8 else "🟡 Buena" if similarity > 0.6 else "🔴 Pobre"
                print(f"{languages[i]} ↔ {languages[j]}: {similarity:.3f} {status}")
        
        # Promedio de similitud
        similarities = []
        for i in range(len(multilingual_texts)):
            for j in range(i+1, len(multilingual_texts)):
                similarities.append(calculate_similarity(multi_embeddings[i], multi_embeddings[j]))
        
        avg_similarity = np.mean(similarities)
        print(f"\n📈 Similitud promedio entre idiomas: {avg_similarity:.3f}")
        
        if avg_similarity > 0.7:
            print("🎉 ¡Excelente capacidad multilingüe!")
        elif avg_similarity > 0.5:
            print("👍 Buena capacidad multilingüe")
        else:
            print("⚠️  Capacidad multilingüe limitada")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba multilingüe: {str(e)}")
        return False


async def test_embedding_performance():
    """Prueba el rendimiento del sistema de embeddings."""
    print("\n⚡ PRUEBA 5: Rendimiento de Embeddings")
    print("=" * 50)
    
    embedding_service = get_embedding_service()
    
    # Generar textos de diferentes tamaños
    test_texts = [
        # Textos cortos
        ["iPhone", "Samsung", "laptop", "cámara", "auriculares"],
        # Textos medianos
        ["smartphone con buena cámara", "laptop para programación", "auriculares inalámbricos premium"],
        # Textos largos
        ["iPhone 15 Pro Max con chip A17 Pro, cámara de 48MP con zoom óptico 5x, pantalla Super Retina XDR de 6.7 pulgadas, batería de larga duración y resistencia al agua IP68 perfecto para fotografía profesional"],
        # Lote grande
        [f"Producto {i} con características especiales y funcionalidades avanzadas" for i in range(50)]
    ]
    
    test_names = ["Textos cortos (5)", "Textos medianos (3)", "Texto largo (1)", "Lote grande (50)"]
    
    import time
    
    for texts, name in zip(test_texts, test_names):
        print(f"\n🧪 {name}:")
        
        try:
            start_time = time.time()
            embeddings = await embedding_service.generate_embeddings(texts)
            end_time = time.time()
            
            elapsed_ms = (end_time - start_time) * 1000
            per_text_ms = elapsed_ms / len(texts)
            
            print(f"   ⏱️  Tiempo total: {elapsed_ms:.1f}ms")
            print(f"   📊 Tiempo por texto: {per_text_ms:.1f}ms")
            print(f"   ✅ Embeddings: {len(embeddings)} x {len(embeddings[0]) if embeddings else 0}d")
            
            # Verificar calidad de embeddings
            if embeddings and len(embeddings) > 1:
                first_embedding = embeddings[0]
                norm = np.linalg.norm(first_embedding)
                print(f"   📏 Norma del primer embedding: {norm:.3f}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


async def main():
    """Ejecuta todas las pruebas de embeddings."""
    print("🧠 SUITE COMPLETA DE PRUEBAS DE EMBEDDINGS")
    print("=" * 60)
    print("🎯 Probando: paraphrase-multilingual-MiniLM-L12-v2")
    print("📐 Dimensiones: 384")
    print()
    
    results = []
    
    # Prueba 1: Básica
    embeddings, texts = await test_basic_embeddings()
    results.append(("Generación básica", embeddings is not None))
    
    # Prueba 2: Similitud
    if embeddings and texts:
        await test_semantic_similarity(embeddings, texts)
        results.append(("Similitud semántica", True))
    else:
        results.append(("Similitud semántica", False))
    
    # Prueba 3: Productos
    products_ok = await test_product_embeddings()
    results.append(("Embeddings de productos", products_ok))
    
    # Prueba 4: Multilingüe
    multilingual_ok = await test_multilingual_embeddings()
    results.append(("Capacidades multilingües", multilingual_ok))
    
    # Prueba 5: Rendimiento
    await test_embedding_performance()
    results.append(("Pruebas de rendimiento", True))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS DE EMBEDDINGS")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}")
        if success:
            passed += 1
    
    success_rate = passed / len(results) * 100
    print(f"\n📊 Resultado: {passed}/{len(results)} pruebas exitosas ({success_rate:.0f}%)")
    
    if success_rate == 100:
        print("🎉 ¡SISTEMA DE EMBEDDINGS FUNCIONANDO PERFECTAMENTE!")
    elif success_rate >= 80:
        print("👍 Sistema de embeddings funcionando bien")
    else:
        print("⚠️  Algunos problemas en el sistema de embeddings")
    
    print("\n💡 Próximos pasos:")
    print("   • Probar con más productos reales")
    print("   • Ajustar parámetros de similitud") 
    print("   • Optimizar rendimiento para lotes grandes")
    
    return success_rate == 100


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)