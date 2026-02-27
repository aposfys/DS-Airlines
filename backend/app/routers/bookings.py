from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.schemas import BookingModel, BookingCreate
from app.database import db
from app.auth import get_current_user
from bson import ObjectId
from datetime import date, datetime

router = APIRouter()

# Create Booking (User)
@router.post("/", response_model=BookingModel, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, current_user: dict = Depends(get_current_user)):
    flight = await db.availableFlights.find_one({"unique_code": booking.flight_code})

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight["availability"] <= 0:
        raise HTTPException(status_code=400, detail="Flight is full")

    booking_dict = booking.model_dump()
    booking_dict["user_id"] = current_user.get("sub") # Storing email/ID as reference
    booking_dict["cost"] = flight["cost"]
    booking_dict["departure"] = flight["departure"]
    booking_dict["destination"] = flight["destination"]
    booking_dict["flight_date"] = flight["date"]
    booking_dict["booking_date"] = datetime.utcnow()

    # Use transaction-like logic if possible, but basic atomic ops suffice for this scope
    # Decrement availability
    result = await db.availableFlights.update_one(
        {"unique_code": booking.flight_code, "availability": {"$gt": 0}},
        {"$inc": {"availability": -1}}
    )

    if result.modified_count == 0:
         raise HTTPException(status_code=409, detail="Flight became full during booking")

    new_booking = await db.bookings.insert_one(booking_dict)

    created_booking = await db.bookings.find_one({"_id": new_booking.inserted_id})
    return created_booking

# Get User Bookings
@router.get("/", response_model=List[BookingModel])
async def get_user_bookings(current_user: dict = Depends(get_current_user)):
    bookings = await db.bookings.find({"user_id": current_user.get("sub")}).to_list(100)
    return bookings

# Cancel Booking (User)
@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    booking = await db.bookings.find_one({"_id": ObjectId(booking_id), "user_id": current_user.get("sub")})

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.bookings.delete_one({"_id": ObjectId(booking_id)})

    # Increase availability
    await db.availableFlights.update_one(
        {"unique_code": booking["flight_code"]},
        {"$inc": {"availability": 1}}
    )

    return
