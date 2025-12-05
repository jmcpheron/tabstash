"""Pytest configuration and shared fixtures."""

import http.server
import socket
import subprocess
import threading
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tabs_fixtures_dir(fixtures_dir: Path) -> Path:
    """Return the path to tab fixtures directory."""
    return fixtures_dir / "tabs"


# === Browser testing fixtures ===


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def built_site(tmp_path_factory) -> Path:
    """Build the site to a temporary directory."""
    output_dir = tmp_path_factory.mktemp("dist")
    project_root = Path(__file__).parent.parent
    subprocess.run(
        ["uv", "run", "tabstash", "build", "--output", str(output_dir)],
        check=True,
        cwd=project_root,
    )
    return output_dir


@pytest.fixture(scope="session")
def live_server(built_site: Path):
    """Start a local HTTP server serving the built site."""
    import socketserver

    port = find_free_port()

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(built_site), **kwargs)

        def log_message(self, format, *args):
            pass  # Suppress logging

    # Use ThreadingHTTPServer for better concurrent request handling
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True

    server = ThreadedHTTPServer(("localhost", port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield f"http://localhost:{port}"

    server.shutdown()
