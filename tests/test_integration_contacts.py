import pytest
from src.services.auth import auth_service

test_contact = {
    "first_name": "test_contact",
    "last_name": "test_test",
    "email": "test_email@email.com",
    "phone": "+1234567890",
    "birthday": "2000-01-01",
    "info": "test_info",
}

test_contacts = [
    {
        "first_name": "test_contact_1",
        "last_name": "test_test_1",
        "email": "test_email_1@email.com",
        "phone": "+1234567890",
        "birthday": "2000-06-25",
        "info": "test_info_1",
        "info": "Test contact_1.",
    },
    {
        "first_name": "test_contact_2",
        "last_name": "test_test_2",
        "email": "test_email_2@email.com",
        "phone": "+2234567890",
        "birthday": "2000-02-02",
        "info": "test_info_2",
        "info": "Test contact_2.",
    },
]


def test_create_contact(
    client,
    get_token,
):

    response = client.post(
        "/api/contacts",
        json=test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_contacts(
    client,
    get_token,
):

    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["first_name"] == test_contact["first_name"]


def test_get_contact_by_id(
    client,
    get_token,
):

    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]


def test_get_contact_by_id_not_found(
    client,
    get_token,
):

    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404


def test_update_contact(
    client,
    get_token,
):

    updated_data = {**test_contact, "first_name": "updated_contact"}
    response = client.put(
        "/api/contacts/1",
        json=updated_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200


def test_update_contact_not_found(
    client,
    get_token,
):

    updated_data = {**test_contact, "first_name": "updated_contact"}
    response = client.put(
        "/api/contacts/2",
        json=updated_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404


def test_delete_contact(
    client,
    get_token,
):

    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 204


def test_delete_contact_not_found(
    client,
    get_token,
):

    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404
