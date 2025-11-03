"""Mutations API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add parent directory to path to import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.db_utils import get_db
from api.models.mutations import MutationDetail
from api.models.common import PaginatedResponse

router = APIRouter(prefix="/mutations", tags=["mutations"])


@router.get("", response_model=PaginatedResponse)
async def list_mutations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get paginated list of mutations with optional filters.
    """
    db = get_db()
    
    # Build WHERE clause
    where_clause = None
    if search:
        where_clause = f"mutation_name LIKE '%{search}%'"
    
    # Get total count
    count_query = "SELECT COUNT(*) as count FROM v_mutations_complete"
    if where_clause:
        count_query += f" WHERE {where_clause}"
    
    count_result = db.execute_query(count_query)
    total = count_result[0]['count'] if count_result else 0
    
    # Calculate pagination
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get mutations
    mutations = db.select(
        'v_mutations_complete',
        where=where_clause,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "data": mutations
    }


@router.get("/{mutation_id}", response_model=MutationDetail)
async def get_mutation(mutation_id: int):
    """
    Get detailed information about a specific mutation.
    
    Includes positive/negative effects, exclusive mutations, and perk interactions.
    """
    db = get_db()
    
    mutations = db.select(
        'v_mutations_complete',
        where=f"mutation_id = {mutation_id}"
    )
    
    if not mutations:
        raise HTTPException(status_code=404, detail="Mutation not found")
    
    return mutations[0]
