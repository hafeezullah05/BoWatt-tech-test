# How I'd evaluate this agent, and why

Right now I have no automated way to measure answer quality — only manual spot-checking (see
the Zephyrine-9 test in [EXAMPLES.md](EXAMPLES.md)). Here's what I'd actually build, in order of
what matters most.

## 1. Faithfulness

Does the answer actually match the retrieved context, or did it make something up? This is the
most important thing to measure in a RAG system specifically, since grounding the answer in
real source material is the whole point of retrieval.

Plan: a small set of test questions with known-correct answers from a source file, then a
second LLM call as a judge — give it the retrieved context and the generated answer, ask it to
score whether every claim is actually supported by the context. This is the standard
"LLM-as-judge" approach used by frameworks like RAGAS, and it's practical without a large
hand-labeled dataset.

## 2. Hallucination rate

Closely related, but tracked separately for the no-context case specifically — when nothing
relevant was retrieved, does the agent clearly say it doesn't know, or does it confidently
invent an answer? Plan: a set of questions with no answer in any uploaded source, checking how
often the agent states uncertainty versus fabricates something plausible.

## 3. Retrieval quality, separate from generation quality

Right now if an answer is wrong, I can't tell whether retrieval pulled the wrong chunks or
Claude misused the right ones. I'd want to check retrieval on its own — for a known
question/source pair, did the correct chunk show up in the top-N results at all? This is also
where I'd check whether adding a similarity threshold (a known gap, see ARCHITECTURE.md)
actually helps or just hurts recall.

## 4. Basic user-facing signals (further out)

Response latency (time to first token matters a lot with streaming), and eventually real user
feedback (thumbs up/down) if this were a real product.

## Why this order

Faithfulness and hallucination are the risks that are actually dangerous in a research tool — a
confident, wrong answer is worse than a slow one. Retrieval quality is the lever I'd pull to fix
those once I could measure them. Everything else is secondary polish.
