"""Request and response models for the API endpoints."""

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    """Body of a POST /api/research request.

    Attributes:
        request: The user's research question, as typed into the frontend.
    """

    request: str
    

class UploadedFileInfo(BaseModel):
    """Metadata about one successfully uploaded source file.

    Attributes:
        name: Original filename.
        size: File size in bytes.
        type: MIME type reported by the browser.
    """

    name: str
    size: int
    type: str


class UploadResponse(BaseModel):
    """Body of a POST /api/sources response.

    Attributes:
        uploaded: Metadata for each file that was embedded and stored.
    """

    uploaded: list[UploadedFileInfo]