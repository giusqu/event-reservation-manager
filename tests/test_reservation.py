async def test_create_reservation(client, created_event_for_reservation):
    response = client.post(
        "/reservations/",
        json={
            "num_guests": 2,
            "user_id": 1,
            "event_id": created_event_for_reservation["id"],
        },
    )
    assert response.status_code == 201
    assert response.json()["num_guests"] == 2


async def test_create_reservation_event_not_found(client):
    response = client.post(
        "/reservations/",
        json={
            "num_guests": 2,
            "user_id": 1,
            "event_id": 999,
        },
    )
    assert response.status_code == 404


async def test_create_reservation_over_capacity(client, created_event_for_reservation):
    response = client.post(
        "/reservations/",
        json={
            "num_guests": 999,
            "user_id": 1,
            "event_id": created_event_for_reservation["id"],
        },
    )
    assert response.status_code == 400


async def test_get_reservations(client):
    response = client.get("/reservations/")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_reservation(client):
    response = client.get("/reservations/1")
    assert response.status_code == 200
    assert response.json()["num_guests"] == 2


async def test_get_reservation_not_found(client):
    response = client.get("/reservations/2")
    assert response.status_code == 404


async def test_update_reservation(client):
    response = client.patch(
        "/reservations/1",
        json={"num_guests": 4},
    )
    assert response.status_code == 200
    assert response.json()["num_guests"] == 4


async def test_update_reservation_not_found(client):
    response = client.patch(
        "/reservations/2",
        json={"num_guests": 4},
    )
    assert response.status_code == 404


async def test_delete_reservation(client):
    response = client.delete("/reservations/1")
    assert response.status_code == 204


async def test_delete_reservation_not_found(client):
    response = client.delete("/reservations/44")
    assert response.status_code == 404
