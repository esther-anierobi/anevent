from datetime import datetime
from typing import List

from fastapi import Depends, APIRouter, Request, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth import create_access_token
from app.auth.dependency import get_current_user
from app.models.enums import UserType
from app.models.users import User
from app.schemas.users import UserCreate, UserResponse, VerifyOTP, LoginResponse, LoginUser, UpdateUser
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

@router.get("/users", response_model=List[UserResponse])
def get_users(
        db: Session = Depends(get_db),
        skip: int = 0, limit: int = 100,
        current_user: User = Depends(get_current_user)
):
    """Get all users"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Unauthorised! Only Admin users can get total users")

    return UserService.get_users(db, skip, limit)

@router.get("/user/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService.get_user_by_id(db, user_id)

@router.put("/user/{user_id}", response_model=UserResponse)
def update_user(
        user_id: str,
        user_data: UpdateUser,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update an existing user in the database"""
    # Only user or admin are authorized
    if current_user.id != user_id and current_user.user_type != UserType.ADMIN :
        raise HTTPException(status_code=403, detail=f"Only Admin users or user with this id {user_id} can update users")

    return UserService.update_user( user_id, db, user_data)

@router.delete("/user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete an existing user in the database"""
    # Only Admin users can delete
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin users can delete users")

    # Check if the user to be deleted exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserService.delete_user(user_id, db)