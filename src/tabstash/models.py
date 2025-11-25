"""Pydantic models for tab metadata and content."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TabMetadata(BaseModel):
    """Validated frontmatter for a tab file."""

    title: str
    artist: str
    key: Optional[str] = None
    capo: int = Field(default=0, ge=0, le=12)
    tuning: str = "standard"
    difficulty: Optional[str] = None
    bpm: Optional[int] = Field(default=None, ge=20, le=300)
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", "artist")
    @classmethod
    def non_empty_string(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v.strip()

    @field_validator("difficulty")
    @classmethod
    def valid_difficulty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        valid = {"beginner", "intermediate", "advanced"}
        if v.lower() not in valid:
            raise ValueError(f"must be one of: {', '.join(valid)}")
        return v.lower()


class Tab(BaseModel):
    """A fully parsed tab with metadata and content."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    metadata: TabMetadata
    content: str
    source_path: Path
    slug: str
    artist_slug: str


class SearchDocument(BaseModel):
    """Document format for the MiniSearch index."""

    id: str
    title: str
    artist: str
    tags: list[str]
    url: str
