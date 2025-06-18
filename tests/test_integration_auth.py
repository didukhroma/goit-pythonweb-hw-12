from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.database.models import User
from tests.confest import TestingSessionLocal

user_data = {
    "username": "testuser",
    "email": "test@test.com",
    "password": "testpassword",
}


# def test_signup(client, monkeypatch):
#     mock_send_email = Mock()
#     monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
#     response = client.post("api/auth/signup", json=user_data)

#     assert response.status_code == 201
#     data = response.json()
#     assert data["username"] == user_data["username"]
#     assert data["email"] == user_data["email"]
#     assert data["avatar"] == "https://example.com/avatar.jpg"
#     assert data["role"] == "user"
#     assert mock_send_email.call_count == 1
