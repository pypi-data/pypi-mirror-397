"""Main CLI application."""

from pathlib import Path

import typer
from rich.console import Console

from kb_trend.cli import init_cmd, keywords, process, run, status

app = typer.Typer(
    name="kb-trend",
    help="Swedish National Library newspaper trend scraper",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)

console = Console()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """KB-Trend: Swedish National Library newspaper trend scraper.

    If no command is specified and no settings.yaml exists, runs the init wizard.
    """
    ctx.obj = {"verbose": verbose}

    # If no subcommand was invoked, check if we should run init
    if ctx.invoked_subcommand is None:
        # Check if settings.yaml exists
        settings_path = Path("settings.yaml")
        if not settings_path.exists():
            # No settings file, run init wizard
            console.print("[yellow]No configuration found. Running setup wizard...[/yellow]\n")
            init_cmd.init_command(
                config_path=settings_path,
                non_interactive=False,
                force=False
            )
        else:
            # Settings exist, show help
            console.print("[green]✓[/green] Configuration found at settings.yaml\n")
            console.print("Available commands:")
            console.print("  [cyan]kb-trend init[/cyan]          - Re-run configuration wizard")
            console.print("  [cyan]kb-trend add-keywords[/cyan]  - Load keywords from file")
            console.print("  [cyan]kb-trend run[/cyan]           - Execute scraping queue")
            console.print("  [cyan]kb-trend process[/cyan]       - Calculate relative frequencies")
            console.print("  [cyan]kb-trend status[/cyan]        - Show database statistics")
            console.print()
            console.print("Run [bold]kb-trend --help[/bold] for more information")


# Register commands
app.command(name="init")(init_cmd.init_command)
app.command(name="add-keywords")(keywords.add_keywords_command)
app.command(name="run")(run.run_command)
app.command(name="process")(process.process_command)
app.command(name="status")(status.status_command)
app.command(name="validate")(status.validate_command)
app.command(name="reset")(status.reset_command)


if __name__ == "__main__":
    app()
