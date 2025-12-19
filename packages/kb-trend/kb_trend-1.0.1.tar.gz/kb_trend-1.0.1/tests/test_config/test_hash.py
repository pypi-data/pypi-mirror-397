"""Tests for configuration hash utilities."""

from kb_trend.utils.hash import calculate_config_hash, validate_config_hash


def test_calculate_config_hash() -> None:
    """Test config hash calculation."""
    config = {
        "db_path": "test.sqlite3",
        "min_year": 1900,
        "max_year": 2000
    }

    hash1 = calculate_config_hash(config)

    # Hash should be consistent
    hash2 = calculate_config_hash(config)
    assert hash1 == hash2

    # Hash should be 64 characters (SHA256)
    assert len(hash1) == 64


def test_config_hash_changes_with_content() -> None:
    """Test that hash changes when config changes."""
    config1 = {"db_path": "test.sqlite3", "min_year": 1900}
    config2 = {"db_path": "test.sqlite3", "min_year": 1901}

    hash1 = calculate_config_hash(config1)
    hash2 = calculate_config_hash(config2)

    assert hash1 != hash2


def test_config_hash_order_independent() -> None:
    """Test that key order doesn't affect hash."""
    config1 = {"a": 1, "b": 2, "c": 3}
    config2 = {"c": 3, "a": 1, "b": 2}

    hash1 = calculate_config_hash(config1)
    hash2 = calculate_config_hash(config2)

    # Hash should be same regardless of key order (sorted internally)
    assert hash1 == hash2


def test_validate_config_hash_no_stored_hash() -> None:
    """Test validation with no stored hash (new database)."""
    config = {"db_path": "test.sqlite3"}

    is_valid, error_msg = validate_config_hash(None, config)

    assert is_valid is True
    assert error_msg == ""


def test_validate_config_hash_match() -> None:
    """Test validation with matching hash."""
    config = {"db_path": "test.sqlite3", "min_year": 1900}
    stored_hash = calculate_config_hash(config)

    is_valid, error_msg = validate_config_hash(stored_hash, config)

    assert is_valid is True
    assert error_msg == ""


def test_validate_config_hash_mismatch() -> None:
    """Test validation with mismatched hash."""
    config1 = {"db_path": "test.sqlite3", "min_year": 1900}
    config2 = {"db_path": "test.sqlite3", "min_year": 1901}

    stored_hash = calculate_config_hash(config1)

    is_valid, error_msg = validate_config_hash(stored_hash, config2)

    assert is_valid is False
    assert "Configuration mismatch detected" in error_msg
    assert stored_hash in error_msg
