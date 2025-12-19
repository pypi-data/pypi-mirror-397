"""Init command for kb-trend CLI."""

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console

from kb_trend.config.manager import ConfigManager
from kb_trend.config.wizard import run_setup_wizard
from kb_trend.database.manager import DatabaseManager
from kb_trend.utils.hash import calculate_config_hash

console = Console()


def init_command(
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Use default settings without prompts"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing configuration"
    ),
) -> None:
    """Initialize kb-trend with configuration wizard."""
    # Check if config exists
    if config_path.exists() and not force:
        console.print(f"[red]✗ Configuration already exists: {config_path}[/red]")
        console.print("  Use --force to overwrite")
        raise typer.Exit(1)

    # Run wizard
    settings = run_setup_wizard(non_interactive)

    # Save config
    config_manager = ConfigManager(config_path)
    config_manager.save(settings)

    # Initialize database
    db_manager = DatabaseManager(settings.db_path)
    db_manager.init_schema()

    # Store config hash
    config_dict = config_manager.to_dict(settings)
    config_hash = calculate_config_hash(config_dict)
    db_manager.set_metadata('config_hash', config_hash)
    db_manager.set_metadata('schema_version', '1.0.0')
    db_manager.set_metadata('created_at', datetime.now().isoformat())

    # Initialize journals
    db_manager.initialize_journals(settings.journals)

    # Create wildcard query for relative frequency calculation
    wildcard_id = db_manager.create_wildcard_query()

    # Populate queue for wildcard query
    db_manager.populate_queue(wildcard_id, settings.journals)

    console.print(f"\n[green]✓[/green] Configuration saved to {config_path}")
    console.print(f"[green]✓[/green] Database initialized at {settings.db_path}")
    console.print(f"[green]✓[/green] Wildcard query created (id={wildcard_id})")

    console.print("\n[bold cyan]Next steps:[/bold cyan]")
    console.print("  1. Add keywords: [bold]kb-trend add-keywords <file>[/bold]")
    console.print("  2. Run scraper: [bold]kb-trend run[/bold]")
    console.print("  3. Calculate relative frequencies: [bold]kb-trend process[/bold]")
    console.print()
