"""Weapons API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add parent directory to path to import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.db_utils import get_db
from api.models.weapons import (
    WeaponListItem,
    WeaponDetail,
    DamageComponent,
    WeaponMechanic,
)
from api.models.common import PaginatedResponse

router = APIRouter(prefix="/weapons", tags=["weapons"])


@router.get("", response_model=PaginatedResponse)
async def list_weapons(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    weapon_type: Optional[str] = Query(None, description="Filter by weapon type"),
    weapon_class: Optional[str] = Query(None, description="Filter by weapon class"),
    min_level: Optional[int] = Query(None, description="Filter by minimum level"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get paginated list of weapons with optional filters.
    
    Returns simplified weapon data for list views.
    """
    db = get_db()
    
    # Build WHERE clause
    where_conditions = []
    if weapon_type:
        where_conditions.append(f"weapon_type = '{weapon_type}'")
    if weapon_class:
        where_conditions.append(f"weapon_class = '{weapon_class}'")
    if min_level is not None:
        where_conditions.append(f"level >= {min_level}")
    if search:
        where_conditions.append(f"weapon_name LIKE '%{search}%'")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else None
    
    # Get total count
    count_query = "SELECT COUNT(*) as count FROM v_weapons_with_perks"
    if where_clause:
        count_query += f" WHERE {where_clause}"
    
    count_result = db.execute_query(count_query)
    total = count_result[0]['count'] if count_result else 0
    
    # Calculate pagination
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get weapons
    weapons = db.select(
        'v_weapons_with_perks',
        columns=['id', 'weapon_name as name', 'weapon_type', 'weapon_class', 'level as min_level', 'damage'],
        where=where_clause,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "data": weapons
    }


@router.get("/{weapon_id}", response_model=WeaponDetail)
async def get_weapon(weapon_id: int):
    """
    Get detailed information about a specific weapon.
    
    Includes damage components, applicable perks, and special mechanics.
    """
    db = get_db()
    
    # Get basic weapon info with perks
    weapon_query = """
        SELECT 
            w.id, w.name, 
            wt.name as weapon_type, 
            wc.name as weapon_class,
            w.min_level,
            w.form_id,
            v.regular_perks,
            v.legendary_perks,
            w.source_url
        FROM weapons w
        LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
        LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
        LEFT JOIN v_weapons_with_perks v ON w.id = v.id
        WHERE w.id = %s
    """
    
    weapons = db.execute_query(weapon_query, (weapon_id,))
    if not weapons:
        raise HTTPException(status_code=404, detail="Weapon not found")
    
    weapon = weapons[0]
    
    # Get damage components
    damage_query = """
        SELECT 
            dt.name as damage_type,
            wdc.min_damage,
            wdc.max_damage,
            wdc.level_tier
        FROM weapon_damage_components wdc
        JOIN damage_types dt ON wdc.damage_type_id = dt.id
        WHERE wdc.weapon_id = %s
        ORDER BY wdc.level_tier, dt.name
    """
    
    damage_components = db.execute_query(damage_query, (weapon_id,))
    
    # Get weapon mechanics
    mechanics_query = """
        SELECT 
            wmt.name as mechanic_type,
            wmt.description,
            wm.numeric_value,
            wm.numeric_value_2,
            wm.string_value,
            wm.unit,
            wm.notes
        FROM weapon_mechanics wm
        JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
        WHERE wm.weapon_id = %s
    """
    
    mechanics = db.execute_query(mechanics_query, (weapon_id,))
    
    return {
        **weapon,
        "damage_components": [DamageComponent(**dc) for dc in damage_components],
        "mechanics": [WeaponMechanic(**m) for m in mechanics]
    }


@router.get("/types/list")
async def list_weapon_types():
    """Get list of all weapon types"""
    db = get_db()
    types = db.execute_query("SELECT name FROM weapon_types ORDER BY name")
    return [t["name"] for t in types]


@router.get("/classes/list")
async def list_weapon_classes():
    """Get list of all weapon classes"""
    db = get_db()
    classes = db.execute_query("SELECT name FROM weapon_classes ORDER BY name")
    return [c["name"] for c in classes]
