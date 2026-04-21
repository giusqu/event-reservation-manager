from typing import List, Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select

from src.database import session_type
from src.events.models import Event

from .errors import NotFoundReservationError
from .models import Reservation
from .schemas import ReservationCreate, ReservationResponse, ReservationUpdate

httpExceptionNotFound = HTTPException(status_code=404, detail="Reservation not found")
reservationNotFound = {"model": NotFoundReservationError}

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
)


@router.get("/", response_model=Optional[List[ReservationResponse]])
async def get_reservations(session: session_type):
    query = select(Reservation)
    query_result = await session.scalars(query)
    result = query_result.all()
    return result


@router.post("/", response_model=ReservationResponse, status_code=201)
async def create_reservation(payload: ReservationCreate, session: session_type):
    # check capacity first
    query = select(Event.capacity).where(Event.id == payload.event_id)
    query_result = await session.scalars(query)
    max_capacity = query_result.first()
    if not max_capacity:
        raise HTTPException(status_code=404, detail="Event not found")

    # retrieve the number of seats already booked
    query = select(Reservation.num_guests).where(Reservation.event_id == payload.event_id)
    query_result = await session.scalars(query)
    num_guests_array = query_result.all()
    num_guest = sum(num_guests_array)

    # recheck capacity
    if num_guest + payload.num_guests > max_capacity:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    # set reservation
    new_reservation = Reservation(
        num_guests=payload.num_guests, user_id=payload.user_id, event_id=payload.event_id
    )
    session.add(new_reservation)
    await session.commit()
    return new_reservation


@router.get(
    "/{reservation_id}", response_model=ReservationResponse, responses={404: reservationNotFound}
)
async def get_reservation(reservation_id: int, session: session_type):
    query = select(Reservation).where(Reservation.id == reservation_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise httpExceptionNotFound

    return result


@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int, payload: ReservationUpdate, session: session_type
):
    query = select(Reservation).where(Reservation.id == reservation_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise httpExceptionNotFound

    for field, value in payload.model_dump().items():
        if value is not None:
            setattr(result, field, value)

    await session.commit()
    return result


@router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(reservation_id: int, session: session_type):
    query = select(Reservation).where(Reservation.id == reservation_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if not result:
        raise httpExceptionNotFound

    await session.delete(result)
    await session.commit()
    return None
