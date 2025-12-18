"""
Command-line interface for the Braid Formula.

Usage:
    braid --revenue 120 --collab "J:50:151.15" --collab "Z:50:90.49"
    
    Or interactively:
    braid --interactive
"""

import argparse
import json
import sys
from decimal import Decimal
from typing import List, Tuple

from .core import settle
from .exceptions import BraidFormulaError


def parse_collaborator(collab_str: str) -> dict:
    """
    Parse collaborator string in format: "name:split_percent:expenses"
    
    Examples:
        "J:50:151.15" -> {"name": "J", "split_percent": 50, "expenses": 151.15}
        "J:50" -> {"name": "J", "split_percent": 50, "expenses": 0}
    """
    parts = collab_str.split(":")
    
    if len(parts) < 2:
        raise ValueError(
            f"Invalid collaborator format: '{collab_str}'. "
            "Use 'name:split_percent' or 'name:split_percent:expenses'"
        )
    
    name = parts[0].strip()
    split_percent = float(parts[1])
    expenses = float(parts[2]) if len(parts) > 2 else 0.0
    
    return {
        "name": name,
        "split_percent": split_percent,
        "expenses": expenses,
    }


def interactive_mode() -> Tuple[float, List[dict]]:
    """Run interactive input mode."""
    print("\n🧶 BRAID FORMULA - Interactive Mode\n")
    
    # Get revenue
    while True:
        try:
            revenue = float(input("Enter total revenue: $"))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Get collaborators
    collaborators = []
    print("\nEnter collaborators (empty name to finish):\n")
    
    remaining_split = 100.0
    
    while remaining_split > 0:
        name = input("  Name: ").strip()
        if not name:
            if not collaborators:
                print("  At least one collaborator required.")
                continue
            break
        
        # Check for duplicate
        if any(c["name"] == name for c in collaborators):
            print(f"  '{name}' already added. Use a different name.")
            continue
        
        print(f"  (Remaining split: {remaining_split}%)")
        
        while True:
            try:
                split = float(input(f"  {name}'s split %: "))
                if split < 0:
                    print("  Split cannot be negative.")
                    continue
                if split > remaining_split:
                    print(f"  Split cannot exceed remaining {remaining_split}%.")
                    continue
                break
            except ValueError:
                print("  Please enter a valid number.")
        
        while True:
            try:
                expenses_input = input(f"  {name}'s expenses (0 if none): $")
                expenses = float(expenses_input) if expenses_input else 0.0
                if expenses < 0:
                    print("  Expenses cannot be negative.")
                    continue
                break
            except ValueError:
                print("  Please enter a valid number.")
        
        collaborators.append({
            "name": name,
            "split_percent": split,
            "expenses": expenses,
        })
        
        remaining_split -= split
        print()
    
    return revenue, collaborators


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate settlement for collaborative projects using the Braid Formula.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --revenue 120 --collab "J:50:151.15" --collab "Z:50:90.49"
  %(prog)s -r 1000 -c "Alice:60:500" -c "Bob:40:200"
  %(prog)s --interactive
  %(prog)s -r 500 -c "A:50" -c "B:50" --json
        """,
    )
    
    parser.add_argument(
        "-r", "--revenue",
        type=float,
        help="Total revenue amount",
    )
    
    parser.add_argument(
        "-c", "--collab",
        action="append",
        dest="collaborators",
        metavar="NAME:SPLIT:EXPENSES",
        help="Collaborator in format 'name:split_percent:expenses' (expenses optional)",
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    args = parser.parse_args()
    
    # Determine input mode
    if args.interactive:
        revenue, collaborators = interactive_mode()
    elif args.revenue is not None and args.collaborators:
        revenue = args.revenue
        try:
            collaborators = [parse_collaborator(c) for c in args.collaborators]
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Calculate settlement
    try:
        result = settle(revenue, collaborators)
    except BraidFormulaError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.summary())


if __name__ == "__main__":
    main()
