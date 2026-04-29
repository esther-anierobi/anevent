from datetime import datetime
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from app.database import Base
from app.models.enums import UserType


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, nullable=False)
    phone = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    country = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    verification_otp = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=False)
    otp_expiry = Column(DateTime, default=datetime.now(), nullable=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)


