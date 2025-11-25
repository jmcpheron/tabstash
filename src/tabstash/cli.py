"""Command-line interface for TabStash."""

import http.server
import os
import socketserver
from pathlib import Path

import click

from .builder import SiteBuilder


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


@click.group()
def main():
    """TabStash - Static guitar tab site generator."""
    pass


@main.command()
@click.option(
    "--content",
    "-c",
    default="content",
    help="Content directory containing tabs",
)
@click.option(
    "--output",
    "-o",
    default="dist",
    help="Output directory for generated site",
)
@click.option(
    "--base-url",
    "-b",
    default="",
    help="Base URL path for GitHub Pages subpath hosting (e.g., /tabstash)",
)
def build(content: str, output: str, base_url: str):
    """Build the static site."""
    root = get_project_root()

    builder = SiteBuilder(
        content_dir=root / content,
        templates_dir=root / "templates",
        static_dir=root / "static",
        output_dir=root / output,
        base_url=base_url,
    )

    result = builder.build()

    if result.success:
        click.echo(f"Built {result.pages_generated} pages")
        click.echo(f"Search index: {result.search_index_size} documents")
        click.echo(f"Output: {root / output}")
    else:
        for error in result.errors:
            click.echo(f"Error: {error}", err=True)
        raise SystemExit(1)


@main.command()
@click.option(
    "--port",
    "-p",
    default=8000,
    help="Port to serve on",
)
@click.option(
    "--output",
    "-o",
    default="dist",
    help="Directory to serve",
)
def serve(port: int, output: str):
    """Start a local development server."""
    root = get_project_root()
    serve_dir = root / output

    if not serve_dir.exists():
        click.echo(f"Error: {serve_dir} does not exist. Run 'tabstash build' first.", err=True)
        raise SystemExit(1)

    os.chdir(serve_dir)

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        click.echo(f"Serving at http://localhost:{port}")
        click.echo("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\nStopped")


if __name__ == "__main__":
    main()
