"""Database manager for all database operations."""

from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from kb_trend.database.schema import Base, Count, Journal, Metadata, Query, QueueItem


class DatabaseManager:
    """Manages all database operations."""

    def __init__(self, db_path: Path):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Auto-initialize schema if database doesn't exist or is empty
        if not db_path.exists() or db_path.stat().st_size == 0:
            self.init_schema()

    def init_schema(self) -> None:
        """Initialize database schema (create all tables)."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()

    # Metadata operations
    def get_metadata(self, key: str) -> str | None:
        """Get metadata value by key.

        Args:
            key: Metadata key

        Returns:
            Metadata value or None if not found
        """
        try:
            with self.get_session() as session:
                result = session.query(Metadata).filter(Metadata.key == key).first()
                return result.value if result else None
        except Exception:
            # Table doesn't exist yet, return None
            return None

    def set_metadata(self, key: str, value: str) -> None:
        """Set metadata key-value pair.

        Args:
            key: Metadata key
            value: Metadata value
        """
        with self.get_session() as session:
            metadata = session.query(Metadata).filter(Metadata.key == key).first()

            if metadata:
                metadata.value = value
                metadata.updated_at = datetime.utcnow()
            else:
                metadata = Metadata(key=key, value=value)
                session.add(metadata)

            session.commit()

    # Journal operations
    def initialize_journals(self, journal_names: list[str]) -> None:
        """Initialize journals from settings.

        Args:
            journal_names: List of journal names
        """
        with self.get_session() as session:
            for name in journal_names:
                existing = session.query(Journal).filter(Journal.name == name).first()
                if not existing:
                    journal = Journal(name=name)
                    session.add(journal)
            session.commit()

    def get_journal_id(self, name: str) -> int | None:
        """Get journal ID by name.

        Args:
            name: Journal name

        Returns:
            Journal ID or None if not found
        """
        with self.get_session() as session:
            journal = session.query(Journal).filter(Journal.name == name).first()
            if journal:
                # Need to access the id before session closes
                journal_id = journal.id
                return journal_id
            return None

    def get_all_journals(self) -> list[Journal]:
        """Get all journals.

        Returns:
            List of Journal objects
        """
        with self.get_session() as session:
            journals = session.query(Journal).all()
            # Detach from session to avoid lazy loading issues
            session.expunge_all()
            return journals

    # Query operations
    def insert_query(
        self, search_string: str, keyword: str, metadata: dict[str, Any] | None = None
    ) -> int:
        """Insert or get existing query.

        Args:
            search_string: Full search query string
            keyword: The keyword being searched
            metadata: Additional metadata from CSV (all columns)

        Returns:
            Query ID
        """
        with self.get_session() as session:
            # Check if query already exists
            existing = (
                session.query(Query)
                .filter(Query.search_string == search_string, Query.keyword == keyword)
                .first()
            )

            if existing:
                return existing.id

            # Create new query
            query = Query(search_string=search_string, keyword=keyword, metadata_json=metadata)
            session.add(query)
            session.commit()
            session.refresh(query)

            return query.id

    def create_wildcard_query(self) -> int:
        """Create wildcard query for baseline measurements.

        Returns:
            Wildcard query ID
        """
        return self.insert_query(search_string="*", keyword="*", metadata={"_wildcard": True})

    def get_query_by_id(self, query_id: int) -> Query | None:
        """Get query by ID.

        Args:
            query_id: Query ID

        Returns:
            Query object or None
        """
        with self.get_session() as session:
            return session.query(Query).filter(Query.id == query_id).first()

    def get_wildcard_query_id(self) -> int | None:
        """Get wildcard query ID.

        Returns:
            Wildcard query ID or None
        """
        with self.get_session() as session:
            query = session.query(Query).filter(Query.keyword == "*").first()
            return query.id if query else None

    # Queue operations
    def populate_queue(self, query_id: int, journals: list[str], year: str = "all") -> int:
        """Populate queue with query/journal combinations.

        Args:
            query_id: Query ID to queue
            journals: List of journal names
            year: Year to process (default: "all")

        Returns:
            Number of items added to queue
        """
        count = 0

        with self.get_session() as session:
            for journal_name in journals:
                journal_id = self.get_journal_id(journal_name)
                if journal_id is None:
                    continue

                # Check if already exists
                existing = (
                    session.query(QueueItem)
                    .filter(
                        QueueItem.query_id == query_id,
                        QueueItem.journal_id == journal_id,
                        QueueItem.year == year,
                    )
                    .first()
                )

                if not existing:
                    queue_item = QueueItem(
                        query_id=query_id, journal_id=journal_id, year=year, status="pending"
                    )
                    session.add(queue_item)
                    count += 1

            session.commit()

        return count

    def get_queue(
        self, status: list[str] | None = None, limit: int | None = None
    ) -> list[QueueItem]:
        """Get queue items.

        Args:
            status: Filter by status values (None = all)
            limit: Maximum number of items to return

        Returns:
            List of QueueItem objects
        """
        with self.get_session() as session:
            query = session.query(QueueItem)

            if status:
                query = query.filter(QueueItem.status.in_(status))

            if limit:
                query = query.limit(limit)

            return query.all()

    def update_queue_status(
        self, item_id: int, status: str, error_message: str | None = None
    ) -> None:
        """Update queue item status.

        Args:
            item_id: Queue item ID
            status: New status
            error_message: Error message if failed
        """
        with self.get_session() as session:
            item = session.query(QueueItem).filter(QueueItem.id == item_id).first()

            if item:
                item.status = status
                item.error_message = error_message

                if status == "completed":
                    item.completed_at = datetime.utcnow()

                session.commit()

    def reset_queue(self) -> int:
        """Reset all queue items to pending status.

        Returns:
            Number of items reset
        """
        with self.get_session() as session:
            result = session.query(QueueItem).update(
                {"status": "pending", "completed_at": None, "error_message": None}
            )
            session.commit()
            return result

    # Count operations
    def insert_count(self, year: int, query_id: int, journal_id: int, count: int) -> None:
        """Insert or update count.

        Args:
            year: Year
            query_id: Query ID
            journal_id: Journal ID
            count: Hit count
        """
        with self.get_session() as session:
            existing = (
                session.query(Count)
                .filter(
                    Count.year == year, Count.query_id == query_id, Count.journal_id == journal_id
                )
                .first()
            )

            if existing:
                existing.count = count
            else:
                count_obj = Count(year=year, query_id=query_id, journal_id=journal_id, count=count)
                session.add(count_obj)

            session.commit()

    def insert_counts_batch(self, counts: list[dict[str, Any]]) -> None:
        """Insert multiple counts in batch.

        Args:
            counts: List of dicts with year, query_id, journal_id, count
        """
        with self.get_session():
            for count_data in counts:
                self.insert_count(**count_data)

    def get_counts_for_query(self, query_id: int) -> list[Count]:
        """Get all counts for a query.

        Args:
            query_id: Query ID

        Returns:
            List of Count objects
        """
        with self.get_session() as session:
            return session.query(Count).filter(Count.query_id == query_id).all()

    def update_relative_frequencies(self, updates: list[dict[str, Any]]) -> int:
        """Update relative frequencies for counts.

        Args:
            updates: List of dicts with id and rel (relative frequency)

        Returns:
            Number of records updated
        """
        count = 0

        with self.get_session() as session:
            for update in updates:
                count_obj = session.query(Count).filter(Count.id == update["id"]).first()
                if count_obj:
                    count_obj.rel = update["rel"]
                    count += 1

            session.commit()

        return count

    # Statistics
    def get_statistics(self) -> dict[str, int]:
        """Get database statistics.

        Returns:
            Dictionary with statistics
        """
        with self.get_session() as session:
            stats = {
                "total_queries": session.query(func.count(Query.id)).scalar(),
                "total_journals": session.query(func.count(Journal.id)).scalar(),
                "total_counts": session.query(func.count(Count.id)).scalar(),
                "queue_pending": session.query(func.count(QueueItem.id))
                .filter(QueueItem.status == "pending")
                .scalar(),
                "queue_completed": session.query(func.count(QueueItem.id))
                .filter(QueueItem.status == "completed")
                .scalar(),
                "queue_failed": session.query(func.count(QueueItem.id))
                .filter(QueueItem.status == "failed")
                .scalar(),
            }

            return stats
