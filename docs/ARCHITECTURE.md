# Architecture and design decisions

I kept this as a small, linear pipeline rather than a full agent framework — something I could
reason about end to end, not something that looks impressive but I can't fully explain.

## Why these choices

**FastAPI** — needed real streaming (frontend reads the response body as it arrives).
`StreamingResponse` + `async`/`await` made that straightforward.

**Claude for generation, a local model for embeddings** — Anthropic doesn't offer an embeddings
endpoint, so rather than pull in a second paid API just for that, I used a small local
`sentence-transformers` model (`all-MiniLM-L6-v2`). Weaker than a hosted embeddings API, but
free, fast enough here, and works offline once cached.

**Chroma** — a vector store that runs locally with zero setup, persists to disk. Not a choice
I'd make for anything that needs to scale past one machine, but fine for this.

## How a request actually flows

1. **Upload** — file is read as text, split into overlapping ~200-word chunks along sentence
   boundaries (so a chunk never cuts a sentence in half), each chunk is embedded, and stored in
   Chroma.
2. **Question** — the question is embedded the same way, Chroma returns the most similar stored
   chunks, and if any are found, they get added to the prompt as context.
3. **Answer** — that prompt goes to Claude, and the response streams back token by token.

That's it — there's no agent "deciding" anything yet. It's a fixed retrieve-then-generate
pipeline, not a true agent. Worth being upfront about that.

## What's missing, and the one decision I want to flag

I did not get to the web-search tool, so "the agent should utilise external sources" isn't
done. With more time, I'd add a `search_web` tool (Tavily) and turn this into a real Claude
tool-calling loop, where Claude itself decides whether to check the knowledge base, search the
web, both, or neither, before answering. That's meaningfully bigger and riskier to get right
(tool-use message handling, running tools concurrently, feeding results back, looping until
done) — I'd rather ship something smaller that works than half-finish the bigger version.

## Other things I knowingly cut for time

Each marked with a `# TODO:` comment at the relevant spot in the code:

- No relevance threshold on retrieval — an irrelevant stored chunk can still get pulled in once
  anything has been uploaded.
- No deduplication on re-uploading the same file.
- No file size/count limits on uploads.
- No system prompt telling Claude how to behave as a research agent.
- Hardcoded `max_tokens` — a long answer could get cut off silently.
