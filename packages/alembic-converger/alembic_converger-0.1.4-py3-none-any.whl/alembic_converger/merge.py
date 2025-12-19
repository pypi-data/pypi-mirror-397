"""
Merge migration creation using Alembic's Python API.

This module handles the creation of merge migrations and validation
that they contain only graph operations (no schema changes).
"""

import re
from pathlib import Path
from typing import List, Optional

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic_converger.errors import SchemaConflictError
from alembic_converger.utils import format_revision_id, get_logger


def create_merge_migration(
    config: Config,
    script_dir: ScriptDirectory,
    heads: List[str],
    message: Optional[str] = None,
) -> str:
    """Create a merge migration for the given heads.

    Uses Alembic's command.merge() to generate a merge migration file.

    Args:
        config: Alembic Config object.
        script_dir: ScriptDirectory instance.
        heads: List of head revision IDs to merge (typically 2).
        message: Optional merge message. If None, auto-generated.

    Returns:
        Revision ID of the created merge migration.

    Raises:
        SchemaConflictError: If the merge contains schema operations.
    """
    logger = get_logger()

    if len(heads) < 2:
        raise ValueError("Need at least 2 heads to create a merge")

    # Format heads for display
    head_display = ", ".join(format_revision_id(h) for h in heads)
    logger.info(f"Creating merge migration for heads: {head_display}")

    # Generate message if not provided
    if message is None:
        message = f"Merge heads: {head_display}"

    try:
        # Use Alembic's merge command
        # This returns the new revision ID
        revision = command.merge(config, revisions=",".join(heads), message=message)

        logger.info(f"Created merge migration: {format_revision_id(revision)}")

        # Validate that the merge is empty (no schema operations)
        validate_merge_is_empty(script_dir, revision)

        return revision

    except Exception as e:
        logger.error(f"Failed to create merge migration: {e}")
        raise


def validate_merge_is_empty(script_dir: ScriptDirectory, revision: str) -> None:
    """Validate that a merge migration contains no schema operations.

    Merge migrations should only update the down_revision tuple to point
    to multiple parents. They should not contain any upgrade() or downgrade()
    operations.

    Args:
        script_dir: ScriptDirectory instance.
        revision: Revision ID to validate.

    Raises:
        SchemaConflictError: If the merge contains schema operations.
    """
    logger = get_logger()
    logger.debug(f"Validating merge {format_revision_id(revision)} is empty")

    # Get the revision script
    try:
        script = script_dir.get_revision(revision)
        module_path = script.module._get_filename()
    except Exception as e:
        raise SchemaConflictError(f"Could not load merge migration {revision}: {e}")

    # Read the migration file
    try:
        with open(module_path) as f:
            content = f.read()
    except Exception as e:
        raise SchemaConflictError(
            f"Could not read merge migration file {module_path}: {e}"
        )

    # Check for schema operations in upgrade() and downgrade()
    if has_schema_operations(content):
        raise SchemaConflictError(
            f"Merge migration {format_revision_id(revision)} contains schema operations. "
            "This indicates conflicts that require manual resolution. "
            f"Please review: {module_path}"
        )

    logger.debug(
        f"Merge {format_revision_id(revision)} is clean (no schema operations)"
    )


def has_schema_operations(migration_content: str) -> bool:
    """Check if migration content contains schema operations.

    A clean merge should have empty upgrade() and downgrade() functions
    with only 'pass' statements.

    Args:
        migration_content: Content of the migration file.

    Returns:
        True if schema operations are found, False otherwise.
    """
    # First, remove comments and docstrings to avoid false positives
    # Remove single-line comments
    content_without_comments = re.sub(r"#.*", "", migration_content)
    # Remove docstrings
    content_without_comments = re.sub(
        r'""".*?"""', "", content_without_comments, flags=re.DOTALL
    )
    content_without_comments = re.sub(
        r"'''.*?'''", "", content_without_comments, flags=re.DOTALL
    )

    # Look for common Alembic operations
    # These patterns indicate actual schema changes
    schema_operations = [
        r"op\.create_table",
        r"op\.drop_table",
        r"op\.add_column",
        r"op\.drop_column",
        r"op\.alter_column",
        r"op\.create_index",
        r"op\.drop_index",
        r"op\.create_constraint",
        r"op\.drop_constraint",
        r"op\.execute",
        r"op\.bulk_insert",
        r"op\.rename_table",
    ]

    for pattern in schema_operations:
        if re.search(pattern, content_without_comments):
            return True

    # Also check if upgrade/downgrade have more than just 'pass'
    # Extract the function bodies
    upgrade_match = re.search(
        r"def upgrade\(\).*?:\s*(.*?)(?=\ndef\s|\Z)",
        content_without_comments,
        re.DOTALL,
    )
    downgrade_match = re.search(
        r"def downgrade\(\).*?:\s*(.*?)(?=\ndef\s|\Z)",
        content_without_comments,
        re.DOTALL,
    )

    for match in [upgrade_match, downgrade_match]:
        if match:
            body = match.group(1).strip()

            # If there's anything other than 'pass', it's suspicious
            if body and body != "pass":
                # Check for non-empty lines that aren't just 'pass'
                lines = [
                    line.strip()
                    for line in body.split("\n")
                    if line.strip() and line.strip() != "pass"
                ]
                if lines:
                    return True

    return False


def delete_merge_migration(script_dir: ScriptDirectory, revision: str) -> None:
    """Delete a merge migration file (used for rollback on failure).

    Args:
        script_dir: ScriptDirectory instance.
        revision: Revision ID to delete.
    """
    logger = get_logger()

    try:
        script = script_dir.get_revision(revision)
        module_path = Path(script.module._get_filename())

        if module_path.exists():
            module_path.unlink()
            logger.info(f"Deleted merge migration: {module_path}")

    except Exception as e:
        logger.warning(f"Could not delete merge migration {revision}: {e}")
