"""Parse markdown tab files with YAML frontmatter."""

import re
from pathlib import Path

import frontmatter

from .models import Tab, TabMetadata


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def parse_file(path: Path) -> Tab:
    """Parse a single markdown tab file."""
    post = frontmatter.load(path)
    metadata = TabMetadata.model_validate(post.metadata)

    # Derive slugs from file path structure: content/tabs/artist/song.md
    song_slug = path.stem
    artist_slug = path.parent.name

    return Tab(
        metadata=metadata,
        content=post.content,
        source_path=path,
        slug=song_slug,
        artist_slug=artist_slug,
    )


def parse_directory(content_dir: Path) -> list[Tab]:
    """Parse all markdown files in the tabs directory."""
    tabs_dir = content_dir / "tabs"
    if not tabs_dir.exists():
        return []

    tabs = []
    for md_file in tabs_dir.rglob("*.md"):
        try:
            tab = parse_file(md_file)
            tabs.append(tab)
        except Exception as e:
            print(f"Warning: Failed to parse {md_file}: {e}")

    # Sort by artist, then title
    tabs.sort(key=lambda t: (t.metadata.artist.lower(), t.metadata.title.lower()))
    return tabs


def extract_sections(content: str) -> list[str]:
    """Extract section headers like [Verse], [Chorus] from content."""
    pattern = r"^\[([^\]]+)\]"
    sections = []
    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            sections.append(match.group(1))
    return sections
