"""Interactive configuration wizard."""

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from kb_trend.config.models import Settings

console = Console()


def run_setup_wizard(non_interactive: bool = False) -> Settings:
    """Run interactive setup wizard.

    Args:
        non_interactive: If True, use default values without prompts

    Returns:
        Configured Settings object
    """
    if non_interactive:
        console.print("[yellow]Using default settings (non-interactive mode)[/yellow]")
        return Settings()

    console.print("[bold blue]═══════════════════════════════════════[/bold blue]")
    console.print("[bold blue]     KB-Trend Configuration Wizard     [/bold blue]")
    console.print("[bold blue]═══════════════════════════════════════[/bold blue]\n")

    # Database path
    console.print("[bold cyan]Database Configuration[/bold cyan]")
    db_path = Prompt.ask(
        "  Database file path",
        default="kb_trend.sqlite3"
    )
    console.print()

    # Year range
    console.print("[bold cyan]Time Range[/bold cyan]")
    use_year_filter = Confirm.ask(
        "  Filter by year range?",
        default=True
    )

    min_year: int | None = None
    max_year: int | None = None

    if use_year_filter:
        min_year = IntPrompt.ask("  Minimum year", default=1820)
        max_year = IntPrompt.ask("  Maximum year", default=2020)

        # Validate year range
        while max_year < min_year:
            console.print("[red]  Error: Maximum year must be >= minimum year[/red]")
            max_year = IntPrompt.ask("  Maximum year", default=2020)

    console.print()

    # Journals
    console.print("[bold cyan]Journals[/bold cyan]")
    console.print('  Enter journal names (one per line, empty line to finish)')
    console.print('  Use "None" to search all journals\n')

    journals: list[str] = []
    journal_count = 1

    while True:
        journal = Prompt.ask(f"  Journal #{journal_count}", default="")
        if not journal:
            break
        journals.append(journal)
        journal_count += 1

    if not journals:
        console.print("[yellow]  No journals specified, using 'None' (all journals)[/yellow]")
        journals = ["None"]

    console.print()

    # Scraping settings
    console.print("[bold cyan]Scraping Behavior[/bold cyan]")
    sleep_timer = FloatPrompt.ask(
        "  Sleep between requests (seconds)",
        default=1.0
    )
    request_timeout = IntPrompt.ask(
        "  Request timeout (seconds)",
        default=30
    )
    console.print()

    # Keyword settings
    console.print("[bold cyan]Keyword Configuration[/bold cyan]")
    keyword_column = Prompt.ask(
        "  CSV column name for keywords",
        default="title"
    )
    console.print()

    # Proximity search
    console.print("[bold cyan]Query Templates[/bold cyan]")
    console.print("  Proximity search allows finding keywords near specific markers")
    console.print('  Example: "gosse SÖKES"~5 finds "gosse" within 5 words of "SÖKES"\n')

    use_proximity = Confirm.ask(
        "  Use proximity search with markers?",
        default=False
    )

    marker_templates: list[str] = []
    proximity_distance = 5

    if use_proximity:
        console.print("\n  Enter proximity markers (e.g., SÖKES, PLATS, ERHÅLLES)")
        console.print("  Empty line to finish\n")

        marker_count = 1
        while True:
            marker = Prompt.ask(f"  Marker #{marker_count}", default="")
            if not marker:
                break
            marker_templates.append(marker.upper())
            marker_count += 1

        if marker_templates:
            proximity_distance = IntPrompt.ask(
                "  Proximity distance (words)",
                default=5
            )
    else:
        console.print("[dim]  Using plain keyword search (no markers)[/dim]")

    # Create settings
    settings = Settings(
        db_path=Path(db_path),
        min_year=min_year,
        max_year=max_year,
        journals=journals,
        sleep_timer=sleep_timer,
        request_timeout=request_timeout,
        keyword_column=keyword_column,
        marker_templates=marker_templates,
        proximity_distance=proximity_distance
    )

    # Display summary
    console.print("\n[bold green]═══════════════════════════════════════[/bold green]")
    console.print("[bold green]     Configuration Summary              [/bold green]")
    console.print("[bold green]═══════════════════════════════════════[/bold green]\n")

    console.print(f"  Database:           {settings.db_path}")
    if settings.min_year and settings.max_year:
        console.print(f"  Year range:         {settings.min_year}-{settings.max_year}")
    else:
        console.print("  Year range:         All years")
    console.print(f"  Journals:           {', '.join(settings.journals)}")
    console.print(f"  Sleep timer:        {settings.sleep_timer}s")
    console.print(f"  Request timeout:    {settings.request_timeout}s")
    console.print(f"  Keyword column:     {settings.keyword_column}")

    if settings.marker_templates:
        console.print(f"  Proximity markers:  {', '.join(settings.marker_templates)}")
        console.print(f"  Proximity distance: {settings.proximity_distance} words")
    else:
        console.print("  Query mode:         Plain keyword search")

    console.print()

    if not Confirm.ask("[bold]Save this configuration?[/bold]", default=True):
        console.print("[yellow]Configuration cancelled.[/yellow]")
        raise typer.Abort()

    return settings
