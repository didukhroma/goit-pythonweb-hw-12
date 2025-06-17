import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import settings


class DatabaseSessionManager:
    """
    A class for managing database sessions.
    """

    def __init__(self, url: str):
        """
        Initializes the database session manager with the given URL.

        Args:
            url (str): The database connection URL.

        Attributes:
            _engine (AsyncEngine | None): The instance of the database engine.
            _session_maker (async_sessionmaker): The instance of the session maker.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Async context manager for database session management.

        Yields:
            AsyncSession: An instance of the database session.

        Raises:
            Exception: If the database session is not initialized.
            SQLAlchemyError: If an error occurs during the session, the session is
            rolled back and the error is raised.
        """

        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = DatabaseSessionManager(settings.database_url)


async def get_db():
    """
    FastAPI dependency that yields a database session.

    Yields:
        AsyncSession: The database session.
    """
    async with session_manager.session() as session:
        yield session
