"""Text embedding using a local sentence-transformers model."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the sentence-transformers model.

    Cached so the (relatively large) model is loaded into memory only once
    per process, not on every embedding call.
    """
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of text chunks into vectors.

    Args:
        texts: The pieces of text to embed (e.g. document chunks from
            chunk_text, or a single-item list containing a user's query).

    Returns:
        One embedding vector per input text, in the same order. Returns an
        empty list if given no texts, rather than calling the model with
        empty input.
    """
    if not texts:
        return []

    model = get_embedding_model()
    vectors = model.encode(texts)
    return vectors.tolist()