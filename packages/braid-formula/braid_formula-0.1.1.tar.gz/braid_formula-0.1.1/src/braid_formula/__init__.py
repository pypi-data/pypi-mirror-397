"""
Braid Formula - A settlement engine for collaborative projects.

The Braid Formula calculates fair payouts when multiple people collaborate
on a project with shared revenue and individual expenses.

Basic Usage:
    >>> from braid_formula import settle
    >>> result = settle(
    ...     revenue=120.00,
    ...     collaborators=[
    ...         {"name": "J", "split_percent": 50, "expenses": 151.15},
    ...         {"name": "Z", "split_percent": 50, "expenses": 90.49},
    ...     ]
    ... )
    >>> for c in result.collaborators:
    ...     print(f"{c.name}: ${c.payout}")
    J: $90.33
    Z: $29.67

Quick Usage:
    >>> from braid_formula import quick_settle
    >>> quick_settle(
    ...     revenue=120,
    ...     splits={"J": 50, "Z": 50},
    ...     expenses={"J": 151.15, "Z": 90.49}
    ... )
    {'J': 90.33, 'Z': 29.67}
"""

__version__ = "0.1.1"
__author__ = "Afro Panther"
__license__ = "MIT"

from .core import settle, quick_settle, validate_inputs
from .models import Collaborator, CollaboratorResult, SettlementResult
from .exceptions import (
    BraidFormulaError,
    ValidationError,
    SplitPercentageError,
    NegativeValueError,
    NoCollaboratorsError,
    DuplicateCollaboratorError,
)

__all__ = [
    # Main functions
    "settle",
    "quick_settle",
    "validate_inputs",
    # Models
    "Collaborator",
    "CollaboratorResult",
    "SettlementResult",
    # Exceptions
    "BraidFormulaError",
    "ValidationError",
    "SplitPercentageError",
    "NegativeValueError",
    "NoCollaboratorsError",
    "DuplicateCollaboratorError",
]
