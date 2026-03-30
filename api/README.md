# Fallout 76 Build Database - API

REST API backend for the Fallout 76 Build Database, providing access to 3,200+ game items and RAG-powered AI queries.

## Quick Start

```bash
# From project root
bash api-start.sh

# Or manually
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:

- **Base URL**: <http://localhost:8000>
- **Interactive Docs**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Tech Stack

- **FastAPI** - Modern, fast Python web framework
- **Pydantic** - Data validation using Python type hints
- **Uvicorn** - ASGI server
- **MariaDB** - Database backend via `database/db_utils.py`
- **RAG System** - Claude AI + ChromaDB integration

## API Endpoints

### Health & Stats

- `GET /` - API information
- `GET /health` - Health check with database connectivity
- `GET /stats` - Database statistics (item counts)

### Weapons

- `GET /api/weapons` - List all weapons (paginated, filterable)
  - Query params: `page`, `limit`, `weapon_type`, `weapon_class`, `min_level`, `search`
- `GET /api/weapons/{id}` - Get weapon details with damage, perks, and mechanics
- `GET /api/weapons/types/list` - Get all weapon types
- `GET /api/weapons/classes/list` - Get all weapon classes

### Armor

- `GET /api/armor` - List all armor pieces (paginated, filterable)
  - Query params: `page`, `limit`, `armor_type`, `armor_class`, `slot`, `set_name`, `search`
- `GET /api/armor/{id}` - Get armor details with all resistances
- `GET /api/armor/types/list` - Get all armor types
- `GET /api/armor/classes/list` - Get all armor classes
- `GET /api/armor/slots/list` - Get all armor slots
- `GET /api/armor/sets/list` - Get all armor sets

### Perks

- `GET /api/perks` - List all regular perks with ranks (paginated, filterable)
  - Query params: `page`, `limit`, `special`, `race`, `search`
- `GET /api/perks/{id}` - Get perk details with all ranks
- `GET /api/perks/legendary` - List all legendary perks with ranks
- `GET /api/perks/legendary/{id}` - Get legendary perk details
- `GET /api/perks/special/list` - Get all SPECIAL attributes

### Mutations

- `GET /api/mutations` - List all mutations (paginated, filterable)
  - Query params: `page`, `limit`, `search`
- `GET /api/mutations/{id}` - Get mutation details with effects

### Consumables

- `GET /api/consumables` - List all consumables (paginated, filterable)
  - Query params: `page`, `limit`, `category`, `subcategory`, `search`
- `GET /api/consumables/{id}` - Get consumable details
- `GET /api/consumables/categories/list` - Get all categories

### RAG (AI Queries)

- `POST /api/rag/query` - Query the RAG system with natural language
  - Request body: `{"query": "your question", "include_context": false}`
  - Returns AI-generated answer with execution time
- `GET /api/rag/health` - Check RAG system health

## Example Requests

```bash
# Get all weapons (first page)
curl "http://localhost:8000/api/weapons?page=1&limit=10"

# Search for weapons
curl "http://localhost:8000/api/weapons?search=gauss&weapon_type=Ranged"

# Get specific weapon
curl "http://localhost:8000/api/weapons/1"

# Query RAG system
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What perks affect shotguns?"}'

# Get database stats
curl "http://localhost:8000/stats"
```

## Response Format

All list endpoints return paginated responses:

```json
{
  "total": 262,
  "page": 1,
  "limit": 20,
  "pages": 14,
  "data": [...]
}
```

## CORS

CORS is currently open (`allow_origins=["*"]`) for development. Tighten this in `api/main.py` before any public deployment.

## Project Structure

```text
api/
├── main.py                 # FastAPI app with route registration
├── routes/
│   ├── weapons.py
│   ├── armor.py
│   ├── perks.py            # regular + legendary
│   ├── mutations.py
│   ├── consumables.py
│   └── rag.py
└── models/
    ├── common.py           # Pagination, health check models
    ├── weapons.py
    ├── armor.py
    ├── perks.py
    ├── mutations.py
    ├── consumables.py
    └── rag.py
```

## Database Integration

The API uses the centralized database utility (`database/db_utils.py`):

- **Connection pooling**: Automatic connection reuse
- **Query caching**: Lookup tables cached in memory (300x faster)
- **Views**: Queries use optimized database views

## Environment Variables

```bash
DB_HOST=localhost
DB_USER=your_mariadb_user
DB_PASSWORD=your_password
DB_NAME=f76
ANTHROPIC_API_KEY=your_key    # for RAG
OPENAI_API_KEY=your_key       # for RAG embeddings
```

## Adding New Endpoints

1. Create model in `api/models/` if needed
2. Create route file in `api/routes/`
3. Register router in `api/main.py`:

```python
from api.routes import my_new_route
app.include_router(my_new_route.router, prefix="/api")
```

## Related Documentation

- Project setup: `../README.md`
- Database schema: `../database/f76_master_schema.sql`
- RAG system: `../rag/`
- Frontend: `../react/`
