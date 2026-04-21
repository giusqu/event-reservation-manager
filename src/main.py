import time
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.comments.models import Comment
from src.comments.routers import router as comment_router
from src.config import settings
from src.database import get_async_session
from src.events.models import Event
from src.events.routers import router as event_router
from src.reservations.routers import router as reservation_router
from src.users.models import User
from src.users.routers import router as user_router

# Template system
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}")
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    yield
    await redis_client.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(user_router)
app.include_router(reservation_router)
app.include_router(comment_router)
app.include_router(event_router)

app.mount("/static", StaticFiles(directory="static"))


@app.get("/long_operation")
@cache(expire=20)
async def longoperation():  # Simulate a long-running operation
    time.sleep(3)
    return {"message": "Very long operation completed"}


connected_users = set()  # store connected users for WebSocket


@app.websocket("/ws")  # WebSocket endpoint where users will connect
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_users.add(websocket)
    try:  # Endless loop to receive and send messages
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message sent was: {data}")
    except WebSocketDisconnect:
        connected_users.remove(websocket)


@app.post("/send_message_to_all_websocket_users")
async def send_message_to_all_websocket_users(payload: dict):
    for user in connected_users:
        await user.send_json(payload)
    return {"message": "Message sent to all connected users"}


@app.get("/events_page", response_class=HTMLResponse)
async def read_items(request: Request, session: AsyncSession = Depends(get_async_session)):
    query = select(Event)
    events = await session.scalars(query)
    events = events.all()

    return templates.TemplateResponse(
        request=request, name="events.html", context={"events": events}
    )


@app.get("/user_page/{user_id}", response_class=HTMLResponse)
async def user_page(
    request: Request, user_id: int, session: AsyncSession = Depends(get_async_session)
):
    query = select(User).where(User.id == user_id)
    user = await session.scalars(query)
    user = user.first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(request=request, name="user.html", context={"user": user})


@app.get("/users_page", response_class=HTMLResponse)
async def users_page(request: Request, session: AsyncSession = Depends(get_async_session)):
    query = select(User)
    users = await session.scalars(query)
    users = users.unique().all()

    return templates.TemplateResponse(request=request, name="users.html", context={"users": users})


@app.get("/comments_page", response_class=HTMLResponse)
async def comments_page(request: Request, session: AsyncSession = Depends(get_async_session)):
    query = select(Comment)
    comments = await session.scalars(query)
    comments = comments.all()

    return templates.TemplateResponse(
        request=request, name="comments.html", context={"comments": comments}
    )
