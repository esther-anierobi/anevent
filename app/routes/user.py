from datetime import datetime
from fastapi import Depends, APIRouter, Request, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth import create_access_token
from app.auth.dependency import get_current_user
from app.models.users import User
from app.schemas.users import UserCreate, UserResponse, VerifyOTP, LoginResponse, LoginUser
from app.services.users import UserService
from app.database import get_db


router = APIRouter(prefix="/user", tags=["user"])
@router.post("/signup", status_code=200, response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """An endpoint for registering/signing up a new user."""
    return UserService.create_user(db, user)

@router.post("/verify-registered-account", status_code=200, response_model=UserResponse)
def verify_registered_account(verify_token: VerifyOTP, db: Session = Depends(get_db)):
    """An endpoint for verifying a newly registered user account."""
    return UserService.verify_user(db, verify_token)

@router.post("/login", status_code=200, response_model=LoginResponse)
def login_user(response: Response, login_data: LoginUser, db: Session = Depends(get_db)):
    """
    Log in with email and password to get an access token.
    """
    user = UserService.login_authenticated_user(db, login_data.email, login_data.password)

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": user.email})

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=access_token,
        httponly=True,
        max_age=86400,  # 24 hours in seconds
        samesite="lax",
        path="/"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.get("/user/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Not Authorized")
    return UserService.get_user_by_id(db, user_id)