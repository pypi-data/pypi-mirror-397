"""Configuration hash utilities."""

import hashlib
from typing import Any

import yaml


def calculate_config_hash(settings_dict: dict[str, Any]) -> str:
    """Calculate SHA256 hash of settings dictionary.

    Args:
        settings_dict: Settings as dictionary

    Returns:
        Hexadecimal hash string
    """
    # Sort keys for deterministic hashing
    sorted_yaml = yaml.dump(settings_dict, sort_keys=True, default_flow_style=False)
    return hashlib.sha256(sorted_yaml.encode('utf-8')).hexdigest()


def validate_config_hash(
    stored_hash: str | None,
    current_settings_dict: dict[str, Any]
) -> tuple[bool, str]:
    """Validate config hash matches stored hash.

    Args:
        stored_hash: Hash stored in database (None if not set)
        current_settings_dict: Current settings as dictionary

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if hash matches or no hash stored
        - error_message: Error message if invalid, empty string otherwise
    """
    if stored_hash is None:
        # No hash stored yet (new database)
        return True, ""

    current_hash = calculate_config_hash(current_settings_dict)

    if stored_hash != current_hash:
        error_msg = (
            "Configuration mismatch detected!\n"
            "Database was created with different settings.\n\n"
            f"Stored hash:  {stored_hash}\n"
            f"Current hash: {current_hash}\n\n"
            "The settings.yaml file has been modified after the database was created.\n"
            "This could lead to inconsistent data.\n\n"
            "Options:\n"
            "  1. Restore the original settings.yaml file\n"
            "  2. Create a new database: kb-trend init --force\n"
            "  3. Contact support if you believe this is an error"
        )
        return False, error_msg

    return True, ""
