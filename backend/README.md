# Evidence Retrieval + Scoring

This folder contains the first version of the backend for a fact-checking pipeline using Tavily API for evidence retrieval and GROQ API for LLM-based scoring.

## Core Modules

### `retrieval.py`
Web-based evidence retrieval using Tavily Search API.
- Searches the web for evidence supporting/contradicting claims
- Returns top 5 relevant sources with titles, URLs, and content snippets
- Uses advanced search depth for comprehensive results
- Truncates long content to 600 characters for efficient processing

**Main Functions:**
- `retrieve_references(claims: List[str]) -> Dict[str, List[Reference]]` — Async function to retrieve evidence for multiple claims
- `retrieve_references_sync(claims: List[str]) -> Dict[str, List[Reference]]` — Synchronous wrapper for scripts/tests

**Requirements:** `TAVILY_API_KEY` environment variable (get free key at https://tavily.com)

### `scoring.py`
LLM-based fact-checking that analyzes claims against retrieved evidence.
- Uses Groq API (team testing) or local Ollama (default) for LLM inference
- Provides verdict (True/False/Uncertain), truth score (0.00-1.00), and reasoning
- Truth score scale: 0.00-0.50 = False, 0.50 = Uncertain, 0.50-1.00 = True
- Limits evidence to 5 pieces and 400 characters each for optimal LLM performance

**Main Functions:**
- `check_claim(claim: str, references: List[Dict]) -> Dict` — Analyzes claim and returns verdict, truth_score, reasoning
- `groq_analyze(prompt: str, system_message: str) -> str` — Groq API LLM inference (requires `GROQ_API_KEY`)
- `local_analyze(prompt: str, system_message: str) -> str` — Local Ollama inference (requires Ollama running with llama3.1:8b)

**Requirements:** 
- Either `GROQ_API_KEY` environment variable OR
- Local Ollama server running with `llama3.1:8b` model

### `main.py`
FastAPI application providing REST API endpoints for fact-checking.

**Endpoints:**
- `GET /` — Health check endpoint
- `POST /retrieve-references` — Main fact-checking endpoint
  - Accepts: `{"claims": ["claim1", "claim2", ...]}`
  - Returns: verdict, truth_score, reasoning, and references for each claim

**Run server:**
```powershell
cd "c:\Users\avina\Comp\Study\SEPG\CiteMe Backend\V1\backend\evidence_retrieval"
uvicorn main:app --reload
```

### `cli.py`
Command-line interface for testing single claims.

**Usage:**
```powershell
python cli.py "The Earth is round"
```

**Output includes:**
- Claim text
- Verdict (True/False/Uncertain)
- Truth Score (0.00-1.00)
- Reasoning
- Evidence sources with titles, URLs, and snippets

### `config.py`
Configuration settings for the application (uses Pydantic BaseSettings).

### `test_all.py`
Comprehensive unit tests for all modules (18 tests total).

**Run tests:**
```powershell
python test_all.py
```

**Test coverage:**
- `TestRetrieval` — 5 tests for retrieval.py
- `TestScoring` — 8 tests for scoring.py
- `TestMain` — 3 tests for FastAPI endpoints
- `TestCLI` — 2 tests for CLI functionality
- `TestIntegration` — 1 full pipeline test

## Setup

1. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Set up Tavily API:**
```powershell
$env:TAVILY_API_KEY = "your-api-key-here"
```

3. **Choose LLM provider:**

**Option A: Local Ollama (recommended)**
```powershell
# Install Ollama from https://ollama.com
ollama serve
ollama pull llama3.1:8b
```

**Option B: Groq API (team testing)**
```powershell
$env:GROQ_API_KEY = "your-groq-api-key"
```

## Quick Start

**CLI Example:**
```powershell
python cli.py "Apples are red"
```

**API Example:**
```powershell
# Start server
uvicorn main:app --reload

# In another terminal
curl -X POST "http://localhost:8000/retrieve-references" -H "Content-Type: application/json" -d '{"claims": ["The Earth is round"]}'
```

## Truth Score Scale

- **0.90-1.00**: Definitely True (strong supporting evidence)
- **0.70-0.89**: Mostly True (good supporting evidence)
- **0.51-0.69**: Somewhat True (weak/mixed evidence leans true)
- **0.50**: Uncertain (insufficient/balanced evidence)
- **0.31-0.49**: Somewhat False (weak/mixed evidence leans false)
- **0.10-0.30**: Mostly False (good contradicting evidence)
- **0.00-0.09**: Definitely False (strong contradicting evidence)
