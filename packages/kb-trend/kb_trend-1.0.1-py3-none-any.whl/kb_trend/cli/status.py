"""Status commands for kb-trend CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from kb_trend.config.manager import ConfigManager
from kb_trend.database.manager import DatabaseManager
from kb_trend.utils.hash import validate_config_hash

console = Console()


def status_command(
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
) -> None:
    """Show database and queue status."""
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

    # Get database manager
    db_manager = DatabaseManager(settings.db_path)

    # Get statistics
    stats = db_manager.get_statistics()

    # Create status table
    table = Table(title="KB-Trend Status", title_style="bold cyan")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", style="green", justify="right")

    table.add_row("Total Queries", str(stats['total_queries']))
    table.add_row("Total Journals", str(stats['total_journals']))
    table.add_row("Total Counts", str(stats['total_counts']))
    table.add_row("─" * 20, "─" * 10)
    table.add_row("Queue Pending", str(stats['queue_pending']))
    table.add_row("Queue Completed", str(stats['queue_completed']))

    if stats['queue_failed'] > 0:
        table.add_row("Queue Failed", str(stats['queue_failed']), style="red")

    console.print()
    console.print(table)

    # Show next steps
    console.print()
    if stats['queue_pending'] > 0:
        console.print("[bold cyan]Next step:[/bold cyan] kb-trend run")
    elif stats['queue_failed'] > 0:
        console.print(
            "[bold yellow]Note:[/bold yellow] Some items failed. "
            "Run 'kb-trend run --resume' to retry"
        )
    elif stats['total_counts'] > 0:
        console.print("[bold cyan]Next step:[/bold cyan] kb-trend process")
    else:
        console.print("[bold cyan]Next step:[/bold cyan] kb-trend add-keywords <file>")

    console.print()


def validate_command(
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
) -> None:
    """Validate configuration hash against database."""
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

    # Validate
    db_manager = DatabaseManager(settings.db_path)
    config_dict = config_manager.to_dict(settings)
    is_valid, error_msg = validate_config_hash(
        db_manager.get_metadata('config_hash'),
        config_dict
    )

    if is_valid:
        console.print("[green]✓ Configuration is valid[/green]")
        console.print("  Settings match database configuration")
    else:
        console.print("[red]✗ Configuration validation failed[/red]\n")
        console.print(error_msg)
        raise typer.Exit(1)


def reset_command(
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
    confirm: bool = typer.Option(
        False,
        "--yes", "-y",
        help="Skip confirmation prompt"
    ),
) -> None:
    """Reset queue status (mark all items as pending)."""
    if not confirm:
        confirmed = typer.confirm(
            "Reset all queue items to pending status?",
            default=False
        )
        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Abort()

    # Load config
    try:
        config_manager = ConfigManager(config_path)
        settings = config_manager.load()
    except FileNotFoundError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    # Reset queue
    db_manager = DatabaseManager(settings.db_path)
    reset_count = db_manager.reset_queue()

    console.print(f"[green]✓[/green] Reset [bold]{reset_count}[/bold] queue items to pending")
    console.print()
    console.print("[bold cyan]Next step:[/bold cyan] kb-trend run")
    console.print()
