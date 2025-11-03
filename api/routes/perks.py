"""Perks API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add parent directory to path to import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.db_utils import get_db
from api.models.perks import PerkDetail, LegendaryPerkDetail
from api.models.common import PaginatedResponse

router = APIRouter(prefix="/perks", tags=["perks"])


@router.get("", response_model=PaginatedResponse)
async def list_perks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    special: Optional[str] = Query(None, description="Filter by SPECIAL attribute"),
    race: Optional[str] = Query(None, description="Filter by race"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get paginated list of regular perks with optional filters.
    
    Returns all ranks for each perk.
    """
    db = get_db()
    
    # Build WHERE clause
    where_conditions = []
    if special:
        where_conditions.append(f"special = '{special}'")
    if race:
        where_conditions.append(f"race LIKE '%{race}%'")
    if search:
        where_conditions.append(f"perk_name LIKE '%{search}%'")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else None
    
    # Get total count of unique perks
    count_query = "SELECT COUNT(DISTINCT perk_id) as count FROM v_perks_all_ranks"
    if where_clause:
        count_query += f" WHERE {where_clause}"
    
    count_result = db.execute_query(count_query)
    total = count_result[0]['count'] if count_result else 0
    
    # Calculate pagination
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get perks with all ranks
    perks = db.select(
        'v_perks_all_ranks',
        where=where_clause,
        limit=limit * 5,  # Multiply by max ranks to get all ranks for paginated perks
        offset=offset * 5
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "data": perks
    }


@router.get("/legendary", response_model=PaginatedResponse)
async def list_legendary_perks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    race: Optional[str] = Query(None, description="Filter by race"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get paginated list of legendary perks with optional filters.
    
    Returns all ranks for each legendary perk.
    """
    db = get_db()
    
    # Build WHERE clause
    where_conditions = []
    if race:
        where_conditions.append(f"race LIKE '%{race}%'")
    if search:
        where_conditions.append(f"perk_name LIKE '%{search}%'")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else None
    
    # Get total count of unique legendary perks
    count_query = "SELECT COUNT(DISTINCT legendary_perk_id) as count FROM v_legendary_perks_all_ranks"
    if where_clause:
        count_query += f" WHERE {where_clause}"
    
    count_result = db.execute_query(count_query)
    total = count_result[0]['count'] if count_result else 0
    
    # Calculate pagination
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get legendary perks with all ranks
    perks = db.select(
        'v_legendary_perks_all_ranks',
        where=where_clause,
        limit=limit * 4,  # Multiply by max ranks (4) to get all ranks for paginated perks
        offset=offset * 4
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "data": perks
    }


@router.get("/{perk_id}")
async def get_perk(perk_id: int):
    """
    Get detailed information about a specific perk.
    
    Returns all ranks for the perk.
    """
    db = get_db()
    
    perks = db.select(
        'v_perks_all_ranks',
        where=f"perk_id = {perk_id}"
    )
    
    if not perks:
        raise HTTPException(status_code=404, detail="Perk not found")
    
    return {
        "perk": perks[0],
        "ranks": perks
    }


@router.get("/legendary/{legendary_perk_id}")
async def get_legendary_perk(legendary_perk_id: int):
    """
    Get detailed information about a specific legendary perk.
    
    Returns all ranks for the legendary perk.
    """
    db = get_db()
    
    perks = db.select(
        'v_legendary_perks_all_ranks',
        where=f"legendary_perk_id = {legendary_perk_id}"
    )
    
    if not perks:
        raise HTTPException(status_code=404, detail="Legendary perk not found")
    
    return {
        "perk": perks[0],
        "ranks": perks
    }


@router.get("/special/list")
async def list_special_attributes():
    """Get list of all SPECIAL attributes"""
    db = get_db()
    special = db.execute_query("SELECT id, code, name FROM special_attributes ORDER BY id")
    return {"special_attributes": special}
