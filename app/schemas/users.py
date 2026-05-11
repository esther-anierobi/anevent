from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.enums import UserType


class UserBase(BaseModel):
    name: str
    email: str
    password: str
    is_active: Optional[bool] = False
    phone: str
    user_type: UserType
    is_verified: Optional[bool] = False
    profile_image: Optional[str] = None
    country: str
    city: str
    address: Optional[str] = None


class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str
    is_active: Optional[bool] = False
    country: str
    city: str
    address: Optional[str] = None
    verification_otp: Optional[str] = None
    is_verified: Optional[bool] = False
    otp_expiry: Optional[datetime] = None
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes = True
    )


class VerifyOTP(BaseModel):
    email: str
    verification_otp: Optional[str] = None


class LoginUser(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class UpdateUser(BaseModel):
    name: Optional[str] = None
    email:Optional[str] = None
    phone: Optional[str]
    is_active: Optional[bool] = False
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None