"""Tests for query builder."""

from kb_trend.keywords.query_builder import QueryBuilder


def test_build_plain_query() -> None:
    """Test plain keyword query (no markers)."""
    builder = QueryBuilder()
    query = builder.build("test")
    assert query == '"test"'


def test_build_proximity_query_single_marker() -> None:
    """Test proximity search with single marker."""
    builder = QueryBuilder(
        marker_templates=["SÖKES"],
        proximity_distance=5
    )
    query = builder.build("gosse")
    assert query == '"gosse SÖKES"~5'


def test_build_proximity_query_multiple_markers() -> None:
    """Test proximity search with multiple markers."""
    builder = QueryBuilder(
        marker_templates=["SÖKES", "PLATS", "ERHÅLLES"],
        proximity_distance=5
    )
    query = builder.build("gosse")
    expected = '"gosse SÖKES"~5 OR "gosse PLATS"~5 OR "gosse ERHÅLLES"~5'
    assert query == expected


def test_build_with_custom_distance() -> None:
    """Test proximity search with custom distance."""
    builder = QueryBuilder(
        marker_templates=["MARKER"],
        proximity_distance=10
    )
    query = builder.build("keyword")
    assert query == '"keyword MARKER"~10'


def test_build_with_empty_markers_list() -> None:
    """Test with explicitly empty markers list."""
    builder = QueryBuilder(marker_templates=[])
    query = builder.build("test")
    assert query == '"test"'


def test_build_with_special_characters() -> None:
    """Test query building with keywords containing special characters."""
    builder = QueryBuilder(marker_templates=["MARKER"])
    query = builder.build("test-keyword")
    assert '"test-keyword MARKER"' in query
