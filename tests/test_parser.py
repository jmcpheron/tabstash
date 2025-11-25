"""Tests for tab parsing."""

from pathlib import Path

import pytest

from tabstash.parser import extract_sections, parse_file, slugify


class TestSlugify:
    """Tests for slugify function."""

    def test_basic_slugify(self):
        """Test basic string slugification."""
        assert slugify("Hello World") == "hello-world"

    def test_removes_special_chars(self):
        """Test that special characters are removed."""
        assert slugify("Rock & Roll") == "rock-roll"
        assert slugify("What's Up?") == "whats-up"

    def test_handles_multiple_spaces(self):
        """Test handling of multiple spaces."""
        assert slugify("Hello   World") == "hello-world"

    def test_handles_hyphens(self):
        """Test that existing hyphens are preserved."""
        assert slugify("semi-charmed") == "semi-charmed"

    def test_strips_leading_trailing(self):
        """Test stripping of leading/trailing dashes."""
        assert slugify("-hello-") == "hello"


class TestExtractSections:
    """Tests for section extraction."""

    def test_extracts_sections(self):
        """Test basic section extraction."""
        content = """
[Intro]
Some intro text

[Verse 1]
Verse text

[Chorus]
Chorus text
"""
        sections = extract_sections(content)
        assert sections == ["Intro", "Verse 1", "Chorus"]

    def test_empty_content(self):
        """Test with no sections."""
        assert extract_sections("Just some text") == []

    def test_handles_brackets_in_content(self):
        """Test that inline brackets are not matched."""
        content = """
[Verse]
Play [Am] chord here
"""
        sections = extract_sections(content)
        assert sections == ["Verse"]


class TestParseFile:
    """Tests for file parsing."""

    def test_parse_valid_tab(self, tabs_fixtures_dir: Path):
        """Test parsing a valid tab file."""
        tab_file = tabs_fixtures_dir / "valid_tab.md"

        # Skip if fixture doesn't exist yet
        if not tab_file.exists():
            pytest.skip("Fixture file not created yet")

        tab = parse_file(tab_file)
        assert tab.metadata.title == "Test Song"
        assert tab.metadata.artist == "Test Artist"
        assert "Verse" in tab.content

    def test_parse_derives_slugs_from_path(self, tmp_path: Path):
        """Test that slugs are derived from file path."""
        # Create a temporary tab file
        artist_dir = tmp_path / "test-artist"
        artist_dir.mkdir()

        tab_file = artist_dir / "test-song.md"
        tab_file.write_text("""---
title: Test Song
artist: Test Artist
---

[Verse]
Test content
""")

        tab = parse_file(tab_file)
        assert tab.slug == "test-song"
        assert tab.artist_slug == "test-artist"
