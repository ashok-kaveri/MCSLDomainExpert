# Phase 1: Foundation - Research

**Researched:** 2026-04-15
**Domain:** Python RAG pipeline — ChromaDB, LangChain, Ollama embeddings, Streamlit, Google Sheets
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RAG-01 | Ingest 26 pre-scraped KB articles from `docs/kb_snapshots/` into `mcsl_knowledge` | KB files confirmed present; pattern: read markdown, RecursiveCharacterTextSplitter, source_type="kb_articles" |
| RAG-02 | Ingest TC sheet from Google Sheets ID `1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY` into `mcsl_knowledge` | FedEx sheets_loader.py pattern directly reusable; service account + public CSV fallback |
| RAG-03 | Index MCSL wiki (241 markdown docs) into `mcsl_knowledge` | FedEx wiki_loader.py directly reusable; adapt _CATEGORY_MAP to MCSL wiki folder structure |
| RAG-04 | Index storepepSAAS `server/src/shared/` JS codebase into `mcsl_code_knowledge` | FedEx code_indexer.py directly reusable; set extensions=[".js"], root=server/src/shared/ |
| RAG-05 | Index mcsl-test-automation repo into `mcsl_code_knowledge` | FedEx codebase_loader.py directly reusable; extensions={".ts", ".json", ".md"}, exclude carrier-envs/ |
| RAG-06 | Auto-embed approved Trello card ACs and test cases into `mcsl_knowledge` after each sprint | FedEx rag_updater.py directly reusable; same upsert_documents() interface |
| RAG-07 | Domain Expert Chat answers MCSL questions using RAG with ≤200-word responses | FedEx chain.py + chat_app.py directly reusable; adapt prompts and quick-ask questions |
| INFRA-01 | `config.py` uses explicit dotenv: `load_dotenv(Path(__file__).parent / ".env")` | Exact pattern verified in FedexDomainExpert/config.py line 5 |
| INFRA-02 | ChromaDB collections: `mcsl_knowledge` + `mcsl_code_knowledge` | Two-collection pattern verified in FedEx; vectorstore.py + code_indexer.py each own one collection |
| INFRA-03 | All env vars in `.env`: ANTHROPIC_API_KEY, CLAUDE_SONNET_MODEL, CLAUDE_HAIKU_MODEL, STORE, SHOPIFY_ACCESS_TOKEN, SHOPIFY_API_VERSION, MCSL_AUTOMATION_REPO_PATH | Config pattern verified; add MCSL-specific vars beyond FedEx set |
| INFRA-04 | MCSL iframe: `iframe[name="app-iframe"]` (Phase 2 concern — scaffold placeholder in config.py) | Noted for config constant; not exercised in Phase 1 |
| INFRA-05 | Partial re-ingest: `python ingest/run_ingest.py --sources wiki shopify_actions` | FedEx run_ingest.py `--sources` argparse pattern directly reusable |
</phase_requirements>

---

## Summary

Phase 1 is a clone-and-adapt operation, not a greenfield build. The FedexDomainExpert at `~/Documents/Fed-Ex-automation/FedexDomainExpert` is the authoritative reference implementation — roughly 70-80% of the code transfers unchanged; the remainder requires MCSL-specific renaming (collection names, source paths, prompts, env var names) and one new ingest source (storepepSAAS JS codebase, which FedEx doesn't have in the same focused form).

The five ingestion sources map cleanly to existing loader patterns: KB articles use a simple markdown file walker (new, trivial), TC sheet reuses `sheets_loader.py` verbatim, MCSL wiki reuses `wiki_loader.py` with a renamed category map, storepepSAAS codebase reuses `code_indexer.py` with JS extensions, and mcsl-test-automation reuses `codebase_loader.py`. The `rag_updater.py` (Trello card auto-embed) and `chat_app.py` (Streamlit chat UI) require only minor text changes.

The single architectural difference from FedEx: two separate ChromaDB collections serve different roles. `mcsl_knowledge` holds human-readable domain content (KB articles, wiki, TC sheet, Trello cards). `mcsl_code_knowledge` holds code content (storepepSAAS backend, mcsl-test-automation). The vectorstore.py and code_indexer.py modules each manage their own collection instance via module-level singletons with HNSW config tuned to avoid a known ChromaDB large-batch HNSW overflow bug.

**Primary recommendation:** Clone FedexDomainExpert file-by-file, do minimal renaming to remove FedEx-specific references, add the MCSL-specific source paths and collection names, then write the KB article loader as the only net-new file. Validate with `python ingest/run_ingest.py --sources kb_articles` before running the full pipeline.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| langchain | >=0.3.0 | Document pipeline, chains, splitters | Already in FedEx requirements.txt; whole project built on it |
| langchain-anthropic | >=0.3.0 | Claude LLM integration | Anthropic API wrapper for ChatAnthropic |
| langchain-chroma | >=0.1.0 | ChromaDB vectorstore wrapper | LangChain-native Chroma integration |
| langchain-ollama | >=0.2.0 | Ollama embeddings (nomic-embed-text) | Local embedding without Anthropic dependency |
| langchain-text-splitters | >=0.3.0 | RecursiveCharacterTextSplitter | Standard chunking strategy |
| chromadb | >=0.5.0 | Vector database persistence | Project decision; already in FedEx |
| streamlit | >=1.39.0 | Chat UI | Project decision; already in FedEx |
| python-dotenv | >=1.0.1 | Env var loading | Required for INFRA-01 explicit dotenv path |
| gspread | >=6.1.2 | Google Sheets private access | Already in FedEx requirements.txt |
| google-auth | >=2.35.0 | Service account credentials | Companion to gspread |
| requests | >=2.32.3 | Public CSV fallback for Google Sheets | Lightweight, already required |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| fastapi + uvicorn | >=0.115.0 / >=0.32.0 | REST API layer | Scaffold now; used in later phases |
| pytest | >=8.3.3 | Test framework | Used in Validation Architecture |
| httpx | >=0.27.2 | Async HTTP test client | Companion to pytest for API tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Ollama nomic-embed-text | OpenAI/Anthropic embeddings | Project decision is local embeddings — don't change |
| ChromaDB | Pinecone, Weaviate, pgvector | Project decision; already running locally |
| gspread service account | Sheets API v4 directly | gspread is already in FedEx, simpler |

**Installation:**
```bash
pip install langchain>=0.3.0 langchain-core>=0.3.0 langchain-community>=0.3.0 \
  langchain-anthropic>=0.3.0 langchain-ollama>=0.2.0 langchain-text-splitters>=0.3.0 \
  chromadb>=0.5.0 langchain-chroma>=0.1.0 \
  streamlit>=1.39.0 \
  fastapi>=0.115.0 uvicorn>=0.32.0 \
  python-dotenv>=1.0.1 \
  gspread>=6.1.2 google-auth>=2.35.0 \
  requests>=2.32.3 \
  pytest>=8.3.3 httpx>=0.27.2
```

---

## Architecture Patterns

### Recommended Project Structure
```
MCSLDomainExpert/
├── config.py                    # INFRA-01: explicit dotenv, all constants
├── .env                         # ANTHROPIC_API_KEY, model names, store credentials
├── credentials.json             # Google service account (gitignored)
├── requirements.txt             # pinned from FedEx, add MCSL specifics
├── data/
│   └── chroma_db/               # ChromaDB persistence (two collections inside)
├── docs/
│   └── kb_snapshots/            # 26 pre-scraped KB markdown files (already present)
├── ingest/
│   ├── __init__.py
│   ├── run_ingest.py            # INFRA-05: --sources argparse, 5 sources
│   ├── kb_loader.py             # RAG-01: new file — walks docs/kb_snapshots/
│   ├── sheets_loader.py         # RAG-02: clone from FedEx, update GOOGLE_SHEETS_ID
│   ├── wiki_loader.py           # RAG-03: clone from FedEx, adapt _CATEGORY_MAP
│   └── codebase_loader.py       # RAG-04/05: clone from FedEx, supports both sources
├── rag/
│   ├── __init__.py
│   ├── vectorstore.py           # INFRA-02: mcsl_knowledge collection + all CRUD helpers
│   ├── code_indexer.py          # INFRA-02: mcsl_code_knowledge collection
│   ├── chain.py                 # RAG-07: conversational RAG chain, MCSL source labels
│   └── prompts.py               # RAG-07: MCSL-specific QA_PROMPT and CONDENSE_QUESTION_PROMPT
├── pipeline/
│   ├── __init__.py
│   └── rag_updater.py           # RAG-06: Trello card upsert into mcsl_knowledge
└── ui/
    ├── __init__.py
    └── chat_app.py              # RAG-07: Streamlit chat UI, MCSL quick-asks
```

### Pattern 1: Explicit dotenv Path (INFRA-01)
**What:** Load `.env` relative to `config.py` location, not the current working directory.
**When to use:** Always — MUST be first line of config.py.
```python
# Source: FedexDomainExpert/config.py line 5 (verified)
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

BASE_DIR = Path(__file__).parent
```

### Pattern 2: Two-Collection ChromaDB (INFRA-02)
**What:** Separate ChromaDB collections for domain knowledge vs. code knowledge. Each module owns one collection via module-level singleton.
**When to use:** vectorstore.py manages `mcsl_knowledge`; code_indexer.py manages `mcsl_code_knowledge`. Both share the same `CHROMA_PATH` (same persist directory, different collection names inside).

```python
# Source: FedexDomainExpert/rag/vectorstore.py (verified)
# HNSW config is critical — prevents 60-150GB link_lists.bin on Python 3.14
_vectorstore_instance = Chroma(
    collection_name=config.CHROMA_COLLECTION,   # "mcsl_knowledge"
    embedding_function=get_embeddings(),
    persist_directory=config.CHROMA_PATH,
    collection_metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 100,
        "hnsw:search_ef": 100,
        "hnsw:M": 16,
        "hnsw:batch_size": 100,
        "hnsw:sync_threshold": 1000,
    },
)
```

### Pattern 3: Source-Tagged Documents with Metadata
**What:** Every LangChain Document gets `source_type` metadata. This enables filtered retrieval and clear source attribution in chat.
**When to use:** All loaders must tag documents with a consistent `source_type` string.

```python
# Pattern used across all FedEx loaders (verified)
Document(
    page_content=chunk,
    metadata={
        "source": "kb_articles:setting-up-shopify-multi-carrier-shipping-label-app.md",
        "source_url": "https://www.pluginhive.com/knowledge-base/...",
        "source_type": "kb_articles",   # used for filtered retrieval
        "file_name": "setting-up-shopify-multi-carrier-shipping-label-app.md",
        "chunk_index": 0,
    },
)
```

### Pattern 4: Partial Re-Ingest via --sources Flag (INFRA-05)
**What:** argparse `--sources` accepts subset of source names. Per-source deletion before re-indexing prevents duplicates.
**When to use:** run_ingest.py entry point. Source names for MCSL: `kb_articles`, `sheets`, `wiki`, `storepepsaas`, `automation`.

```python
# Source: FedexDomainExpert/ingest/run_ingest.py (verified)
parser.add_argument(
    "--sources",
    nargs="*",
    choices=["kb_articles", "sheets", "wiki", "storepepsaas", "automation"],
    help="Which sources to ingest (default: all)",
)
# When a source is re-ingested, first delete existing chunks by source_type:
# vectorstore.delete_by_source_type("wiki") then add fresh docs
```

### Pattern 5: Upsert Semantics for RAG Auto-Updater (RAG-06)
**What:** Trello card content uses stable IDs (`{card_id}__ac`, `{card_id}__test_cases`) so re-running replaces instead of duplicates.
**When to use:** `rag_updater.py` — call `upsert_documents(docs, ids)` from vectorstore.py.

### Pattern 6: Google Sheets — Service Account + CSV Fallback (RAG-02)
**What:** Try `credentials.json` service account first; fall back to public CSV export if unavailable.
**When to use:** The MCSL TC sheet ID is `1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY`. The sheet has multiple tabs (Draft Plan, Sections, Single Label Generation, Orders Grid, Batch Flow, etc.) — must use gspread to iterate all worksheets, not just the first.

```python
# Source: FedexDomainExpert/ingest/sheets_loader.py (verified)
# Multi-tab access — critical for MCSL (FedEx sheet was single-tab)
for worksheet in spreadsheet.worksheets():
    all_rows.extend(worksheet.get_all_values())
```

### Pattern 7: Streamlit Chat with sys.path Fix
**What:** `chat_app.py` must insert project root into `sys.path` before any project imports because `streamlit run ui/chat_app.py` sets cwd to `ui/`.
```python
# Source: FedexDomainExpert/ui/chat_app.py lines 10-11 (verified)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

### Anti-Patterns to Avoid
- **Plain `load_dotenv()`:** Silently loads nothing when launched from a different working directory. Always use explicit path.
- **Single ChromaDB collection for everything:** Code chunks pollute domain knowledge retrieval. Keep `mcsl_knowledge` and `mcsl_code_knowledge` separate.
- **Large batch inserts without HNSW config:** ChromaDB + Python 3.14 allocates 60-150GB `link_lists.bin` without explicit HNSW parameters. Always set `hnsw:space`, `hnsw:M`, etc.
- **Batch size > 500 in add_documents:** Use `_CHROMA_BATCH_SIZE = 500` and loop. Verified fix in FedEx vectorstore.py.
- **Ingesting all of storepepSAAS:** 1,684 JS files including node_modules, tests, migrations is too noisy. Scope to `server/src/shared/` (929 JS files) and exclude node_modules, test/, migrations.
- **Re-running full ingest to update one source:** Use `--sources` flag + `delete_by_source_type()` to avoid rebuilding all embeddings.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text chunking | Custom splitter | `RecursiveCharacterTextSplitter` | Handles code, markdown, prose; overlap prevents context loss at boundaries |
| Vector similarity search | Custom cosine distance | `Chroma.similarity_search()` | HNSW index handles at-scale lookup; hand-rolled brute-force breaks at 10k+ chunks |
| LLM conversation memory | Custom dict-based history | `SimpleConversationalChain` pattern from FedEx | Already handles condensation, window truncation, multi-turn |
| Google Sheets auth | Raw `requests` to Sheets API | `gspread` + `google-auth` | OAuth token refresh, multi-worksheet iteration, service account handling already solved |
| Document deduplication | MD5 hashing all chunks | `_deduplicate()` using first-200-chars key | Fast, effective for exact duplicates from overlapping scrapes |
| Upsert semantics | Delete collection + rebuild | `delete_by_source_type()` + re-add | Preserves other sources; enables partial re-ingest (INFRA-05) |

**Key insight:** ChromaDB's HNSW index is not a toy — the vectorstore initialization parameters (hnsw:space, hnsw:M, batch_size) are non-obvious and getting them wrong causes silent disk bloat or search quality degradation. Use the exact config from FedexDomainExpert/rag/vectorstore.py without modification.

---

## Common Pitfalls

### Pitfall 1: Silent dotenv Load Failure
**What goes wrong:** `load_dotenv()` with no path argument resolves relative to CWD. When `streamlit run ui/chat_app.py` is invoked, CWD is the `ui/` directory, and `.env` is not found. All `os.getenv()` calls return `""` or default — ANTHROPIC_API_KEY is empty, API calls fail with auth errors.
**Why it happens:** Python `dotenv` searches upward from CWD by default, which fails in nested invocation contexts.
**How to avoid:** INFRA-01 mandates `load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)` in config.py. Already in FedEx; must be first thing in MCSL config.py.
**Warning signs:** `ANTHROPIC_API_KEY is not set` RuntimeError from `get_llm()`; ChromaDB path resolves to wrong directory.

### Pitfall 2: ChromaDB HNSW link_lists.bin Overflow
**What goes wrong:** On Python 3.14 + chromadb >= 0.5.0, creating a collection without explicit HNSW metadata causes an integer overflow in `max_elements` calculation. A 60-150GB sparse file (`link_lists.bin`) is created in the persist directory.
**Why it happens:** hnswlib uses `max_elements` to pre-allocate the index. Without `hnsw:M=16` and `hnsw:batch_size` set, the default is computed from a formula that overflows on 64-bit Python 3.14.
**How to avoid:** Always pass `collection_metadata` with all HNSW keys as shown in Pattern 2. This fix is already in FedexDomainExpert/rag/vectorstore.py.
**Warning signs:** Disk usage spikes to tens of GB immediately after first `add_documents()` call.

### Pitfall 3: Google Sheets — HTML Response Instead of CSV
**What goes wrong:** `_fetch_public_csv()` receives an HTML login page instead of CSV data when the sheet is not publicly shared. No exception is raised — the CSV parser silently produces garbage rows.
**Why it happens:** Google redirects unauthorized CSV export requests to the sign-in page with a 200 status.
**How to avoid:** Check `Content-Type` header: if `text/html`, raise `ValueError` and fall through to service account method. Pattern already in FedEx sheets_loader.py.
**Warning signs:** Chunks contain `<html>` or `Sign in - Google Accounts` text in ChromaDB.

### Pitfall 4: storepepSAAS Scope Creep
**What goes wrong:** Indexing the full `storepepSAAS/` tree (2,383 total JS files including node_modules and frontend) adds thousands of irrelevant chunks, degrading retrieval quality for carrier and order logic queries.
**Why it happens:** `os.walk()` without a strict skip list descends into `node_modules/` (often 1,500+ files) and `dist/`.
**How to avoid:** Scope the indexer root to `server/src/shared/` specifically (929 JS files confirmed). Add `node_modules`, `test`, `migrations`, `dist` to `_SKIP_DIRS`. File size limit of 100KB from code_indexer.py handles minified files.

### Pitfall 5: MCSL Wiki Category Map Mismatch
**What goes wrong:** Copying FedEx wiki_loader.py verbatim causes all MCSL wiki chunks to be tagged with FedEx-specific categories (`"Dashboard & Metrics"`, `"00_dashboard"`, etc.) which don't match the MCSL wiki folder structure.
**Why it happens:** `_CATEGORY_MAP` keys must match the actual top-level folder names in the wiki.
**How to avoid:** Map MCSL wiki top-level folders: `architecture/`, `modules/`, `patterns/`, `product/`, `zendesk/`, `support/`, `operations/`. Update `_CATEGORY_MAP` in wiki_loader.py accordingly.

### Pitfall 6: Missing sys.path in chat_app.py
**What goes wrong:** `import config` and `from rag.chain import ...` raise `ModuleNotFoundError` when Streamlit is launched as `streamlit run ui/chat_app.py`.
**Why it happens:** Streamlit sets CWD and sys.path based on the script location (`ui/`), not the project root.
**How to avoid:** Insert project root into sys.path at the top of chat_app.py before any project imports. Pattern is in FedexDomainExpert/ui/chat_app.py lines 10-11.

---

## Code Examples

### KB Article Loader (new file — RAG-01)
```python
# ingest/kb_loader.py — load pre-scraped KB articles from docs/kb_snapshots/
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config

def load_kb_articles() -> list[Document]:
    kb_dir = config.BASE_DIR / "docs" / "kb_snapshots"
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    documents = []
    for md_file in sorted(kb_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="replace").strip()
        if len(text) < 50:
            continue
        for i, chunk in enumerate(splitter.split_text(text)):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "source": f"kb_articles:{md_file.name}",
                    "source_url": _extract_source_url(text),
                    "source_type": "kb_articles",
                    "file_name": md_file.name,
                    "chunk_index": i,
                },
            ))
    return documents

def _extract_source_url(text: str) -> str:
    """Extract Source: URL from KB article header."""
    for line in text.splitlines()[:5]:
        if line.startswith("**Source:**"):
            return line.replace("**Source:**", "").strip()
    return ""
```

### config.py MCSL Variant (INFRA-01, INFRA-02, INFRA-03)
```python
# config.py — key MCSL-specific constants
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

BASE_DIR = Path(__file__).parent

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_SONNET_MODEL = os.getenv("CLAUDE_SONNET_MODEL", "claude-sonnet-4-6")
CLAUDE_HAIKU_MODEL = os.getenv("CLAUDE_HAIKU_MODEL", "claude-haiku-4-5-20251001")
DOMAIN_EXPERT_MODEL = os.getenv("DOMAIN_EXPERT_MODEL", CLAUDE_SONNET_MODEL)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

CHROMA_PATH = str(BASE_DIR / "data" / "chroma_db")
CHROMA_COLLECTION = "mcsl_knowledge"          # domain knowledge
CHROMA_CODE_COLLECTION = "mcsl_code_knowledge"  # codebase

# MCSL-specific paths
MCSL_AUTOMATION_REPO_PATH = os.getenv(
    "MCSL_AUTOMATION_REPO_PATH",
    str(Path.home() / "Documents" / "mcsl-test-automation"),
)
STOREPEPSAAS_SHARED_PATH = os.getenv(
    "STOREPEPSAAS_SHARED_PATH",
    str(Path.home() / "Documents" / "storepep-react" / "storepepSAAS" / "server" / "src" / "shared"),
)
MCSL_WIKI_PATH = os.getenv(
    "MCSL_WIKI_PATH",
    str(Path.home() / "Documents" / "mcsl-wiki" / "wiki"),
)
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", str(BASE_DIR / "credentials.json"))

# Shopify store
STORE = os.getenv("STORE", "mcsl-automation.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2023-01")

# RAG settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 8
MEMORY_WINDOW = 10
CODE_FILE_EXTENSIONS = [".ts", ".tsx", ".js", ".jsx", ".py", ".md"]

# MCSL iframe selector (used in Phase 2)
MCSL_IFRAME_SELECTOR = 'iframe[name="app-iframe"]'
```

### run_ingest.py MCSL 5-Source Structure (INFRA-05)
```python
# Source names for MCSL:
_DEFAULT_SOURCES = ["kb_articles", "sheets", "wiki", "storepepsaas", "automation"]
# kb_articles   — 26 pre-scraped KB markdown files from docs/kb_snapshots/
# sheets        — TC sheet from Google Sheets (all tabs)
# wiki          — 241 markdown docs from mcsl-wiki/wiki/
# storepepsaas  — JS files from storepepSAAS/server/src/shared/ → mcsl_code_knowledge
# automation    — TS/JSON/MD from mcsl-test-automation/ → mcsl_code_knowledge
```

### MCSL-Specific Domain Expert Prompt (RAG-07)
```python
# rag/prompts.py — adapt FedEx prompt for MCSL domain
DOMAIN_EXPERT_SYSTEM = """You are a senior domain expert for the PluginHive Shopify Multi Carrier Shipping Label (MCSL) App.

You have deep knowledge of:
- Every feature, setting, and workflow in the MCSL App (label generation, carrier setup, packaging, rates, batch processing)
- All supported carriers: FedEx, UPS, USPS, DHL, Canada Post, Aramex, TNT, Australia Post, and more
- The Playwright + TypeScript test automation suite for MCSL
- All test cases, expected behaviours, and acceptance criteria from the TC sheet and Trello cards

Rules you MUST follow:
1. Base your answer on the provided context. Synthesise across multiple chunks — do not require one chunk to have the full answer.
2. If context contains partial info, give the best answer and note gaps. Only say you don't know if context has nothing relevant.
3. Cite where information came from (e.g. "Source: MCSL wiki" or "Source: KB article").
4. Use bullet points for steps or lists. Keep answers to ≤200 words unless detail is explicitly requested.
5. Never invent carrier API behaviour. Only state what is in the retrieved context.

Context from knowledge base:
{context}"""
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `load_dotenv()` plain call | `load_dotenv(dotenv_path=Path(__file__).parent / ".env")` | FedEx project | Eliminates silent load failures across CWDs |
| Single ChromaDB collection | Two collections: domain + code | FedEx project | Cleaner retrieval; code chunks don't pollute domain search |
| Default ChromaDB HNSW | Explicit `collection_metadata` with all HNSW params | chromadb >=0.5.0 bug | Prevents 60-150GB disk allocation |

**Deprecated/outdated:**
- `langchain.vectorstores.Chroma`: Replaced by `langchain_chroma.Chroma` (separate package). Use `langchain-chroma>=0.1.0`.
- `langchain.embeddings.OllamaEmbeddings`: Replaced by `langchain_ollama.OllamaEmbeddings`.

---

## Open Questions

1. **Google Sheets access (RAG-02)**
   - What we know: Sheet ID confirmed. `credentials.json` for FedEx already exists in FedexDomainExpert. gspread multi-tab pattern works.
   - What's unclear: Whether a `credentials.json` service account exists for the MCSL TC sheet or if public CSV export is enabled. The FedEx credentials.json cannot be reused for a different Sheets owner.
   - Recommendation: Check if `credentials.json` needs to be provisioned for MCSL. If the sheet is publicly readable, the CSV fallback works with no credentials. Test with public CSV first; if it returns HTML, need service account credentials.

2. **storepepSAAS JS file scope for RAG-04**
   - What we know: `server/src/shared/` has 929 JS files. Key subdirectories confirmed: `storepepAdaptors/`, `order/`, `settings/`, `ratesApi/`.
   - What's unclear: Whether to index all 929 files or further narrow to specific subdirectories. More files = longer ingest time but better code coverage.
   - Recommendation: Start with full `server/src/shared/` (929 files), exclude `node_modules`, `test`, `migrations`. If retrieval quality degrades, narrow to key subdirectories.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 8.3.3 |
| Config file | None — Wave 0 creates `pytest.ini` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RAG-01 | KB articles load and produce >0 chunks | unit | `pytest tests/test_kb_loader.py -x` | ❌ Wave 0 |
| RAG-02 | TC sheet loads (public CSV fallback) and produces >0 chunks | unit | `pytest tests/test_sheets_loader.py -x` | ❌ Wave 0 |
| RAG-03 | MCSL wiki loader reads 241 files and produces >0 chunks | unit | `pytest tests/test_wiki_loader.py -x` | ❌ Wave 0 |
| RAG-04 | storepepSAAS codebase indexes >0 chunks into mcsl_code_knowledge | unit | `pytest tests/test_code_indexer.py::test_storepepsaas -x` | ❌ Wave 0 |
| RAG-05 | mcsl-test-automation indexes >0 chunks into mcsl_code_knowledge | unit | `pytest tests/test_code_indexer.py::test_automation -x` | ❌ Wave 0 |
| RAG-06 | rag_updater.update_rag_from_card() returns chunks_added>0 and is idempotent | unit | `pytest tests/test_rag_updater.py -x` | ❌ Wave 0 |
| RAG-07 | ask() returns a non-empty answer for a known MCSL question | integration | `pytest tests/test_chat.py -x` | ❌ Wave 0 |
| INFRA-01 | config.py loads ANTHROPIC_API_KEY from .env via explicit path | unit | `pytest tests/test_config.py::test_dotenv_explicit_path -x` | ❌ Wave 0 |
| INFRA-02 | Both collections exist in ChromaDB after ingest | integration | `pytest tests/test_vectorstore.py::test_both_collections -x` | ❌ Wave 0 |
| INFRA-03 | All required env vars present in .env.template | unit | `pytest tests/test_config.py::test_env_vars -x` | ❌ Wave 0 |
| INFRA-04 | MCSL_IFRAME_SELECTOR constant is defined in config | unit | `pytest tests/test_config.py::test_iframe_selector -x` | ❌ Wave 0 |
| INFRA-05 | run_ingest.py --sources wiki only reindexes wiki chunks | integration | `pytest tests/test_run_ingest.py::test_partial_reingest -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q --ignore=tests/test_chat.py` (skip LLM integration)
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/__init__.py` — empty init
- [ ] `tests/conftest.py` — shared fixtures: tmp ChromaDB path, mock embeddings, sample docs
- [ ] `tests/test_config.py` — covers INFRA-01, INFRA-03, INFRA-04
- [ ] `tests/test_kb_loader.py` — covers RAG-01
- [ ] `tests/test_sheets_loader.py` — covers RAG-02 (mock HTTP for CSV fallback)
- [ ] `tests/test_wiki_loader.py` — covers RAG-03
- [ ] `tests/test_code_indexer.py` — covers RAG-04, RAG-05
- [ ] `tests/test_rag_updater.py` — covers RAG-06
- [ ] `tests/test_vectorstore.py` — covers INFRA-02
- [ ] `tests/test_run_ingest.py` — covers INFRA-05
- [ ] `tests/test_chat.py` — covers RAG-07 (integration, requires live Ollama + Anthropic)
- [ ] `pytest.ini` — project root, testpaths=tests
- [ ] Framework install: `pip install pytest>=8.3.3 httpx>=0.27.2` (from requirements.txt)

---

## Sources

### Primary (HIGH confidence)
- FedexDomainExpert/config.py — explicit dotenv pattern, collection names, chunk settings
- FedexDomainExpert/rag/vectorstore.py — HNSW config, batch size, deduplication, upsert, delete_by_source_type
- FedexDomainExpert/rag/code_indexer.py — two-collection pattern, git sync, skip dirs, language map
- FedexDomainExpert/rag/chain.py — SimpleConversationalChain, labeled context, source_type grouping
- FedexDomainExpert/rag/prompts.py — QA_PROMPT and CONDENSE_QUESTION_PROMPT structure
- FedexDomainExpert/ingest/run_ingest.py — argparse --sources pattern, source dispatch
- FedexDomainExpert/ingest/wiki_loader.py — markdown walker, category mapping, chunk metadata
- FedexDomainExpert/ingest/sheets_loader.py — service account + public CSV fallback, multi-tab
- FedexDomainExpert/ingest/codebase_loader.py — generic code directory walker
- FedexDomainExpert/ui/chat_app.py — sys.path fix, session state, Streamlit chat pattern
- FedexDomainExpert/requirements.txt — canonical library versions
- MCSLDomainExpert/docs/kb_snapshots/ — 26 files confirmed present
- /Users/madan/Documents/mcsl-wiki/wiki/ — 241 markdown files confirmed
- /Users/madan/Documents/storepep-react/storepepSAAS/server/src/shared/ — 929 JS files confirmed
- /Users/madan/Documents/mcsl-test-automation/ — 58 TS files confirmed in tests/

### Secondary (MEDIUM confidence)
- MCSLDomainExpert/.planning/PROJECT.md — storepepSAAS key dirs, carrier codes, wiki subfolders
- MCSLDomainExpert/.planning/REQUIREMENTS.md — all req IDs and descriptions

### Tertiary (LOW confidence)
- None — all findings are directly verified from source files or confirmed directory scans.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified from FedexDomainExpert/requirements.txt and live file inspection
- Architecture: HIGH — verified by reading all key source files in reference implementation
- Pitfalls: HIGH — HNSW bug and dotenv pitfalls are documented in Fedex code comments with explicit fixes

**Research date:** 2026-04-15
**Valid until:** 2026-07-15 (stable libraries; ChromaDB and LangChain APIs change infrequently)
