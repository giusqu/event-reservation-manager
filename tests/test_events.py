async def test_create_event(created_event):
    pass  # just to test the fixture


async def test_get_events(client):
    response = client.get("/events/")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_event(client):
    response = client.get("/events/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Event"


async def test_get_event_not_found(client):
    response = client.get("/events/2")
    assert response.status_code == 404


async def test_update_event(client, auth_token):
    response = client.patch(
        "/events/1",
        json={"name": "Updated Event"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Event"


async def test_update_event_not_found(client, auth_token):
    response = client.patch(
        "/events/2",
        json={"name": "Ghost Event"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


async def test_delete_event(client, auth_token):
    response = client.delete(
        "/events/1",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204


async def test_delete_event_not_found(client, auth_token):
    response = client.delete(
        "/events/2",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
