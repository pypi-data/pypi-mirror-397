"""Tests for configuration models."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from kb_trend.config.models import Settings


def test_settings_defaults() -> None:
    """Test settings with default values."""
    settings = Settings()

    assert settings.db_path == Path("kb_trend.sqlite3")
    assert settings.min_year is None
    assert settings.max_year is None
    assert settings.journals == ["None"]
    assert settings.sleep_timer == 1.0
    assert settings.request_timeout == 30
    assert settings.keyword_column == "title"
    assert settings.marker_templates == []
    assert settings.proximity_distance == 5


def test_settings_custom_values() -> None:
    """Test settings with custom values."""
    settings = Settings(
        db_path=Path("/tmp/custom.sqlite3"),
        min_year=1820,
        max_year=2020,
        journals=["Journal 1", "Journal 2"],
        sleep_timer=0.5,
        request_timeout=60,
        keyword_column="keyword",
        marker_templates=["MARKER1", "MARKER2"],
        proximity_distance=10
    )

    assert settings.db_path == Path("/tmp/custom.sqlite3")
    assert settings.min_year == 1820
    assert settings.max_year == 2020
    assert settings.journals == ["Journal 1", "Journal 2"]
    assert settings.sleep_timer == 0.5
    assert settings.request_timeout == 60
    assert settings.keyword_column == "keyword"
    assert settings.marker_templates == ["MARKER1", "MARKER2"]
    assert settings.proximity_distance == 10


def test_db_path_auto_extension() -> None:
    """Test that .sqlite3 extension is added automatically."""
    settings = Settings(db_path=Path("mydb"))
    assert settings.db_path == Path("mydb.sqlite3")

    settings = Settings(db_path=Path("mydb.db"))
    assert settings.db_path == Path("mydb.db.sqlite3")


def test_year_range_validation() -> None:
    """Test year range validation."""
    # Valid range
    settings = Settings(min_year=1900, max_year=2000)
    assert settings.min_year == 1900
    assert settings.max_year == 2000

    # Invalid range (max < min)
    with pytest.raises(ValidationError, match="max_year.*must be >= min_year"):
        Settings(min_year=2000, max_year=1900)


def test_empty_journals() -> None:
    """Test that empty journals list defaults to ['None']."""
    settings = Settings(journals=[])
    assert settings.journals == ["None"]


def test_year_bounds() -> None:
    """Test year bounds validation."""
    # Valid years
    Settings(min_year=1000, max_year=3000)

    # Invalid min_year
    with pytest.raises(ValidationError):
        Settings(min_year=999)

    # Invalid max_year
    with pytest.raises(ValidationError):
        Settings(max_year=3001)


def test_sleep_timer_bounds() -> None:
    """Test sleep timer bounds."""
    # Valid value
    Settings(sleep_timer=0.1)

    # Invalid value (too small)
    with pytest.raises(ValidationError):
        Settings(sleep_timer=0.09)


def test_proximity_distance_bounds() -> None:
    """Test proximity distance bounds."""
    # Valid values
    Settings(proximity_distance=1)
    Settings(proximity_distance=100)

    # Invalid values
    with pytest.raises(ValidationError):
        Settings(proximity_distance=0)

    with pytest.raises(ValidationError):
        Settings(proximity_distance=101)
