"""RAG (Retrieval Augmented Generation) API endpoints"""
from fastapi import APIRouter, HTTPException
import sys
import os
import time

# Add parent directory to path to import RAG modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from rag.hybrid_query_engine import HybridFalloutRAG
from api.models.rag import RAGQueryRequest, RAGQueryResponse

router = APIRouter(prefix="/rag", tags=["rag"])

# Initialize RAG engine (singleton pattern)
_rag_engine = None


def get_rag_engine():
    """Get or create RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = HybridFalloutRAG()
    return _rag_engine


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Query the RAG system with natural language.
    
    The system automatically routes queries to either:
    - SQL engine for exact lookups (e.g., "What is the damage of Gauss Shotgun?")
    - Vector search for semantic queries (e.g., "Best bloodied heavy gunner build")
    - Hybrid approach combining both
    
    Example queries:
    - "What perks affect shotguns?"
    - "Best bloodied heavy gunner build"
    - "Which weapons can be charged?"
    - "Compare Gauss Rifle and Gauss Shotgun"
    """
    try:
        start_time = time.time()
        
        engine = get_rag_engine()
        answer = engine.query(request.query)
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        response = {
            "query": request.query,
            "answer": answer,
            "execution_time_ms": round(execution_time, 2)
        }
        
        # Add sources if requested
        if request.include_context:
            # Note: Current implementation doesn't expose sources
            # This can be enhanced to return source documents/SQL queries
            response["sources"] = ["Source tracking not yet implemented"]
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing RAG query: {str(e)}"
        )


@router.get("/health")
async def rag_health():
    """
    Check RAG system health.
    
    Verifies that the RAG engine can be initialized and is ready to process queries.
    """
    try:
        engine = get_rag_engine()
        return {
            "status": "healthy",
            "engine_initialized": engine is not None,
            "message": "RAG system is operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"RAG system unavailable: {str(e)}"
        )
