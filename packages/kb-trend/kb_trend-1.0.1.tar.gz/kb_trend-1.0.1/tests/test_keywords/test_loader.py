"""Tests for keyword loader."""

from pathlib import Path

import pytest

from kb_trend.keywords.loader import KeywordLoader


def test_load_txt_file(temp_dir: Path) -> None:
    """Test loading keywords from .txt file."""
    # Create test file
    txt_file = temp_dir / "keywords.txt"
    txt_file.write_text("keyword1\nkeyword2\nkeyword3\n", encoding='utf-8')

    loader = KeywordLoader(keyword_column="title")
    keywords = loader.load(txt_file)

    assert len(keywords) == 3
    assert keywords[0] == {"title": "keyword1"}
    assert keywords[1] == {"title": "keyword2"}
    assert keywords[2] == {"title": "keyword3"}


def test_load_txt_file_with_empty_lines(temp_dir: Path) -> None:
    """Test loading .txt file with empty lines."""
    txt_file = temp_dir / "keywords.txt"
    txt_file.write_text("keyword1\n\nkeyword2\n  \nkeyword3", encoding='utf-8')

    loader = KeywordLoader(keyword_column="title")
    keywords = loader.load(txt_file)

    # Empty lines should be skipped
    assert len(keywords) == 3


def test_load_csv_file(temp_dir: Path) -> None:
    """Test loading keywords from .csv file."""
    csv_file = temp_dir / "keywords.csv"
    csv_file.write_text(
        "title,gender,category\n"
        "gosse,male,youth\n"
        "flicka,female,youth\n",
        encoding='utf-8'
    )

    loader = KeywordLoader(keyword_column="title")
    keywords = loader.load(csv_file)

    assert len(keywords) == 2
    assert keywords[0] == {"title": "gosse", "gender": "male", "category": "youth"}
    assert keywords[1] == {"title": "flicka", "gender": "female", "category": "youth"}


def test_load_tsv_file(temp_dir: Path) -> None:
    """Test loading keywords from .tsv file."""
    tsv_file = temp_dir / "keywords.tsv"
    tsv_file.write_text(
        "title\tgender\tcategory\n"
        "gosse\tmale\tyouth\n"
        "flicka\tfemale\tyouth\n",
        encoding='utf-8'
    )

    loader = KeywordLoader(keyword_column="title")
    keywords = loader.load(tsv_file)

    assert len(keywords) == 2
    assert keywords[0] == {"title": "gosse", "gender": "male", "category": "youth"}


def test_load_csv_missing_column(temp_dir: Path) -> None:
    """Test error when keyword column is missing."""
    csv_file = temp_dir / "keywords.csv"
    csv_file.write_text(
        "name,value\n"
        "test1,1\n",
        encoding='utf-8'
    )

    loader = KeywordLoader(keyword_column="title")

    with pytest.raises(ValueError, match="Column 'title' not found"):
        loader.load(csv_file)


def test_load_unsupported_format(temp_dir: Path) -> None:
    """Test error with unsupported file format."""
    json_file = temp_dir / "keywords.json"
    json_file.write_text('{"test": "data"}', encoding='utf-8')

    loader = KeywordLoader(keyword_column="title")

    with pytest.raises(ValueError, match="Unsupported file format"):
        loader.load(json_file)


def test_load_csv_with_custom_column_name(temp_dir: Path) -> None:
    """Test loading CSV with custom keyword column."""
    csv_file = temp_dir / "keywords.csv"
    csv_file.write_text(
        "word,category\n"
        "test1,cat1\n"
        "test2,cat2\n",
        encoding='utf-8'
    )

    loader = KeywordLoader(keyword_column="word")
    keywords = loader.load(csv_file)

    assert len(keywords) == 2
    assert keywords[0] == {"word": "test1", "category": "cat1"}
