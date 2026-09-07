"""Splitting text into semantically coherent chunks for embedding."""

import re

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries.

    Args:
        text: The text to split.

    Returns:
        A list of individual sentences.
    """
    return [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    """Split text into overlapping, sentence-aligned chunks.

    Sentences are grouped together up to roughly chunk_size words per chunk,
    so a chunk boundary never lands in the middle of a sentence. Consecutive
    chunks share the last `overlap` words of the previous chunk, so meaning
    at the boundary isn't lost.

    Args:
        text: The full text to split.
        chunk_size: Target number of words per chunk.
        overlap: Number of words repeated at the start of the next chunk.

    Returns:
        A list of text chunks.
    """
    sentences = split_into_sentences(text)
    chunks: list[str] = []
    current_words: list[str] = []

    for sentence in sentences:
        current_words.extend(sentence.split())

        if len(current_words) >= chunk_size:
            chunks.append(" ".join(current_words))
            current_words = current_words[-overlap:]

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks