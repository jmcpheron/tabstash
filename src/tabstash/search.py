"""Generate search index for MiniSearch."""

import json
from pathlib import Path

from .models import SearchDocument, Tab


def generate_search_index(tabs: list[Tab], output_path: Path) -> int:
    """Generate JSON search index for MiniSearch.

    Returns the number of documents indexed.
    """
    documents = [
        SearchDocument(
            id=f"{tab.artist_slug}/{tab.slug}",
            title=tab.metadata.title,
            artist=tab.metadata.artist,
            tags=tab.metadata.tags,
            url=f"/tabs/{tab.artist_slug}/{tab.slug}.html",
        ).model_dump()
        for tab in tabs
    ]

    output_path.write_text(json.dumps(documents, indent=2))
    return len(documents)
