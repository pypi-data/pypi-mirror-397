# Braid Formula

**A settlement engine for collaborative projects.**

[![PyPI version](https://badge.fury.io/py/braid-formula.svg)](https://pypi.org/project/braid-formula/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## What is this?

When people collaborate on a project—a workshop, an event, a pop-up—someone has to figure out who gets paid what. It's not just "split the revenue." Real collaborations involve:

- Different expense amounts per person
- Different profit-sharing percentages
- The need to reimburse everyone for what they spent
- Handling losses fairly when things don't go as planned

**The Braid Formula handles all of this.**

---

## Installation

```bash
pip install braid-formula
```

---

## Quick Start

```python
from braid_formula import settle

result = settle(
    revenue=120.00,
    collaborators=[
        {"name": "J", "split_percent": 50, "expenses": 151.15},
        {"name": "Z", "split_percent": 50, "expenses": 90.49},
    ]
)

for c in result.collaborators:
    print(f"{c.name} gets ${c.payout}")

# Output:
# J gets $90.33
# Z gets $29.67
```

Even simpler:

```python
from braid_formula import quick_settle

payouts = quick_settle(
    revenue=120,
    splits={"J": 50, "Z": 50},
    expenses={"J": 151.15, "Z": 90.49}
)

print(payouts)
# {'J': 90.33, 'Z': 29.67}
```

---

## The Math

The Braid Formula calculates fair settlements in three steps:

### Step 1: Calculate Net Profit (or Loss)

```
Net Profit = Revenue - Total Expenses
```

### Step 2: Calculate Each Person's Profit Share

```
Profit Share = Net Profit × (Split % / 100)
```

### Step 3: Calculate Payout

```
Payout = Expenses + Profit Share
```

That's it. Everyone gets reimbursed for what they spent, then profit (or loss) is split according to the agreed percentages.

---

## Real Example: The Floral Workshop

J and Z run a floral arrangement workshop together:

| Person | Split | Expenses |
|--------|-------|----------|
| J | 50% | $151.15 |
| Z | 50% | $90.49 |

They collect **$120** in revenue.

**Step 1: Net Profit**
```
Total Expenses = $151.15 + $90.49 = $241.64
Net Profit = $120 - $241.64 = -$121.64 (a loss)
```

**Step 2: Profit Share (Loss Share)**
```
J's share = -$121.64 × 0.50 = -$60.82
Z's share = -$121.64 × 0.50 = -$60.82
```

**Step 3: Payouts**
```
J's payout = $151.15 + (-$60.82) = $90.33
Z's payout = $90.49 + (-$60.82) = $29.67
```

**Result:** J gets $90.33, Z gets $29.67. The $120 revenue is distributed, and the loss is shared equally.

---

## Command Line Usage

```bash
# Simple calculation
braid --revenue 120 --collab "J:50:151.15" --collab "Z:50:90.49"

# Interactive mode
braid --interactive

# JSON output
braid -r 1000 -c "Alice:60:500" -c "Bob:40:200" --json
```

---

## API Reference

### `settle(revenue, collaborators, ...)`

The main settlement function.

**Parameters:**
- `revenue` (number): Total revenue from the project
- `collaborators` (list): List of collaborators, each with:
  - `name` (str): Person's name
  - `split_percent` (number): Their percentage share (must sum to 100)
  - `expenses` (number, optional): What they spent (default 0)
- `allow_negative_revenue` (bool): Allow refund scenarios (default False)
- `validate` (bool): Validate inputs (default True)

**Returns:** `SettlementResult` with:
- `revenue`: Total revenue
- `total_expenses`: Sum of all expenses
- `net_profit`: Revenue minus expenses
- `is_profitable`: True if net_profit >= 0
- `collaborators`: List of `CollaboratorResult` objects

### `quick_settle(revenue, splits, expenses)`

Simplified interface returning just the payouts.

```python
quick_settle(
    revenue=1000,
    splits={"Alice": 60, "Bob": 40},
    expenses={"Alice": 200, "Bob": 100}
)
# Returns: {'Alice': 620.0, 'Bob': 380.0}
```

---

## Handling Edge Cases

### Negative Payouts

If someone's share of the loss exceeds their expenses, they'll have a negative payout—meaning they owe money to the other collaborators.

```python
result = settle(
    revenue=100,
    collaborators=[
        {"name": "A", "split_percent": 50, "expenses": 10},
        {"name": "B", "split_percent": 50, "expenses": 190},
    ]
)
# A's payout: -$40 (owes $40)
# B's payout: $140
```

### Zero Revenue

```python
result = settle(
    revenue=0,
    collaborators=[
        {"name": "A", "split_percent": 50, "expenses": 100},
        {"name": "B", "split_percent": 50, "expenses": 100},
    ]
)
# Both get $0 (nothing to distribute)
```

### Unequal Splits

```python
result = settle(
    revenue=1000,
    collaborators=[
        {"name": "Lead", "split_percent": 70, "expenses": 200},
        {"name": "Support", "split_percent": 30, "expenses": 100},
    ]
)
# Net profit: $700
# Lead: $200 + ($700 × 0.70) = $690
# Support: $100 + ($700 × 0.30) = $310
```

---

## Validation

The formula validates inputs and raises descriptive errors:

```python
from braid_formula import settle, SplitPercentageError

try:
    settle(revenue=100, collaborators=[
        {"name": "A", "split_percent": 60},
        {"name": "B", "split_percent": 60},  # Total 120%!
    ])
except SplitPercentageError as e:
    print(e)  # "Split percentages must sum to 100%, got 120%"
```

**Validation checks:**
- At least one collaborator required
- Split percentages must sum to exactly 100
- Revenue cannot be negative (unless `allow_negative_revenue=True`)
- Expenses cannot be negative
- Collaborator names must be unique

---

## Why "Braid"?

Like threads woven together, collaborations intertwine different contributions—time, money, skills—into something greater. The Braid Formula weaves these together into fair settlements.

---

## Why Open Source?

The formula is transparent and auditable. Anyone can verify the math. Trust is built into the code.

The formula is free. **Braid** (the app) is for people who don't want to run Python scripts after a pottery class.

---

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Run `pytest tests/` to verify
5. Submit a PR

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Credits

Created by [The Bloc Foundation](https://theblocfoundation.org).

Part of the **Braid** ecosystem for collaborative economics.
