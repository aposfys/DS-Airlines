from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.schemas import UserCreate, UserLogin, UserModel
from app.database import db
from app.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from datetime import timedelta
import re

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    # Check if user already exists
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    if await db.users.find_one({"passport_num": user.passport_num}):
        raise HTTPException(status_code=400, detail="Passport number already in use")

    # Basic Validation
    if len(user.password) < 8 or not re.search(r"\d", user.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 chars and contain a number")
    if len(user.passport_num) != 9 or not re.match(r"^[A-Za-z]{2}\d{7}$", user.passport_num):
        raise HTTPException(status_code=400, detail="Invalid Passport Number format (2 letters + 7 digits)")

    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["is_admin"] = False

    new_user = await db.users.insert_one(user_dict)

    return {"message": "User registered successfully", "id": str(new_user.inserted_id)}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Allow login with email or username (OAuth2 form uses 'username' field)
    user = await db.users.find_one({"$or": [{"email": form_data.username}, {"username": form_data.username}]})

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "is_admin": user.get("is_admin", False), "username": user["username"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
