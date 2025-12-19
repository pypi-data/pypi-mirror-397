"""Pytest configuration and fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from kb_trend.config.models import Settings
from kb_trend.database.manager import DatabaseManager


@pytest.fixture
def temp_db() -> Path:
    """Create temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def test_settings(temp_db: Path) -> Settings:
    """Create test settings."""
    return Settings(
        db_path=temp_db,
        min_year=1900,
        max_year=2000,
        journals=["TEST_JOURNAL", "None"],
        sleep_timer=0.1,
        request_timeout=10,
        keyword_column="title",
        marker_templates=["SÖKES", "PLATS"],
        proximity_distance=5
    )


@pytest.fixture
def db_manager(test_settings: Settings) -> DatabaseManager:
    """Create initialized database manager."""
    manager = DatabaseManager(test_settings.db_path)
    manager.init_schema()
    manager.initialize_journals(test_settings.journals)
    return manager


@pytest.fixture
def mock_api_response() -> dict[str, Any]:
    """Load mock API response from fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "response.example.json"

    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def temp_dir() -> Path:
    """Create temporary directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # Cleanup
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
