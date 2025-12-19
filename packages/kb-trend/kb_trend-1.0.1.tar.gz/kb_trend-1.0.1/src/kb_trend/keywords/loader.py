"""Keyword loader for various file formats."""

import csv
from pathlib import Path
from typing import Any


class KeywordLoader:
    """Load keywords from various file formats."""

    def __init__(self, keyword_column: str):
        """Initialize keyword loader.

        Args:
            keyword_column: Column name to use as keyword
        """
        self.keyword_column = keyword_column

    def load(self, file_path: Path) -> list[dict[str, Any]]:
        """Load keywords from file.

        Args:
            file_path: Path to keyword file (.txt, .csv, .tsv)

        Returns:
            List of dictionaries with all columns

        Raises:
            ValueError: If file format is unsupported or invalid
        """
        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            return self._load_txt(file_path)
        elif suffix == ".csv":
            return self._load_csv(file_path, delimiter=",")
        elif suffix == ".tsv":
            return self._load_csv(file_path, delimiter="\t")
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}\n"
                f"Supported formats: .txt, .csv, .tsv"
            )

    def _load_txt(self, file_path: Path) -> list[dict[str, str]]:
        """Load from plain text file (one keyword per line).

        Args:
            file_path: Path to .txt file

        Returns:
            List of dicts with keyword_column as key
        """
        keywords = []

        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    keywords.append({self.keyword_column: line})

        return keywords

    def _load_csv(self, file_path: Path, delimiter: str) -> list[dict[str, Any]]:
        """Load from CSV/TSV file.

        Args:
            file_path: Path to CSV/TSV file
            delimiter: Field delimiter

        Returns:
            List of dicts with all columns

        Raises:
            ValueError: If keyword_column not found in file
        """
        keywords = []

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            # Read all rows
            for row in reader:
                keywords.append(row)

        # Validate keyword column exists
        if keywords and self.keyword_column not in keywords[0]:
            available_columns = ', '.join(keywords[0].keys())
            raise ValueError(
                f"Column '{self.keyword_column}' not found in file.\n"
                f"Available columns: {available_columns}"
            )

        return keywords
