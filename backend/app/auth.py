from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "your-super-secret-key-change-this-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt requires bytes
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        # If password is too long for bcrypt (>72 bytes) or other error
        return False

def get_password_hash(password: str) -> str:
    # bcrypt has a 72 byte limit for passwords
    # If longer, we could pre-hash or truncate.
    # Here we check length and raise error if too long to be safe.
    pw_bytes = password.encode('utf-8')
    if len(pw_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 72 bytes or less"
        )
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Normally we would fetch user from DB here to confirm existence,
    # but for simplicity we rely on JWT content or inject DB dependency if needed.
    return payload

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    # Check if user is active (logic can be expanded)
    return current_user

async def get_current_admin(current_user: dict = Depends(get_current_active_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform this action"
        )
    return current_user
