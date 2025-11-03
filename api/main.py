"""
Fallout 76 Build Database - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_utils import get_db
from api.routes import weapons, armor, perks, mutations, consumables, rag

# Create FastAPI app
app = FastAPI(
    title="Fallout 76 Build Database API",
    description="""
    REST API for Fallout 76 game data including weapons, armor, perks, mutations, and consumables.
    
    Features:
    - **Weapons**: 262 weapons with damage stats, perks, and special mechanics
    - **Armor**: 477 armor pieces with full resistance data
    - **Perks**: 240 regular perks and 28 legendary perks with all ranks
    - **Mutations**: 19 mutations with effects and perk interactions
    - **Consumables**: 11 build-relevant consumables
    - **RAG**: Natural language queries powered by Claude AI
    
    Data sourced from Fallout Wiki and processed through normalized MySQL database.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Fallout 76 Build Database API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "weapons": "/api/weapons",
            "armor": "/api/armor",
            "perks": "/api/perks",
            "mutations": "/api/mutations",
            "consumables": "/api/consumables",
            "rag": "/api/rag/query"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Verifies database connectivity and API availability.
    """
    try:
        db = get_db()
        # Test database connection
        result = db.execute_query("SELECT COUNT(*) as count FROM weapons")
        weapons_count = result[0]['count'] if result else 0
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0",
            "stats": {
                "weapons": weapons_count
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/stats", tags=["stats"])
async def get_stats():
    """
    Get database statistics.
    
    Returns counts of all major entity types.
    """
    try:
        db = get_db()
        
        # Get counts
        weapons_count = db.execute_query("SELECT COUNT(*) as count FROM weapons")[0]['count']
        armor_count = db.execute_query("SELECT COUNT(*) as count FROM armor")[0]['count']
        perks_count = db.execute_query("SELECT COUNT(*) as count FROM perks")[0]['count']
        legendary_perks_count = db.execute_query("SELECT COUNT(*) as count FROM legendary_perks")[0]['count']
        mutations_count = db.execute_query("SELECT COUNT(*) as count FROM mutations")[0]['count']
        consumables_count = db.execute_query("SELECT COUNT(*) as count FROM consumables")[0]['count']
        
        return {
            "weapons": weapons_count,
            "armor": armor_count,
            "perks": perks_count,
            "legendary_perks": legendary_perks_count,
            "mutations": mutations_count,
            "consumables": consumables_count,
            "total_items": weapons_count + armor_count + perks_count + legendary_perks_count + mutations_count + consumables_count
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# Include routers with /api prefix
app.include_router(weapons.router, prefix="/api")
app.include_router(armor.router, prefix="/api")
app.include_router(perks.router, prefix="/api")
app.include_router(mutations.router, prefix="/api")
app.include_router(consumables.router, prefix="/api")
app.include_router(rag.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
