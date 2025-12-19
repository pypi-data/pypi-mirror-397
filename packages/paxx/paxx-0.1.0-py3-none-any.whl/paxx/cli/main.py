"""Main CLI entry point for paxx."""

import typer

from paxx import __version__
from paxx.cli.bootstrap import create_project
from paxx.cli.db import app as db_app
from paxx.cli.feature import app as feature_app
from paxx.cli.start import start

app = typer.Typer(
    name="paxx",
    help="paxx - Python Async API - a domain-oriented web framework built on top of FastAPI",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(db_app, name="db")
app.add_typer(feature_app, name="feature")

# Register top-level commands
app.command("bootstrap")(create_project)
app.command("start")(start)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"paxx version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the paxx version and exit.",
    ),
) -> None:
    """paxx - Python Async API - a domain-oriented web framework built on top of FastAPI."""


if __name__ == "__main__":
    app()
