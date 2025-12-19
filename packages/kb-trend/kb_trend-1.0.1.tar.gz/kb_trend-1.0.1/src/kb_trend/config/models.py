"""Pydantic models for configuration."""

from pathlib import Path

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Settings(BaseModel):
    """Application settings."""

    # Database
    db_path: Path = Field(default=Path("kb_trend.sqlite3"), description="Database file path")

    # Time range
    min_year: int | None = Field(
        default=None, ge=1000, le=3000, description="Minimum year for search range"
    )
    max_year: int | None = Field(
        default=None, ge=1000, le=3000, description="Maximum year for search range"
    )

    # Journals
    journals: list[str] = Field(
        default_factory=lambda: ["None"],
        description="Journal names to query ('None' means all journals)",
    )

    # Scraping behavior
    sleep_timer: float = Field(default=1.0, ge=0.1, description="Sleep between requests (seconds)")
    request_timeout: int = Field(default=30, ge=1, description="HTTP request timeout (seconds)")

    # Keywords
    keyword_column: str = Field(default="title", description="CSV column name to use as keyword")

    # Query templates
    marker_templates: list[str] = Field(
        default_factory=list,
        description="Proximity search markers (e.g., ['SÖKES', 'PLATS', 'ERHÅLLES'])",
    )
    proximity_distance: int = Field(
        default=5, ge=1, le=100, description="Proximity search distance (words)"
    )

    @field_validator("max_year")
    @classmethod
    def validate_year_range(cls, v: int | None, info: ValidationInfo) -> int | None:
        """Validate that max_year >= min_year if both are set."""
        min_year = info.data.get("min_year")
        if min_year is not None and v is not None:
            if v < min_year:
                raise ValueError(f"max_year ({v}) must be >= min_year ({min_year})")
        return v

    @field_validator("db_path")
    @classmethod
    def ensure_sqlite_extension(cls, v: Path) -> Path:
        """Ensure database file has .sqlite3 extension."""
        if not str(v).endswith(".sqlite3"):
            return Path(str(v) + ".sqlite3")
        return v

    @field_validator("journals")
    @classmethod
    def ensure_non_empty_journals(cls, v: list[str]) -> list[str]:
        """Ensure journals list is not empty."""
        if not v:
            return ["None"]
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "db_path": "kb_trend.sqlite3",
                    "min_year": 1820,
                    "max_year": 2020,
                    "journals": ["None", "DAGENS NYHETER"],
                    "sleep_timer": 1.0,
                    "request_timeout": 30,
                    "keyword_column": "title",
                    "marker_templates": ["SÖKES", "PLATS", "ERHÅLLES"],
                    "proximity_distance": 5,
                }
            ]
        }
    }
