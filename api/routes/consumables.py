"""Consumables API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add parent directory to path to import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.db_utils import get_db
from api.models.consumables import ConsumableDetail
from api.models.common import PaginatedResponse

router = APIRouter(prefix="/consumables", tags=["consumables"])


@router.get("", response_model=PaginatedResponse)
async def list_consumables(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get paginated list of consumables with optional filters.
    """
    db = get_db()
    
    # Build WHERE clause
    where_conditions = []
    if category:
        where_conditions.append(f"category = '{category}'")
    if subcategory:
        where_conditions.append(f"subcategory = '{subcategory}'")
    if search:
        where_conditions.append(f"consumable_name LIKE '%{search}%'")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else None
    
    # Get total count
    count_query = "SELECT COUNT(*) as count FROM v_consumables_complete"
    if where_clause:
        count_query += f" WHERE {where_clause}"
    
    count_result = db.execute_query(count_query)
    total = count_result[0]['count'] if count_result else 0
    
    # Calculate pagination
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get consumables
    consumables = db.select(
        'v_consumables_complete',
        where=where_clause,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "data": consumables
    }


@router.get("/{consumable_id}", response_model=ConsumableDetail)
async def get_consumable(consumable_id: int):
    """
    Get detailed information about a specific consumable.
    
    Includes effects, SPECIAL modifiers, and all stats.
    """
    db = get_db()
    
    consumables = db.select(
        'v_consumables_complete',
        where=f"consumable_id = {consumable_id}"
    )
    
    if not consumables:
        raise HTTPException(status_code=404, detail="Consumable not found")
    
    return consumables[0]


@router.get("/categories/list")
async def list_consumable_categories():
    """Get list of all consumable categories"""
    db = get_db()
    categories = db.execute_query(
        "SELECT DISTINCT category FROM consumables ORDER BY category"
    )
    return [c["category"] for c in categories]
