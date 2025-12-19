"""Run command for kb-trend CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from kb_trend.config.manager import ConfigManager
from kb_trend.database.manager import DatabaseManager
from kb_trend.scraper.worker import ScraperWorker
from kb_trend.utils.hash import validate_config_hash

console = Console()


def run_command(
    config_path: Path = typer.Option(
        Path("settings.yaml"),
        "--config", "-c",
        help="Path to settings file"
    ),
    limit: int = typer.Option(
        None,
        "--limit", "-n",
        help="Process only N items"
    ),
    resume: bool = typer.Option(
        True,
        "--resume/--restart",
        help="Resume from last run or restart from beginning"
    ),
) -> None:
    """Execute scraping queue."""
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

    # Get queue
    status_filter = ['pending', 'failed'] if resume else ['pending']
    queue_items = db_manager.get_queue(status=status_filter, limit=limit)

    if not queue_items:
        console.print("[yellow]⚠ No items in queue[/yellow]")
        console.print("  Add keywords with: kb-trend add-keywords <file>")
        return

    console.print(f"Processing [cyan]{len(queue_items)}[/cyan] queue items")
    if resume:
        console.print("[dim]  Resuming from last run (including failed items)[/dim]")
    console.print()

    # Create worker
    worker = ScraperWorker(db_manager=db_manager, settings=settings)

    # Process queue with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Scraping...", total=len(queue_items))

        success_count = 0
        failed_count = 0

        for idx, item in enumerate(queue_items, 1):
            try:
                # Get query keyword for display
                query = db_manager.get_query_by_id(item.query_id)
                keyword = query.keyword if query else f"ID{item.query_id}"

                progress.update(
                    task,
                    description=f"[cyan]Scraping[/cyan] [{idx}/{len(queue_items)}] {keyword}",
                    advance=0
                )

                worker.process_item(item)
                success_count += 1

                progress.update(task, advance=1)

            except KeyboardInterrupt:
                console.print("\n[yellow]⚠ Interrupted by user[/yellow]")
                break

            except Exception as e:
                failed_count += 1
                console.print(f"\n[red]✗ Error processing item {item.id}: {e}[/red]")
                progress.update(task, advance=1)
                continue

    # Close worker
    worker.close()

    # Summary
    console.print()
    console.print("[bold green]Scraping Summary:[/bold green]")
    console.print(f"  Success: [green]{success_count}[/green]")
    if failed_count > 0:
        console.print(f"  Failed:  [red]{failed_count}[/red]")

    # Show stats
    stats = db_manager.get_statistics()
    console.print()
    console.print("[bold cyan]Database Status:[/bold cyan]")
    console.print(f"  Total counts:     {stats['total_counts']}")
    console.print(f"  Queue pending:    {stats['queue_pending']}")
    console.print(f"  Queue completed:  {stats['queue_completed']}")
    if stats['queue_failed'] > 0:
        console.print(f"  Queue failed:     {stats['queue_failed']}")

    console.print()
    if stats['queue_pending'] == 0 and stats['queue_failed'] == 0:
        console.print("[bold green]✓ All items processed![/bold green]")
        console.print("  Next step: kb-trend process (calculate relative frequencies)")
    console.print()
