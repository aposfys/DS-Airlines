from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.schemas import FlightModel, FlightCreate, FlightUpdate, BookingModel, BookingCreate
from app.database import db
from app.auth import get_current_user
from bson import ObjectId
from datetime import date, datetime

router = APIRouter()

# Search Flights
@router.get("/", response_model=List[FlightModel])
async def search_flights(
    departure: Optional[str] = None,
    destination: Optional[str] = None,
    date: Optional[str] = None
):
    query = {}
    if departure:
        query["departure"] = {"$regex": departure, "$options": "i"} # Case-insensitive partial match
    if destination:
        query["destination"] = {"$regex": destination, "$options": "i"}
    if date:
        query["date"] = date

    flights = await db.availableFlights.find(query).to_list(100)
    return flights

@router.get("/{unique_code}", response_model=FlightModel)
async def get_flight(unique_code: str):
    flight = await db.availableFlights.find_one({"unique_code": unique_code})
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

# Create Flight (Admin Only)
@router.post("/", response_model=FlightModel, status_code=status.HTTP_201_CREATED)
async def create_flight(flight: FlightCreate, current_user: dict = Depends(get_current_user)):
    # Check if admin
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Generate unique code logic
    # Example: Athens->Berlin on 2022-09-08 at 14:00 -> AB22090814
    dep_code = flight.departure[0].upper() if flight.departure else 'X'
    dest_code = flight.destination[0].upper() if flight.destination else 'X'

    # Assuming date is YYYY-MM-DD
    try:
        date_part = flight.date.replace('-', '')[2:] # YYMMDD
        time_part = flight.time.replace(':', '')[:2] # HH
        unique_code = f"{dep_code}{dest_code}{date_part}{time_part}"
    except IndexError:
        unique_code = f"FLIGHT{int(datetime.utcnow().timestamp())}"

    # Check if exists
    if await db.availableFlights.find_one({"unique_code": unique_code}):
        raise HTTPException(status_code=400, detail="Flight with this code already exists")

    flight_dict = flight.model_dump()
    flight_dict["unique_code"] = unique_code
    flight_dict["availability"] = 220
    flight_dict["created_at"] = datetime.utcnow()

    new_flight = await db.availableFlights.insert_one(flight_dict)
    created_flight = await db.availableFlights.find_one({"_id": new_flight.inserted_id})
    return created_flight

# Update Flight (Admin Only)
@router.put("/{unique_code}", response_model=FlightModel)
async def update_flight(unique_code: str, flight_update: FlightUpdate, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    flight = await db.availableFlights.find_one({"unique_code": unique_code})
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # Validation: Only allow price update if flight is empty (220 seats)
    if flight_update.cost is not None and flight["availability"] != 220:
         raise HTTPException(status_code=400, detail="Cannot update price of non-empty flight")

    update_data = flight_update.model_dump(exclude_unset=True)

    if update_data:
        await db.availableFlights.update_one(
            {"unique_code": unique_code},
            {"$set": update_data}
        )

    updated_flight = await db.availableFlights.find_one({"unique_code": unique_code})
    return updated_flight

# Delete Flight (Admin Only)
@router.delete("/{unique_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(unique_code: str, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.availableFlights.delete_one({"unique_code": unique_code})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Flight not found")

    return
