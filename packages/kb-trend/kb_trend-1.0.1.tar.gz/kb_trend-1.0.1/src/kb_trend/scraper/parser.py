"""Parser for KB.se API responses."""

from typing import Any


class ResponseParser:
    """Parse KB.se API responses."""

    @staticmethod
    def extract_year_counts(response: dict[str, Any]) -> list[dict[str, int]]:
        """Extract year/count pairs from API response.

        Args:
            response: JSON response from KB API

        Returns:
            List of dicts with 'year' and 'count' keys

        Raises:
            ValueError: If response format is invalid
        """
        try:
            # Navigate to aggregations
            aggs = response.get("aggs", {})
            date_published = aggs.get("datePublished", {})
            values = date_published.get("values", [])

            results = []

            for item in values:
                # Extract year from value (can be "YYYY" or "YYYY-MM-DD")
                year_str = item["value"]

                if "-" in year_str:
                    # Format: "1895-01-15" -> extract year
                    year = int(year_str.split("-")[0])
                else:
                    # Format: "1895"
                    year = int(year_str)

                count = item["count"]

                results.append({"year": year, "count": count})

            return results

        except (KeyError, ValueError, TypeError, IndexError) as e:
            raise ValueError(f"Failed to parse response: {e}")

    @staticmethod
    def get_total_hits(response: dict[str, Any]) -> int:
        """Get total number of hits from response.

        Args:
            response: JSON response from KB API

        Returns:
            Total hit count
        """
        result = response.get("total", 0)
        if type(result) is not int:
            raise ValueError(f"Expected int {result}")
        return int(result)
