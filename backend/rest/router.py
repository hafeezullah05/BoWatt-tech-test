"""HTTP endpoints for the research agent API."""

import asyncio

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.agent.research_agent import stream_research
from app.ingestion.chunking import chunk_text
from app.ingestion.embeddings import embed_texts
from app.ingestion.vector_store import add_chunks
from app.schemas import ResearchRequest, UploadedFileInfo, UploadResponse

router = APIRouter()


@router.post("/api/research")
async def research(payload: ResearchRequest) -> StreamingResponse:
    """Stream a markdown research answer back to the frontend."""
    if not payload.request.strip():
        raise HTTPException(status_code=400, detail="Research request cannot be empty.")

    # TODO: edge case of a very long `request` values could exceed the model's
    # context window or run up cost unexpectedly. Consider a max length check.

    return StreamingResponse(
        stream_research(payload.request),
        media_type="text/plain",
    )


async def _process_file(file: UploadFile) -> UploadedFileInfo | None:
    """Extract, chunk, embed, and store one uploaded source file.

    Returns:
        Metadata for the stored file, or None if it could not be processed
        (e.g. not valid UTF-8 text) — so one bad file doesn't fail the
        entire upload batch.
    """
    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        # TODO: report this failure back to the frontend (e.g. a per-file
        # status in the response) instead of silently dropping the file.
        return None

    chunks = chunk_text(text)
    vectors = await asyncio.to_thread(embed_texts, chunks)
    add_chunks(chunks, vectors, file.filename)

    return UploadedFileInfo(name=file.filename, size=len(content), type=file.content_type)


@router.post("/api/sources")
async def upload_sources(files: list[UploadFile] = File(...)) -> UploadResponse:
    """Embed and store uploaded source files for later retrieval."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    # TODO: edge case when there is no limit on file size or count; a very large upload
    # could exhaust memory or take a long time to embed.
    # TODO: edge case when re-uploading the same file creates duplicate chunks
    # in Chroma; no deduplication exists.

    results = await asyncio.gather(*(_process_file(file) for file in files))
    uploaded = [result for result in results if result is not None]

    return UploadResponse(uploaded=uploaded)
