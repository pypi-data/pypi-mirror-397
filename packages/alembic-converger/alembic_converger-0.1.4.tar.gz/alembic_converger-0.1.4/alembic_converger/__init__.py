"""
Alembic Converger - Safely converge Alembic migration graphs.

This package provides tools to automatically detect and converge multiple Alembic
migration heads by generating minimal merge migrations without schema operations.
"""

__version__ = "0.1.4"

from alembic_converger.converge import converge_migrations
from alembic_converger.errors import (
    ConfigurationError,
    ConvergenceError,
    MultipleBasesError,
    SchemaConflictError,
    ValidationError,
)

__all__ = [
    "__version__",
    "converge_migrations",
    "ConvergenceError",
    "MultipleBasesError",
    "ValidationError",
    "SchemaConflictError",
    "ConfigurationError",
]
