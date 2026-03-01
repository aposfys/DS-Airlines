from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import get_password_hash, create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import db
from datetime import timedelta
from typing import Annotated, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    try:
        # Validate uniqueness
        if await db.users.find_one({"email": user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if await db.users.find_one({"username": user.username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user document
        user_dict = user.model_dump()
        user_dict["password"] = hashed_password
        
        # Insert user
        new_user = await db.users.insert_one(user_dict)
        
        # Fetch created user
        created_user = await db.users.find_one({"_id": new_user.inserted_id})
        
        return created_user

    except HTTPException:
        # Re-raise HTTPExceptions as is
        raise
    except Exception as e:
        # Log unexpected errors and return 500
        logger.error(f"Error registering user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )

# To support both OAuth2 form data (for Swagger UI) and JSON (for frontend), we can make dependency optional or create separate endpoint.
# But clearer is to have /token for OAuth2 (form data) and /login for App (JSON).
# However, modifying frontend is harder if I don't see it fully.
# The previous code used OAuth2PasswordRequestForm.
# I will change /login to accept JSON body using UserLogin model.
# And add /token endpoint for Swagger UI using OAuth2PasswordRequestForm.

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    try:
        user = await db.users.find_one({"username": user_login.username})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(user_login.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await db.users.find_one({"username": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
