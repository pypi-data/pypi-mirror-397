"""Tests for database manager."""

from kb_trend.config.models import Settings
from kb_trend.database.manager import DatabaseManager


def test_init_schema(db_manager: DatabaseManager) -> None:
    """Test database schema initialization."""
    # Schema should be initialized by fixture
    stats = db_manager.get_statistics()

    assert stats is not None
    assert "total_queries" in stats
    assert "total_journals" in stats


def test_metadata_operations(db_manager: DatabaseManager) -> None:
    """Test metadata get/set operations."""
    # Set metadata
    db_manager.set_metadata("test_key", "test_value")

    # Get metadata
    value = db_manager.get_metadata("test_key")
    assert value == "test_value"

    # Update metadata
    db_manager.set_metadata("test_key", "new_value")
    value = db_manager.get_metadata("test_key")
    assert value == "new_value"

    # Get non-existent key
    value = db_manager.get_metadata("non_existent")
    assert value is None


def test_initialize_journals(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test journal initialization."""
    # Journals should be initialized by fixture
    journals = db_manager.get_all_journals()

    assert len(journals) >= len(test_settings.journals)

    # Get journal ID
    journal_id = db_manager.get_journal_id(test_settings.journals[0])
    assert journal_id is not None

    # Non-existent journal
    journal_id = db_manager.get_journal_id("NON_EXISTENT")
    assert journal_id is None


def test_insert_query(db_manager: DatabaseManager) -> None:
    """Test query insertion."""
    query_id = db_manager.insert_query(
        search_string='"test"',
        keyword="test",
        metadata={"gender": "male", "category": "youth"}
    )

    assert query_id is not None

    # Inserting same query should return same ID
    query_id2 = db_manager.insert_query(
        search_string='"test"',
        keyword="test"
    )
    assert query_id2 == query_id

    # Get query
    query = db_manager.get_query_by_id(query_id)
    assert query is not None
    assert query.keyword == "test"
    assert query.search_string == '"test"'


def test_wildcard_query(db_manager: DatabaseManager) -> None:
    """Test wildcard query creation."""
    wildcard_id = db_manager.create_wildcard_query()
    assert wildcard_id is not None

    # Get wildcard query ID
    wildcard_id2 = db_manager.get_wildcard_query_id()
    assert wildcard_id2 == wildcard_id

    # Get query
    query = db_manager.get_query_by_id(wildcard_id)
    assert query.keyword == '*'
    assert query.search_string == '*'


def test_populate_queue(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test queue population."""
    # Create query
    query_id = db_manager.insert_query(
        search_string='"test"',
        keyword="test"
    )

    # Populate queue
    count = db_manager.populate_queue(query_id, test_settings.journals)
    assert count == len(test_settings.journals)

    # Populating again should not add duplicates
    count = db_manager.populate_queue(query_id, test_settings.journals)
    assert count == 0


def test_get_queue(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test getting queue items."""
    # Create query and populate queue
    query_id = db_manager.insert_query(search_string='"test"', keyword="test")
    db_manager.populate_queue(query_id, test_settings.journals)

    # Get all queue items
    queue_items = db_manager.get_queue()
    assert len(queue_items) >= len(test_settings.journals)

    # Get pending items
    pending_items = db_manager.get_queue(status=['pending'])
    assert len(pending_items) >= len(test_settings.journals)

    # Get with limit
    limited_items = db_manager.get_queue(limit=1)
    assert len(limited_items) == 1


def test_update_queue_status(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test updating queue status."""
    # Create query and populate queue
    query_id = db_manager.insert_query(search_string='"test"', keyword="test")
    db_manager.populate_queue(query_id, test_settings.journals)

    # Get first item
    items = db_manager.get_queue(limit=1)
    item = items[0]

    # Update to in_progress
    db_manager.update_queue_status(item.id, 'in_progress')

    # Update to completed
    db_manager.update_queue_status(item.id, 'completed')

    # Verify
    stats = db_manager.get_statistics()
    assert stats['queue_completed'] >= 1


def test_insert_count(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test inserting count data."""
    # Create query and journal
    query_id = db_manager.insert_query(search_string='"test"', keyword="test")
    journal_id = db_manager.get_journal_id(test_settings.journals[0])

    # Insert count
    db_manager.insert_count(
        year=1900,
        query_id=query_id,
        journal_id=journal_id,
        count=42
    )

    # Get counts
    counts = db_manager.get_counts_for_query(query_id)
    assert len(counts) == 1
    assert counts[0].year == 1900
    assert counts[0].count == 42

    # Updating should work (not duplicate)
    db_manager.insert_count(
        year=1900,
        query_id=query_id,
        journal_id=journal_id,
        count=50
    )

    counts = db_manager.get_counts_for_query(query_id)
    assert len(counts) == 1
    assert counts[0].count == 50


def test_update_relative_frequencies(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test updating relative frequencies."""
    # Create query and insert counts
    query_id = db_manager.insert_query(search_string='"test"', keyword="test")
    journal_id = db_manager.get_journal_id(test_settings.journals[0])

    db_manager.insert_count(year=1900, query_id=query_id, journal_id=journal_id, count=10)

    # Get count ID
    counts = db_manager.get_counts_for_query(query_id)
    count_id = counts[0].id

    # Update relative frequency
    updates = [{"id": count_id, "rel": 0.5}]
    updated = db_manager.update_relative_frequencies(updates)

    assert updated == 1

    # Verify
    counts = db_manager.get_counts_for_query(query_id)
    assert counts[0].rel == 0.5


def test_reset_queue(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test resetting queue."""
    # Create query and populate queue
    query_id = db_manager.insert_query(search_string='"test"', keyword="test")
    count = db_manager.populate_queue(query_id, test_settings.journals)

    # Mark some as completed
    items = db_manager.get_queue(limit=1)
    db_manager.update_queue_status(items[0].id, 'completed')

    # Reset queue
    reset_count = db_manager.reset_queue()
    assert reset_count >= count

    # All should be pending now
    pending = db_manager.get_queue(status=['pending'])
    assert len(pending) >= count


def test_get_statistics(db_manager: DatabaseManager, test_settings: Settings) -> None:
    """Test getting statistics."""
    # Create some data
    query_id = db_manager.insert_query(search_string='"test"', keyword="test")
    db_manager.populate_queue(query_id, test_settings.journals)

    # Get stats
    stats = db_manager.get_statistics()

    assert stats['total_queries'] >= 1
    assert stats['total_journals'] >= len(test_settings.journals)
    assert stats['queue_pending'] >= len(test_settings.journals)
    assert stats['queue_completed'] >= 0
    assert stats['queue_failed'] >= 0
