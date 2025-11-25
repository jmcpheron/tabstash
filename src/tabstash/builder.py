"""Static site builder for TabStash."""

import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .models import Tab
from .parser import extract_sections, parse_directory
from .search import generate_search_index


@dataclass
class BuildResult:
    """Result of a build operation."""

    pages_generated: int = 0
    search_index_size: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class SiteBuilder:
    """Builds the static site from tab content."""

    def __init__(
        self,
        content_dir: Path,
        templates_dir: Path,
        static_dir: Path,
        output_dir: Path,
    ):
        self.content_dir = content_dir
        self.templates_dir = templates_dir
        self.static_dir = static_dir
        self.output_dir = output_dir

        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
        )

    def build(self) -> BuildResult:
        """Build the complete static site."""
        result = BuildResult()

        # Clean and create output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

        # Copy static assets
        if self.static_dir.exists():
            shutil.copytree(self.static_dir, self.output_dir / "static")

        # Parse all tabs
        tabs = parse_directory(self.content_dir)
        if not tabs:
            result.errors.append("No tabs found in content directory")
            return result

        # Group tabs by artist
        tabs_by_artist: dict[str, list[Tab]] = defaultdict(list)
        for tab in tabs:
            tabs_by_artist[tab.artist_slug].append(tab)

        # Generate index page
        self._render_index(tabs, tabs_by_artist)
        result.pages_generated += 1

        # Generate artist pages
        for artist_slug, artist_tabs in tabs_by_artist.items():
            self._render_artist_page(artist_slug, artist_tabs)
            result.pages_generated += 1

        # Generate individual tab pages
        tabs_output = self.output_dir / "tabs"
        tabs_output.mkdir(exist_ok=True)

        for tab in tabs:
            self._render_tab_page(tab)
            result.pages_generated += 1

        # Generate search index
        search_index_path = self.output_dir / "search-index.json"
        result.search_index_size = generate_search_index(tabs, search_index_path)

        return result

    def _render_index(
        self, tabs: list[Tab], tabs_by_artist: dict[str, list[Tab]]
    ) -> None:
        """Render the home page."""
        template = self.env.get_template("index.html")

        # Get unique artists with their display names
        artists = [
            {"slug": slug, "name": artist_tabs[0].metadata.artist, "count": len(artist_tabs)}
            for slug, artist_tabs in sorted(tabs_by_artist.items())
        ]

        html = template.render(
            tabs=tabs,
            artists=artists,
            total_tabs=len(tabs),
        )
        (self.output_dir / "index.html").write_text(html)

    def _render_artist_page(self, artist_slug: str, tabs: list[Tab]) -> None:
        """Render an artist's tab listing page."""
        template = self.env.get_template("artist.html")

        html = template.render(
            artist_name=tabs[0].metadata.artist,
            artist_slug=artist_slug,
            tabs=tabs,
        )

        artist_dir = self.output_dir / "artist"
        artist_dir.mkdir(exist_ok=True)
        (artist_dir / f"{artist_slug}.html").write_text(html)

    def _render_tab_page(self, tab: Tab) -> None:
        """Render a single tab page."""
        template = self.env.get_template("tab.html")

        sections = extract_sections(tab.content)

        html = template.render(
            tab=tab,
            sections=sections,
        )

        # Create artist subdirectory
        tab_dir = self.output_dir / "tabs" / tab.artist_slug
        tab_dir.mkdir(parents=True, exist_ok=True)
        (tab_dir / f"{tab.slug}.html").write_text(html)
