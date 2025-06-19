from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.database.models import User
from tests.conftest import TestingSessionLocal
from src.services.auth import auth_service

user_data = {
    "username": "testuser1",
    "email": "test1@test.com",
    "password": "testpassword1",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == "user"
    assert mock_send_email.call_count == 1


def test_signup_repeat(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exist"}


def test_signup_repeat_username(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    test_user = user_data.copy()
    test_user["email"] = "test2@test.com"
    response = client.post("api/auth/signup", json=test_user)

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this name already exist"}


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed_email = True
            await session.commit()
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_login_wrong_password(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid login or password"


def test_login_wrong_username(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": "wrong_username",
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid login or password"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_confirmed_email(client, get_token):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed_email = False
            await session.commit()
    response = client.get(f"/api/auth/confirmed_email/{get_token}")

    assert response.status_code == 200
    assert response.json() == {"message": "Email confirmed"}


def test_confirmed_email_already_confirmed(client, get_token):
    response = client.get(f"/api/auth/confirmed_email/{get_token}")

    assert response.status_code == 409
    assert response.json() == {"detail": "Your email is already confirmed"}


def test_confirmed_email_invalid_token(client):
    response = client.get("/api/auth/confirmed_email/invalid_token")

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid token for email verification"}


def test_request_email_already_confirmed(client):
    response = client.post(
        "api/auth/request_email", json={"email": user_data.get("email")}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Your email is already confirmed"}


@pytest.mark.asyncio
async def test_request_email(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed_email = False
            await session.commit()
    response = client.post(
        "api/auth/request_email", json={"email": user_data.get("email")}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Check your email for confirmation"}


def test_request_email_invalid_email(client):
    response = client.post("api/auth/request_email", json={"email": "invalid_email"})
    assert response.status_code == 422


def test_forgot_password_email_not_confirmed(client):
    response = client.post(
        "api/auth/forgot_password", json={"email": user_data.get("email")}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Email not confirmed"}


def test_forgot_password_wrong_email(client):
    response = client.post(
        "api/auth/forgot_password", json={"email": "test2test@test.com"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Verification error"}


@pytest.mark.asyncio
async def test_forgot_password(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed_email = True
            await session.commit()
    response = client.post(
        "api/auth/forgot_password", json={"email": user_data.get("email")}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Check your email for confirmation"}


def test_reset_password(client, get_token):
    response = client.post(
        f"api/auth/reset_password/{get_token}", data={"password": "new_password"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Password successfully changed"}
