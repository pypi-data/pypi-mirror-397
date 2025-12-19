# KB-Trend

A CLI tool for scraping historical newspaper trend data from the Swedish
National Library (Kungliga biblioteket).

## Features

- **Modern CLI** built with Typer and Rich for a great user experience
- **Flexible keyword loading** from .txt, .csv, or .tsv files
- **Proximity search** support with customizable markers
- **Configuration validation** via SHA256 hashing to prevent data corruption
- **SQLite database** with SQLAlchemy ORM for reliable data storage
- **Type-safe** with full type hints and mypy validation

## Installation

### Using pipx (Recommended)

```bash
pipx install kb-trend
```

### Using pip

```bash
python -m pip install kb-trend
```

### Development Installation

```bash
git clone https://github.com/matjoha/kb-trend
cd kb-trend
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize Configuration

Run the interactive setup wizard:

```bash
kb-trend init
```

Or use non-interactive mode with defaults:

```bash
kb-trend init --non-interactive
```

This creates:
- `settings.yaml` - Configuration file
- `kb_trend.sqlite3` - SQLite database
- Wildcard query for baseline measurements

### 2. Add Keywords

Load keywords from a file:

```bash
# From plain text file (one keyword per line)
kb-trend add-keywords keywords.txt

# From CSV file
kb-trend add-keywords keywords.csv

# From TSV file
kb-trend add-keywords keywords.tsv
```

**Example CSV format:**
```csv
title,gender,category
gosse,male,youth
flicka,female,youth
```

All columns are stored as metadata, and you specify which column is the keyword
in `settings.yaml`.

### 3. Run the Scraper

Execute the scraping queue:

```bash
kb-trend run
```

Options:
- `--limit N` - Process only N items
- `--resume/--restart` - Resume from last run or restart
- `--config PATH` - Use alternate config file

### 4. Calculate Relative Frequencies

Normalize counts against baseline:

```bash
kb-trend process
```

### 5. Check Status

View database statistics:

```bash
kb-trend status
```

## Configuration

The `settings.yaml` file controls all aspects of the scraper:

```yaml
db_path: kb_trend.sqlite3
min_year: 1820                   # Optional: filter start year
max_year: 2020                   # Optional: filter end year
journals:                         # List of newspapers
  - "None"                        # "None" searches all journals
  - "DAGENS NYHETER"
sleep_timer: 1.0                  # Seconds between requests
request_timeout: 30               # HTTP timeout
keyword_column: "title"           # Which CSV column is the keyword
marker_templates:                 # Empty = plain search
  - "SÖKES"
  - "PLATS"
  - "ERHÅLLES"
proximity_distance: 5             # Proximity search window
```

### Configuration Hash Validation

KB-Trend calculates a SHA256 hash of your configuration and stores it in the
database. This prevents accidental data corruption if settings change after the
database is created.

If you modify `settings.yaml`, you'll need to:
1. Restore the original settings, or
2. Create a new database with `kb-trend init --force`

Validate your configuration:

```bash
kb-trend validate
```

## Query Types

### Plain Keyword Search

When `marker_templates` is empty:
```
Query: "gosse"
```

### Proximity Search

When markers are configured:
```
Query: "gosse SÖKES"~5 OR "gosse PLATS"~5 OR "gosse ERHÅLLES"~5
```

This finds "gosse" within 5 words of the markers.

## API

KB-Trend uses the new KB.se data API:

```
https://data.kb.se/search/?q=PHRASE&searchGranularity=part&from=YYYY-MM-DD&to=YYYY-MM-DD&isPartOf=JOURNAL
```

This replaces the old Selenium-based scraping of the tidningar.kb.se interface,
providing:
- Faster, more reliable scraping
- JSON responses instead of HTML parsing
- No browser dependencies
- Better error handling

## Database Schema

- **metadata**: Configuration hash, schema version
- **query**: Search queries with metadata from CSV
- **journal**: Newspaper definitions
- **counts**: Hit counts by year/query/journal
- **queue**: Processing queue with status tracking

## CLI Commands

| Command | Description |
|---------|-------------|
| `kb-trend init` | Run configuration wizard |
| `kb-trend add-keywords <file>` | Load keywords from file |
| `kb-trend run` | Execute scraping queue |
| `kb-trend process` | Calculate relative frequencies |
| `kb-trend status` | Show database statistics |
| `kb-trend validate` | Validate configuration hash |
| `kb-trend reset` | Reset queue to pending |

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_keywords/test_loader.py
```

### Type Checking

```bash
mypy src/kb_trend
```

### Linting

```bash
ruff check src/kb_trend tests
```

## Migration from Old Version

The original KB_TrendScraper used Selenium to scrape the tidningar.kb.se
interface. This new version:

1. Uses the official KB data API (faster, more reliable)
2. Provides a proper CLI with subcommands
3. Supports flexible keyword file formats
4. Validates configuration to prevent errors
5. Has comprehensive test coverage

**No automatic migration** is provided. To migrate:
1. Export your old data if needed
2. Run `kb-trend init` to create new configuration
3. Load your keywords with `kb-trend add-keywords`
4. Run the scraper

## License

CC BY NC 4.0

## Credits

Based on the original KB_TrendScraper project, modernized with:
- Typer for CLI
- httpx for HTTP requests
- SQLAlchemy for database
- Pydantic for configuration validation
- pytest for comprehensive testing


# Citing this tool

If you use KB-Trend in your research, please cite it as:

```bibtex
@software{johansson2025kbtrend,
  author = {Johansson, Mathias},
  title = {{KB-Trend: Swedish National Library newspaper trend scraper}},
  year = {2025},
  version = {1.0.0},
  url = {https://github.com/DigitalHistory-Lund/kb-trend},
  license = {CC-BY-NC-4.0}
}

Or in APA format:

Johansson, M. (2025). KB-Trend: Swedish National Library newspaper trend scraper (Version 1.0.0) [Computer software]. https://github.com/DigitalHistory-Lund/kb-trend
