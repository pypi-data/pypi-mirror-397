"""Data models for the Braid Formula."""

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional


@dataclass
class Collaborator:
    """A person involved in the collaborative project."""
    
    name: str
    split_percent: Decimal
    expenses: Decimal = field(default_factory=lambda: Decimal("0.00"))
    
    def __post_init__(self):
        """Normalize inputs to Decimal with 2 decimal places."""
        if not isinstance(self.split_percent, Decimal):
            self.split_percent = Decimal(str(self.split_percent))
        if not isinstance(self.expenses, Decimal):
            self.expenses = Decimal(str(self.expenses))
        
        # Round to 2 decimal places
        self.expenses = self.expenses.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class CollaboratorResult:
    """Settlement result for a single collaborator."""
    
    name: str
    split_percent: Decimal
    expenses: Decimal
    expense_reimbursement: Decimal
    profit_share: Decimal
    payout: Decimal
    
    def to_dict(self) -> dict:
        """Convert to dictionary with float values for JSON serialization."""
        return {
            "name": self.name,
            "split_percent": float(self.split_percent),
            "expenses": float(self.expenses),
            "expense_reimbursement": float(self.expense_reimbursement),
            "profit_share": float(self.profit_share),
            "payout": float(self.payout),
        }


@dataclass
class SettlementResult:
    """Complete settlement calculation result."""
    
    revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    is_profitable: bool
    collaborators: List[CollaboratorResult]
    rounding_adjustment: Decimal = field(default_factory=lambda: Decimal("0.00"))
    
    def to_dict(self) -> dict:
        """Convert to dictionary with float values for JSON serialization."""
        return {
            "revenue": float(self.revenue),
            "total_expenses": float(self.total_expenses),
            "net_profit": float(self.net_profit),
            "is_profitable": self.is_profitable,
            "rounding_adjustment": float(self.rounding_adjustment),
            "collaborators": [c.to_dict() for c in self.collaborators],
        }
    
    def summary(self) -> str:
        """Human-readable summary of the settlement."""
        lines = [
            "=" * 50,
            "BRAID SETTLEMENT",
            "=" * 50,
            f"Revenue:         ${self.revenue:,.2f}",
            f"Total Expenses:  ${self.total_expenses:,.2f}",
            f"Net Profit:      ${self.net_profit:,.2f}",
            f"Status:          {'PROFIT' if self.is_profitable else 'LOSS'}",
            "-" * 50,
            "PAYOUTS:",
        ]
        
        for c in self.collaborators:
            lines.append(f"  {c.name}:")
            lines.append(f"    Split:        {c.split_percent}%")
            lines.append(f"    Expenses:     ${c.expenses:,.2f}")
            lines.append(f"    Reimbursed:   ${c.expense_reimbursement:,.2f}")
            lines.append(f"    Profit Share: ${c.profit_share:,.2f}")
            lines.append(f"    PAYOUT:       ${c.payout:,.2f}")
        
        if self.rounding_adjustment != Decimal("0.00"):
            lines.append("-" * 50)
            lines.append(f"Rounding Adj:    ${self.rounding_adjustment:,.2f}")
        
        lines.append("=" * 50)
        return "\n".join(lines)
