#!/usr/bin/env python3
"""Ejemplo interactivo para probar embeddings paso a paso."""

import asyncio
import sys
from pathlib import Path
import json

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from services.embedding_service import get_embedding_service
from services.elasticsearch_service import get_elasticsearch_service


async def embedding_playground():
    """Playground interactivo para probar embeddings."""
    print("🎮 EMBEDDING PLAYGROUND - Prueba Interactiva")
    print("=" * 60)
    print("Escribe 'exit' para salir, 'help' para ayuda")
    print()
    
    embedding_service = get_embedding_service()
    
    # Cache de embeddings para comparaciones
    embedding_cache = {}
    
    while True:
        try:
            # Solicitar input del usuario
            user_input = input("💭 Ingresa texto para generar embedding: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 ¡Hasta luego!")
                break
            elif user_input.lower() == 'help':
                show_help()
                continue
            elif user_input.lower() == 'compare':
                await compare_cached_embeddings(embedding_cache)
                continue
            elif user_input.lower() == 'clear':
                embedding_cache.clear()
                print("🧹 Cache de embeddings limpiado")
                continue
            elif user_input.lower() == 'list':
                list_cached_embeddings(embedding_cache)
                continue
            elif not user_input:
                continue
            
            # Generar embedding
            print(f"🧠 Generando embedding para: '{user_input}'")
            
            embeddings = await embedding_service.generate_embeddings([user_input])
            if embeddings:
                embedding = embeddings[0]
                
                # Guardar en cache
                embedding_cache[user_input] = embedding
                
                # Mostrar información del embedding
                print(f"✅ Embedding generado:")
                print(f"   📏 Dimensiones: {len(embedding)}")
                print(f"   📊 Rango: [{min(embedding):.4f}, {max(embedding):.4f}]")
                print(f"   🎯 Norma: {sum(x*x for x in embedding)**0.5:.4f}")
                print(f"   📈 Media: {sum(embedding)/len(embedding):.4f}")
                
                # Si hay otros embeddings, calcular similitudes
                if len(embedding_cache) > 1:
                    print(f"\n🔍 Similitudes con embeddings anteriores:")
                    await show_similarities(user_input, embedding_cache)
            else:
                print("❌ Error generando embedding")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def show_help():
    """Muestra ayuda del playground."""
    print("\n📚 COMANDOS DISPONIBLES:")
    print("  • Escribe cualquier texto → genera embedding")
    print("  • 'compare' → compara todos los embeddings guardados")
    print("  • 'list' → muestra todos los embeddings en cache")
    print("  • 'clear' → limpia el cache de embeddings")
    print("  • 'help' → muestra esta ayuda")
    print("  • 'exit' → salir del playground")
    print()


def list_cached_embeddings(cache):
    """Lista embeddings en cache."""
    if not cache:
        print("📭 No hay embeddings en cache")
        return
    
    print(f"\n📋 EMBEDDINGS EN CACHE ({len(cache)}):")
    for i, text in enumerate(cache.keys(), 1):
        text_preview = text[:50] + "..." if len(text) > 50 else text
        print(f"  {i}. '{text_preview}'")


async def show_similarities(current_text, cache):
    """Muestra similitudes con embeddings en cache."""
    current_embedding = cache[current_text]
    
    similarities = []
    for text, embedding in cache.items():
        if text != current_text:
            similarity = calculate_cosine_similarity(current_embedding, embedding)
            similarities.append((similarity, text))
    
    # Ordenar por similitud
    similarities.sort(reverse=True)
    
    # Mostrar top 5
    for i, (similarity, text) in enumerate(similarities[:5], 1):
        # Indicador de similitud
        if similarity > 0.8:
            indicator = "🟢 Muy similar"
        elif similarity > 0.6:
            indicator = "🟡 Similar"  
        elif similarity > 0.3:
            indicator = "🟠 Poco similar"
        else:
            indicator = "🔴 No similar"
            
        text_preview = text[:40] + "..." if len(text) > 40 else text
        print(f"   {i}. {similarity:.3f} {indicator} - '{text_preview}'")


async def compare_cached_embeddings(cache):
    """Compara todos los embeddings en cache."""
    if len(cache) < 2:
        print("⚠️  Necesitas al menos 2 embeddings para comparar")
        return
    
    print(f"\n🔬 COMPARACIÓN DE {len(cache)} EMBEDDINGS")
    print("=" * 50)
    
    texts = list(cache.keys())
    
    # Matriz de similitud
    print("Similitud".ljust(20), end="")
    for i in range(len(texts)):
        print(f"{i+1:>6}", end="")
    print()
    print("-" * (20 + 6 * len(texts)))
    
    for i, text1 in enumerate(texts):
        text_short = f"{i+1}. {text1[:15]}..." if len(text1) > 15 else f"{i+1}. {text1}"
        print(text_short.ljust(20), end="")
        
        for j, text2 in enumerate(texts):
            if i == j:
                print("  1.00", end="")
            else:
                similarity = calculate_cosine_similarity(cache[text1], cache[text2])
                print(f"{similarity:6.2f}", end="")
        print()


def calculate_cosine_similarity(vec1, vec2):
    """Calcula similitud coseno entre dos vectores."""
    import math
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


async def quick_embedding_test():
    """Test rápido de embeddings con ejemplos predefinidos."""
    print("⚡ QUICK TEST - Ejemplos Predefinidos")
    print("=" * 50)
    
    examples = [
        "smartphone iPhone cámara",
        "teléfono móvil fotografía", 
        "laptop MacBook programar",
        "computadora portátil desarrollo",
        "auriculares música sonido",
        "pizza comida italiana"
    ]
    
    embedding_service = get_embedding_service()
    
    print("🧠 Generando embeddings para ejemplos...")
    embeddings = await embedding_service.generate_embeddings(examples)
    
    if not embeddings:
        print("❌ Error generando embeddings")
        return
    
    print("✅ Embeddings generados exitosamente")
    
    # Mostrar matriz de similitud
    print(f"\n📊 MATRIZ DE SIMILITUD ({len(examples)}x{len(examples)}):")
    print("-" * 60)
    
    # Header
    print("Ejemplo".ljust(25), end="")
    for i in range(len(examples)):
        print(f"{i+1:>6}", end="")
    print()
    print("-" * (25 + 6 * len(examples)))
    
    # Filas
    for i, example1 in enumerate(examples):
        example_short = f"{i+1}. {example1[:20]}..." if len(example1) > 20 else f"{i+1}. {example1}"
        print(example_short.ljust(25), end="")
        
        for j, example2 in enumerate(examples):
            if i == j:
                print("  1.00", end="")
            else:
                similarity = calculate_cosine_similarity(embeddings[i], embeddings[j])
                print(f"{similarity:6.2f}", end="")
        print()
    
    # Encontrar pares más similares
    print(f"\n🎯 PARES MÁS SIMILARES:")
    pairs = []
    for i in range(len(examples)):
        for j in range(i+1, len(examples)):
            similarity = calculate_cosine_similarity(embeddings[i], embeddings[j])
            pairs.append((similarity, i, j))
    
    pairs.sort(reverse=True)
    
    for similarity, i, j in pairs[:3]:
        print(f"   {similarity:.3f} - '{examples[i]}' ↔ '{examples[j]}'")


if __name__ == "__main__":
    print("🧪 HERRAMIENTAS DE PRUEBA DE EMBEDDINGS")
    print("=" * 60)
    
    while True:
        print("\n¿Qué quieres hacer?")
        print("1. 🎮 Playground interactivo")
        print("2. ⚡ Quick test predefinido") 
        print("3. 🚪 Salir")
        
        choice = input("\nElige una opción (1-3): ").strip()
        
        if choice == "1":
            asyncio.run(embedding_playground())
        elif choice == "2":
            asyncio.run(quick_embedding_test())
        elif choice == "3":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida, intenta de nuevo")