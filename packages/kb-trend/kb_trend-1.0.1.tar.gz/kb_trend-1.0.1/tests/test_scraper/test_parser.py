"""Tests for response parser."""

from typing import Any

import pytest

from kb_trend.scraper.parser import ResponseParser


def test_extract_year_counts(mock_api_response: dict[str, Any]) -> None:
    """Test extracting year counts from real API response."""
    parser = ResponseParser()
    results = parser.extract_year_counts(mock_api_response)

    assert len(results) > 0
    assert all("year" in r and "count" in r for r in results)
    assert all(isinstance(r["year"], int) for r in results)
    assert all(isinstance(r["count"], int) for r in results)

    # Check first entry from the example
    first_result = results[0]
    assert first_result["year"] == 1210
    assert first_result["count"] == 4


def test_extract_year_counts_with_date_format() -> None:
    """Test parsing when value is in YYYY-MM-DD format."""
    response = {
        "aggs": {
            "datePublished": {
                "values": [
                    {"value": "1895-01-15", "count": 42},
                    {"value": "1896-03-20", "count": 38},
                ]
            }
        }
    }

    parser = ResponseParser()
    results = parser.extract_year_counts(response)

    assert len(results) == 2
    assert results[0] == {"year": 1895, "count": 42}
    assert results[1] == {"year": 1896, "count": 38}


def test_extract_year_counts_with_year_format() -> None:
    """Test parsing when value is in YYYY format."""
    response = {
        "aggs": {
            "datePublished": {
                "values": [
                    {"value": "1895", "count": 42},
                    {"value": "1896", "count": 38},
                ]
            }
        }
    }

    parser = ResponseParser()
    results = parser.extract_year_counts(response)

    assert len(results) == 2
    assert results[0] == {"year": 1895, "count": 42}
    assert results[1] == {"year": 1896, "count": 38}


def test_extract_year_counts_empty_response() -> None:
    """Test parsing empty aggregations."""
    response = {
        "aggs": {
            "datePublished": {
                "values": []
            }
        }
    }

    parser = ResponseParser()
    results = parser.extract_year_counts(response)

    assert results == []


def test_extract_year_counts_invalid_response() -> None:
    """Test parser handles invalid response."""
    parser = ResponseParser()

    # Missing aggs - returns empty list
    result = parser.extract_year_counts({"invalid": "data"})
    assert result == []

    # Missing datePublished - returns empty list
    result = parser.extract_year_counts({"aggs": {}})
    assert result == []

    # Invalid value format - should raise error
    with pytest.raises(ValueError, match="Failed to parse"):
        parser.extract_year_counts({
            "aggs": {
                "datePublished": {
                    "values": [{"value": "invalid", "count": 1}]
                }
            }
        })


def test_get_total_hits() -> None:
    """Test extracting total hits."""
    response = {"total": 12345}

    parser = ResponseParser()
    total = parser.get_total_hits(response)

    assert total == 12345


def test_get_total_hits_missing() -> None:
    """Test total hits defaults to 0 if missing."""
    response = {}

    parser = ResponseParser()
    total = parser.get_total_hits(response)

    assert total == 0
