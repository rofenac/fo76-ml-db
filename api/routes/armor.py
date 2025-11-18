"""Armor API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add parent directory to path to import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.db_utils import get_db
from api.models.armor import ArmorDetail
from api.models.common import PaginatedResponse

router = APIRouter(prefix="/armor", tags=["armor"])


@router.get("", response_model=PaginatedResponse)
async def list_armor(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    armor_type: Optional[str] = Query(None, description="Filter by armor type"),
    armor_class: Optional[str] = Query(None, description="Filter by armor class"),
    slot: Optional[str] = Query(None, description="Filter by equipment slot"),
    set_name: Optional[str] = Query(None, description="Filter by armor set"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get paginated list of armor pieces with optional filters.
    """
    db = get_db()
    
    # Build WHERE clause
    where_conditions = []
    if armor_type:
        where_conditions.append(f"armor_type = '{armor_type}'")
    if armor_class:
        where_conditions.append(f"class = '{armor_class}'")
    if slot:
        where_conditions.append(f"slot = '{slot}'")
    if set_name:
        where_conditions.append(f"set_name = '{set_name}'")
    if search:
        where_conditions.append(f"name LIKE '%{search}%'")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else None
    
    # Get total count
    count_query = "SELECT COUNT(*) as count FROM v_armor_complete"
    if where_clause:
        count_query += f" WHERE {where_clause}"
    
    count_result = db.execute_query(count_query)
    total = count_result[0]['count'] if count_result else 0
    
    # Calculate pagination
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get armor pieces
    armor = db.select(
        'v_armor_complete',
        where=where_clause,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "data": armor
    }


@router.get("/{armor_id}", response_model=ArmorDetail)
async def get_armor(armor_id: int):
    """
    Get detailed information about a specific armor piece.
    
    Includes all resistance values and set information.
    """
    db = get_db()
    
    armor = db.select(
        'v_armor_complete',
        where=f"id = {armor_id}"
    )
    
    if not armor:
        raise HTTPException(status_code=404, detail="Armor piece not found")
    
    return armor[0]


@router.get("/types/list")
async def list_armor_types():
    """Get list of all armor types"""
    db = get_db()
    types = db.execute_query("SELECT name FROM armor_types ORDER BY name")
    return [t["name"] for t in types]


@router.get("/classes/list")
async def list_armor_classes():
    """Get list of all armor classes"""
    db = get_db()
    classes = db.execute_query("SELECT name FROM armor_classes ORDER BY name")
    return [c["name"] for c in classes]


@router.get("/slots/list")
async def list_armor_slots():
    """Get list of all armor slots"""
    db = get_db()
    slots = db.execute_query("SELECT name FROM armor_slots ORDER BY name")
    return [s["name"] for s in slots]


@router.get("/sets/list")
async def list_armor_sets():
    """Get list of all armor sets"""
    db = get_db()
    sets = db.execute_query(
        "SELECT DISTINCT set_name FROM armor WHERE set_name IS NOT NULL ORDER BY set_name"
    )
    return [s["set_name"] for s in sets]
