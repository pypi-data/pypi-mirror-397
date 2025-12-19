"""
Alembic configuration loading and validation.
"""

from pathlib import Path
from typing import Optional

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.script.revision import RevisionMap

from alembic_converger.errors import ConfigurationError
from alembic_converger.utils import get_logger, resolve_config_path


def load_alembic_config(config_path: Optional[str] = None) -> Config:
    """Load Alembic configuration from file.

    Args:
        config_path: Path to alembic.ini file. If None, uses alembic.ini
                    in current directory.

    Returns:
        Alembic Config object.

    Raises:
        ConfigurationError: If configuration cannot be loaded.
    """
    logger = get_logger()

    try:
        path = resolve_config_path(config_path)
        logger.debug(f"Loading Alembic config from: {path}")

        config = Config(str(path))

        # Validate that script_location is set
        script_location = config.get_main_option("script_location")
        if not script_location:
            raise ConfigurationError("script_location not set in Alembic configuration")

        return config

    except FileNotFoundError as e:
        raise ConfigurationError(str(e))
    except Exception as e:
        raise ConfigurationError(f"Failed to load Alembic configuration: {e}")


def get_script_directory(config: Config) -> ScriptDirectory:
    """Get ScriptDirectory instance from Alembic config.

    Args:
        config: Alembic Config object.

    Returns:
        ScriptDirectory instance.

    Raises:
        ConfigurationError: If script directory cannot be created.
    """
    logger = get_logger()

    try:
        script_dir = ScriptDirectory.from_config(config)

        # Validate that versions directory exists
        versions_path = Path(script_dir.versions)
        if not versions_path.exists():
            raise ConfigurationError(
                f"Versions directory does not exist: {versions_path}"
            )

        logger.debug(f"Script directory: {script_dir.dir}")
        logger.debug(f"Versions directory: {script_dir.versions}")

        return script_dir

    except Exception as e:
        raise ConfigurationError(f"Failed to create ScriptDirectory: {e}")


def get_revision_map(script_dir: ScriptDirectory) -> RevisionMap:
    """Get RevisionMap from ScriptDirectory.

    Args:
        script_dir: ScriptDirectory instance.

    Returns:
        RevisionMap instance for graph traversal.
    """
    return script_dir.revision_map
