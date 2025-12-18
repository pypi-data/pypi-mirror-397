"""PDFRenderer: Render codebooks to PDF using fpdf2."""

from pathlib import Path
from typing import TYPE_CHECKING

from fpdf import FPDF

if TYPE_CHECKING:
    from ..bookit import BookIt


class CodebookPDF(FPDF):
    """Custom FPDF subclass with page numbering in footer."""
    
    def footer(self) -> None:
        """Add page number to footer (skip pages 1-2)."""
        if self.page_no() <= 2:
            return  # No page number on title and TOC pages
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


class PDFRenderer:
    """Render a BookIt codebook to PDF format.
    
    Uses fpdf2 for PDF generation with a clean, professional layout.
    
    Attributes:
        book: The BookIt instance to render.
        
    Example:
        >>> renderer = PDFRenderer(book)
        >>> renderer.render("output.pdf")
    """
    
    # Color palette (RGB)
    COLORS = {
        "primary": (41, 65, 114),      # Deep blue
        "secondary": (100, 100, 100),  # Gray
        "accent": (70, 130, 180),      # Steel blue
        "light_bg": (245, 247, 250),   # Light gray-blue
        "border": (200, 200, 200),     # Light gray
    }
    
    def __init__(self, book: "BookIt") -> None:
        """Initialize renderer with a BookIt instance.
        
        Args:
            book: The BookIt codebook to render.
        """
        self.book = book
        self.pdf = CodebookPDF()
        self.pdf.set_auto_page_break(auto=True, margin=20)
        self._setup_fonts()
        self._toc_entries: list[tuple[str, int, str]] = []  # (name, page_num, link)
    
    def _setup_fonts(self) -> None:
        """Configure fonts for the PDF."""
        # Using built-in fonts for simplicity
        self.pdf.set_font("Helvetica", size=10)
    
    def render(self, path: str | Path) -> None:
        """Render the codebook to a PDF file.
        
        Args:
            path: Output file path.
        """
        if self.book.config.include_title_page:
            self._render_title_page()
        
        if self.book.config.include_toc:
            self._render_toc_placeholder()
        
        # Render each variable
        for var in self.book.variables:
            self._render_variable(var)
        
        # Go back and fill in TOC if needed
        if self.book.config.include_toc:
            self._fill_toc()
        
        self.pdf.output(str(path))
    
    def _render_title_page(self) -> None:
        """Render the title page."""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_y(80)
        self.pdf.set_font("Helvetica", "B", 28)
        self.pdf.set_text_color(*self.COLORS["primary"])
        self.pdf.cell(0, 15, self.book.config.title, align="C", ln=True)
        
        # Subtitle line
        self.pdf.set_draw_color(*self.COLORS["accent"])
        self.pdf.set_line_width(0.5)
        self.pdf.line(60, self.pdf.get_y() + 5, 150, self.pdf.get_y() + 5)
        
        # Author
        if self.book.config.author:
            self.pdf.set_y(self.pdf.get_y() + 20)
            self.pdf.set_font("Helvetica", "", 14)
            self.pdf.set_text_color(*self.COLORS["secondary"])
            self.pdf.cell(0, 10, self.book.config.author, align="C", ln=True)
        
        # Date
        self.pdf.set_y(self.pdf.get_y() + 5)
        self.pdf.set_font("Helvetica", "I", 11)
        self.pdf.cell(0, 10, self.book.config.date, align="C", ln=True)
        
        # Variable count
        self.pdf.set_y(self.pdf.get_y() + 30)
        self.pdf.set_font("Helvetica", "", 11)
        var_text = f"{len(self.book.variables)} variables documented"
        self.pdf.cell(0, 10, var_text, align="C", ln=True)
    
    def _render_toc_placeholder(self) -> None:
        """Add a placeholder page for TOC (filled in later)."""
        self.pdf.add_page()
        self._toc_page = self.pdf.page_no()
        
        # Create link target for "Back to TOC"
        self._toc_link = self.pdf.add_link()
        self.pdf.set_link(self._toc_link)
        
        # Title
        self.pdf.set_font("Helvetica", "B", 18)
        self.pdf.set_text_color(*self.COLORS["primary"])
        self.pdf.cell(0, 15, "Table of Contents", ln=True)
        self.pdf.ln(5)
    
    def _fill_toc(self) -> None:
        """Fill in the TOC with collected entries (with clickable links)."""
        if not self._toc_entries:
            return
        
        # Save current page
        current_page = self.pdf.page_no()
        
        # Go to TOC page
        self.pdf.page = self._toc_page
        self.pdf.set_y(35)  # Below "Table of Contents" heading
        
        self.pdf.set_font("Helvetica", "", 10)
        
        for name, page_num, link in self._toc_entries:
            # Variable name (clickable link)
            self.pdf.set_text_color(*self.COLORS["primary"])
            name_width = self.pdf.get_string_width(name)
            self.pdf.cell(name_width + 2, 6, name, link=link)
            
            # Dotted leader line
            page_str = str(page_num)
            page_width = self.pdf.get_string_width(page_str)
            dots_width = 180 - name_width - page_width - 10  # Available space for dots
            if dots_width > 0:
                self.pdf.set_text_color(*self.COLORS["border"])
                # Calculate how many dots fit
                dot_char = "."
                dot_width = self.pdf.get_string_width(dot_char + " ")
                num_dots = int(dots_width / dot_width)
                dots = (dot_char + " ") * num_dots
                self.pdf.cell(dots_width, 6, dots)
            
            # Page number
            self.pdf.set_text_color(*self.COLORS["secondary"])
            self.pdf.cell(0, 6, page_str, align="R", ln=True)
        
        # Restore page
        self.pdf.page = current_page
    
    def _render_variable(self, var: "Variable") -> None:
        """Render a single variable entry."""
        from ..variable import Variable
        
        self.pdf.add_page()
        page_num = self.pdf.page_no()
        
        # Create internal link for TOC
        link = self.pdf.add_link()
        self.pdf.set_link(link)  # Sets link destination to current position
        self._toc_entries.append((var.name, page_num, link))
        
        # "Back to TOC" link in header (right-aligned)
        if hasattr(self, '_toc_link'):
            self.pdf.set_font("Helvetica", "I", 9)
            self.pdf.set_text_color(*self.COLORS["accent"])
            self.pdf.set_xy(self.pdf.w - 35, 10)  # Top right
            self.pdf.cell(25, 5, "< Back to TOC", link=self._toc_link, align="R")
            self.pdf.set_xy(10, 10)  # Reset position
        
        # Variable name header
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.set_text_color(*self.COLORS["primary"])
        self.pdf.cell(0, 10, var.name, ln=True)
        
        # Horizontal line
        self.pdf.set_draw_color(*self.COLORS["accent"])
        self.pdf.set_line_width(0.3)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(5)
        
        # Description
        if var.description:
            self.pdf.set_font("Helvetica", "", 11)
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.multi_cell(0, 6, var.description)
            self.pdf.ln(3)
        
        # Data type
        if var.dtype:
            self._render_field("Type", var.dtype)
        
        # Context notes
        if var.context:
            self.pdf.ln(3)
            self.pdf.set_fill_color(*self.COLORS["light_bg"])
            self.pdf.set_font("Helvetica", "I", 10)
            self.pdf.set_text_color(*self.COLORS["secondary"])
            self.pdf.multi_cell(0, 6, f"Note: {var.context}", fill=True)
            self.pdf.ln(3)
        
        # Statistics
        if var.stats and self.book.config.include_stats:
            self._render_stats(var.stats, var.suppress_numeric_stats)
        
        # Chart placement depends on type:
        # - Histograms: render before value labels
        # - Bar charts: render after value labels
        has_chart = var.chart_data and self.book.config.include_charts
        is_bar_chart = has_chart and self._is_bar_chart_variable(var)
        
        # Histogram goes here (before value labels)
        if has_chart and not is_bar_chart:
            self._render_chart(var)
        
        # Bar chart goes after stats
        if has_chart and is_bar_chart:
            self._render_chart(var)
    
    def _render_field(self, label: str, value: str) -> None:
        """Render a label-value pair."""
        self.pdf.set_font("Helvetica", "B", 10)
        self.pdf.set_text_color(*self.COLORS["secondary"])
        self.pdf.cell(30, 6, f"{label}:")
        
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(0, 6, value, ln=True)
    
    def _render_stats(self, stats: "VariableStats", suppress_numeric: bool = False) -> None:
        """Render statistics section.
        
        Args:
            stats: The VariableStats to render.
            suppress_numeric: If True, hide mean/std/min/max.
        """
        from ..variable import VariableStats
        
        self.pdf.ln(3)
        self.pdf.set_font("Helvetica", "B", 11)
        self.pdf.set_text_color(*self.COLORS["primary"])
        self.pdf.cell(0, 8, "Summary Statistics", ln=True)
        
        # Stats table
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(0, 0, 0)
        
        row_data = [
            ("Count", str(stats.count)),
            ("Valid", str(stats.valid)),
            ("Missing", f"{stats.missing} ({stats.missing_pct:.1f}%)"),
            ("Unique", str(stats.unique)),
        ]
        
        # Only add numeric stats if not suppressed
        if not suppress_numeric:
            if stats.mean is not None:
                row_data.append(("Mean", f"{stats.mean:.2f}"))
            if stats.std is not None:
                row_data.append(("Std Dev", f"{stats.std:.2f}"))
            if stats.min is not None:
                row_data.append(("Min", str(stats.min)))
            if stats.max is not None:
                row_data.append(("Max", str(stats.max)))
        
        # Render as compact grid
        self.pdf.set_fill_color(*self.COLORS["light_bg"])
        for i, (label, value) in enumerate(row_data):
            fill = (i % 2 == 0)
            self.pdf.set_font("Helvetica", "B", 9)
            self.pdf.cell(35, 6, label, fill=fill)
            self.pdf.set_font("Helvetica", "", 9)
            self.pdf.cell(45, 6, value, fill=fill, ln=True)
    
    def _render_value_labels(self, values: dict) -> None:
        """Render value labels section."""
        self.pdf.ln(3)
        self.pdf.set_font("Helvetica", "B", 11)
        self.pdf.set_text_color(*self.COLORS["primary"])
        self.pdf.cell(0, 8, "Value Labels", ln=True)
        
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(0, 0, 0)
        
        for i, (code, label) in enumerate(values.items()):
            fill = (i % 2 == 0)
            self.pdf.set_fill_color(*self.COLORS["light_bg"])
            self.pdf.set_font("Helvetica", "B", 9)
            self.pdf.cell(25, 6, str(code), fill=fill)
            self.pdf.set_font("Helvetica", "", 9)
            self.pdf.cell(0, 6, label, fill=fill, ln=True)
    
    def _is_bar_chart_variable(self, var: "Variable") -> bool:
        """Determine if a variable should use a bar chart (vs histogram).
        
        Returns True for categorical variables, False for numeric.
        """
        from ..variable import Variable
        
        data = var.chart_data
        if not data:
            return False
        
        # Check if data is numeric
        try:
            [float(x) for x in data if x is not None]
            is_numeric = True
        except (ValueError, TypeError):
            is_numeric = False
        
        # Use bar chart if: explicitly suppressed, has value labels, or non-numeric
        return (
            var.suppress_numeric_stats or 
            var.values or
            not is_numeric
        )
    
    def _render_chart(self, var: "Variable") -> None:
        """Render a chart for the variable.
        
        Bar chart for categorical variables, histogram for numeric.
        """
        import io
        import tempfile
        
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        
        from ..variable import Variable
        
        data = var.chart_data
        if not data:
            return
        
        # Check if data is numeric
        try:
            numeric_data = [float(x) for x in data if x is not None]
            is_numeric = len(numeric_data) == len(data) and len(numeric_data) > 0
        except (ValueError, TypeError):
            is_numeric = False
            numeric_data = []
        
        # Use bar chart for categorical, histogram for numeric
        # Categorical if: explicitly suppressed, has value labels, or data is non-numeric
        use_bar_chart = (
            var.suppress_numeric_stats or 
            var.values or  # Has value labels
            not is_numeric  # Non-numeric data (strings, etc.)
        )
        
        # Create figure with styling
        fig, ax = plt.subplots(figsize=(5, 2.5))
        
        # Style settings
        bar_color = '#4682B4'  # Steel blue (matches accent color)
        
        # Common embed width for both chart types
        embed_width = 140  # mm
        
        if use_bar_chart:
            # Bar chart for categorical - only if <= 25 unique values
            from collections import Counter
            counts = Counter(data)
            
            # Skip bar chart if too many unique values
            if len(counts) > 25:
                plt.close(fig)
                return
            
            plt.close(fig)
            
            # Sort by count descending, show all values
            sorted_items = sorted(counts.items(), key=lambda x: -x[1])
            raw_values = [item[0] for item in sorted_items]
            bar_counts = [item[1] for item in sorted_items]
            
            # Create labels in format "value (label)" or just "value"
            labels = []
            for val in raw_values:
                if var.values and val in var.values:
                    label = f"{val} ({var.values[val]})"
                else:
                    label = str(val)
                # Truncate long labels
                if len(label) > 30:
                    label = label[:27] + '...'
                labels.append(label)
            
            # Dynamic figure height based on number of items
            # 0.5 inches per bar ensures readable text at 140mm embed width
            num_bars = len(labels)
            fig_height = max(2, num_bars * 0.5)
            fig, ax = plt.subplots(figsize=(7, fig_height))
            
            bars = ax.barh(range(len(labels)), bar_counts, color=bar_color)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=10)
            ax.invert_yaxis()  # Top to bottom
            ax.set_xlabel('Count', fontsize=10)
            ax.tick_params(axis='both', labelsize=10)
            
            # Add labels at end of bars: n/N (pct%)
            total = sum(bar_counts)
            for bar, count in zip(bars, bar_counts):
                pct = (count / total) * 100 if total > 0 else 0
                label_text = f"{count}/{total} ({pct:.1f}%)"
                ax.text(
                    bar.get_width() + 0.3, 
                    bar.get_y() + bar.get_height() / 2,
                    label_text,
                    va='center', fontsize=9, color='#666666'
                )
        else:
            # Histogram for numeric - fixed size
            plt.close(fig)
            fig, ax = plt.subplots(figsize=(7, 3))  # Same width as bar charts
            
            ax.hist(numeric_data, color=bar_color, edgecolor='white', alpha=0.8)
            ax.set_xlabel('Value', fontsize=11)
            ax.set_ylabel('Count', fontsize=11)
            ax.tick_params(axis='both', labelsize=11)
            # Rotate x-axis labels and right-align to tick marks
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Clean styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Save to temporary file and embed
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            plt.savefig(tmp.name, dpi=200, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            # Add to PDF - same width for both chart types
            self.pdf.ln(5)
            self.pdf.image(tmp.name, x=15, w=embed_width)
            self.pdf.ln(3)
