# CLAUDE.md

## 1. Project Scope & Goals

You are helping develop and maintain a **Fallout 76 build database and RAG system** with a **MySQL 8+ backend**, a **Python RAG/API layer**, and a **React 19 + TypeScript frontend**. The system:

* Scrapes Fallout 76 data (weapons, armor, perks, mutations, consumables, collectibles)
* Stores it in a **fully normalized 3NF MySQL database** (`f76`)
* Exposes the data via:

  * A **hybrid SQL + vector RAG system** (ChromaDB + OpenAI embeddings)
  * A **FastAPI REST API**
  * A **React frontend** for character/build exploration

Your job: write and refactor code, database queries, and tests **within this repo**, using the existing architecture and tools, while following strict anti-hallucination and DB safety rules.

---

## 2. ALWAYS Use MCP Tools First

When running as Claude Code with MCPs available, **prefer MCP tools over ad-hoc code** for operations they support.

Use them as follows:

* **`mcp__mysql`** – Inspect schema, run SQL queries, verify data, debug RAG queries.
* **`mcp__filesystem`** – Read, edit, and create files in this repo (code, SQL, docs).
* **`mcp__memory`** – Store persistent knowledge about the project (e.g., schema version, design decisions).
* **`mcp__github`** – Interact with the GitHub repo (issues, PR context, etc.) if enabled.
* **`mcp__context7`** – Pull up-to-date library/framework docs as needed.
* **`mcp__playwright`** – Browser automation and scraping workflows.
* **`mcp__sequential-thinking`** – For complex multi-step refactors or design questions.
* **`mcp__fetch`** – Fetch external web content when needed.

**Default behavior:** before writing code that touches DB, filesystem, GitHub, browser, or external docs, ask: *“Can an MCP tool do this?”* If yes, use it.

---

## 3. Repository & Architecture Mental Model

High-level layout (you should keep this model in mind):

* **Backend / API**

  * `api/` – FastAPI app (entry in `api/main.py`, routes in `api/routes/`, Pydantic models in `api/models/`).
* **RAG Layer**

  * `rag/cli.py` – Interactive CLI for natural language queries.
  * `rag/query_engine.py`, `rag/hybrid_query_engine.py` – SQL and hybrid SQL+vector engines.
  * `rag/populate_vector_db.py` – Build ChromaDB embeddings.
  * `rag/test_no_hallucination.py` – Automated hallucination tests.
* **Database**

  * `database/f76_master_schema.sql` – **Single source of truth** for schema (fully normalized 3NF).
  * `database/db_utils.py` – Centralized DB utility (connection pooling, caching).
  * `database/import_all.sh` and `database/import_*.py` – Data import scripts (weapons, armor, perks, mutations, consumables, collectibles, mechanics).
* **Scrapers**

  * `scrapers/` – Playwright-based scrapers for the FO76 data sources.
* **Frontend**

  * `react/` – React 19 + TypeScript + Vite + TailwindCSS + DaisyUI + GSAP frontend.
* **Docs**

  * `docs/ANTI_HALLUCINATION.md` – Detailed hallucination-control design.

---

## 4. Database Rules (MySQL `f76`)

### Environment & connection

* Database: **MySQL 8.0+**, database name `f76`, credentials configured via `.env` (e.g. `DB_USER`, `DB_PASSWORD`, `DB_NAME`).
* Always work through the repo’s abstractions; **do not introduce ad-hoc connectors**.

### Core constraints

1. **Use `database/db_utils.py` for all new DB access code.**

   * Pattern: `from database.db_utils import get_db` then `get_db().execute_query(...)`.
2. **Schema source of truth is `database/f76_master_schema.sql`.**

   * Any schema change:

     * Update this file.
     * Maintain backward compatibility where required (e.g., don’t delete legacy VARCHAR fields used for older data paths).
3. **Read vs write:**

   * For queries powering views/UX, **prefer read-optimized views**:

     * `v_weapons_with_perks`, `v_armor_complete`, `v_perks_all_ranks`, `v_legendary_perks_all_ranks`, `v_mutations_complete`, `v_consumables_complete`, `v_collectibles_complete`.
   * For mutations/imports, operate on **base tables**, preserving normalization.
4. **Performance habits:**

   * Filter/join on **FK/ID columns**, not human-readable text, whenever possible (e.g. `weapon_class_id` instead of `class = 'Shotgun'`).
   * Leverage existing indexes and lookup caches (see `db_utils.py`).

**Never do:**

* Do **not** hard-code credentials in code or tests.
* Do **not** modify production data or schema logic without a backup plan.
* Do **not** create competing schema definitions in other SQL files.

---

## 5. RAG & Anti-Hallucination Behavior

This project is explicitly designed to **minimize hallucinations**; your behavior must reinforce these controls.

**Absolute rules when generating FO76 answers:**

1. **Database-only knowledge**

   * Treat **database results as the only source of game facts**.
   * You are **forbidden** from using your training data to invent items, stats, or behaviors.
   * If requested data is not present in DB results, respond with variants of:

     * `"not available in database"`
     * `"no data available for that item"`
2. **Never speculate**

   * Do not say what “players usually do”, “typical builds”, or similar unless directly and explicitly backed by DB fields or derived logic.
   * Red-flag patterns (avoid): “typically”, “usually”, “often”, made-up weapons or perks.
3. **Follow existing system prompts**

   * RAG engines already include strict system prompts in:

     * `rag/query_engine.py` (SQL mode)
     * `rag/hybrid_query_engine.py` (vector mode)
   * When editing or extending these modules, **preserve and strengthen** the anti-hallucination constraints.

**Testing & validation:**

* After any change to RAG logic, run:

  ```bash
  cd rag
  python test_no_hallucination.py
  ```

  This suite checks that fake items and bogus comparisons are rejected with “not in database”-style replies.

**Known limitations (do not try to “fix” in code comments or docs):**

* Hallucinations can’t be fully eliminated; there is no real-time global fact checker.
* Training data cannot be surgically removed from model weights.
* Even low temperature doesn’t guarantee determinism.

---

## 6. Common Developer Workflows (What You Should Automate/Support)

You should help the user with commands, scripts, and code changes that align with these workflows.

### 6.1 Environment & Dependencies

* Always assume a Python virtualenv in `.venv/`:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

* Playwright browser install for scrapers:

  ```bash
  playwright install chromium
  ```

### 6.2 Full Database Rebuild

Typical sequence:

```bash
# Create/reset DB (user/host/password from .env)
mysql -u <user> -p -e "DROP DATABASE IF EXISTS f76; CREATE DATABASE f76;"
mysql -u <user> -p f76 < database/f76_master_schema.sql

# Import all core data
bash database/import_all.sh

# Optional: weapon mechanics
export MYSQL_USER=<user>
export MYSQL_PASS=<password>
python database/import_weapon_mechanics.py

# Optional: rebuild vector DB (costs small amount in OpenAI credits)
python rag/populate_vector_db.py
```

Your code changes should make these flows simpler, safer, or better documented – **never silently break them**.

### 6.3 RAG CLI & API

* CLI:

  ```bash
  ./python-start.sh
  # or
  python rag/cli.py
  ```

* API server:

  ```bash
  ./api-start.sh
  # or
  cd api && uvicorn main:app --reload
  ```

You may refactor, extend, or create routes/models as long as you respect the anti-hallucination constraints and DB abstractions.

### 6.4 Frontend Dev (React)

The React app lives in `react/` and is a **character builder frontend** that talks to this backend.

Typical commands:

```bash
cd react
npm install
npm run dev      # http://localhost:5173
npm run build
npm run preview
npm run lint
```

When editing frontend code, remember:

* React 19 + TypeScript + Vite + TailwindCSS v4 + DaisyUI + GSAP.
* ESM imports only; follow the patterns in any existing development guidelines.

---

## 7. Coding Style & Constraints

When writing or refactoring code:

1. **Prefer incremental, well-scoped changes** with clear separation of concerns.
2. **Reuse existing utilities** (e.g. `db_utils.py`) instead of introducing parallel solutions.
3. **Document non-obvious behavior** with concise comments rather than new markdown files (unless truly necessary).
4. **Never commit secrets**, and never propose code that writes secrets to logs or front-end bundles.
5. **Treat README.md as the canonical source for installation instructions**. Do not duplicate that content into other docs.

---

## 8. How to Interpret User Requests

When the user asks for help inside this repo, assume:

* They want solutions that **fit into this architecture and tooling**.
* They care about:

  * **Data correctness**
  * **Low hallucination**
  * **Performance and normalization**

* You should:

  * Suggest concrete file paths and functions to edit.
  * Provide ready-to-paste code blocks.
  * Propose and, if allowed, run relevant tests (e.g. `tests/`, `rag/test_no_hallucination.py`).
  * Use MCP tools to inspect current code and DB state before making assumptions.

* You SHALL NOT:

  * Create ANY new documentation unless the user explicitly requests it or the user gives you explicit permission to do so. This is a hard rule that will never be broken for any reason. It is immutable law. PERIOD.
