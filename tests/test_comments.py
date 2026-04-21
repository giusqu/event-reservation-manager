async def test_create_comment(client, created_event):
    response = client.post(
        "/comments/",
        json={
            "content": {"title": "Test Comment", "text": "Test Comment", "rating": 5},
            "user_id": 1,
            "event_id": 1,
        },
    )
    assert response.status_code == 201
    assert response.json()["content"]["title"] == "Test Comment"


async def test_get_comment(client):
    response = client.get("/comments/1")
    assert response.status_code == 200
    assert response.json()["content"]["title"] == "Test Comment"


async def test_get_comment_not_found(client):
    response = client.get("/comments/2")
    assert response.status_code == 404


async def test_get_comments(client):
    response = client.get("/comments/")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_update_comment(client):
    response = client.patch(
        "/comments/1",
        json={"content": {"title": "Updated Title", "text": "Updated Comment", "rating": 3}},
    )
    assert response.status_code == 200
    assert response.json()["content"]["title"] == "Updated Title"


async def test_update_comment_not_found(client):
    response = client.patch(
        "/comments/2",
        json={"content": {"title": "Ghost Title", "text": "Ghost Comment", "rating": 3}},
    )
    assert response.status_code == 404


async def test_delete_comment(client):
    response = client.delete("/comments/1")
    assert response.status_code == 204


async def test_delete_comment_not_found(client):
    response = client.delete("/comments/2")
    assert response.status_code == 404
