# What I'd do next, if I kept working on this

- Build the `search_web` tool (Tavily) and a real Claude tool-calling loop — the biggest
  remaining gap against the brief. See [ARCHITECTURE.md](ARCHITECTURE.md) for why I skipped it.
- Turn the evaluation approach in [EVALUATION.md](EVALUATION.md) into an actual runnable script,
  not just a description.
- Add a similarity/relevance threshold to retrieval instead of always returning the top-N.
- Write unit tests for the pieces that don't need a live API key (chunking, prompt building).
- Containerize with Docker so setup isn't dependent on my local Python/conda environment.
- Add basic upload queueing so large or many files don't block on each other unnecessarily.
