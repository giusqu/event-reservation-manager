from datetime import datetime
from typing import List

from passlib.context import CryptContext
from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

psw_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password: Mapped[str] = mapped_column(Text)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # server-side timestamp; otherwise, client-side with timezone
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # cascade to delete all events associated with a user when the user is deleted
    # # delete-orphan to remove orphaned events (events with no associated user)
    events: Mapped[List["Event"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined"
    )
    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def password_setter(self):
        raise AttributeError("Password is write-only!")

    @password_setter.setter
    def password_setter(self, password: str) -> None:
        self.password = psw_context.hash(password)

    def check_password(self, password: str) -> bool:  # plaintext password
        return psw_context.verify(password, self.password)
