"""Query builder for search strings."""



class QueryBuilder:
    """Build search queries from keywords."""

    def __init__(
        self,
        marker_templates: list[str] | None = None,
        proximity_distance: int = 5
    ):
        """Initialize query builder.

        Args:
            marker_templates: List of proximity markers (e.g., ["SÖKES", "PLATS"])
            proximity_distance: Number of words for proximity search
        """
        self.marker_templates = marker_templates or []
        self.proximity_distance = proximity_distance

    def build(self, keyword: str) -> str:
        """Build search query from keyword.

        Args:
            keyword: The keyword to search for

        Returns:
            Search query string
        """
        if not self.marker_templates:
            # Plain keyword search (quoted for exact phrase)
            return f'"{keyword}"'

        # Proximity search with markers
        parts = [
            f'"{keyword} {marker}"~{self.proximity_distance}'
            for marker in self.marker_templates
        ]

        return " OR ".join(parts)
