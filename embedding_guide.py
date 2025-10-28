#!/usr/bin/env python3
"""Guía práctica para crear y usar embeddings personalizados."""

import asyncio
import sys
from pathlib import Path
import json
from typing import List, Dict, Any

# Agregar el directorio raíz al path  
sys.path.append(str(Path(__file__).parent))

from services.embedding_service import get_embedding_service


class CustomEmbeddingHelper:
    """Helper para trabajar con embeddings personalizados."""
    
    def __init__(self):
        self.embedding_service = None
        
    async def initialize(self):
        """Inicializa el servicio de embeddings."""
        self.embedding_service = get_embedding_service()
    
    async def create_product_embeddings(self, products: List[Dict]) -> Dict[str, Any]:
        """Crea embeddings para una lista de productos."""
        print("📦 CREANDO EMBEDDINGS PARA PRODUCTOS")
        print("=" * 50)
        
        # Preparar textos para embeddings
        product_texts = []
        for product in products:
            # Estrategia 1: Solo nombre
            # text = product['name']
            
            # Estrategia 2: Nombre + descripción
            # text = f"{product['name']} {product['description']}"
            
            # Estrategia 3: Información completa estructurada (RECOMENDADA)
            text = f"{product['name']} {product['description']} categoría {product['category']}"
            
            product_texts.append(text)
        
        print(f"🧠 Generando embeddings para {len(products)} productos...")
        
        embeddings = await self.embedding_service.generate_embeddings(product_texts)
        
        if not embeddings:
            return {"error": "No se pudieron generar embeddings"}
        
        # Crear resultado estructurado
        result = {
            "total_products": len(products),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
            "products_with_embeddings": []
        }
        
        for i, (product, embedding, text) in enumerate(zip(products, embeddings, product_texts)):
            result["products_with_embeddings"].append({
                "id": product.get('id', f'product_{i}'),
                "name": product['name'],
                "category": product['category'],
                "text_used": text,
                "embedding": embedding,
                "embedding_stats": {
                    "dimension": len(embedding),
                    "norm": (sum(x*x for x in embedding) ** 0.5),
                    "mean": sum(embedding) / len(embedding),
                    "min_value": min(embedding),
                    "max_value": max(embedding)
                }
            })
        
        print(f"✅ Embeddings creados exitosamente")
        print(f"📏 Dimensión: {result['embedding_dimension']}")
        
        return result
    
    async def semantic_search(self, query: str, product_embeddings: List[Dict], top_k: int = 5) -> List[Dict]:
        """Realiza búsqueda semántica en embeddings de productos."""
        print(f"🔍 BÚSQUEDA SEMÁNTICA: '{query}'")
        print("=" * 50)
        
        # Generar embedding para la query
        query_embeddings = await self.embedding_service.generate_embeddings([query])
        if not query_embeddings:
            return []
        
        query_embedding = query_embeddings[0]
        
        # Calcular similitudes
        similarities = []
        for product in product_embeddings:
            similarity = self._cosine_similarity(query_embedding, product['embedding'])
            
            similarities.append({
                "id": product['id'],
                "name": product['name'],
                "category": product['category'],
                "similarity": similarity,
                "text_used": product['text_used']
            })
        
        # Ordenar por similitud
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Retornar top_k resultados
        top_results = similarities[:top_k]
        
        print(f"📊 Encontrados {len(similarities)} productos, mostrando top {len(top_results)}:")
        for i, result in enumerate(top_results, 1):
            relevance = self._get_relevance_label(result['similarity'])
            print(f"   {i}. {result['similarity']:.3f} {relevance} - {result['name']} ({result['category']})")
        
        return top_results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similitud coseno entre dos vectores."""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _get_relevance_label(self, similarity: float) -> str:
        """Obtiene etiqueta de relevancia basada en similitud."""
        if similarity >= 0.8:
            return "🟢 Alta"
        elif similarity >= 0.6:
            return "🟡 Media"
        elif similarity >= 0.4:
            return "🟠 Baja"
        else:
            return "🔴 Muy baja"
    
    async def compare_embedding_strategies(self, products: List[Dict]) -> None:
        """Compara diferentes estrategias para crear embeddings."""
        print("📊 COMPARACIÓN DE ESTRATEGIAS DE EMBEDDING")
        print("=" * 60)
        
        strategies = {
            "Solo nombre": lambda p: p['name'],
            "Nombre + descripción": lambda p: f"{p['name']} {p['description']}",
            "Información completa": lambda p: f"{p['name']} {p['description']} categoría {p['category']}",
            "Descripción optimizada": lambda p: f"{p['name']} - {p['description']} - Categoría: {p['category']} - Producto tecnológico"
        }
        
        test_query = "smartphone con excelente cámara"
        
        for strategy_name, text_func in strategies.items():
            print(f"\n🧪 Estrategia: {strategy_name}")
            
            # Crear textos con esta estrategia
            texts = [text_func(product) for product in products]
            
            # Generar embeddings
            embeddings = await self.embedding_service.generate_embeddings(texts + [test_query])
            if not embeddings:
                print("   ❌ Error generando embeddings")
                continue
            
            # Separar query embedding
            query_embedding = embeddings[-1]
            product_embeddings = embeddings[:-1]
            
            # Calcular similitudes
            similarities = []
            for i, product in enumerate(products):
                similarity = self._cosine_similarity(query_embedding, product_embeddings[i])
                similarities.append((similarity, product['name']))
            
            # Ordenar y mostrar top 3
            similarities.sort(reverse=True)
            print(f"   📊 Top 3 resultados para '{test_query}':")
            
            for j, (similarity, name) in enumerate(similarities[:3], 1):
                relevance = self._get_relevance_label(similarity)
                print(f"      {j}. {similarity:.3f} {relevance} - {name}")


async def practical_example():
    """Ejemplo práctico de uso de embeddings."""
    print("🛠️  EJEMPLO PRÁCTICO DE EMBEDDINGS")
    print("=" * 60)
    
    # Productos de ejemplo
    sample_products = [
        {
            "id": "iphone15",
            "name": "iPhone 15 Pro Max",
            "description": "Smartphone premium con chip A17 Pro, cámara de 48MP con zoom óptico 5x, pantalla Super Retina XDR",
            "category": "Smartphones"
        },
        {
            "id": "macbook",
            "name": "MacBook Pro M3",
            "description": "Laptop profesional con chip Apple M3, ideal para desarrollo de software y edición de video",
            "category": "Laptops"
        },
        {
            "id": "airpods",
            "name": "AirPods Pro 2",
            "description": "Auriculares inalámbricos con cancelación activa de ruido y audio espacial",
            "category": "Audio"
        },
        {
            "id": "camera",
            "name": "Canon EOS R5",
            "description": "Cámara mirrorless profesional de 45MP con grabación de video 8K y estabilización",
            "category": "Fotografía"
        }
    ]
    
    # Inicializar helper
    helper = CustomEmbeddingHelper()
    await helper.initialize()
    
    # Crear embeddings
    print("📦 Paso 1: Crear embeddings para productos")
    embedding_data = await helper.create_product_embeddings(sample_products)
    
    if "error" in embedding_data:
        print(f"❌ Error: {embedding_data['error']}")
        return
    
    # Realizar búsquedas semánticas
    print(f"\n🔍 Paso 2: Búsquedas semánticas")
    
    test_queries = [
        "teléfono con buena cámara",
        "computadora para programar", 
        "auriculares para música",
        "equipo de fotografía profesional",
        "dispositivo Apple"
    ]
    
    for query in test_queries:
        await helper.semantic_search(query, embedding_data["products_with_embeddings"], top_k=3)
        print()
    
    # Comparar estrategias
    print(f"\n📊 Paso 3: Comparar estrategias de embedding")
    await helper.compare_embedding_strategies(sample_products)


async def embedding_best_practices():
    """Muestra las mejores prácticas para embeddings."""
    print("\n💡 MEJORES PRÁCTICAS PARA EMBEDDINGS")
    print("=" * 60)
    
    practices = [
        {
            "title": "📝 Preparación de Texto",
            "tips": [
                "Combina nombre + descripción + categoría",
                "Normaliza el texto (minúsculas, sin caracteres especiales)",
                "Incluye sinónimos relevantes",
                "Mantén consistencia en el formato"
            ]
        },
        {
            "title": "🎯 Optimización de Búsqueda", 
            "tips": [
                "Usa umbrales de similitud apropiados (>0.7 alta, >0.5 media)",
                "Implementa filtros combinados (categoría + precio + embeddings)",
                "Considera el contexto del usuario",
                "Prueba con queries diversas"
            ]
        },
        {
            "title": "⚡ Rendimiento",
            "tips": [
                "Cachea embeddings precalculados",
                "Usa batch processing para múltiples textos",
                "Considera índices especializados (FAISS, Pinecone)",
                "Monitorea el tiempo de respuesta"
            ]
        },
        {
            "title": "📊 Evaluación",
            "tips": [
                "Mide precisión con datasets de prueba",
                "Analiza distribución de scores de similitud",
                "Prueba con queries reales de usuarios",
                "Ajusta umbrales basándose en feedback"
            ]
        }
    ]
    
    for practice in practices:
        print(f"\n{practice['title']}")
        for tip in practice['tips']:
            print(f"   • {tip}")
    
    print(f"\n🔧 CONFIGURACIÓN RECOMENDADA:")
    print(f"   • Modelo: paraphrase-multilingual-MiniLM-L12-v2")
    print(f"   • Dimensiones: 384")
    print(f"   • Similitud: Coseno")
    print(f"   • Umbral alto: >0.7")
    print(f"   • Umbral medio: 0.5-0.7")
    print(f"   • Umbral bajo: 0.3-0.5")


if __name__ == "__main__":
    print("🎓 GUÍA COMPLETA DE EMBEDDINGS PERSONALIZADOS")
    print("=" * 70)
    
    asyncio.run(practical_example())
    asyncio.run(embedding_best_practices())
    
    print(f"\n" + "=" * 70)
    print("🎉 GUÍA COMPLETADA")
    print("💡 ¡Ya sabes cómo crear y usar embeddings personalizados!")
    print("🔗 Revisa los otros scripts para más ejemplos y herramientas.")