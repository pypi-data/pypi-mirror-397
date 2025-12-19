"""
Custom exceptions for the alembic-converger package.

All exceptions inherit from ConvergenceError for easy catching.
"""


class ConvergenceError(Exception):
    """Base exception for all convergence-related errors."""

    pass


class MultipleBasesError(ConvergenceError):
    """Raised when multiple unrelated base revisions are detected.

    This indicates that the migration heads do not share a common ancestor,
    which makes automatic convergence unsafe.
    """

    pass


class ValidationError(ConvergenceError):
    """Raised when migration upgrade validation fails.

    This typically indicates that the merge migration created conflicts
    or that the upgrade path is broken.
    """

    pass


class SchemaConflictError(ConvergenceError):
    """Raised when a merge migration contains schema operations.

    Merge migrations should only contain graph operations (down_revision tuple).
    Schema operations indicate conflicts that require manual resolution.
    """

    pass


class ConfigurationError(ConvergenceError):
    """Raised when Alembic configuration is invalid or cannot be loaded."""

    pass


class GraphError(ConvergenceError):
    """Raised when migration graph analysis fails."""

    pass
