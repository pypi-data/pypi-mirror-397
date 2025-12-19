"""
Core convergence algorithm for Alembic migration graphs.

This module orchestrates the entire convergence process:
1. Load configuration and revision map
2. Find heads descending from base revision
3. Iteratively merge heads until only one remains
4. Validate after each merge
"""

from typing import List, Optional

from alembic_converger.config import (
    get_revision_map,
    get_script_directory,
    load_alembic_config,
)
from alembic_converger.graph import (
    get_heads_from_base,
    sort_heads_deterministically,
    validate_single_base,
)
from alembic_converger.merge import create_merge_migration, delete_merge_migration
from alembic_converger.utils import format_revision_id, setup_logging
from alembic_converger.validate import check_database_available, validate_upgrade


class ConvergenceResult:
    """Result of a convergence operation."""

    def __init__(self):
        self.initial_heads: List[str] = []
        self.final_head: Optional[str] = None
        self.merges_created: List[str] = []
        self.already_converged: bool = False

    def __str__(self) -> str:
        if self.already_converged:
            return "Already converged (0 or 1 head)"

        return (
            f"Convergence successful:\n"
            f"  Initial heads: {len(self.initial_heads)}\n"
            f"  Merges created: {len(self.merges_created)}\n"
            f"  Final head: {format_revision_id(self.final_head)}"
        )


def converge_migrations(
    base_revision: str,
    config_path: Optional[str] = None,
    dry_run: bool = False,
    skip_validation: bool = False,
    verbose: bool = False,
) -> ConvergenceResult:
    """Converge multiple Alembic migration heads into a single head.

    This is the main entry point for the convergence algorithm.

    Algorithm:
    1. Load Alembic configuration and revision map
    2. Find all heads descending from base_revision
    3. If 0 or 1 heads, return (already converged)
    4. Validate all heads share a common base
    5. While more than one head exists:
       a. Pick two heads (deterministically)
       b. Create merge migration
       c. Validate merge is empty (no schema ops)
       d. Optionally validate upgrade path
       e. Reload revision map
    6. Return convergence result

    Args:
        base_revision: Base revision to converge from. All heads must descend
                      from this revision.
        config_path: Path to alembic.ini file. If None, uses "alembic.ini"
                    in current directory.
        dry_run: If True, show what would be done without making changes.
        skip_validation: If True, skip upgrade validation (faster but less safe).
        verbose: If True, enable debug logging.

    Returns:
        ConvergenceResult object with details about the convergence.

    Raises:
        ConvergenceError: If convergence fails for any reason.
        ConfigurationError: If Alembic configuration is invalid.
        MultipleBasesError: If heads have unrelated bases.
        ValidationError: If upgrade validation fails.
        SchemaConflictError: If merge contains schema operations.
    """
    # Set up logging
    logger = setup_logging(verbose)

    logger.info("=" * 60)
    logger.info("Starting Alembic convergence")
    logger.info(f"Base revision: {format_revision_id(base_revision)}")
    logger.info(f"Dry run: {dry_run}")
    logger.info(f"Skip validation: {skip_validation}")
    logger.info("=" * 60)

    result = ConvergenceResult()
    created_merges: List[str] = []

    try:
        # 1. Load configuration
        config = load_alembic_config(config_path)
        script_dir = get_script_directory(config)

        # 2. Find all heads from base
        revision_map = get_revision_map(script_dir)
        heads = get_heads_from_base(revision_map, base_revision)
        result.initial_heads = heads.copy()

        logger.info(f"Found {len(heads)} head(s)")

        # 3. Check if already converged
        if len(heads) <= 1:
            logger.info("Already converged (0 or 1 head)")
            result.already_converged = True
            result.final_head = heads[0] if heads else None
            return result

        # 4. Validate single base
        validate_single_base(revision_map, heads)

        # 5. Check database availability for validation
        db_available = False
        if not skip_validation:
            db_available = check_database_available(config)
            if not db_available:
                logger.warning(
                    "Database not available - skipping upgrade validation. "
                    "Use --skip-validation to suppress this warning."
                )
                skip_validation = True

        if dry_run:
            logger.info("DRY RUN: Would create the following merges:")

        # 6. Iteratively merge heads
        iteration = 0
        while len(heads) > 1:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")
            logger.info(f"Current heads: {[format_revision_id(h) for h in heads]}")

            # Sort heads deterministically
            heads = sort_heads_deterministically(heads)

            # Pick first two heads to merge
            head1, head2 = heads[0], heads[1]
            logger.info(
                f"Merging: {format_revision_id(head1)} + {format_revision_id(head2)}"
            )

            if dry_run:
                # In dry run, simulate merge
                logger.info(f"  [DRY RUN] Would create merge of {head1}, {head2}")
                # Assume merge succeeds and remove the two heads
                heads = heads[2:]
                # Add a simulated merge head
                simulated_merge = f"<merge_{iteration}>"
                heads.append(simulated_merge)
                created_merges.append(simulated_merge)
            else:
                # Create actual merge
                merge_rev = create_merge_migration(config, script_dir, [head1, head2])
                created_merges.append(merge_rev)

                # Validate upgrade if requested
                if not skip_validation:
                    logger.info("Validating upgrade path...")
                    validate_upgrade(
                        config, base_revision, "head", use_subprocess=False
                    )

                # Reload revision map to see new merge
                script_dir = get_script_directory(config)
                revision_map = get_revision_map(script_dir)
                heads = get_heads_from_base(revision_map, base_revision)

                logger.info(f"After merge: {len(heads)} head(s) remaining")

        # 7. Success
        result.merges_created = created_merges
        result.final_head = heads[0] if heads else None

        logger.info("\n" + "=" * 60)
        logger.info("Convergence complete!")
        logger.info(f"Created {len(created_merges)} merge migration(s)")
        logger.info(f"Final head: {format_revision_id(result.final_head)}")
        logger.info("=" * 60)

        return result

    except Exception as e:
        # Rollback on failure (delete created merges)
        if not dry_run and created_merges:
            logger.error(f"Convergence failed: {e}")
            logger.info("Rolling back created merge migrations...")

            for merge_rev in reversed(created_merges):
                try:
                    delete_merge_migration(script_dir, merge_rev)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up {merge_rev}: {cleanup_error}")

        raise
