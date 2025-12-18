"""CodebookConfig: Configuration options for codebook generation."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class CodebookConfig:
    """Configuration settings for a codebook.
    
    Attributes:
        title: The title of the codebook (appears on title page and header).
        author: Author name(s) for the codebook.
        date: Date string for the codebook. Defaults to today's date.
        include_toc: Whether to include a table of contents.
        include_title_page: Whether to include a title page.
        include_stats: Whether to include summary statistics for variables.
        include_charts: Whether to include charts (bar charts for categorical,
                        histograms for numeric variables).
    
    Example:
        >>> config = CodebookConfig(
        ...     title="Survey Codebook",
        ...     author="Research Team",
        ...     include_toc=True
        ... )
    """
    
    title: str = "Codebook"
    author: str = ""
    date: str = field(default_factory=lambda: date.today().isoformat())
    include_toc: bool = True
    include_title_page: bool = True
    include_stats: bool = True
    include_charts: bool = True
