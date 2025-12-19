"""Process command for kb-trend CLI."""

from pathlib import Path

import typer
from rich.console import Console

from kb_trend.config.manager import ConfigManager
from kb_trend.database.manager import DatabaseManager
from kb_trend.processor.relative import RelativeFrequencyProcessor
from kb_trend.utils.hash import validate_config_hash

console = Console()


def process_command(
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
) -> None:
    """Calculate relative frequencies."""
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

    # Check if wildcard query has been processed
    wildcard_id = db_manager.get_wildcard_query_id()
    if wildcard_id is None:
        console.print("[red]✗ Wildcard query not found[/red]")
        console.print("  Run 'kb-trend init' to create it")
        raise typer.Exit(1)

    # Check if wildcard has counts
    wildcard_counts = db_manager.get_counts_for_query(wildcard_id)
    if not wildcard_counts:
        console.print("[yellow]⚠ No counts found for wildcard query[/yellow]")
        console.print("  Run 'kb-trend run' to collect baseline data")
        console.print("  The wildcard query must be processed first")
        raise typer.Exit(1)

    # Process
    console.print("Calculating relative frequencies...")

    try:
        processor = RelativeFrequencyProcessor(db_manager)
        updated_count = processor.calculate_all()

        console.print(f"[green]✓[/green] Updated [bold]{updated_count}[/bold] records")

        # Show stats
        stats = db_manager.get_statistics()
        console.print()
        console.print("[bold cyan]Database Status:[/bold cyan]")
        console.print(f"  Total counts: {stats['total_counts']}")
        console.print()

    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)
