"""
Migration validation through upgrade testing.

This module provides functions to validate that migrations can be
successfully applied by running upgrade operations.
"""

import subprocess

from alembic import command
from alembic.config import Config

from alembic_converger.errors import ValidationError
from alembic_converger.utils import format_revision_id, get_logger


def validate_upgrade(
    config: Config,
    from_revision: str,
    to_revision: str = "head",
    use_subprocess: bool = True,
) -> None:
    """Validate that upgrade from one revision to another succeeds.

    This runs an actual Alembic upgrade to test the migration path.
    It requires a database connection configured in alembic.ini.

    Args:
        config: Alembic Config object.
        from_revision: Starting revision.
        to_revision: Target revision (default: "head").
        use_subprocess: If True, use subprocess to isolate the upgrade.
                       If False, use Alembic's command API directly.

    Raises:
        ValidationError: If the upgrade fails.
    """
    logger = get_logger()

    revision_range = f"{format_revision_id(from_revision)}:{to_revision}"
    logger.info(f"Validating upgrade: {revision_range}")

    try:
        if use_subprocess:
            _validate_upgrade_subprocess(config, from_revision, to_revision)
        else:
            _validate_upgrade_direct(config, from_revision, to_revision)

        logger.info(f"Upgrade validation successful: {revision_range}")

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Upgrade validation failed for {revision_range}: {e}")


def _validate_upgrade_direct(
    config: Config, from_revision: str, to_revision: str
) -> None:
    """Validate upgrade using Alembic's command API directly.

    Args:
        config: Alembic Config object.
        from_revision: Starting revision.
        to_revision: Target revision.

    Raises:
        ValidationError: If the upgrade fails.
    """
    try:
        # First downgrade to from_revision
        command.downgrade(config, from_revision)

        # Then upgrade to to_revision
        command.upgrade(config, to_revision)

    except Exception as e:
        raise ValidationError(f"Upgrade {from_revision}:{to_revision} failed: {e}")


def _validate_upgrade_subprocess(
    config: Config, from_revision: str, to_revision: str
) -> None:
    """Validate upgrade using subprocess (more isolated).

    Args:
        config: Alembic Config object.
        from_revision: Starting revision.
        to_revision: Target revision.

    Raises:
        ValidationError: If the upgrade fails.
    """
    config_file = config.config_file_name
    if not config_file:
        raise ValidationError("Config file path not available")

    # Run alembic upgrade via subprocess
    revision_range = f"{from_revision}:{to_revision}"

    try:
        # First downgrade
        result = subprocess.run(
            ["alembic", "-c", config_file, "downgrade", from_revision],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode != 0:
            raise ValidationError(
                f"Downgrade to {from_revision} failed:\n{result.stderr}"
            )

        # Then upgrade
        result = subprocess.run(
            ["alembic", "-c", config_file, "upgrade", to_revision],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode != 0:
            raise ValidationError(f"Upgrade to {to_revision} failed:\n{result.stderr}")

    except subprocess.TimeoutExpired:
        raise ValidationError(f"Upgrade validation timed out for {revision_range}")
    except FileNotFoundError:
        raise ValidationError("alembic command not found. Is Alembic installed?")


def check_database_available(config: Config) -> bool:
    """Check if database is available for validation.

    Args:
        config: Alembic Config object.

    Returns:
        True if database connection can be established, False otherwise.
    """
    logger = get_logger()

    try:
        # Try to get current revision
        command.current(config)
        return True
    except Exception as e:
        logger.debug(f"Database not available: {e}")
        return False
