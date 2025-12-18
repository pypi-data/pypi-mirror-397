"""Statistics computation for DataFrames (polars and pandas)."""

from typing import Any

from .variable import VariableStats


def compute_stats(data: Any) -> VariableStats:
    """Compute summary statistics from data.
    
    Supports polars Series, pandas Series, list, tuple, and numpy array.
    Automatically detects the type and dispatches to the appropriate implementation.
    
    Args:
        data: A polars Series, pandas Series, list, tuple, or numpy array.
        
    Returns:
        VariableStats with computed statistics.
        
    Example:
        >>> import polars as pl
        >>> s = pl.Series("age", [25, 30, 35, None, 40])
        >>> stats = compute_stats(s)
        >>> stats.count
        5
        >>> stats.missing
        1
        
        >>> # Also works with plain lists
        >>> stats = compute_stats([1, 2, 3, None, 5])
    """
    # Detect data type by module name (duck typing)
    module = type(data).__module__
    type_name = type(data).__name__
    
    if module.startswith("polars"):
        return _compute_stats_polars(data)
    elif module.startswith("pandas"):
        return _compute_stats_pandas(data)
    elif module.startswith("numpy") or type_name == "ndarray":
        return _compute_stats_sequence(data, from_numpy=True)
    elif isinstance(data, (list, tuple)):
        return _compute_stats_sequence(data, from_numpy=False)
    else:
        raise TypeError(
            f"Unsupported data type: {type(data)}. "
            "Expected polars.Series, pandas.Series, list, tuple, or numpy.ndarray."
        )


def _compute_stats_polars(series: Any) -> VariableStats:
    """Compute statistics for a polars Series."""
    import polars as pl
    
    count = len(series)
    missing = series.null_count()
    unique = series.n_unique()
    
    # Initialize stats
    stats = VariableStats(
        count=count,
        missing=missing,
        unique=unique,
    )
    
    # Numeric statistics
    if series.dtype.is_numeric():
        stats.mean = series.mean()
        stats.std = series.std()
        stats.min = series.min()
        stats.max = series.max()
    else:
        # For non-numeric, still get min/max if orderable
        try:
            stats.min = series.min()
            stats.max = series.max()
        except Exception:
            pass
    
    # Top values for categorical-like columns
    if unique <= 20 or not series.dtype.is_numeric():
        value_counts = series.drop_nulls().value_counts().sort("count", descending=True)
        top_n = min(10, len(value_counts))
        if top_n > 0:
            # Get column names - polars value_counts returns the series name as first column
            col_name = series.name if series.name else "value"
            stats.top_values = [
                (row[col_name], row["count"])
                for row in value_counts.iter_rows(named=True)
            ]
    
    return stats


def _compute_stats_pandas(series: Any) -> VariableStats:
    """Compute statistics for a pandas Series."""
    import pandas as pd
    import numpy as np
    
    count = len(series)
    missing = int(series.isna().sum())
    unique = series.nunique(dropna=True)
    
    stats = VariableStats(
        count=count,
        missing=missing,
        unique=unique,
    )
    
    # Numeric statistics
    if pd.api.types.is_numeric_dtype(series):
        stats.mean = float(series.mean()) if not pd.isna(series.mean()) else None
        stats.std = float(series.std()) if not pd.isna(series.std()) else None
        stats.min = series.min() if not pd.isna(series.min()) else None
        stats.max = series.max() if not pd.isna(series.max()) else None
    else:
        # For non-numeric, try to get min/max
        try:
            stats.min = series.min()
            stats.max = series.max()
        except Exception:
            pass
    
    # Top values for categorical-like columns
    if unique <= 20 or not pd.api.types.is_numeric_dtype(series):
        value_counts = series.dropna().value_counts().head(10)
        stats.top_values = list(value_counts.items())
    
    return stats


def get_dtype_string(data: Any) -> str:
    """Get a human-readable dtype string from data.
    
    Args:
        data: A polars Series, pandas Series, list, tuple, or numpy array.
        
    Returns:
        Human-readable data type string.
    """
    module = type(data).__module__
    type_name = type(data).__name__
    
    if module.startswith("polars"):
        return str(data.dtype)
    elif module.startswith("pandas"):
        return str(data.dtype)
    elif module.startswith("numpy") or type_name == "ndarray":
        return str(data.dtype)
    elif isinstance(data, (list, tuple)):
        # Infer type from first non-None element
        for item in data:
            if item is not None:
                return type(item).__name__
        return "unknown"
    else:
        return "unknown"


def _compute_stats_sequence(data: Any, from_numpy: bool = False) -> VariableStats:
    """Compute statistics for a list, tuple, or numpy array.
    
    Converts to polars Series internally for consistent stats computation.
    """
    import polars as pl
    
    # Convert to polars Series for consistent handling
    series = pl.Series("data", list(data))
    return _compute_stats_polars(series)
