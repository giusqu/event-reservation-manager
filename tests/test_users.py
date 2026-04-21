async def test_create_user(created_user):
    pass  # just to test the fixture


async def test_create_user_duplicate(ac):
    response = await ac.post(
        "/users/",
        json={
            "username": "username",
            "email": "user@example.com",
            "password": "username123",
            "is_admin": False,
        },
    )
    assert response.status_code == 400


async def test_login(client):
    response = client.post("/users/login", json={"username": "username", "password": "username123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]


async def test_login_wrong_password(client):
    response = client.post("/users/login", json={"username": "username", "password": "wrong"})
    assert response.status_code == 401


async def test_user_list(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_me(client, auth_token):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "username"


async def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 200


async def test_get_user_not_found(client):
    response = client.get("/users/2")
    assert response.status_code == 404


async def ttest_delete_user(client, auth_token):
    response = client.delete("/users/1", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 204


async def test_delete_user_not_found(client, auth_token):
    response = client.delete("/users/2", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 404
