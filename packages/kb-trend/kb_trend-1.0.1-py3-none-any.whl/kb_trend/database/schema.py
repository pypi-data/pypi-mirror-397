"""SQLAlchemy database schema."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class Metadata(Base):
    """System metadata table for config hash and version tracking."""

    __tablename__ = "metadata"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Metadata(key='{self.key}', value='{self.value}')>"


class Journal(Base):
    """Newspaper/journal definitions."""

    __tablename__ = "journal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    # Relationships
    counts: Mapped[list["Count"]] = relationship(
        "Count", back_populates="journal", cascade="all, delete-orphan"
    )
    queue_items: Mapped[list["QueueItem"]] = relationship(
        "QueueItem", back_populates="journal", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Journal(id={self.id}, name='{self.name}')>"


class Query(Base):
    """Search queries with metadata."""

    __tablename__ = "query"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    search_string: Mapped[str] = mapped_column(String, nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String, nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Unique constraint on search_string + keyword
    __table_args__ = (
        UniqueConstraint("search_string", "keyword", name="uq_query_search_keyword"),
        Index("idx_query_keyword", "keyword"),
    )

    # Relationships
    counts: Mapped[list["Count"]] = relationship(
        "Count", back_populates="query", cascade="all, delete-orphan"
    )
    queue_items: Mapped[list["QueueItem"]] = relationship(
        "QueueItem", back_populates="query", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Query(id={self.id}, keyword='{self.keyword}')>"


class Count(Base):
    """Hit counts from scraping."""

    __tablename__ = "counts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    query_id: Mapped[int] = mapped_column(Integer, ForeignKey("query.id"), nullable=False)
    journal_id: Mapped[int] = mapped_column(Integer, ForeignKey("journal.id"), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rel: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("year", "query_id", "journal_id", name="uq_count_year_query_journal"),
        Index("idx_count_query", "query_id"),
        Index("idx_count_journal", "journal_id"),
        Index("idx_count_year", "year"),
    )

    # Relationships
    query: Mapped["Query"] = relationship("Query", back_populates="counts")
    journal: Mapped["Journal"] = relationship("Journal", back_populates="counts")

    def __repr__(self) -> str:
        return (
            f"<Count(id={self.id}, year={self.year}, query_id={self.query_id}, "
            f"journal_id={self.journal_id}, count={self.count})>"
        )


class QueueItem(Base):
    """Scraping queue."""

    __tablename__ = "queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query_id: Mapped[int] = mapped_column(Integer, ForeignKey("query.id"), nullable=False)
    journal_id: Mapped[int] = mapped_column(Integer, ForeignKey("journal.id"), nullable=False)
    year: Mapped[str] = mapped_column(String, nullable=False)  # Can be "all" or specific year
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("query_id", "journal_id", "year", name="uq_queue_query_journal_year"),
        Index("idx_queue_status", "status"),
        Index("idx_queue_query", "query_id"),
    )

    # Relationships
    query: Mapped["Query"] = relationship("Query", back_populates="queue_items")
    journal: Mapped["Journal"] = relationship("Journal", back_populates="queue_items")

    def __repr__(self) -> str:
        return (
            f"<QueueItem(id={self.id}, query_id={self.query_id}, "
            f"journal_id={self.journal_id}, status='{self.status}')>"
        )
