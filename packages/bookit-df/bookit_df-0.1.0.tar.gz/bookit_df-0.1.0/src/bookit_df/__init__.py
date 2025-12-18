"""BookIt: A codebook creation package for DataFrames.

BookIt helps you create professional PDF codebooks documenting the variables
in your polars or pandas DataFrames.

Example:
    >>> import polars as pl
    >>> from bookit_df import BookIt
    >>>
    >>> df = pl.read_csv("data.csv")
    >>> with BookIt("My Codebook", output="codebook.pdf") as book:
    ...     book.from_dataframe(df)
    # Codebook saved automatically!
"""

from .bookit import BookIt
from .config import CodebookConfig
from .variable import Variable, VariableStats

__all__ = [
    "BookIt",
    "CodebookConfig",
    "Variable",
    "VariableStats",
]

__version__ = "0.1.0"
