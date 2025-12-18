"""Custom exceptions for the Braid Formula."""


class BraidFormulaError(Exception):
    """Base exception for all Braid Formula errors."""
    pass


class ValidationError(BraidFormulaError):
    """Raised when input validation fails."""
    pass


class SplitPercentageError(ValidationError):
    """Raised when split percentages don't sum to 100."""
    
    def __init__(self, total: float, expected: float = 100.0):
        self.total = total
        self.expected = expected
        super().__init__(
            f"Split percentages must sum to {expected}%, got {total}%"
        )


class NegativeValueError(ValidationError):
    """Raised when a value that should be non-negative is negative."""
    
    def __init__(self, field: str, value: float):
        self.field = field
        self.value = value
        super().__init__(
            f"{field} cannot be negative, got {value}"
        )


class NoCollaboratorsError(ValidationError):
    """Raised when no collaborators are provided."""
    
    def __init__(self):
        super().__init__("At least one collaborator is required")


class DuplicateCollaboratorError(ValidationError):
    """Raised when collaborator names are not unique."""
    
    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Duplicate collaborator name: '{name}'"
        )
