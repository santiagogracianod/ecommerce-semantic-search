"""Monitoring utilities for ML logging."""
import httpx
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import get_settings

settings = get_settings()
MONITORING_SERVICE_URL = "http://localhost:8003/api/v1"


async def log_search_prediction(
    query: str,
    embedding: Optional[List[float]],
    results: List[Dict[str, Any]],
    latency_ms: float,
    category_filter: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    error: Optional[str] = None,
):
    """Log search prediction to monitoring service."""
    try:
        # Calculate metrics
        embedding_norm = None
        if embedding:
            embedding_array = np.array(embedding)
            embedding_norm = float(np.linalg.norm(embedding_array))

        top_score = None
        avg_score = None
        if results:
            scores = [r.get("score_semantico", 0) for r in results]
            top_score = float(max(scores)) if scores else None
            avg_score = float(np.mean(scores)) if scores else None

        payload = {
            "query": query,
            "query_length": len(query),
            "embedding_norm": embedding_norm,
            "num_results": len(results),
            "top_score": top_score,
            "avg_score": avg_score,
            "category_filter": category_filter,
            "price_min": price_min,
            "price_max": price_max,
            "latency_ms": latency_ms,
            "error": error,
        }

        # Send async request
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{MONITORING_SERVICE_URL}/predictions/search",
                json=payload
            )

    except Exception as e:
        # Don't fail the main request if monitoring fails
        print(f"Warning: Failed to log prediction to monitoring: {e}")