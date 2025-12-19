"""
Configuration for adaptive image sizing.

This module provides configuration dataclasses and dimension calculation utilities
for generating optimally-sized images (charts, diagrams, tables) and their
integration into PDF documents.
"""

import re
from dataclasses import dataclass


@dataclass
class ImageSizingConfig:
    """Configuration for adaptive image sizing.

    This dataclass defines all default dimensions and constraints for:
    - Chart image generation
    - Mermaid diagram generation
    - Table image generation
    - PDF embedding constraints

    Attributes:
        chart_min_width: Minimum width for chart images (default: 1200px)
        chart_min_height: Minimum height for chart images (default: 900px)
        chart_width_per_datapoint: Additional width per data point beyond 10 (default: 80px)
        mermaid_base_width: Base width for Mermaid diagrams (default: 1200px)
        mermaid_base_height: Base height for Mermaid diagrams (default: 800px)
        mermaid_width_per_node: Additional width per node beyond 15 (default: 50px)
        mermaid_height_per_node: Additional height per node beyond 15 (default: 40px)
        table_min_width: Minimum width for table images (default: 800px)
        table_width_per_column: Width allocated per column (default: 150px)
        table_min_width_many_columns: Minimum width for tables with >5 columns (default: 1200px)
        absolute_min_width: Absolute minimum width for any image (default: 600px)
        absolute_min_height: Absolute minimum height for any image (default: 400px)
        pdf_page_width_px: PDF page width in pixels at 96 DPI (default: 793px for A4)
        pdf_page_height_px: PDF page height in pixels at 96 DPI (default: 1122px for A4 minus margins)
        pdf_max_image_dimension: Maximum dimension before downsampling (default: 4000px)
        pdf_min_dpi: Minimum DPI for print quality (default: 150)
        min_readable_width: Minimum width for readable images (default: 400px)
        min_readable_height: Minimum height for readable images (default: 300px)
    """

    # Chart defaults
    chart_min_width: int = 1200
    chart_min_height: int = 900
    chart_width_per_datapoint: int = 80  # Additional width per data point > 10

    # Mermaid defaults
    mermaid_base_width: int = 1200
    mermaid_base_height: int = 800
    mermaid_width_per_node: int = 50  # Additional width per node > 15
    mermaid_height_per_node: int = 40  # Additional height per node > 15

    # Table defaults
    table_min_width: int = 800
    table_width_per_column: int = 150
    table_min_width_many_columns: int = 1200  # For > 5 columns

    # Absolute minimums
    absolute_min_width: int = 600
    absolute_min_height: int = 400

    # PDF constraints
    pdf_page_width_px: int = 793  # A4 at 96 DPI minus margins
    pdf_page_height_px: int = 1122  # A4 at 96 DPI minus 2cm margins
    pdf_max_image_dimension: int = 4000
    pdf_min_dpi: int = 150

    # Minimum readable dimensions
    min_readable_width: int = 400
    min_readable_height: int = 300


class ImageDimensionCalculator:
    """Calculates optimal image dimensions based on content.

    This class provides methods to calculate appropriate dimensions for
    different types of generated images (charts, Mermaid diagrams, tables)
    based on their content complexity.

    Example:
        calculator = ImageDimensionCalculator()

        # Calculate chart dimensions for 15 data points
        width, height = calculator.calculate_chart_dimensions(data_point_count=15)

        # Calculate Mermaid dimensions from diagram code
        width, height = calculator.calculate_mermaid_dimensions(mermaid_code)

        # Calculate table dimensions for 8 columns
        width, height = calculator.calculate_table_dimensions(column_count=8, row_count=10)
    """

    def __init__(self, config: ImageSizingConfig | None = None):
        """Initialize the calculator with optional custom configuration.

        Args:
            config: Custom sizing configuration. If None, uses defaults.
        """
        self.config = config or ImageSizingConfig()

    def _apply_minimums_with_aspect_ratio(
        self,
        width: int,
        height: int,
        min_width: int,
        min_height: int,
    ) -> tuple[int, int]:
        """Apply minimum dimensions while preserving aspect ratio.

        If either dimension is below the minimum, scale up both dimensions
        proportionally to meet the minimum while preserving the original
        aspect ratio.

        Args:
            width: Current width
            height: Current height
            min_width: Minimum required width
            min_height: Minimum required height

        Returns:
            Tuple of (width, height) that meets minimums while preserving ratio
        """
        if width <= 0 or height <= 0:
            return (min_width, min_height)

        # Calculate scale factors needed to meet each minimum
        width_scale = min_width / width if width < min_width else 1.0
        height_scale = min_height / height if height < min_height else 1.0

        # Use the larger scale factor to ensure both minimums are met
        scale = max(width_scale, height_scale)

        if scale > 1.0:
            # Scale up both dimensions proportionally
            new_width = int(width * scale)
            new_height = int(height * scale)
            return (new_width, new_height)

        return (width, height)

    def calculate_chart_dimensions(
        self,
        data_point_count: int,
        requested_width: int | None = None,
        requested_height: int | None = None,
    ) -> tuple[int, int]:
        """Calculate optimal chart dimensions based on data complexity.

        For charts with more than 10 data points, the width is automatically
        increased to accommodate labels without overlap. If user-requested
        dimensions are provided, they are scaled up proportionally to meet
        minimum requirements while preserving the aspect ratio.

        Args:
            data_point_count: Number of data points in the chart
            requested_width: User-requested width (optional)
            requested_height: User-requested height (optional)

        Returns:
            Tuple of (width, height) in pixels
        """
        # If user provided both dimensions, preserve their aspect ratio
        if requested_width is not None and requested_height is not None:
            width, height = self._apply_minimums_with_aspect_ratio(
                requested_width,
                requested_height,
                self.config.chart_min_width,
                self.config.chart_min_height,
            )
            # Still scale for many data points if needed
            if data_point_count > 10:
                extra_points = data_point_count - 10
                extra_width = extra_points * self.config.chart_width_per_datapoint
                if width < self.config.chart_min_width + extra_width:
                    # Scale both dimensions to accommodate data points
                    scale = (self.config.chart_min_width + extra_width) / width
                    width = int(width * scale)
                    height = int(height * scale)
            return (width, height)

        # Start with minimum dimensions
        width = self.config.chart_min_width
        height = self.config.chart_min_height

        # Scale width for many data points
        if data_point_count > 10:
            extra_points = data_point_count - 10
            width += extra_points * self.config.chart_width_per_datapoint

        # Apply user-requested dimensions if provided (single dimension)
        if requested_width is not None:
            width = max(requested_width, self.config.chart_min_width)

        if requested_height is not None:
            height = max(requested_height, self.config.chart_min_height)

        return (width, height)

    def count_mermaid_nodes(self, mermaid_code: str) -> int:
        """Count the number of nodes in a Mermaid diagram.

        Uses regex patterns to identify node definitions in various
        Mermaid diagram types (flowchart, sequence, class, etc.).

        Args:
            mermaid_code: The Mermaid diagram code

        Returns:
            Estimated number of nodes in the diagram
        """
        if not mermaid_code:
            return 0

        # Clean the code
        clean_code = mermaid_code.strip()

        # Remove markdown code block markers if present
        if clean_code.startswith("```"):
            clean_code = re.sub(r"```\w*\n?", "", clean_code)
            clean_code = clean_code.replace("```", "").strip()

        nodes: set[str] = set()

        # Pattern for flowchart/graph nodes: A, B[text], C{text}, D((text)), E>text], F[(text)]
        # Matches node IDs at the start of lines or after arrows
        flowchart_pattern = r"(?:^|\s|-->|--\>|->|--|-\.-|==>|==\>|-.->)([A-Za-z_][A-Za-z0-9_]*)(?:\[|\{|\(|\>|$|\s|;)"

        # Pattern for sequence diagram participants
        sequence_pattern = r"(?:participant|actor)\s+([A-Za-z_][A-Za-z0-9_]*)"

        # Pattern for class diagram classes
        class_pattern = r"(?:class)\s+([A-Za-z_][A-Za-z0-9_]*)"

        # Pattern for state diagram states
        state_pattern = r'(?:state)\s+(?:"[^"]*"\s+as\s+)?([A-Za-z_][A-Za-z0-9_]*)'

        # Pattern for ER diagram entities
        er_pattern = r"([A-Za-z_][A-Za-z0-9_]*)\s+(?:\{|\|\||\|o|o\|)"

        # Pattern for gantt tasks
        gantt_pattern = r"^\s*([A-Za-z_][A-Za-z0-9_ ]*?)\s*:"

        # Pattern for pie chart sections
        pie_pattern = r'"([^"]+)"\s*:\s*\d+'

        # Apply all patterns
        for pattern in [
            flowchart_pattern,
            sequence_pattern,
            class_pattern,
            state_pattern,
            er_pattern,
        ]:
            matches = re.findall(pattern, clean_code, re.MULTILINE | re.IGNORECASE)
            nodes.update(m for m in matches if m and len(m) > 0)

        # Gantt and pie patterns (count lines/sections)
        gantt_matches = re.findall(gantt_pattern, clean_code, re.MULTILINE)
        pie_matches = re.findall(pie_pattern, clean_code)

        # Add gantt tasks and pie sections
        nodes.update(f"gantt_{i}" for i, _ in enumerate(gantt_matches))
        nodes.update(f"pie_{i}" for i, _ in enumerate(pie_matches))

        # Fallback: count lines with arrows or relationships as a minimum
        if len(nodes) == 0:
            arrow_lines = re.findall(r".*(?:-->|->|--|==>|=>|\.->).*", clean_code)
            return max(len(arrow_lines) * 2, 2)  # At least 2 nodes per arrow line

        return len(nodes)

    def calculate_mermaid_dimensions(
        self,
        mermaid_code: str,
        requested_width: int | None = None,
        requested_height: int | None = None,
    ) -> tuple[int, int]:
        """Calculate optimal Mermaid diagram dimensions based on complexity.

        For diagrams with more than 15 nodes, dimensions are automatically
        increased proportionally to ensure readability. If user-requested
        dimensions are provided, they are scaled up proportionally to meet
        minimum requirements while preserving the aspect ratio.

        Args:
            mermaid_code: The Mermaid diagram code
            requested_width: User-requested width (optional)
            requested_height: User-requested height (optional)

        Returns:
            Tuple of (width, height) in pixels
        """
        # Count nodes to determine complexity
        node_count = self.count_mermaid_nodes(mermaid_code)

        # Calculate minimum dimensions based on complexity
        min_width = self.config.mermaid_base_width
        min_height = self.config.mermaid_base_height

        if node_count > 15:
            extra_nodes = node_count - 15
            min_width += extra_nodes * self.config.mermaid_width_per_node
            min_height += extra_nodes * self.config.mermaid_height_per_node

        # If user provided both dimensions, preserve their aspect ratio
        if requested_width is not None and requested_height is not None:
            width, height = self._apply_minimums_with_aspect_ratio(
                requested_width,
                requested_height,
                min_width,
                min_height,
            )
            return (width, height)

        # Start with calculated minimum dimensions
        width = min_width
        height = min_height

        # Apply user-requested dimensions if provided (single dimension)
        if requested_width is not None:
            width = max(requested_width, min_width)

        if requested_height is not None:
            height = max(requested_height, min_height)

        return (width, height)

    def calculate_table_dimensions(
        self,
        column_count: int,
        row_count: int,
        content_lengths: list[int] | None = None,
        requested_width: int | None = None,
        requested_height: int | None = None,
    ) -> tuple[int, int]:
        """Calculate optimal table dimensions based on content.

        Width is calculated based on column count, with a minimum of 1200px
        for tables with more than 5 columns. If user-requested dimensions
        are provided, they are scaled up proportionally to meet minimum
        requirements while preserving the aspect ratio.

        Args:
            column_count: Number of columns in the table
            row_count: Number of rows in the table
            content_lengths: Optional list of average content lengths per column
            requested_width: User-requested width (optional)
            requested_height: User-requested height (optional)

        Returns:
            Tuple of (width, height) in pixels
        """
        # Calculate minimum width from column count
        min_width = max(
            self.config.table_min_width, column_count * self.config.table_width_per_column
        )

        # Enforce minimum for many columns
        if column_count > 5:
            min_width = max(min_width, self.config.table_min_width_many_columns)

        # Adjust for content lengths if provided
        if content_lengths:
            avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
            if avg_length > 20:  # Long content
                min_width = int(min_width * 1.2)

        # Calculate minimum height based on row count
        row_height = 40
        header_height = 50
        padding = 60
        min_height = max(
            self.config.absolute_min_height, header_height + (row_count * row_height) + padding
        )

        # If user provided both dimensions, preserve their aspect ratio
        if requested_width is not None and requested_height is not None:
            width, height = self._apply_minimums_with_aspect_ratio(
                requested_width,
                requested_height,
                min_width,
                min_height,
            )
            return (width, height)

        # Start with calculated minimum dimensions
        width = min_width
        height = min_height

        # Apply user-requested dimensions if provided (single dimension)
        if requested_width is not None:
            width = max(requested_width, min_width)

        if requested_height is not None:
            height = max(requested_height, min_height)

        return (width, height)


__all__ = ["ImageSizingConfig", "ImageDimensionCalculator"]
