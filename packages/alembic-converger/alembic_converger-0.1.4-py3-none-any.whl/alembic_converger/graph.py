"""
Migration graph analysis and traversal utilities.

This module provides functions for analyzing the Alembic migration DAG,
including head detection, ancestor queries, and graph validation.
"""

from typing import List, Optional, Tuple

from alembic.script.revision import RevisionMap

from alembic_converger.errors import GraphError, MultipleBasesError
from alembic_converger.utils import format_revision_id, get_logger


def get_heads_from_base(revision_map: RevisionMap, base_revision: str) -> List[str]:
    """Find all heads that descend from the given base revision.

    A head is a revision with no descendants. This function finds all heads
    that can be reached by traversing forward from the base revision.

    Args:
        revision_map: Alembic RevisionMap instance.
        base_revision: Starting revision ID.

    Returns:
        List of head revision IDs that descend from base.

    Raises:
        GraphError: If base revision doesn't exist or graph traversal fails.
    """
    logger = get_logger()

    try:
        # Get the base revision script
        revision_map.get_revision(base_revision)
    except Exception as e:
        raise GraphError(
            f"Base revision '{base_revision}' not found in migration graph: {e}"
        )

    logger.debug(f"Finding heads from base: {format_revision_id(base_revision)}")

    # Get all heads in the revision map
    all_heads = revision_map.heads
    logger.debug(f"All heads in graph: {[format_revision_id(h) for h in all_heads]}")

    # Filter heads that descend from base
    descendant_heads = []
    for head in all_heads:
        if is_descendant_of(revision_map, head, base_revision):
            descendant_heads.append(head)

    logger.info(
        f"Found {len(descendant_heads)} head(s) descending from "
        f"{format_revision_id(base_revision)}: "
        f"{[format_revision_id(h) for h in descendant_heads]}"
    )

    return descendant_heads


def is_descendant_of(revision_map: RevisionMap, revision: str, ancestor: str) -> bool:
    """Check if revision is a descendant of ancestor.

    Args:
        revision_map: Alembic RevisionMap instance.
        revision: Revision to check.
        ancestor: Potential ancestor revision.

    Returns:
        True if revision descends from ancestor, False otherwise.
    """
    if revision == ancestor:
        return True

    try:
        # Get all revisions between ancestor and revision (inclusive)
        # iterate_revisions goes backwards from revision to base
        for rev in revision_map.iterate_revisions(
            revision, ancestor, implicit_base=False
        ):
            if rev.revision == ancestor:
                return True
        return False
    except Exception:
        # If iteration fails, they're not related
        return False


def validate_single_base(revision_map: RevisionMap, heads: List[str]) -> None:
    """Validate that all heads share a single common base.

    This ensures that the heads can be safely merged - they must all
    descend from a common ancestor.

    Args:
        revision_map: Alembic RevisionMap instance.
        heads: List of head revision IDs.

    Raises:
        MultipleBasesError: If heads have multiple unrelated bases.
    """
    if len(heads) <= 1:
        return

    logger = get_logger()
    logger.debug("Validating that all heads share a common base")

    # Find common ancestor of all heads
    common_ancestor = None
    for i, head in enumerate(heads):
        if i == 0:
            # Start with first head's ancestors
            common_ancestor = head
        else:
            # Find LCA with next head
            common_ancestor = get_common_ancestor(revision_map, common_ancestor, head)
            if common_ancestor is None:
                raise MultipleBasesError(
                    f"Heads {format_revision_id(heads[0])} and "
                    f"{format_revision_id(head)} have no common ancestor. "
                    "Cannot safely converge unrelated migration branches."
                )

    logger.debug(
        f"All heads share common ancestor: {format_revision_id(common_ancestor)}"
    )


def get_common_ancestor(
    revision_map: RevisionMap, rev1: str, rev2: str
) -> Optional[str]:
    """Find the lowest common ancestor of two revisions.

    Args:
        revision_map: Alembic RevisionMap instance.
        rev1: First revision ID.
        rev2: Second revision ID.

    Returns:
        Common ancestor revision ID, or None if no common ancestor exists.
    """
    # Get all ancestors of rev1
    ancestors1 = set()
    try:
        for rev in revision_map.iterate_revisions(rev1, "base"):
            ancestors1.add(rev.revision)
    except Exception:
        pass

    # Find first ancestor of rev2 that's also an ancestor of rev1
    try:
        for rev in revision_map.iterate_revisions(rev2, "base"):
            if rev.revision in ancestors1:
                return rev.revision
    except Exception:
        pass

    return None


def sort_heads_deterministically(heads: List[str]) -> List[str]:
    """Sort heads deterministically for reproducible convergence.

    Args:
        heads: List of head revision IDs.

    Returns:
        Sorted list of head revision IDs.
    """
    # Sort alphabetically for deterministic behavior
    return sorted(heads)


def get_merge_pairs(heads: List[str]) -> List[Tuple[str, str]]:
    """Generate pairs of heads to merge.

    For efficient convergence, we merge heads pairwise until only one remains.
    This generates the minimal number of merge operations.

    Args:
        heads: List of head revision IDs (should be sorted deterministically).

    Returns:
        List of (head1, head2) tuples to merge.
    """
    if len(heads) <= 1:
        return []

    # Sort for determinism
    sorted_heads = sort_heads_deterministically(heads)

    # For N heads, we need N-1 merges
    # We'll merge pairwise: (h1, h2) -> m1, then (m1, h3) -> m2, etc.
    pairs = []

    # Start with first two heads
    if len(sorted_heads) >= 2:
        pairs.append((sorted_heads[0], sorted_heads[1]))

    return pairs
