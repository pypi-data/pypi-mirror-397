"""Scraper worker for processing queue."""

import time
from typing import Any

from loguru import logger

from kb_trend.config.models import Settings
from kb_trend.database.manager import DatabaseManager
from kb_trend.database.schema import QueueItem
from kb_trend.scraper.client import KBClient
from kb_trend.scraper.parser import ResponseParser


class ScraperWorker:
    """Worker for processing scraping queue."""

    def __init__(self, db_manager: DatabaseManager, settings: Settings):
        """Initialize scraper worker.

        Args:
            db_manager: Database manager instance
            settings: Application settings
        """
        self.db_manager = db_manager
        self.settings = settings
        self.client = KBClient(timeout=settings.request_timeout)
        self.parser = ResponseParser()

    def process_item(self, item: QueueItem) -> None:
        """Process a single queue item.

        Args:
            item: Queue item to process
        """
        # Mark as in progress
        self.db_manager.update_queue_status(item.id, "in_progress")

        try:
            # Get query and journal info
            query = self.db_manager.get_query_by_id(item.query_id)
            if not query:
                raise ValueError(f"Query {item.query_id} not found")

            # Get journal name
            with self.db_manager.get_session() as session:
                from kb_trend.database.schema import Journal as JournalModel

                journal = session.query(JournalModel).get(item.journal_id)
                if not journal:
                    raise ValueError(f"Journal {item.journal_id} not found")
                journal_name = journal.name

            # Build date range
            from_date: str | None = None
            to_date: str | None = None

            if self.settings.min_year:
                from_date = f"{self.settings.min_year}-01-01"
            if self.settings.max_year:
                to_date = f"{self.settings.max_year}-12-31"

            # Execute search
            logger.debug(
                f"Searching: query='{query.keyword}' journal='{journal_name}' "
                f"from={from_date} to={to_date}"
            )

            response = self.client.search(
                query=query.search_string,
                journal=journal_name,
                from_date=from_date,
                to_date=to_date,
            )

            # Parse response
            year_counts = self.parser.extract_year_counts(response)

            # Insert counts into database
            for item_data in year_counts:
                self.db_manager.insert_count(
                    year=item_data["year"],
                    query_id=item.query_id,
                    journal_id=item.journal_id,
                    count=item_data["count"],
                )

            # Mark as completed
            self.db_manager.update_queue_status(item.id, "completed")

            # Sleep between requests
            time.sleep(self.settings.sleep_timer)

        except Exception as e:
            # Mark as failed
            error_msg = str(e)
            logger.error(f"Error processing queue item {item.id}: {error_msg}")
            self.db_manager.update_queue_status(item.id, "failed", error_message=error_msg)
            raise

    def close(self) -> None:
        """Close client resources."""
        self.client.close()

    def __enter__(self) -> "ScraperWorker":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
