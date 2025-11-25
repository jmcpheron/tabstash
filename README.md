# TabStash

A static guitar tab site generator with mobile-first design for practicing.

## Features

- Mobile-first dark theme optimized for reading tabs
- Auto-scroll for hands-free practice
- Client-side fuzzy search with MiniSearch
- Section navigation (jump to Verse, Chorus, etc.)
- Organized by artist with YAML frontmatter metadata

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
---

[Intro]
G  C  D  G

[Verse]
G               C
Lyrics with chords above
D               G
More lyrics here
```

## Deployment

Push to GitHub and enable GitHub Pages. The included workflow will automatically build and deploy.

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/
```
