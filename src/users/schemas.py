from datetime import datetime
from typing import Annotated, Optional

from pydantic import EmailStr, Field, PositiveInt

from src.schemas import CustomBase

username_type = Annotated[str, Field(..., min_length=3, max_length=20, example="username")]
password_type = Annotated[str, Field(..., min_length=5, max_length=30, example="password123")]


class UserResponse(CustomBase):
    id: PositiveInt
    username: username_type
    email: EmailStr
    is_admin: bool
    created_at: datetime


class UserCreate(CustomBase):
    username: username_type
    email: EmailStr
    password: password_type
    is_admin: bool = Field(default=False)


class UserUpdate(CustomBase):  # update user using patch (put does not allow optional fields)
    username: username_type | None
    email: Optional[EmailStr] = Field(None)
    password: password_type | None
    is_admin: Optional[bool] = Field(None)


class UserLogin(CustomBase):
    username: username_type
    password: password_type
    username: username_type
    password: password_type
