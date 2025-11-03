"""Common Pydantic models for API request/response"""
from typing import Optional
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    data: list = Field(description="Array of items")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="API status")
    database: str = Field(description="Database connection status")
    version: str = Field(default="1.0.0", description="API version")
