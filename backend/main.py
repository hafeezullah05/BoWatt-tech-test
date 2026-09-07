"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from rest.router import router as research_router

settings = get_settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research_router)