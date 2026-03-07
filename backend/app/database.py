"""Database setup and session management."""
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    # SQLite can only handle one writer at a time.  Give concurrent
    # requests up to 30 seconds to acquire the lock instead of
    # failing immediately with "database is locked".
    connect_args={"timeout": 30},
)

# Enable WAL mode for better concurrent access — allows readers
# to proceed while a write is in progress.
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def _add_missing_columns(conn):
    """Add columns that were introduced after initial table creation."""
    import sqlalchemy as sa

    inspector = sa.inspect(conn)
    if inspector.has_table("implementation_submissions"):
        columns = [c["name"] for c in inspector.get_columns("implementation_submissions")]
        if "generated_files" not in columns:
            conn.execute(sa.text(
                "ALTER TABLE implementation_submissions ADD COLUMN generated_files JSON DEFAULT '{}'"
            ))


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_add_missing_columns)


async def close_db():
    """Close database connections."""
    await engine.dispose()
