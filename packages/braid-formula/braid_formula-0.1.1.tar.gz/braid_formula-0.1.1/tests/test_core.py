"""
Comprehensive test suite for the Braid Formula.

Run with: pytest tests/ -v
"""

import pytest
from decimal import Decimal

from braid_formula import (
    settle,
    quick_settle,
    Collaborator,
    SettlementResult,
    ValidationError,
    SplitPercentageError,
    NegativeValueError,
    NoCollaboratorsError,
    DuplicateCollaboratorError,
)


class TestFloralWorkshop:
    """
    The original use case - J's girlfriend's floral workshop.
    
    Real numbers:
    - Revenue: $120.00
    - J's expenses: $151.15
    - Z's expenses: $90.49
    - Split: 50/50
    """
    
    def test_floral_workshop_exact(self):
        """Test the exact floral workshop scenario."""
        result = settle(
            revenue=120.00,
            collaborators=[
                {"name": "J", "split_percent": 50, "expenses": 151.15},
                {"name": "Z", "split_percent": 50, "expenses": 90.49},
            ]
        )
        
        # Verify totals
        assert result.revenue == Decimal("120.00")
        assert result.total_expenses == Decimal("241.64")
        assert result.net_profit == Decimal("-121.64")
        assert result.is_profitable is False
        
        # Find J and Z
        j = next(c for c in result.collaborators if c.name == "J")
        z = next(c for c in result.collaborators if c.name == "Z")
        
        # J paid more, gets more back (but still less than expenses due to loss)
        assert j.payout == Decimal("90.33")
        assert z.payout == Decimal("29.67")
        
        # Payouts must sum to revenue
        assert j.payout + z.payout == Decimal("120.00")
    
    def test_floral_workshop_quick(self):
        """Test using quick_settle helper."""
        payouts = quick_settle(
            revenue=120,
            splits={"J": 50, "Z": 50},
            expenses={"J": 151.15, "Z": 90.49}
        )
        
        assert payouts["J"] == 90.33
        assert payouts["Z"] == 29.67


class TestProfitableScenarios:
    """Test scenarios where the project makes a profit."""
    
    def test_simple_profit_equal_split(self):
        """Two people, equal split, equal expenses, profit."""
        result = settle(
            revenue=1000,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 100},
                {"name": "B", "split_percent": 50, "expenses": 100},
            ]
        )
        
        assert result.is_profitable is True
        assert result.net_profit == Decimal("800.00")
        
        a = result.collaborators[0]
        b = result.collaborators[1]
        
        # Each gets expenses back + half of profit
        assert a.expense_reimbursement == Decimal("100.00")
        assert a.profit_share == Decimal("400.00")
        assert a.payout == Decimal("500.00")
        
        assert b.payout == Decimal("500.00")
    
    def test_profit_unequal_split(self):
        """Unequal split percentages."""
        result = settle(
            revenue=1000,
            collaborators=[
                {"name": "A", "split_percent": 70, "expenses": 100},
                {"name": "B", "split_percent": 30, "expenses": 100},
            ]
        )
        
        a, b = result.collaborators
        
        # Net profit is 800
        # A gets 70% of 800 = 560 + 100 expenses = 660
        # B gets 30% of 800 = 240 + 100 expenses = 340
        assert a.payout == Decimal("660.00")
        assert b.payout == Decimal("340.00")
    
    def test_profit_unequal_expenses(self):
        """Same split but different expenses."""
        result = settle(
            revenue=1000,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 300},
                {"name": "B", "split_percent": 50, "expenses": 100},
            ]
        )
        
        a, b = result.collaborators
        
        # Net profit is 600
        # Each gets 50% of 600 = 300
        # A gets 300 + 300 = 600
        # B gets 100 + 300 = 400
        assert a.payout == Decimal("600.00")
        assert b.payout == Decimal("400.00")
    
    def test_no_expenses(self):
        """All profit, no expenses."""
        result = settle(
            revenue=1000,
            collaborators=[
                {"name": "A", "split_percent": 50},
                {"name": "B", "split_percent": 50},
            ]
        )
        
        assert result.total_expenses == Decimal("0.00")
        assert result.net_profit == Decimal("1000.00")
        
        for c in result.collaborators:
            assert c.payout == Decimal("500.00")


class TestLossScenarios:
    """Test scenarios where the project loses money."""
    
    def test_simple_loss(self):
        """Basic loss scenario."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 100},
                {"name": "B", "split_percent": 50, "expenses": 100},
            ]
        )
        
        assert result.is_profitable is False
        assert result.net_profit == Decimal("-100.00")
        
        # Each takes 50% of the loss
        for c in result.collaborators:
            # Expenses - (loss share) = 100 - 50 = 50
            assert c.payout == Decimal("50.00")
    
    def test_total_loss(self):
        """Revenue is zero."""
        result = settle(
            revenue=0,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 100},
                {"name": "B", "split_percent": 50, "expenses": 100},
            ]
        )
        
        assert result.revenue == Decimal("0.00")
        
        # All payouts should be zero (can't pay from nothing)
        for c in result.collaborators:
            assert c.payout == Decimal("0.00")
    
    def test_negative_payout_scenario(self):
        """
        Scenario where one person's share of loss exceeds their expenses.
        
        Example: A spent $10, B spent $190. Revenue $100. 50/50 split.
        Loss = $100. Each owes $50.
        A: $10 expense - $50 loss share = -$40 (owes money)
        B: $190 expense - $50 loss share = $140
        """
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 10},
                {"name": "B", "split_percent": 50, "expenses": 190},
            ]
        )
        
        a, b = result.collaborators
        
        # A's payout would be negative (they owe B)
        assert a.payout == Decimal("-40.00")
        assert b.payout == Decimal("140.00")
        
        # Still sums to revenue
        assert a.payout + b.payout == Decimal("100.00")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_collaborator(self):
        """One person gets everything."""
        result = settle(
            revenue=1000,
            collaborators=[
                {"name": "Solo", "split_percent": 100, "expenses": 200},
            ]
        )
        
        assert len(result.collaborators) == 1
        assert result.collaborators[0].payout == Decimal("1000.00")
    
    def test_many_collaborators(self):
        """Many collaborators with small splits."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": f"Person{i}", "split_percent": 10, "expenses": 0}
                for i in range(10)
            ]
        )
        
        for c in result.collaborators:
            assert c.payout == Decimal("10.00")
    
    def test_fractional_splits(self):
        """Non-integer split percentages."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": 33.33, "expenses": 0},
                {"name": "B", "split_percent": 33.33, "expenses": 0},
                {"name": "C", "split_percent": 33.34, "expenses": 0},
            ]
        )
        
        total = sum(c.payout for c in result.collaborators)
        assert total == Decimal("100.00")
    
    def test_very_small_amounts(self):
        """Very small revenue and expenses."""
        result = settle(
            revenue=0.03,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 0.01},
                {"name": "B", "split_percent": 50, "expenses": 0.01},
            ]
        )
        
        # Net profit = 0.01, split = 0.005 each
        total = sum(c.payout for c in result.collaborators)
        assert total == Decimal("0.03")
    
    def test_very_large_amounts(self):
        """Large amounts (millions)."""
        result = settle(
            revenue=10_000_000,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 1_000_000},
                {"name": "B", "split_percent": 50, "expenses": 2_000_000},
            ]
        )
        
        assert result.net_profit == Decimal("7000000.00")
        
        a, b = result.collaborators
        assert a.payout == Decimal("4500000.00")
        assert b.payout == Decimal("5500000.00")
    
    def test_exact_breakeven(self):
        """Revenue exactly equals expenses."""
        result = settle(
            revenue=200,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 100},
                {"name": "B", "split_percent": 50, "expenses": 100},
            ]
        )
        
        assert result.net_profit == Decimal("0.00")
        assert result.is_profitable is True  # Zero profit is not a loss
        
        # Each gets exactly their expenses back
        for c in result.collaborators:
            assert c.payout == Decimal("100.00")


class TestValidation:
    """Test input validation."""
    
    def test_no_collaborators(self):
        """Must have at least one collaborator."""
        with pytest.raises(NoCollaboratorsError):
            settle(revenue=100, collaborators=[])
    
    def test_splits_under_100(self):
        """Split percentages must sum to 100."""
        with pytest.raises(SplitPercentageError) as exc:
            settle(
                revenue=100,
                collaborators=[
                    {"name": "A", "split_percent": 40, "expenses": 0},
                    {"name": "B", "split_percent": 40, "expenses": 0},
                ]
            )
        assert exc.value.total == 80.0
    
    def test_splits_over_100(self):
        """Split percentages must sum to 100."""
        with pytest.raises(SplitPercentageError):
            settle(
                revenue=100,
                collaborators=[
                    {"name": "A", "split_percent": 60, "expenses": 0},
                    {"name": "B", "split_percent": 60, "expenses": 0},
                ]
            )
    
    def test_negative_revenue(self):
        """Revenue cannot be negative by default."""
        with pytest.raises(NegativeValueError):
            settle(
                revenue=-100,
                collaborators=[
                    {"name": "A", "split_percent": 100, "expenses": 0},
                ]
            )
    
    def test_negative_revenue_allowed(self):
        """Negative revenue allowed when flag is set (refunds)."""
        result = settle(
            revenue=-100,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 50},
                {"name": "B", "split_percent": 50, "expenses": 50},
            ],
            allow_negative_revenue=True,
        )
        
        assert result.revenue == Decimal("-100.00")
    
    def test_negative_expenses(self):
        """Expenses cannot be negative."""
        with pytest.raises(NegativeValueError):
            settle(
                revenue=100,
                collaborators=[
                    {"name": "A", "split_percent": 100, "expenses": -50},
                ]
            )
    
    def test_negative_split(self):
        """Split percentage cannot be negative."""
        with pytest.raises(NegativeValueError):
            settle(
                revenue=100,
                collaborators=[
                    {"name": "A", "split_percent": 120, "expenses": 0},
                    {"name": "B", "split_percent": -20, "expenses": 0},
                ]
            )
    
    def test_duplicate_names(self):
        """Collaborator names must be unique."""
        with pytest.raises(DuplicateCollaboratorError):
            settle(
                revenue=100,
                collaborators=[
                    {"name": "A", "split_percent": 50, "expenses": 0},
                    {"name": "A", "split_percent": 50, "expenses": 0},
                ]
            )


class TestInputFormats:
    """Test various input formats."""
    
    def test_collaborator_objects(self):
        """Using Collaborator objects directly."""
        result = settle(
            revenue=100,
            collaborators=[
                Collaborator(name="A", split_percent=Decimal("50"), expenses=Decimal("10")),
                Collaborator(name="B", split_percent=Decimal("50"), expenses=Decimal("10")),
            ]
        )
        
        assert result.revenue == Decimal("100.00")
    
    def test_string_numbers(self):
        """Numbers as strings should work."""
        result = settle(
            revenue="100.00",
            collaborators=[
                {"name": "A", "split_percent": "50", "expenses": "10"},
                {"name": "B", "split_percent": "50", "expenses": "10"},
            ]
        )
        
        assert result.revenue == Decimal("100.00")
    
    def test_integer_inputs(self):
        """Integer inputs should work."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 10},
                {"name": "B", "split_percent": 50, "expenses": 10},
            ]
        )
        
        assert result.revenue == Decimal("100.00")
    
    def test_mixed_inputs(self):
        """Mixed input types should work."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split": 50, "expenses": 10},  # 'split' alias
                {"name": "B", "split_percent": "50", "expenses": Decimal("10")},
            ]
        )
        
        assert len(result.collaborators) == 2


class TestOutputFormats:
    """Test output formatting."""
    
    def test_to_dict(self):
        """Test JSON-serializable output."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 10},
                {"name": "B", "split_percent": 50, "expenses": 10},
            ]
        )
        
        d = result.to_dict()
        
        assert isinstance(d["revenue"], float)
        assert isinstance(d["collaborators"], list)
        assert isinstance(d["collaborators"][0]["payout"], float)
    
    def test_summary(self):
        """Test human-readable summary."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": 50, "expenses": 10},
                {"name": "B", "split_percent": 50, "expenses": 10},
            ]
        )
        
        summary = result.summary()
        
        assert "BRAID SETTLEMENT" in summary
        assert "Revenue:" in summary
        assert "$100.00" in summary


class TestRoundingConsistency:
    """Ensure payouts always sum to revenue exactly."""
    
    def test_rounding_three_way_split(self):
        """Three-way split with rounding issues."""
        result = settle(
            revenue=100,
            collaborators=[
                {"name": "A", "split_percent": Decimal("33.33"), "expenses": 0},
                {"name": "B", "split_percent": Decimal("33.33"), "expenses": 0},
                {"name": "C", "split_percent": Decimal("33.34"), "expenses": 0},
            ]
        )
        
        total = sum(c.payout for c in result.collaborators)
        assert total == Decimal("100.00")
    
    def test_rounding_complex_scenario(self):
        """Complex scenario with many decimal places."""
        result = settle(
            revenue=99.99,
            collaborators=[
                {"name": "A", "split_percent": 33.33, "expenses": 11.11},
                {"name": "B", "split_percent": 33.33, "expenses": 22.22},
                {"name": "C", "split_percent": 33.34, "expenses": 33.33},
            ]
        )
        
        total = sum(c.payout for c in result.collaborators)
        assert total == Decimal("99.99")
