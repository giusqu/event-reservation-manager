# Event Reservation Manager (ERM)

## 1. Project overview

ERM is a FastAPI REST API used to manage:
- users
- events
- reservations
- comments

The platform allows users to create events by specifying the location, description, and maximum booking capacity. In addition, all users can comment on individual events.

Main stack:
- FastAPI
- PostgreSQL + async SQLAlchemy
- Alembic for migrations
- JWT authentication
- Redis caching
- Jinja2 for basic HTML pages
- WebSocket for realtime communication

Main features:
- CRUD for users/events/reservations/comments
- login with JWT token and protected endpoints (for example `/users/me`)
- user image upload (JPEG only) in `static/images/`
- HTML pages:
  - `/events_page`
  - `/user_page/{user_id}`
  - `/users_page`
  - `/comments`
- realtime:
  - WebSocket `/ws`
  - broadcast endpoint `POST /send_message_to_all_websocket_users`
- Redis cache on `GET /long_operation` (20-second TTL)

### Recommended usage order

1. Prepare configuration
   - create `.env` (local) or `deploy.env` (docker)
   - set DB, Redis, JWT, and `*_TEST` variables
2. Start infrastructure
   - PostgreSQL
   - Redis (optional)
3. Initialize database schema with Alembic
   ```powershell
   alembic upgrade head
   ```
4. Start FastAPI
   ```powershell
   python run.py
   ```
   or
   ```powershell
   uvicorn src.main:app --reload
   ```
5. Seed base data  
   Swagger UI http://localhost:8000/docs (locale) oppure http://localhost:9999/docs (docker)
   - create user (`POST /users/`)
   - login (`POST /users/login`)
   - create events (`POST /events/`)
   - then reservations/comments
6. Use UI and realtime
   - Jinja2: `/events_page`, `/user_page/{id}`
   - WebSocket: `/ws` + broadcast `POST /send_message_to_all_websocket_users`
7. Run tests
   ```powershell
   python run_tests.py
   ```

## 2. How to run (local)

Prerequisites:
- Python 3.13+
- PostgreSQL
- Redis (to be downloaded from an external source)

Setup:
1. Create and activate virtual environment
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```
3. Create `.env` (see dedicated section)
4. Apply database migrations
   ```powershell
   alembic upgrade head
   ```
5. Start the app
   ```powershell
   python run.py
   ```
   or
   ```powershell
   uvicorn src.main:app --reload
   ```

Useful URLs:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## 3. Run with Docker Compose

```powershell
docker compose up --build
```

Expected services:
- `app` (host port `9999` -> container `8000`)
- `db` (Postgres on internal port `1221`)
- `redis` (internal port `5370`)

## 4. Files to create/edit

Local files:
- `.env` (local development, loaded by `src/config.py`)
- `deploy.env` (used by `docker-compose.yaml`)

Example in:
- `.env.example`
- `deploy.env.example`

## 5. How to use Redis

Redis is used for API caching. Quick check:
1. Start redis-server
2. Call `GET /long_operation` twice within a few seconds.
3. The second response should be returned from cache.

## 6. How to use WebSocket

FastAPI’s interactive documentation (/docs) does not support WebSocket connections directly, so use an external tool to establish the connection.

Already available for realtime:
- WebSocket `GET /ws` ("ws://localhost:8000/ws")
- Broadcast `POST /send_message_to_all_websocket_users`

## 7. How to use pytest

Tests are in `tests/` and use a dedicated test DB via `*_TEST` variables.

Before running tests:
- create a test database (for example `DB_NAME_TEST=test`)
- set in `.env`:
  - `DB_HOST_TEST`
  - `DB_PORT_TEST`
  - `DB_NAME_TEST`
  - `DB_USER_TEST`
  - `DB_PASS_TEST`

Commands:
```powershell
python run_tests.py
```
or
```powershell
pytest -v tests/ --asyncio-mode=auto --disable-warnings
```

## 8. How to view Jinja2 pages

Jinja2 pages must be opened in the browser using HTML routes, not from Swagger.

Local run:
1. Start the app:
   ```powershell
   python run.py
   ```
   or
   ```powershell
   uvicorn src.main:app --reload
   ```
2. Open:
   - `http://localhost:8000/events`
   - `http://localhost:8000/user_page/1` (replace `1` with an existing `user_id`)
   - `http://localhost:8000/users_page`
   - `http://localhost:8000/comments_page`

   With Docker, change port from 8000 to 9999

> **Note:** To see real content, the database must contain data (migrations applied + at least one user/event).

## 9. Additional useful notes

Migrations:
```powershell
alembic revision --autogenerate -m "migration_name"
alembic upgrade head
```

JWT flow:
1. call `POST /users/login` to get `access_token`
2. send `Authorization: Bearer <token>` for protected endpoints

Image upload:
- `POST /users/upload_image` accepts only `image/jpeg`
