from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.database import session_type
from src.events.schemas import EventResponse
from src.security import JWTBearer, sign_in_jwt
from src.users.models import User
from src.users.schemas import UserCreate, UserLogin, UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

user_id_type = Annotated[int, Depends(JWTBearer())]


# get me endpoint
@router.get("/me")
async def get_me(session: session_type, user_id: user_id_type):
    query = select(User).where(User.id == user_id)
    query_result = await session.scalars(query)  # exec query
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    return result


# get all users
@router.get("/", response_model=Optional[List[UserResponse]])
@cache(expire=20)
async def get_users(session: session_type):
    query = select(User)
    query_result = await session.scalars(query)
    result = query_result.unique().all()

    return result


# login
@router.post("/login")
async def login(payload: UserLogin, session: session_type):
    query = select(User).where(User.username == payload.username)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None or not result.check_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return sign_in_jwt(result.id)


# create user
@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, session: session_type):
    new_user = User(
        username=user.username,
        email=user.email,
        password_setter=user.password,
        is_admin=user.is_admin,
    )
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        # await session.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")

    return new_user


# upload image
@router.post("/upload_image")
async def upload_image(image: UploadFile, user_id: user_id_type):
    if image.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="Deve essere un jpeg/jpg")
    with open(f"static/images/{user_id}.jpg", "wb") as f:
        f.write(image.file.read())
    return {"message": f"Image {image.filename} uploaded successfully"}


# download image endpoint
@router.get("/image_download")
async def image_download(user_id: int):
    return FileResponse(f"static/images/{user_id}.jpg")


# get single user by id
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: session_type):
    query = select(User).where(User.id == user_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    return result


# edit user (patch to modify only some fields, put to modify all fields)
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserUpdate, session: session_type):
    query = select(User).where(User.id == user_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in payload.model_dump().items():  # model_dump() returns model fields dictionary
        if value is not None:
            setattr(result, key, value)

    # commit changes
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already in use")

    return result


# delete user
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, session: session_type):
    query = select(User).where(User.id == user_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(result)
    await session.commit()

    return None  # 204 No Content


# get user events
@router.get("/{user_id}/events", response_model=Optional[List[EventResponse]])
async def get_user_events(user_id: int, session: session_type):
    query = select(User).where(User.id == user_id)
    query_result = await session.scalars(query)
    result = query_result.first()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result.events
