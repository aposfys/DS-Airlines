from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_admin
from app.models.schemas import UserCreate, UserModel
from app.database import db
from app.auth import get_password_hash
from typing import List

router = APIRouter()

@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def dashboard(current_user: dict = Depends(get_current_admin)):
    return {"message": f"Welcome Admin {current_user.get('sub')}"}

@router.post("/create_admin", status_code=status.HTTP_201_CREATED)
async def create_admin(user: UserCreate, current_user: dict = Depends(get_current_admin)):
    # Create new admin logic
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["is_admin"] = True

    new_user = await db.users.insert_one(user_dict)
    return {"message": "Admin created", "id": str(new_user.inserted_id)}
