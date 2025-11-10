# Fallout 76 ML DB - Quick Reference Guide

## What This Project Does

A **Fallout 76 game database** with AI-powered natural language queries. Ask questions like "Best bloodied build?" or "What perks affect shotguns?" and get intelligent answers powered by Claude AI + semantic search.

**Core Capability**: 1,206+ game items (weapons, armor, perks, mutations, consumables) in a searchable MySQL database accessible via REST API and RAG (Retrieval Augmented Generation).

---

## Project Status At A Glance

| Component | Status | Details |
|-----------|--------|---------|
| Database | ✅ Complete | MySQL 3NF schema, 1,206+ items, fully normalized |
| RAG System | ✅ Complete | Hybrid SQL+Vector search, Claude AI integration |
| REST API | ✅ Complete | FastAPI endpoints for all data types |
| Vector DB | ✅ Complete | 1,519 embeddings, ChromaDB, HNSW index |
| CLI Interface | ✅ Complete | Interactive REPL with conversation history |
| React Frontend | 🔄 70% | Skeleton exists, UI components in progress |
| Tests | ❌ None | Not implemented |
| Build System | ❌ None | No save/share functionality yet |

---

## Quick Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add credentials

# Initialize database
mysql -u user -p -e "CREATE DATABASE f76"
mysql -u user -p f76 < database/f76_master_schema.sql
bash database/import_all.sh
python rag/populate_vector_db.py  # Generate embeddings

# Run services
./api-start.sh              # FastAPI (localhost:8000)
./python-start.sh           # CLI RAG interface
cd react && npm run dev     # React frontend (localhost:5173)

# Development
cd api && uvicorn main:app --reload --port 8000
cd react && npm run dev
python -c "from rag.hybrid_query_engine import HybridFalloutRAG; rag = HybridFalloutRAG()"
```

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                  CLIENT LAYER                                   │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐              │
│  │React (dev) │  │  CLI REPL  │  │ External API │              │
│  └──────┬─────┘  └──────┬─────┘  └──────┬───────┘              │
└─────────┼────────────────┼──────────────┼──────────────────────┘
          │                │              │
          │  HTTP          │  Direct      │  HTTP
          │                │              │
┌─────────▼────────────────▼──────────────▼──────────────────────┐
│              FASTAPI REST SERVER (port 8000)                    │
│  /api/weapons  /api/armor  /api/perks  /api/rag/query         │
└─────────┬──────────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────────┐
│              RAG SYSTEM (Hybrid SQL + Vector)                   │
│  ├─ SQL Router (exact queries via Claude)                      │
│  ├─ Vector Router (semantic search via OpenAI + ChromaDB)     │
│  └─ Response Formatter (Claude natural language)               │
└─────────┬──────────────────────────────────────────────────────┘
          │
    ┌─────┴──────────┐
    │                │
┌───▼────────┐  ┌────▼──────────────┐
│  MySQL     │  │  ChromaDB Vectors │
│  Database  │  │  (1,519 embeds)   │
│ (1,206+    │  │  ~20MB storage    │
│  items)    │  │                    │
└────────────┘  └────────────────────┘
```

---

## Data Overview

### What's in the Database

**Weapons** (262 items)
- All ranged & melee weapons
- Multi-level damage values
- Special mechanics: charge, spin-up, chain lightning, explosive AOE

**Armor** (477 pieces)
- Regular armor (light, sturdy, heavy variants)
- Power armor
- All resistance types: DR, ER, RR, Cryo, Fire, Poison

**Perks** (240 regular + 28 legendary = 268 total)
- Regular perks: 1-5 ranks each (449 rank records)
- Legendary perks: 4 ranks each (112 rank records)
- SPECIAL requirements and race variants

**Mutations** (19)
- Positive/negative effects documented
- Exclusivity rules (Carnivore/Herbivore mutually exclusive)
- Class Freak/Strange in Numbers interactions

**Consumables** (180)
- Chems, food, aid, alcohol, beverages
- Effects and duration data
- Build-relevant modifiers

**Collectibles**
- Magazines and bobbleheads
- Series tracking
- Effect information

---

## API Endpoints

### Quick Reference

```
Health & Info
  GET  /              → API info
  GET  /health        → Health check
  GET  /stats         → Item counts

Weapons
  GET  /api/weapons?page=1&limit=20              → List (paginated)
  GET  /api/weapons/1                            → Get one
  GET  /api/weapons?search=gauss                 → Search
  GET  /api/weapons/types/list                   → All types

Armor
  GET  /api/armor?page=1&slot=chest              → List + filter
  GET  /api/armor/1                              → Get one
  GET  /api/armor/types/list                     → All types

Perks
  GET  /api/perks?page=1&special=strength        → Regular perks
  GET  /api/perks/legendary                      → Legendary perks
  GET  /api/perks/1                              → Get one with ranks

Mutations
  GET  /api/mutations?page=1                     → List
  GET  /api/mutations/1                          → Get one

Consumables
  GET  /api/consumables?category=chem            → List + filter
  GET  /api/consumables/1                        → Get one

RAG (AI Queries)
  POST /api/rag/query                            → Query
  GET  /api/rag/health                           → RAG health
```

Example:
```bash
curl "http://localhost:8000/api/weapons?search=gauss&limit=5"
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What perks affect shotguns?"}'
```

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Core backend |
| **Web** | FastAPI | 0.115.6 | REST API |
| **Server** | Uvicorn | 0.38.0 | ASGI server |
| **Database** | MySQL | 8.0+ | Main data storage |
| **Vector DB** | ChromaDB | 1.2.1 | Embeddings storage |
| **AI/ML** | Claude | (Anthropic) | SQL + responses |
| **Embeddings** | OpenAI | text-embedding-3-small | Semantic search |
| **Frontend** | React | 19 | Web UI (dev) |
| **Frontend Build** | Vite | Latest | Build tool |
| **Styling** | TailwindCSS | v4 | CSS framework |
| **Scraping** | Playwright | 1.55.0 | Web automation |
| **Data** | Pandas | 2.3.3 | CSV processing |

---

## Key Files to Know

| Path | Purpose | Lines |
|------|---------|-------|
| `database/f76_master_schema.sql` | Database schema | ~1500 |
| `database/db_utils.py` | DB utility (centralized) | 439 |
| `api/main.py` | FastAPI app entry | 156 |
| `rag/hybrid_query_engine.py` | Hybrid RAG system | ~400 |
| `rag/cli.py` | Interactive REPL | ~80 |
| `rag/query_engine.py` | SQL-based RAG | ~300 |
| `database/import_*.py` | Data import scripts | ~1600 total |
| `react/src/App.tsx` | React main component | TBD |

---

## Common Tasks

### Query the Database via API

```bash
# Get all weapons
curl "http://localhost:8000/api/weapons?page=1&limit=20"

# Search weapons
curl "http://localhost:8000/api/weapons?search=gauss"

# Get specific weapon
curl "http://localhost:8000/api/weapons/1"

# Filter by type
curl "http://localhost:8000/api/weapons?weapon_type=Ranged"

# Ask AI a question
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Best heavy gunner build?"}'
```

### Use the CLI RAG Interface

```bash
./python-start.sh

# Type natural language queries:
# > What's the damage of Gauss Shotgun?
# > Best bloodied build recommendations
# > Mutations that work with stealth rifles
# > Which perks affect heavy weapons?

# Commands:
# Type 'exit' or 'quit' to leave
# Type 'clear' to reset conversation
```

### Rebuild Embeddings

```bash
python rag/populate_vector_db.py

# This will:
# 1. Query all items from database
# 2. Generate OpenAI embeddings
# 3. Store in ChromaDB
# 4. Create HNSW index
# Cost: ~$0.001 for 1,200+ items
```

### Backup Database

```bash
mysqldump -u user -p f76 > backup.sql
tar -czf chroma_backup.tar.gz rag/chroma_db/
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ANTHROPIC_API_KEY not set` | Edit .env file with key from https://console.anthropic.com/settings/keys |
| `OPENAI_API_KEY not set` | Edit .env file with key from https://platform.openai.com/api-keys |
| `Database connection failed` | Check MySQL is running, credentials in .env |
| `Vector DB not found` | Run `python rag/populate_vector_db.py` |
| `React can't connect to API` | Make sure FastAPI server running on :8000 |
| `Import script fails` | Check CSV files in `data/input/` exist |

---

## Performance Metrics

- **SQL queries**: 50-200ms
- **Vector search**: 100-500ms  
- **Hybrid queries**: 200-800ms
- **RAG total**: 2-3 seconds
- **Lookup caching**: 300x faster
- **Cost per query**: $0.01-0.03
- **Database size**: ~50MB
- **Vector storage**: ~20MB
- **Total**: ~80MB

---

## Development Roadmap

**Current (70% complete)**
- Database: ✅
- RAG: ✅
- API: ✅
- CLI: ✅

**Next (Priority)**
1. Complete React frontend UI
2. Add build save/share
3. Implement synergy detection
4. Expand collectibles
5. Add tests

---

## Environment Setup

```bash
# .env file should contain:
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=f76

ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

---

## Support & Resources

- **README.md** - Full project documentation
- **PROJECT_ANALYSIS.md** - Comprehensive status report
- **ARCHITECTURE_OVERVIEW.md** - Technical architecture & diagrams
- **docs/TODO.md** - Detailed roadmap
- **api/README.md** - API documentation
- **react/README.md** - Frontend documentation

---

## File Structure at a Glance

```
fo76-ml-db/
├── api/                  # REST API (FastAPI)
├── rag/                  # RAG system + CLI
├── database/             # Schema + import scripts
├── data/                 # CSV source data
├── react/                # Frontend (React 19)
├── scrapers/             # Web scrapers
├── tests/                # Diagnostic scripts
├── docs/                 # Documentation
├── requirements.txt      # Dependencies
├── .env                  # Credentials (create from .env.example)
├── api-start.sh          # Start FastAPI
├── python-start.sh       # Start CLI
└── README.md             # Main documentation
```

---

**Last Updated**: November 10, 2025
**Project Maturity**: 70% Complete
**Active Development**: Yes
