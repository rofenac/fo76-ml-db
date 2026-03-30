# Fallout 76 Build Database & RAG System

> **Note:** The frontend exists but needs significant work. The CLI and API are fully functional. Use `bash python-start.sh` for the CLI or `bash api-start.sh` for the REST API.
>
> This project incurs a small monetary cost via Anthropic and OpenAI API fees. Feel free to adapt it to local models if desired.

Python-based system that scrapes Fallout 76 game data, stores it in a fully normalized MariaDB database, and exposes it via a hybrid SQL + vector RAG layer, a FastAPI REST API, a React frontend, and a CLI.

The database contains weapons, armor, perks, legendary perks, mutations, consumables, and collectibles — 3,200+ records across 33 tables and 11 views, optimized for fast queries via a centralized database utility and read-optimized views.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rofenac/fo76-ml-db.git
cd fo76-ml-db
```

---

### 2. Python environment & dependencies

Dependencies are managed via [`uv`](https://docs.astral.sh/uv/). Install it first:

```bash
# Arch Linux
sudo pacman -S uv

# macOS / Linux (official installer)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sync all Python dependencies (uv creates `.venv` automatically):

```bash
uv sync
```

---

### 3. MariaDB setup

Install and initialize MariaDB:

```bash
# Arch Linux
sudo pacman -S mariadb
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl enable --now mariadb
sudo mysql_secure_installation
```

Create the database and apply the schema:

```bash
sudo mariadb -e "CREATE DATABASE IF NOT EXISTS f76;"
sudo mariadb f76 < database/f76_master_schema.sql
```

> `database/f76_master_schema.sql` is the single source of truth for the normalized schema.

> **If you import a schema dumped on another machine**, views may fail with a `definer does not exist` error. Fix it by running:
> ```bash
> sudo mariadb f76 -sN -e "SELECT CONCAT('CREATE OR REPLACE DEFINER=\`YOUR_USER\`@\`localhost\` SQL SECURITY DEFINER VIEW \`', TABLE_NAME, '\` AS ', VIEW_DEFINITION, ';') FROM information_schema.VIEWS WHERE TABLE_SCHEMA = 'f76';" | sudo mariadb f76
> ```

---

### 4. Environment configuration

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
ANTHROPIC_API_KEY=sk-ant-...       # Required for RAG queries
OPENAI_API_KEY=sk-...              # Required for vector embeddings
DB_HOST=localhost
DB_USER=your_mariadb_user
DB_PASSWORD=your_password
DB_NAME=f76
```

> **Windows users:** If you edited `.env` on Windows, strip carriage returns before running scripts:
> ```bash
> sed -i 's/\r//' .env
> ```

---

### 5. Import game data

```bash
bash database/import_all.sh
```

---

### 6. Build the vector database (optional but recommended for RAG/CLI)

Generates OpenAI embeddings and populates the ChromaDB vector store (~$0.001 cost):

```bash
uv run python rag/populate_vector_db.py
```

---

### 7. Frontend dependencies (optional)

```bash
cd react
npm install
```

---

## Usage

### CLI (RAG queries)

```bash
bash python-start.sh
# or directly:
uv run python rag/cli.py
```

### API server

```bash
bash api-start.sh
```

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>

### Frontend (development)

```bash
cd react && npm run dev   # http://localhost:5173
```

---

## Optional: Playwright (scrapers only)

Only needed if you want to re-scrape data from the Fallout Wiki.

```bash
uv run playwright install chromium

# Arch Linux — install missing system libs:
sudo pacman -S --needed nss nspr at-spi2-core libcups libdrm libxcb \
    libxkbcommon libxcomposite libxdamage libxrandr mesa pango cairo alsa-lib
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| Database | MariaDB 10.x+ (MySQL-compatible) |
| Python runtime | Python 3.12+, managed by `uv` |
| API | FastAPI + Uvicorn |
| RAG | Anthropic Claude + OpenAI embeddings + ChromaDB |
| Scrapers | Playwright + BeautifulSoup |
| Frontend | React 19 + TypeScript + Vite + TailwindCSS v4 + DaisyUI |
