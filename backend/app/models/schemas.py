from pydantic import BaseModel, Field, EmailStr, GetJsonSchemaHandler, ConfigDict, BeforeValidator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Optional, List, Any, Annotated
from bson import ObjectId
from datetime import datetime, date

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

# This is a helper to allow ObjectId to be used as string in Pydantic models
def validate_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid ObjectId")

ObjectIdStr = Annotated[str, BeforeValidator(str)]

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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    fullname: str
    password: str
    passport_num: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    username: str
    fullname: str
    passport_num: Optional[str] = None
    is_admin: bool = False
    is_active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str}
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class BookingCreate(BaseModel):
    flight_code: str
    full_name: str
    passport_num: str
    credit_card: str
