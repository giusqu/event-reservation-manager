import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings as s
from src.database import Base, get_async_session
from src.main import app

DATABASE_URL_TEST = (
    f"postgresql+asyncpg://{s.db_user_test}:{s.db_pass_test.get_secret_value()}"
    f"@{s.db_host_test}:{s.db_port_test}/{s.db_name_test}"
)
# poolclass=NullPool = no connection pooling, every connection is opened and closed on each request
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


# session=scope = once per test session
# autouse=True = runs before every test
@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def created_user(ac):
    response = await ac.post(
        "/users/",
        json={
            "username": "username",
            "email": "user@example.com",
            "password": "username123",
            "is_admin": False,
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "username"
    assert response.json()["is_admin"] is False
    return response.json()


@pytest.fixture(scope="session")
def auth_token(client, created_user):
    response = client.post("/users/login", json={"username": "username", "password": "username123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def created_event(client, auth_token):
    response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "date": "2025-01-01T00:00:00",
            "location": "Naples",
            "capacity": 100,
            "user_id": 1,
            "content": {"description": "Test description"},
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Event"
    assert response.json()["content"]["description"] == "Test description"
    return response.json()


# the event get deleted before running reservation tests, so it needs to be recreated
@pytest.fixture(scope="session")
def created_event_for_reservation(client, auth_token):
    response = client.post(
        "/events/",
        json={
            "name": "Reservation Event",
            "date": "2025-06-01T00:00:00",
            "location": "Rome",
            "capacity": 100,
            "user_id": 1,
            "content": {"description": "For reservation tests"},
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    return response.json()
