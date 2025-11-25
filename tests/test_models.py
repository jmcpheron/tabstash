"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from tabstash.models import TabMetadata


class TestTabMetadata:
    """Tests for TabMetadata model."""

    def test_valid_minimal_metadata(self):
        """Test creating metadata with only required fields."""
        meta = TabMetadata(title="Wonderwall", artist="Oasis")
        assert meta.title == "Wonderwall"
        assert meta.artist == "Oasis"
        assert meta.capo == 0
        assert meta.tuning == "standard"
        assert meta.key is None
        assert meta.difficulty is None
        assert meta.bpm is None
        assert meta.tags == []

    def test_valid_full_metadata(self):
        """Test creating metadata with all fields."""
        meta = TabMetadata(
            title="Wish You Were Here",
            artist="Pink Floyd",
            key="G",
            capo=0,
            tuning="standard",
            difficulty="intermediate",
            bpm=60,
            tags=["acoustic", "classic"],
        )
        assert meta.title == "Wish You Were Here"
        assert meta.artist == "Pink Floyd"
        assert meta.key == "G"
        assert meta.difficulty == "intermediate"
        assert meta.bpm == 60
        assert meta.tags == ["acoustic", "classic"]

    def test_rejects_empty_title(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError, match="must not be empty"):
            TabMetadata(title="", artist="Oasis")

    def test_rejects_whitespace_title(self):
        """Test that whitespace-only title is rejected."""
        with pytest.raises(ValidationError, match="must not be empty"):
            TabMetadata(title="   ", artist="Oasis")

    def test_rejects_empty_artist(self):
        """Test that empty artist is rejected."""
        with pytest.raises(ValidationError, match="must not be empty"):
            TabMetadata(title="Wonderwall", artist="")

    def test_strips_whitespace(self):
        """Test that title and artist are stripped of whitespace."""
        meta = TabMetadata(title="  Wonderwall  ", artist="  Oasis  ")
        assert meta.title == "Wonderwall"
        assert meta.artist == "Oasis"

    def test_capo_min_bound(self):
        """Test that capo cannot be negative."""
        with pytest.raises(ValidationError):
            TabMetadata(title="Test", artist="Test", capo=-1)

    def test_capo_max_bound(self):
        """Test that capo cannot exceed 12."""
        with pytest.raises(ValidationError):
            TabMetadata(title="Test", artist="Test", capo=13)

    def test_valid_capo_range(self):
        """Test valid capo values."""
        for capo in range(0, 13):
            meta = TabMetadata(title="Test", artist="Test", capo=capo)
            assert meta.capo == capo

    def test_valid_difficulty_values(self):
        """Test all valid difficulty values."""
        for difficulty in ["beginner", "intermediate", "advanced"]:
            meta = TabMetadata(title="Test", artist="Test", difficulty=difficulty)
            assert meta.difficulty == difficulty

    def test_difficulty_case_insensitive(self):
        """Test that difficulty is case-insensitive."""
        meta = TabMetadata(title="Test", artist="Test", difficulty="BEGINNER")
        assert meta.difficulty == "beginner"

    def test_invalid_difficulty(self):
        """Test that invalid difficulty is rejected."""
        with pytest.raises(ValidationError, match="must be one of"):
            TabMetadata(title="Test", artist="Test", difficulty="expert")

    def test_bpm_min_bound(self):
        """Test that BPM has minimum bound."""
        with pytest.raises(ValidationError):
            TabMetadata(title="Test", artist="Test", bpm=10)

    def test_bpm_max_bound(self):
        """Test that BPM has maximum bound."""
        with pytest.raises(ValidationError):
            TabMetadata(title="Test", artist="Test", bpm=400)

    def test_valid_bpm_range(self):
        """Test valid BPM values."""
        meta = TabMetadata(title="Test", artist="Test", bpm=120)
        assert meta.bpm == 120
