import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app  # Replace with your actual app import
from slowapi import Limiter
from slowapi.util import get_remote_address


# Create a test app instance
@pytest.fixture(scope="session")
def test_app():
    # Initialize Limiter for the test app
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    return app


# Create a test client fixture
@pytest.fixture(scope="session")
def client(test_app):
    return TestClient(test_app)


# Optional: Fixture to set up test database (if needed)
@pytest.fixture(scope="function")
async def setup_test_db():
    # Add code to set up test database if needed
    yield
    # Add code to clean up test database
