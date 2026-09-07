# BoWatt Case Study — Research Agent

React frontend + FastAPI backend. Ask a research question, optionally upload source files, get
a streamed markdown answer that uses your uploaded sources when relevant.

Docs: [Architecture & design decisions](docs/ARCHITECTURE.md) ·
[Example queries](docs/EXAMPLES.md) ·
[Evaluation approach](docs/EVALUATION.md) ·
[Next steps](docs/NEXT-STEPS.md)

## What's working

- `POST /api/research` — streams a Claude-generated answer.
- `POST /api/sources` — uploads `.txt`-style files, chunks + embeds them locally, stores them in
  Chroma.
- Retrieval: before answering, the backend embeds the question, pulls relevant stored chunks (if
  any), and feeds them to Claude as context.
- Error handling on the crash-prone paths: empty requests, empty upload batches, non-UTF-8
  files, API failures mid-stream.
- Concurrency: multiple file uploads processed in parallel; blocking calls (embedding, vector
  search) run off the event loop.

Not built yet: a web-search tool, and a real tool-calling agent loop. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for why, and [docs/NEXT-STEPS.md](docs/NEXT-STEPS.md)
for the plan.

## Prerequisites

- Python 3.11
- Node.js
- An [Anthropic API key](https://console.anthropic.com)
- A [Tavily API key](https://tavily.com) (for the planned web-search tool, not required yet)

## Setup

**Backend**

```bash
conda create -n bowatt-backend python=3.11 -y
conda activate bowatt-backend
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and add your real `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`.

**Frontend**

```bash
cd frontend
npm install
```

## Run it

Two terminals, from the project root.

```bash
cd backend
conda activate bowatt-backend
uvicorn main:app --reload --port 8787
```

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

## Try it

1. Upload a `.txt` file with something Claude wouldn't already know.
2. Ask about it — the answer should reflect the file, not general knowledge.
3. Ask something unrelated with nothing uploaded — it should fall back to Claude's own
   knowledge.

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for the exact test I ran.

## Project structure

```
backend/
  main.py                    # FastAPI app, CORS
  rest/router.py              # POST /api/research, POST /api/sources
  app/
    config.py                 # settings from .env
    schemas.py                  # request/response models
    agent/research_agent.py      # retrieval + streamed Claude answer
    ingestion/
      chunking.py                # text -> overlapping chunks
      embeddings.py                 # local sentence-transformers model
      vector_store.py                # Chroma (add/query)
frontend/                        # provided React + Vite UI
```
