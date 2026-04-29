
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.auth import get_password_hash, verify_password
from app.models.users import User
from app.schemas.users import UserCreate, VerifyOTP
from app.utils.otp import generate_otp


class UserService:
    @staticmethod
    def create_user(db: Session , user_data: UserCreate) -> User:
        """A service to create a new user"""
        # Check if user with the email already exists
        user = db.query(User).filter(func.lower(User.email) == func.lower(user_data.email)).first()
        if user:
            raise HTTPException(status_code=400, detail="User with the email already registered")

        # Generate verification otp
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=10)

        #create user object
        user_dict = user_data.model_dump()
        user_dict['email'] = user_dict['email'].lower()
        user_dict['password'] = get_password_hash(user_dict['password'])
        user_id = str(uuid4())
        user_obj = User(
            id=user_id,
            verification_otp=otp,
            otp_expiry=otp_expiry,
            **user_dict
        )

        # Save user to database
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)

        return user_obj


    @staticmethod
    def verify_user(db: Session, otp:VerifyOTP) -> User:
        """A service to verify a new user with the email and sent otp"""
        user = db.query(User).filter(func.lower(User.email) == func.lower(otp.email)).first()
        if not user:
            raise HTTPException(status_code=400, detail="User with the email not found")
        if user.verification_otp != otp.verification_otp:
            raise HTTPException(status_code=400, detail="Verification OTP does not match (Invalid)")
        if datetime.now() > user.otp_expiry:
            raise HTTPException(status_code=400, detail="OTP has expired")

        user.is_active = True
        user.verification_otp = None
        user.otp_expiry = None

        db.commit()
        return user


    @staticmethod
    def login_authenticated_user(db: Session, email: str, password: str) -> User:
        """A function to authenticate a user for login"""
        user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="User with the email not found")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return user

    @staticmethod
    def get_user_by_id(
            db: Session,
            user_id:str
    ):
        # Get a user by id
        # First check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User with the id does not exist")

        return user