# Fallout 76 ML Database - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT APPLICATIONS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐         ┌──────────────────────┐                  │
│  │   React Frontend     │         │   CLI Interface      │                  │
│  │   (React 19 + TS)    │         │  (Interactive REPL)  │                  │
│  │                      │         │                      │                  │
│  │  • Character Builder │         │  • Hybrid RAG        │                  │
│  │  • Perk Calculator   │         │  • Conversation      │                  │
│  │  • Build Planner     │         │  • Direct SQL        │                  │
│  │  • RAG Chat          │         │  • Vector search     │                  │
│  └──────────┬───────────┘         └──────────┬───────────┘                  │
│             │                                 │                             │
│             └────────────────────┬────────────┘                             │
│                                  │                                          │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
                    ┌──────────────▼────────────────┐
                    │    FASTAPI REST SERVER       │
                    │  (http://localhost:8000)     │
                    ├──────────────────────────────┤
                    │  Endpoints:                  │
                    │  • /api/weapons              │
                    │  • /api/armor                │
                    │  • /api/perks                │
                    │  • /api/mutations            │
                    │  • /api/consumables          │
                    │  • /api/rag/query            │
                    └──────────────┬───────────────┘
                                   │
     ┌─────────────────────────────┼─────────────────────────────┐
     │                             │                             │
     ▼                             ▼                             ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   DATABASE       │      │ RAG SYSTEM       │      │  VECTOR DB       │
│   LAYER          │      │ (Hybrid)         │      │  (ChromaDB)      │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│                  │      │                  │      │                  │
│ db_utils.py      │      │ Hybrid Engine    │      │ Embeddings:      │
│ (Centralized)    │      │ ├─ SQL Router    │      │ • 1,519 vectors  │
│                  │      │ ├─ Vector Router │      │ • 1536-dim       │
│ Features:        │      │ └─ Claude Format │      │ • HNSW index     │
│ • Singleton      │      │                  │      │ • ~20MB storage  │
│ • Caching (300x) │      │ Query Engine     │      │                  │
│ • Pooling        │      │ ├─ SQL mode      │      │ Collections:     │
│ • Transactions   │      │ └─ Vector mode   │      │ • fallout76      │
│                  │      │                  │      │                  │
│ Data Access:     │      │ AI Providers:    │      │ Use Cases:       │
│ • CRUD ops       │      │ • Claude (SQL)   │      │ • Semantic       │
│ • Bulk insert    │      │ • Claude (resp)  │      │   search         │
│ • Parameterized  │      │ • OpenAI (emb)   │      │ • Conceptual     │
│   queries        │      │                  │      │   queries        │
│ • Transactions   │      │ Context:         │      │                  │
│                  │      │ • 3-msg history  │      │                  │
└────────┬─────────┘      └──────────────────┘      └──────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│            MYSQL DATABASE (f76_master_schema.sql)                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CORE TABLES (1,206+ items)                                    │
│  ├─ weapons (262)              ─ Damage, type, mechanics       │
│  ├─ armor (477)                ─ Resistances, slot, class      │
│  ├─ perks (240)                ─ SPECIAL requirement, ranks    │
│  ├─ perk_ranks (449)           ─ Rank-specific effects        │
│  ├─ legendary_perks (28)       ─ Endgame 4-rank perks        │
│  ├─ legendary_perk_ranks (112) ─ Legendary rank effects       │
│  ├─ mutations (19)             ─ Effects, exclusivity         │
│  ├─ consumables (180)          ─ Chems/food/aid effects      │
│  └─ collectibles               ─ Magazines, bobbleheads       │
│                                                                  │
│  RELATIONSHIP TABLES                                           │
│  ├─ weapon_mechanics           ─ Charge, spin-up, etc.        │
│  ├─ perk_interactions          ─ Perk affects weapon/armor    │
│  ├─ consumable_effects         ─ Effect details              │
│  ├─ collectible_effects        ─ Collectible bonuses         │
│  └─ collectible_series         ─ Magazine series info        │
│                                                                  │
│  LOOKUP TABLES (Cached 300x faster)                           │
│  ├─ weapon_types, weapon_classes                             │
│  ├─ armor_types, armor_slots, armor_classes                  │
│  ├─ damage_types, special_attributes                         │
│  └─ races (Human, Ghoul)                                     │
│                                                                  │
│  VIEWS (For backward compatibility)                           │
│  ├─ v_weapons_with_perks        ─ Weapons + applicable perks │
│  ├─ v_armor_complete            ─ Armor + full stats         │
│  ├─ v_perks_all_ranks           ─ Perks expanded             │
│  ├─ v_mutations_complete        ─ Mutations + effects        │
│  └─ v_consumables_complete      ─ Consumables + modifiers    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────┐
│  User Query         │  "What perks affect shotguns?"
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ RAG Query Router                        │
│ • Analyze query intent                  │
│ • Determine if SQL or Vector            │
└──────────────┬────────────┬─────────────┘
               │            │
        ┌──────▼──────┐  ┌──▼────────────┐
        │ SQL Router  │  │ Vector Router │
        │ (Exact)     │  │ (Semantic)    │
        └──────┬──────┘  └──┬────────────┘
               │            │
       ┌───────▼────────┐   │
       │ Generate SQL   │   │
       │ via Claude     │   │
       └───────┬────────┘   │
               │            │
       ┌───────▼─────────────▼───────────┐
       │ Execute Query                   │
       ├─────────────────────────────────┤
       │ SQL: Direct database lookup     │
       │ Vector: Semantic search +       │
       │         SQL enrichment          │
       └───────┬─────────────────────────┘
               │
       ┌───────▼─────────────────────────┐
       │ Format Response (Claude)        │
       │ • Natural language output       │
       │ • Game mechanics context        │
       │ • Conversation awareness        │
       └───────┬─────────────────────────┘
               │
       ┌───────▼─────────────────────────┐
       │ Return to Client                │
       │ • Text response                 │
       │ • Execution time (ms)           │
       │ • Method used (SQL/Vector)      │
       └─────────────────────────────────┘
```

## Data Import Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ • Fallout Wiki (scraped via Playwright)                       │
│ • CSV files (data/input/*.csv)                                │
│ • Game databases (processed & manually verified)              │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │  Import Scripts (database/)       │
         ├───────────────────────────────────┤
         │                                   │
         │ • import_to_db.py                 │
         │   └─ Weapons & armor             │
         │                                   │
         │ • import_weapon_mechanics.py      │
         │   └─ Charge, spin-up, etc.      │
         │                                   │
         │ • import_armor.py                 │
         │   └─ Resistances, types, slots   │
         │                                   │
         │ • import_consumables.py           │
         │   └─ Chems, food, aid, alcohol   │
         │                                   │
         │ • import_mutations.py             │
         │   └─ Effects, exclusivity        │
         │                                   │
         │ • import_collectibles.py          │
         │   └─ Magazines, bobbleheads      │
         │                                   │
         │ Orchestrator:                     │
         │ └─ import_all.sh (bash script)   │
         │                                   │
         └─────────────────┬─────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │  DATA TRANSFORMATION              │
         ├───────────────────────────────────┤
         │                                   │
         │ • CSV parsing                     │
         │ • Data validation                 │
         │ • Normalization                   │
         │ • Deduplication                   │
         │ • Type conversion                 │
         │                                   │
         └─────────────────┬─────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │  BULK INSERT TO MYSQL             │
         ├───────────────────────────────────┤
         │                                   │
         │ Via db_utils.py:                  │
         │ • insert_many() for bulk ops      │
         │ • Transaction support            │
         │ • Foreign key constraints         │
         │ • Cascading deletes               │
         │                                   │
         └─────────────────┬─────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │  EMBEDDING GENERATION             │
         ├───────────────────────────────────┤
         │                                   │
         │ populate_vector_db.py:            │
         │                                   │
         │ 1. Query database for items      │
         │ 2. Generate embeddings (OpenAI)  │
         │ 3. Store in ChromaDB             │
         │ 4. Create HNSW index             │
         │                                   │
         │ Result: 1,519 vectors            │
         │         1536-dim (384 original)   │
         │         ~20MB storage            │
         │                                   │
         └─────────────────┬─────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │  READY FOR QUERIES                │
         ├───────────────────────────────────┤
         │                                   │
         │ • SQL queries via RAG             │
         │ • Vector semantic search          │
         │ • Hybrid approach                 │
         │ • REST API endpoints              │
         │                                   │
         └───────────────────────────────────┘
```

## Query Routing Logic

```
User Query Input
    │
    ▼
┌─────────────────────────────────────┐
│ Analyze Intent                      │
├─────────────────────────────────────┤
│                                     │
│ Heuristics:                         │
│ • Exact stats mention (damage, DR) │
│   → SQL query                      │
│ • Comparison/recommendation        │
│   → Vector + SQL (hybrid)          │
│ • Open-ended conceptual            │
│   → Vector search                  │
│ • Multiple factors involved        │
│   → Hybrid approach                │
│                                     │
└─────────────────┬───────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌──────────┐
   │ SQL    │  │ VECTOR │  │ HYBRID   │
   │ MODE   │  │ MODE   │  │ MODE     │
   └────┬───┘  └────┬───┘  └────┬─────┘
        │           │           │
        │     ┌─────▼─────┐     │
        │     │ Semantic  │     │
        │     │ Search    │     │
        │     │ (ChromaDB)│     │
        │     └─────┬─────┘     │
        │           │           │
        ├───────────┼───────────┤
        │           │           │
        ▼           ▼           ▼
   ┌────────────────────────────┐
   │ Format & Enrich Result      │
   │ (via Claude AI)             │
   │                             │
   │ • Natural language format   │
   │ • Game mechanics context    │
   │ • Conversation history      │
   │ • Coherent response         │
   └────────────────────────────┘
        │
        ▼
   Response with:
   • Answer text
   • Execution time (ms)
   • Query method (SQL/Vector/Hybrid)
```

## Technology Integration Points

```
┌───────────────────────────────────────────────────────────────┐
│                    ANTHROPIC CLAUDE                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Uses:                                                         │
│ 1. SQL Generation                                             │
│    • Analyze natural language                                │
│    • Generate MySQL queries                                  │
│    • Interpret results                                       │
│                                                               │
│ 2. Response Formatting                                        │
│    • Convert data to natural language                         │
│    • Add game mechanics context                              │
│    • Maintain conversation flow                              │
│                                                               │
│ API Key: ANTHROPIC_API_KEY                                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
              │                                    │
              │                                    │
┌─────────────▼──────────────┐  ┌────────────────▼─────────────┐
│      OPENAI EMBEDDINGS      │  │     MYSQL DATABASE          │
├─────────────────────────────┤  ├─────────────────────────────┤
│                             │  │                             │
│ Model:                      │  │ Schema: 3NF Normalized     │
│ text-embedding-3-small      │  │                             │
│                             │  │ Tables:                     │
│ Dimensions: 1536            │  │ • Core entities (weapons,   │
│                             │  │   armor, perks, etc)       │
│ Use:                        │  │ • Relationships            │
│ • Embed query text          │  │ • Lookup tables (cached)   │
│ • Embed item descriptions   │  │ • Views                    │
│ • Similarity search         │  │                             │
│                             │  │ Performance:                │
│ API Key: OPENAI_API_KEY     │  │ • Indexes on key columns  │
│                             │  │ • 300x faster with cache  │
│ Vectors: 1,519 total        │  │ • Foreign key constraints  │
│ Storage: ~20MB (ChromaDB)   │  │                             │
│                             │  │                             │
└─────────────────────────────┘  └─────────────────────────────┘
         │                                 │
         │                                 │
         └────────────────┬────────────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │   USER API   │
                    │  (FastAPI)   │
                    └──────────────┘
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT MACHINE                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  .env file (credentials):                                      │
│  • DB_HOST, DB_USER, DB_PASSWORD, DB_NAME                    │
│  • ANTHROPIC_API_KEY                                          │
│  • OPENAI_API_KEY                                             │
│                                                                │
│  Virtual Environment:                                         │
│  • .venv/bin/python                                           │
│  • requirements.txt (all dependencies)                        │
│                                                                │
│  Services (parallel execution):                               │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  FastAPI Server (port 8000)                          │    │
│  │  $ uvicorn api/main:app --reload --port 8000        │    │
│  │  └─ REST endpoints for all data                      │    │
│  │  └─ Health/stats monitoring                          │    │
│  │  └─ RAG query processing                             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  React Dev Server (port 5173)                        │    │
│  │  $ cd react && npm run dev                           │    │
│  │  └─ Vite dev server with HMR                         │    │
│  │  └─ Connects to API on localhost:8000                │    │
│  │  └─ TailwindCSS compilation                          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  CLI RAG Interface (interactive)                     │    │
│  │  $ python rag/cli.py                                 │    │
│  │  └─ Hybrid RAG system                                │    │
│  │  └─ Direct database access                           │    │
│  │  └─ Conversation history                             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
│  MySQL Server (local or networked):                          │
│  • Database: f76                                             │
│  • Schema: f76_master_schema.sql                             │
│  • Port: 3306 (default)                                      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## File Dependencies & Imports

```
api/main.py
├─ database/db_utils.py (centralized DB)
├─ api/routes/weapons.py
├─ api/routes/armor.py
├─ api/routes/perks.py
├─ api/routes/mutations.py
├─ api/routes/consumables.py
└─ api/routes/rag.py
   └─ rag/hybrid_query_engine.py
      ├─ database/db_utils.py
      ├─ rag/query_engine.py
      │  └─ database/db_utils.py
      ├─ chromadb (vector DB)
      ├─ anthropic.Anthropic (Claude)
      └─ openai.OpenAI (embeddings)

rag/cli.py
└─ rag/hybrid_query_engine.py
   └─ [same dependencies as above]

database/db_utils.py
└─ database/legacy_connector.py
   └─ mysql.connector

database/import_*.py files
├─ database/db_utils.py
├─ database/import_utils.py
├─ pandas (CSV parsing)
└─ anthropic.Anthropic (for data validation)
```

---

## Performance Characteristics

### Query Performance
- **SQL queries**: 50-200ms (direct database lookup)
- **Vector search**: 100-500ms (embedding similarity search)
- **Hybrid queries**: 200-800ms (combined approach)
- **RAG formatting**: 1-2 seconds (Claude response generation)
- **Total end-to-end**: 2-3 seconds

### Storage
- **MySQL database**: ~50MB (1,206+ items)
- **ChromaDB vectors**: ~20MB (1,519 embeddings)
- **Indexes**: ~10MB
- **Total**: ~80MB

### Caching
- **Lookup tables**: 300x faster (in-memory)
- **Cache size**: Minimal (lookup tables only)
- **Cache strategy**: Lazy loading on first access

### Cost
- **API calls per query**: 1-2 (Claude completion + embeddings)
- **Cost per query**: $0.01-0.03
- **Monthly estimate**: ~$3-10 with moderate usage

---

## Future Architecture Enhancements

Planned improvements for scalability and features:

1. **Async Operations**
   - FastAPI async/await throughout
   - Concurrent database operations
   - Background task processing

2. **Caching Layer**
   - Redis for distributed caching
   - Query result caching
   - Embedding cache

3. **Monitoring & Observability**
   - Query logging
   - Performance metrics
   - Error tracking
   - Analytics dashboard

4. **Advanced RAG**
   - Streaming responses
   - Follow-up question support
   - Source attribution
   - Confidence scoring

5. **Scaling**
   - Database replication
   - Load balancing
   - Microservices architecture
   - Containerization (Docker)

---

**Last Updated**: November 10, 2025
