import asyncio

import pytest
import pytest_asyncio

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.database.db import get_db
from src.database.models import Base, User
from src.services.auth import auth_service

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "testuser",
    "email": "test@test.com",
    "password": "testpassword",
    "role": "USER",
    "avatar": "https://example.com/avatar.jpg",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            user = User(**test_user)
            user.hashed_password = auth_service.get_password_hash(test_user["password"])
            session.add(user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
def get_token():
    token = auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture(autouse=True)
def setup_redis_for_auth():
    import fakeredis

    auth_service.r = fakeredis.FakeRedis()
