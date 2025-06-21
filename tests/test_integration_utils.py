import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from src.database.db import get_db


def test_healthchecker(client):
    response = client.get("/api/healthchecker")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI"}


@pytest.mark.asyncio
async def test_healthchecker_db_connection_error(client):
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = Exception("Database connection error")

    async def override_get_db():  # Debugging output
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/api/healthchecker")

    assert response.status_code == 500, response.text
    assert response.json() == {"detail": "Error connecting to database"}

    app.dependency_overrides.clear()  # Reset the dependency override
