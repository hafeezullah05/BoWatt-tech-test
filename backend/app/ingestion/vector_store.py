"""Chroma vector store for embedded source chunks."""

import uuid
from functools import lru_cache

import chromadb
from chromadb import Collection

from app.config import get_settings


@lru_cache
def get_collection() -> Collection:
    """Return the Chroma collection holding embedded source chunks.

    Cached so the same persistent client and collection are reused across
    requests instead of being reopened every time.
    """
    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection("sources")


def add_chunks(chunks: list[str], embeddings: list[list[float]], source_name: str) -> None:
    """Store embedded chunks from one uploaded source file.

    Args:
        chunks: The text chunks (from chunk_text).
        embeddings: The corresponding embedding vectors (from embed_texts),
            same length and order as chunks.
        source_name: The original filename, stored as metadata so retrieved
            chunks can be attributed back to their source.
    """
    if not chunks:
        # Nothing to store (e.g. an empty uploaded file). Avoid calling
        # Chroma with empty lists.
        return

    collection = get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": source_name} for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query(query_embedding: list[float], n_results: int = 5) -> list[str]:
    """Find the stored chunks most relevant to a query embedding.

    Args:
        query_embedding: The embedding of the user's research question.
        n_results: Maximum number of chunks to return.

    Returns:
        The most relevant chunk texts, most relevant first. Returns an
        empty list if the store is empty or the query fails, so a
        retrieval problem never blocks answering the question.
    """
    # TODO: edge case — no relevance threshold. Irrelevant chunks are still
    # returned and injected into the prompt as long as *something* has been
    # uploaded, even if nothing stored is actually related to the question.
    collection = get_collection()

    if collection.count() == 0:
        return []

    try:
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    except Exception:
        # TODO: log this properly instead of silently swallowing it.
        return []

    return results["documents"][0]