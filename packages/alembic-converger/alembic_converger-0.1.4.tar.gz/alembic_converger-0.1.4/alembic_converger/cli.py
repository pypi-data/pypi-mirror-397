"""
Command-line interface for alembic-converger.

This module provides a Click-based CLI for converging Alembic migrations.
"""

import sys

import click

from alembic_converger import __version__
from alembic_converger.converge import converge_migrations
from alembic_converger.errors import (
    ConfigurationError,
    ConvergenceError,
    MultipleBasesError,
    ValidationError,
)


@click.group()
@click.version_option(version=__version__, prog_name="alembic-converger")
def cli():
    """Alembic Converger - Safely converge Alembic migration graphs.

    This tool automatically detects and converges multiple Alembic migration
    heads by generating minimal merge migrations without schema operations.
    """
    pass


@cli.command()
@click.option(
    "--from-revision",
    required=True,
    help="Base revision to converge from. All heads must descend from this revision.",
)
@click.option(
    "--alembic-config",
    default="alembic.ini",
    help="Path to alembic.ini configuration file.",
    show_default=True,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes.",
)
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip upgrade validation (faster but less safe, not recommended).",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable debug logging.",
)
def converge(
    from_revision: str,
    alembic_config: str,
    dry_run: bool,
    skip_validation: bool,
    verbose: bool,
):
    """Converge multiple migration heads into a single head.

    This command finds all heads descending from FROM_REVISION and merges
    them iteratively until only one head remains.

    Examples:

      # Converge heads from revision ae1027a6acf
      alembic-converger converge --from-revision ae1027a6acf

      # Dry run to see what would be done
      alembic-converger converge --from-revision ae1027a6acf --dry-run

      # Use custom alembic.ini location
      alembic-converger converge --from-revision ae1027a6acf \\
          --alembic-config config/alembic.ini

    Exit codes:
      0: Success (already converged or successfully merged)
      1: Convergence failed (validation error, conflicts, etc.)
      2: Configuration error
    """
    try:
        # Run convergence
        result = converge_migrations(
            base_revision=from_revision,
            config_path=alembic_config,
            dry_run=dry_run,
            skip_validation=skip_validation,
            verbose=verbose,
        )

        # Print summary
        if result.already_converged:
            click.echo(
                click.style("✓ ", fg="green", bold=True)
                + "Already converged (0 or 1 head)"
            )
            if result.final_head:
                click.echo(f"  Current head: {result.final_head}")
        else:
            click.echo(
                click.style("✓ ", fg="green", bold=True) + "Convergence successful!"
            )
            click.echo(f"  Initial heads: {len(result.initial_heads)}")
            click.echo(f"  Merges created: {len(result.merges_created)}")
            click.echo(f"  Final head: {result.final_head}")

            if dry_run:
                click.echo(
                    click.style("\n  Note: ", fg="yellow", bold=True)
                    + "This was a dry run. No changes were made."
                )

        sys.exit(0)

    except ConfigurationError as e:
        click.echo(
            click.style("✗ Configuration Error: ", fg="red", bold=True) + str(e),
            err=True,
        )
        sys.exit(2)

    except MultipleBasesError as e:
        click.echo(
            click.style("✗ Multiple Bases Error: ", fg="red", bold=True) + str(e),
            err=True,
        )
        click.echo(
            "\n"
            + click.style("Hint: ", fg="yellow", bold=True)
            + "The heads do not share a common ancestor. This usually means "
            "you have migrations from unrelated sources or branches.",
            err=True,
        )
        sys.exit(1)

    except ValidationError as e:
        click.echo(
            click.style("✗ Validation Error: ", fg="red", bold=True) + str(e), err=True
        )
        click.echo(
            "\n"
            + click.style("Hint: ", fg="yellow", bold=True)
            + "The merge migration validation failed. This usually indicates "
            "schema conflicts that require manual resolution.",
            err=True,
        )
        sys.exit(1)

    except ConvergenceError as e:
        click.echo(
            click.style("✗ Convergence Error: ", fg="red", bold=True) + str(e), err=True
        )
        sys.exit(1)

    except Exception as e:
        click.echo(
            click.style("✗ Unexpected Error: ", fg="red", bold=True) + str(e), err=True
        )
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
