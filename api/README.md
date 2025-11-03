# Fallout 76 Build Database - API

REST API backend for the Fallout 76 Build Database, providing access to 1,037 game items and RAG-powered AI queries.

## Quick Start

```bash
# From project root
./api-start.sh

# Or manually
source .venv/bin/activate
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Tech Stack

- **FastAPI** - Modern, fast Python web framework
- **Pydantic** - Data validation using Python type hints
- **Uvicorn** - Lightning-fast ASGI server
- **MySQL** - Database backend via `database/db_utils.py`
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

### Get all weapons (first page)
```bash
curl "http://localhost:8000/api/weapons?page=1&limit=10"
```

### Search for weapons
```bash
curl "http://localhost:8000/api/weapons?search=gauss&weapon_type=Ranged"
```

### Get specific weapon
```bash
curl "http://localhost:8000/api/weapons/1"
```

### Query RAG system
```bash
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What perks affect shotguns?"}'
```

### Get database stats
```bash
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

## CORS Configuration

CORS is enabled for:
- `http://localhost:5173` (React dev server - Vite)
- `http://localhost:3000` (Alternative React port)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

To add more origins, edit `api/main.py` and add them to the `allow_origins` list.

## Project Structure

```
api/
├── main.py                 # FastAPI app with route registration
├── routes/
│   ├── weapons.py          # Weapons endpoints
│   ├── armor.py            # Armor endpoints
│   ├── perks.py            # Perks endpoints (regular + legendary)
│   ├── mutations.py        # Mutations endpoints
│   ├── consumables.py      # Consumables endpoints
│   └── rag.py              # RAG query endpoints
└── models/
    ├── common.py           # Pagination, health check models
    ├── weapons.py          # Weapon Pydantic models
    ├── armor.py            # Armor Pydantic models
    ├── perks.py            # Perk Pydantic models
    ├── mutations.py        # Mutation Pydantic models
    ├── consumables.py      # Consumable Pydantic models
    └── rag.py              # RAG query models
```

## Database Integration

The API uses the centralized database utility (`database/db_utils.py`) for all database operations:

- **Connection pooling**: Automatic connection reuse
- **Query caching**: Lookup tables cached in memory (300x faster)
- **Views**: Queries use optimized database views for backward compatibility

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `404` - Resource not found
- `422` - Validation error
- `500` - Server error
- `503` - Service unavailable (database/RAG system)

Error responses include a `detail` field with the error message.

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# With custom log level
uvicorn main:app --reload --log-level debug
```

### Adding New Endpoints

1. Create model in `api/models/` if needed
2. Create route file in `api/routes/`
3. Register router in `api/main.py`

Example:
```python
# In api/main.py
from api.routes import my_new_route
app.include_router(my_new_route.router, prefix="/api")
```

## Environment Variables

The API uses the same `.env` file as the rest of the project:

```bash
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=f76

# AI APIs (for RAG)
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## Performance

- **Database queries**: 5-10ms (with caching)
- **RAG queries**: 2-3s (includes AI processing)
- **Pagination**: Efficient with indexed queries
- **Concurrent requests**: Handled by Uvicorn's async capabilities

## Related Documentation

- Parent project: `../README.md`
- Database schema: `../database/f76_schema_normalized.sql`
- RAG system: `../rag/`
- Frontend: `../react/`

## License

MIT
