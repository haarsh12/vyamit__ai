from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
import os

# 1. Configuration
# We try to get the secret from .env, otherwise use a default (unsafe) one
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-this-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 Days

# 2. Security scheme for Bearer token
security = HTTPBearer()

# 3. Function to Create a Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a JWT Token.
    data: Dictionary containing user info (e.g., {"sub": "user_id"})
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 4. Function to Verify Token and Get Current User
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validates JWT Token and returns the current user.
    This is used as a dependency in protected routes.
    
    Usage in routes:
    @router.get("/protected")
    def protected_route(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        return {"user_id": current_user.id}
    """
    # Import here to avoid circular imports
    from app.db.models import User
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from Bearer credentials
        token = credentials.credentials
        
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            print("DEBUG: Token payload missing 'sub' field")
            raise credentials_exception
            
    except JWTError as e:
        print(f"DEBUG: JWT Error: {e}")
        raise credentials_exception
    
    # Return the user_id - the actual user lookup will happen in the endpoint
    # This is a partial user object that contains just the ID
    class UserStub:
        def __init__(self, user_id: int):
            self.id = user_id
    
    print(f"DEBUG: Token validated for user ID: {user_id}")
    return UserStub(int(user_id))