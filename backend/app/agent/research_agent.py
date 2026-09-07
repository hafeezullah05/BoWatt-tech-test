"""Streaming research agent with retrieval over uploaded sources."""

import asyncio
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.config import get_settings
from app.ingestion.embeddings import embed_texts
from app.ingestion.vector_store import query


def _build_prompt(request: str, context_chunks: list[str]) -> str:
    """Combine the user's request with any relevant retrieved context.

    Args:
        request: The user's research question.
        context_chunks: Relevant chunks retrieved from uploaded sources, if any.

    Returns:
        The final prompt text to send to Claude.
    """
    if not context_chunks:
        return request

    context = "\n\n".join(context_chunks)
    return (
        "Use the following context from the user's uploaded sources if it is "
        f"relevant to the question.\n\nContext:\n{context}\n\nQuestion: {request}"
    )


async def stream_research(request: str) -> AsyncIterator[str]:
    """Stream a Claude-generated markdown answer to a research request.

    Retrieves relevant chunks from uploaded sources before asking Claude,
    so the answer can draw on the user's own documents when relevant.

    Args:
        request: The user's research question.

    Yields:
        Successive text chunks of the answer as they are generated. If
        retrieval fails, falls back to answering without context rather than
        failing the whole request. If the Claude call itself fails, yields a
        readable error message instead of letting the exception crash the
        stream mid-response.
    """
    settings = get_settings()

    try:
        query_vector = (await asyncio.to_thread(embed_texts, [request]))[0]
        context_chunks = await asyncio.to_thread(query, query_vector, 3)
    except Exception:
        # TODO: log this properly. Failing open (no context) is preferable
        # to failing the whole research request over a retrieval problem.
        context_chunks = []

    prompt = _build_prompt(request, context_chunks)
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    # TODO: no system prompt — Claude isn't explicitly instructed to behave
    # like a research agent, cite when it uses retrieved context, or say
    # when it doesn't know something.
    # TODO: max_tokens is hardcoded; a long answer could be cut off silently.

    try:
        async with client.messages.stream(
            model=settings.claude_model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except Exception as error:
        yield f"\n\n_Sorry, something went wrong while generating the answer: {error}_"