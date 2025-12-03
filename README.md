# Fallout 76 Build Database & RAG System

## NOTE: The frontend is currently in development. If you clone this project, you'll have to use the CLI version only until I can get the web gui up and running. Also, this project as written incurs some monetary cost via Anthropic and OpenAI API fees. Feel free to adapt it to local models if desired

Python-based system that scrapes Fallout 76 game data, stores it in a fully normalized MySQL 8+ database, and exposes it via a hybrid SQL + vector RAG layer, a FastAPI REST API, and a React frontend.

The database currently contains weapons, armor, perks, legendary perks, mutations, consumables, and collectibles, and is optimized for fast, reliable queries via a centralized database utility and read-optimized views.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rofenac/fo76-ml-db.git
cd fo76-ml-db
```

---

### 2. Python environment & dependencies

Create and activate a virtual environment, then install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Install Playwright’s Chromium browser for the scrapers (optional, only needed if you plan to scrape fresh data):

```bash
sudo apt-get install libnspr4 libnss3 libasound2t64
```

Or if you want to install ALL dependencies:

```bash
sudo .venv/bin/python -m playwright install-deps
```

---

### 3. MySQL setup

Create the `f76` database and apply the master schema (MySQL 8.0+):

```bash
mysql -u your_user -p -e "CREATE DATABASE IF NOT EXISTS f76;"
mysql -u your_user -p f76 < database/f76_master_schema.sql
```

The file `database/f76_master_schema.sql` is the **single source of truth** for the normalized schema.

---

### 4. Environment configuration

Copy the example environment file and edit it with your settings:

```bash
cp .env.example .env
```

Set at least:

* `DB_USER`, `DB_PASSWORD`, `DB_NAME` – your MySQL credentials and database name
* `ANTHROPIC_API_KEY` – Claude API key
* `OPENAI_API_KEY` – OpenAI API key (for embeddings)

Keys and DB credentials are read by the backend via this `.env` file; do not hard-code them in code.

---

### 5. Import game data

Use the provided scripts to load all scraped data into the database:

```bash
bash database/import_all.sh
```

### 6. Build the vector database for RAG (optional but recommended)

Generate OpenAI embeddings and populate the ChromaDB vector store:

```bash
python rag/populate_vector_db.py
```

This step incurs a small OpenAI cost (on the order of ~$0.001 per full rebuild).

---

### 7. Install frontend dependencies (React app)

The React character builder frontend lives in the `react/` directory.

```bash
cd react
npm install
# For development:
npm run dev      # http://localhost:5173
# For production build:
npm run build
```

The frontend is built with **React 19**, **TypeScript**, **Vite**, **TailwindCSS v4**, **DaisyUI**, and **GSAP**.

---

Once these steps are complete, the project is fully installed locally with:

* MySQL schema and data loaded
* Python dependencies and RAG components ready
* Optional vector database populated
* Frontend dependencies installed
