from unittest.mock import patch
from src.services.auth import auth_service
from src.database.models import User, UserRole
from sqlalchemy import select
import pytest
from tests.conftest import test_user, TestingSessionLocal


@pytest.mark.asyncio
async def test_get_me(client, get_token, redis_client):
    auth_service.r = redis_client
    response = client.get(
        "api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )
    print(response.json())
    assert response.status_code == 200


@patch("src.services.upload_file.UploadFileService.upload_file")
def test_update_avatar_user_invalid_user_role(mock_upload_file, client, get_token):

    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url
    headers = {"Authorization": f"Bearer {get_token}"}

    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    assert response.status_code == 403


# @pytest.mark.asyncio
# @patch("src.services.upload_file.UploadFileService.upload_file")
# async def test_update_avatar_user(mock_upload_file, client, get_token):
#     async with TestingSessionLocal() as session:
#         current_user = await session.execute(
#             select(User).where(User.email == test_user.get("email"))
#         )

#         current_user = current_user.scalar_one_or_none()
#         if current_user:
#             current_user.confirmed_email = True
#             current_user.role = UserRole.ADMIN
#             await session.commit()

#     fake_url = "<http://example.com/avatar.jpg>"
#     mock_upload_file.return_value = fake_url
#     headers = {"Authorization": f"Bearer {get_token}"}

#     file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

#     response = client.patch("/api/users/avatar", headers=headers, files=file_data)

#     assert response.status_code == 200, response.text

#     data = response.json()
#     assert data["username"] == test_user["username"]
#     assert data["email"] == test_user["email"]
#     assert data["avatar"] == fake_url

#     mock_upload_file.assert_called_once()
