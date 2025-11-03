"""RAG query-related Pydantic models"""
from typing import Optional, List
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """RAG query request"""
    query: str = Field(description="Natural language query")
    include_context: bool = Field(default=False, description="Include source context in response")


class RAGQueryResponse(BaseModel):
    """RAG query response"""
    query: str = Field(description="Original query")
    answer: str = Field(description="AI-generated answer")
    query_type: Optional[str] = Field(default=None, description="Type of query (SQL, Vector, or Hybrid)")
    sources: Optional[List[str]] = Field(default=None, description="Source documents or SQL results")
    execution_time_ms: Optional[float] = Field(default=None, description="Query execution time in milliseconds")
