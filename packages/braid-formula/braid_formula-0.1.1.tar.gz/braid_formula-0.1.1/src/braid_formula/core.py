"""
Core settlement formula for collaborative projects.

THE BRAID FORMULA
=================

Given:
- Revenue (R): Total money coming in
- Collaborators: Each with split_percent (S%) and expenses (E)

The formula calculates fair settlements by:
1. Summing all expenses: Total_E = sum of all E
2. Calculating net profit: P = R - Total_E
3. For each collaborator:
   - Profit share = P × (S% / 100)
   - Payout = Expenses + Profit share
   
This ensures:
- Everyone gets reimbursed for their expenses FIRST
- Remaining profit (or loss) is split according to percentages
- In loss scenarios, those who spent more take larger hits proportionally
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Union, Dict, Any

from .models import Collaborator, CollaboratorResult, SettlementResult
from .exceptions import (
    ValidationError,
    SplitPercentageError,
    NegativeValueError,
    NoCollaboratorsError,
    DuplicateCollaboratorError,
)


def _to_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
    """Convert a value to Decimal with proper precision."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _round_currency(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_inputs(
    revenue: Decimal,
    collaborators: List[Collaborator],
    allow_negative_revenue: bool = False,
) -> None:
    """
    Validate all inputs before calculation.
    
    Args:
        revenue: Total revenue
        collaborators: List of collaborators
        allow_negative_revenue: If True, allows negative revenue (for refund scenarios)
    
    Raises:
        ValidationError: If any validation fails
    """
    # Check for collaborators
    if not collaborators:
        raise NoCollaboratorsError()
    
    # Check revenue
    if not allow_negative_revenue and revenue < 0:
        raise NegativeValueError("revenue", float(revenue))
    
    # Check for duplicate names
    names = [c.name for c in collaborators]
    seen = set()
    for name in names:
        if name in seen:
            raise DuplicateCollaboratorError(name)
        seen.add(name)
    
    # Check split percentages sum to 100
    total_split = sum(c.split_percent for c in collaborators)
    if total_split != Decimal("100"):
        raise SplitPercentageError(float(total_split))
    
    # Check individual values
    for c in collaborators:
        if c.split_percent < 0:
            raise NegativeValueError(f"{c.name}'s split_percent", float(c.split_percent))
        if c.expenses < 0:
            raise NegativeValueError(f"{c.name}'s expenses", float(c.expenses))


def settle(
    revenue: Union[int, float, str, Decimal],
    collaborators: Union[List[Collaborator], List[Dict[str, Any]]],
    allow_negative_revenue: bool = False,
    validate: bool = True,
) -> SettlementResult:
    """
    Calculate settlement for a collaborative project.
    
    This is the main entry point for the Braid Formula.
    
    Args:
        revenue: Total revenue from the project
        collaborators: List of Collaborator objects or dicts with keys:
            - name: str
            - split_percent: number (must sum to 100 across all collaborators)
            - expenses: number (optional, defaults to 0)
        allow_negative_revenue: Allow negative revenue for refund scenarios
        validate: Whether to validate inputs (disable for performance if pre-validated)
    
    Returns:
        SettlementResult containing the complete breakdown
    
    Raises:
        ValidationError: If inputs are invalid
    
    Example:
        >>> result = settle(
        ...     revenue=120.00,
        ...     collaborators=[
        ...         {"name": "J", "split_percent": 50, "expenses": 151.15},
        ...         {"name": "Z", "split_percent": 50, "expenses": 90.49},
        ...     ]
        ... )
        >>> print(result.collaborators[0].payout)
        90.33
    """
    # Convert revenue to Decimal
    revenue_dec = _to_decimal(revenue)
    
    # Convert collaborator dicts to Collaborator objects
    collab_objects: List[Collaborator] = []
    for c in collaborators:
        if isinstance(c, Collaborator):
            collab_objects.append(c)
        elif isinstance(c, dict):
            collab_objects.append(Collaborator(
                name=c["name"],
                split_percent=_to_decimal(c.get("split_percent", c.get("split", 0))),
                expenses=_to_decimal(c.get("expenses", 0)),
            ))
        else:
            raise ValidationError(f"Invalid collaborator type: {type(c)}")
    
    # Validate if requested
    if validate:
        validate_inputs(revenue_dec, collab_objects, allow_negative_revenue)
    
    # Calculate totals
    total_expenses = sum(c.expenses for c in collab_objects)
    net_profit = revenue_dec - total_expenses
    is_profitable = net_profit >= 0
    
    # Calculate each collaborator's settlement
    results: List[CollaboratorResult] = []
    running_total = Decimal("0.00")
    
    for i, c in enumerate(collab_objects):
        # Calculate profit share (can be negative if loss)
        profit_share = _round_currency(net_profit * (c.split_percent / Decimal("100")))
        
        # Payout = expenses reimbursed + profit share
        payout = _round_currency(c.expenses + profit_share)
        
        results.append(CollaboratorResult(
            name=c.name,
            split_percent=c.split_percent,
            expenses=c.expenses,
            expense_reimbursement=c.expenses,
            profit_share=profit_share,
            payout=payout,
        ))
        
        running_total += payout
    
    # Handle rounding adjustments to ensure payouts sum to revenue exactly
    rounding_adjustment = Decimal("0.00")
    expected_total = revenue_dec
    
    if running_total != expected_total:
        rounding_adjustment = expected_total - running_total
        # Apply adjustment to the last collaborator
        if results:
            last = results[-1]
            adjusted_payout = last.payout + rounding_adjustment
            results[-1] = CollaboratorResult(
                name=last.name,
                split_percent=last.split_percent,
                expenses=last.expenses,
                expense_reimbursement=last.expense_reimbursement,
                profit_share=last.profit_share + rounding_adjustment,
                payout=adjusted_payout,
            )
    
    return SettlementResult(
        revenue=_round_currency(revenue_dec),
        total_expenses=_round_currency(total_expenses),
        net_profit=_round_currency(net_profit),
        is_profitable=is_profitable,
        collaborators=results,
        rounding_adjustment=rounding_adjustment,
    )


def quick_settle(
    revenue: Union[int, float],
    splits: Dict[str, float],
    expenses: Dict[str, float] = None,
) -> Dict[str, float]:
    """
    Simplified interface for quick calculations.
    
    Args:
        revenue: Total revenue
        splits: Dict mapping name to split percentage (must sum to 100)
        expenses: Dict mapping name to expenses (optional)
    
    Returns:
        Dict mapping name to payout amount
    
    Example:
        >>> quick_settle(
        ...     revenue=120,
        ...     splits={"J": 50, "Z": 50},
        ...     expenses={"J": 151.15, "Z": 90.49}
        ... )
        {'J': 90.33, 'Z': 29.67}
    """
    expenses = expenses or {}
    
    collaborators = [
        {"name": name, "split_percent": split, "expenses": expenses.get(name, 0)}
        for name, split in splits.items()
    ]
    
    result = settle(revenue, collaborators)
    
    return {c.name: float(c.payout) for c in result.collaborators}
