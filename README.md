# TabStash

[![Tests](https://github.com/jmcpheron/tabstash/actions/workflows/deploy.yml/badge.svg)](https://github.com/jmcpheron/tabstash/actions/workflows/deploy.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A static guitar tab site generator with mobile-first design for practicing.

## Features

- **Mobile-first dark theme** optimized for reading tabs on any device
- **Auto-scroll** for hands-free practice (works on iOS Safari, Android, and desktop)
- **Client-side fuzzy search** powered by MiniSearch
- **Section navigation** - jump to Verse, Chorus, Bridge, etc.
- **Organized by artist** with rich YAML frontmatter metadata
- **Speed control** - slow, medium, or fast auto-scroll speeds
- **Tap to toggle** - tap anywhere on the tab content to start/stop scrolling

## Quick Start

```bash
# Install dependencies
uv sync

# Build the site
uv run tabstash build

# Preview locally
uv run tabstash serve
```

## Adding Tabs

Create markdown files in `content/tabs/artist-name/song-name.md`:

```markdown
---
title: "Song Title"
artist: "Artist Name"
key: "G"
capo: 0
tuning: "standard"
difficulty: "intermediate"
bpm: 120
tags: ["acoustic", "rock"]
featured: true
---

[Intro]
G  C  D  G

[Verse]
G               C
Lyrics with chords above
D               G
More lyrics here
```

### Metadata Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Song title |
| `artist` | Yes | Artist name |
| `key` | No | Musical key (e.g., "G", "Am") |
| `capo` | No | Capo position (0-12) |
| `tuning` | No | Guitar tuning (default: "standard") |
| `difficulty` | No | "beginner", "intermediate", or "advanced" |
| `bpm` | No | Tempo in beats per minute (20-300) |
| `tags` | No | List of tags for categorization |
| `featured` | No | Set to `true` to feature on homepage |
| `format` | No | "full" for tabs, "compact" for chord charts |

## Deployment

Push to GitHub and enable GitHub Pages. The included workflow will automatically:

1. Run unit tests and browser tests (Chromium + WebKit)
2. Build the site
3. Deploy to GitHub Pages

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest

# Run browser tests only
uv run pytest tests/test_browser.py --browser chromium --browser webkit

# Run browser tests in headed mode (see the browser)
uv run pytest tests/test_browser.py --browser webkit --headed

# Lint
uv run ruff check src/ tests/
```

### Browser Testing

TabStash uses [Playwright](https://playwright.dev/) for browser testing to ensure features like auto-scroll work across different browsers, including iOS Safari (via WebKit).

```bash
# Install Playwright browsers
uv run playwright install

# Run WebKit tests (Safari engine)
uv run pytest tests/test_browser.py --browser webkit -v
```
