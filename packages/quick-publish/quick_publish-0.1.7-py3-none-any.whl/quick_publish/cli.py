"""Command line interface for quick-publish."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from .core import Publisher
from .exceptions import QuickPublishError

console = Console()


@click.command()
@click.option(
    "--depcost",
    is_flag=True,
    default=False,
    help="Generate or update `DEPCOST.md`, defaults to `false`",
)
@click.option(
    "--push/--no-push",
    default=True,
    help="Execute git push & tag push to remote git origin, defaults to `true`",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without making changes",
)
@click.option(
    "--version-override",
    "version_override",
    type=str,
    help="Specify version directly instead of interactive selection",
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Enable verbose output"
)
@click.version_option()
def main(
    depcost: bool,
    push: bool,
    dry_run: bool,
    version_override: str | None,
    verbose: bool,
) -> None:
    """Shipped a standard `publish` workflow with one click."""
    try:
        publisher = Publisher(
            working_dir=Path.cwd(),
            verbose=verbose,
        )

        if dry_run:
            console.print("[yellow]Dry run mode - no changes will be made[/yellow]")

        publisher.publish(
            generate_depcost=depcost,
            push_to_remote=push,
            dry_run=dry_run,
            version_override=version_override,
        )

    except QuickPublishError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
