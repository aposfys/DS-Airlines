from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, date

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    username: str
    fullname: str
    passport_num: Optional[str] = None
    hashed_password: str
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    fullname: str
    password: str
    passport_num: str

class UserLogin(BaseModel):
    email: str
    password: str

class FlightModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    unique_code: str
    departure: str
    destination: str
    date: str # YYYY-MM-DD
    time: str # HH:MM
    cost: float
    duration: str
    availability: int = 220
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FlightCreate(BaseModel):
    departure: str
    destination: str
    date: str
    time: str
    cost: float
    duration: str

class FlightUpdate(BaseModel):
    cost: Optional[float] = None
    availability: Optional[int] = None

class BookingModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    flight_code: str
    full_name: str
    passport_num: str
    credit_card: str
    booking_date: datetime = Field(default_factory=datetime.utcnow)
    cost: float
    departure: str
    destination: str
    flight_date: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BookingCreate(BaseModel):
    flight_code: str
    full_name: str
    passport_num: str
    credit_card: str
