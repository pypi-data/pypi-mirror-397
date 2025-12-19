"""Main entry point for kb-trend CLI."""

from kb_trend.cli.app import app


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
