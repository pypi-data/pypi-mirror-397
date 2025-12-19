"""Relative frequency processor."""


from kb_trend.database.manager import DatabaseManager


class RelativeFrequencyProcessor:
    """Calculate relative frequencies for all counts."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize processor.

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def calculate_all(self) -> int:
        """Calculate relative frequencies for all counts.

        Uses the wildcard query (keyword='*') as the denominator.

        Returns:
            Number of records updated
        """
        # Get wildcard query ID
        wildcard_query_id = self.db_manager.get_wildcard_query_id()

        if wildcard_query_id is None:
            raise ValueError(
                "Wildcard query not found. "
                "Run 'kb-trend init' to create it."
            )

        # Build dictionary of (journal_id, year) -> count for wildcard query
        wildcard_counts: dict[tuple[int, int], int] = {}

        with self.db_manager.get_session() as session:
            from kb_trend.database.schema import Count

            # Get all wildcard counts
            wildcard_results = session.query(Count).filter(
                Count.query_id == wildcard_query_id
            ).all()

            for count_obj in wildcard_results:
                key = (count_obj.journal_id, count_obj.year)
                wildcard_counts[key] = count_obj.count

        # Get all non-wildcard counts and calculate relative frequencies
        updates: list[dict] = []

        with self.db_manager.get_session() as session:
            from kb_trend.database.schema import Count

            # Get all counts
            all_counts = session.query(Count).filter(
                Count.query_id != wildcard_query_id
            ).all()

            for count_obj in all_counts:
                key = (count_obj.journal_id, count_obj.year)
                denominator = wildcard_counts.get(key, 0)

                # Validate data integrity
                if denominator < count_obj.count:
                    raise ValueError(
                        f"Data integrity error: wildcard count ({denominator}) < "
                        f"query count ({count_obj.count}) for year={count_obj.year}, "
                        f"journal_id={count_obj.journal_id}"
                    )

                # Calculate relative frequency
                if denominator == 0:
                    if count_obj.count != 0:
                        raise ValueError(
                            f"Data error: denominator is 0 but count is {count_obj.count}"
                        )
                    rel = 0.0
                else:
                    rel = count_obj.count / denominator

                updates.append({
                    'id': count_obj.id,
                    'rel': rel
                })

        # Update database
        updated_count = self.db_manager.update_relative_frequencies(updates)

        return updated_count
