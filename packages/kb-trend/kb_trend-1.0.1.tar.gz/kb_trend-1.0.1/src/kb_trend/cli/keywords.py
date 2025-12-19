"""Add keywords command for kb-trend CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import track

from kb_trend.config.manager import ConfigManager
from kb_trend.database.manager import DatabaseManager
from kb_trend.keywords.loader import KeywordLoader
from kb_trend.keywords.query_builder import QueryBuilder
from kb_trend.utils.hash import validate_config_hash

console = Console()


def add_keywords_command(
    file_path: Path = typer.Argument(..., help="Path to keywords file (.txt, .csv, .tsv)"),
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
) -> None:
    """Load keywords from file and populate query queue."""
    # Check if file exists
    if not file_path.exists():
        console.print(f"[red]✗ File not found: {file_path}[/red]")
        raise typer.Exit(1)

    # Load config
    try:
        config_manager = ConfigManager(config_path)
        settings = config_manager.load()
    except FileNotFoundError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error loading configuration: {e}[/red]")
        raise typer.Exit(1)

    # Validate config hash
    db_manager = DatabaseManager(settings.db_path)
    config_dict = config_manager.to_dict(settings)
    is_valid, error_msg = validate_config_hash(
        db_manager.get_metadata('config_hash'),
        config_dict
    )

    if not is_valid:
        console.print(f"[red]✗ {error_msg}[/red]")
        raise typer.Exit(1)

    # Load keywords
    console.print(f"Loading keywords from [cyan]{file_path}[/cyan]...")
    try:
        loader = KeywordLoader(settings.keyword_column)
        keywords = loader.load(file_path)
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"  Loaded [green]{len(keywords)}[/green] keywords")

    # Build queries
    query_builder = QueryBuilder(
        marker_templates=settings.marker_templates,
        proximity_distance=settings.proximity_distance
    )

    # Insert queries and populate queue
    added_count = 0
    skipped_count = 0

    for keyword_data in track(keywords, description="Adding keywords to database..."):
        try:
            keyword = keyword_data[settings.keyword_column]

            # Build search string
            search_string = query_builder.build(keyword)

            # Insert query
            query_id = db_manager.insert_query(
                search_string=search_string,
                keyword=keyword,
                metadata=keyword_data
            )

            # Check if this is a new query or existing
            # (insert_query returns existing id if already exists)
            # Populate queue for all journals
            items_added = db_manager.populate_queue(query_id, settings.journals)

            if items_added > 0:
                added_count += 1
            else:
                skipped_count += 1

        except KeyError:
            console.print(
                f"[yellow]⚠[/yellow] Skipping row: missing column '{settings.keyword_column}'"
            )
            skipped_count += 1
            continue

    console.print()
    console.print(f"[green]✓[/green] Added [bold]{added_count}[/bold] keywords to queue")

    if skipped_count > 0:
        console.print(f"[yellow]⚠[/yellow] Skipped [bold]{skipped_count}[/bold] duplicate keywords")

    # Show status
    stats = db_manager.get_statistics()
    console.print()
    console.print("[bold cyan]Database Status:[/bold cyan]")
    console.print(f"  Total queries:  {stats['total_queries']}")
    console.print(f"  Queue pending:  {stats['queue_pending']}")
    console.print()
