from unittest.mock import patch
from src.services.auth import auth_service
from src.schemas.users import UserModel
import pytest
from conftest import test_user


@pytest.mark.asyncio
async def test_get_me(client, get_token, redis_client):
    auth_service.r = redis_client
    response = client.get(
        "api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )
    print(response.json())
    assert response.status_code == 200
