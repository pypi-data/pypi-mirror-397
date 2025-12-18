"""Variable and VariableStats: Core data models for codebook entries."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VariableStats:
    """Summary statistics for a variable.
    
    Attributes:
        count: Total number of observations.
        missing: Number of missing values.
        unique: Number of unique values.
        mean: Mean value (numeric variables only).
        std: Standard deviation (numeric variables only).
        min: Minimum value.
        max: Maximum value.
        top_values: Most frequent values with counts (categorical variables).
    
    Example:
        >>> stats = VariableStats(count=1000, missing=50, unique=10)
    """
    
    count: int = 0
    missing: int = 0
    unique: int = 0
    mean: float | None = None
    std: float | None = None
    min: Any = None
    max: Any = None
    top_values: list[tuple[Any, int]] = field(default_factory=list)
    
    @property
    def valid(self) -> int:
        """Number of non-missing observations."""
        return self.count - self.missing
    
    @property
    def missing_pct(self) -> float:
        """Percentage of missing values."""
        if self.count == 0:
            return 0.0
        return (self.missing / self.count) * 100


@dataclass
class Variable:
    """Represents a single variable in the codebook.
    
    Attributes:
        name: The variable name (column name in DataFrame).
        description: Human-readable description of the variable.
        dtype: Data type of the variable.
        values: Value labels for categorical variables (e.g., {1: "Male", 2: "Female"}).
        stats: Computed summary statistics.
        context: Additional contextual notes about the variable.
        missing_codes: Codes that represent missing values.
        suppress_numeric_stats: If True, hide mean/std/min/max in output.
    
    Example:
        >>> var = Variable(
        ...     name="age",
        ...     description="Respondent's age in years",
        ...     dtype="int64"
        ... )
    """
    
    name: str
    description: str = ""
    dtype: str = ""
    values: dict[Any, str] = field(default_factory=dict)
    stats: VariableStats | None = None
    context: str = ""
    missing_codes: list[Any] = field(default_factory=list)
    suppress_numeric_stats: bool = False
    chart_data: list[Any] | None = None  # Raw data for chart generation
    
    def __repr__(self) -> str:
        """Concise representation for debugging."""
        return f"Variable(name={self.name!r}, dtype={self.dtype!r})"
