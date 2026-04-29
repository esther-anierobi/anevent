import os
import secrets
from datetime import timedelta, datetime
from typing import Optional

from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.users import User

# Authentication Configuration.
# Generate a secure random key as fallback if environment variable is not set.
# This ensures a strong random key is always used,even in development.

DEFAULT_SECRET_KEY = secrets.token_hex(32)
SECRET_KEY = os.getenv('SECRET_KEY', DEFAULT_SECRET_KEY)
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_HOURS = 24  # Increased to expire at 24 hours
INACTIVITY_TIMEOUT_MINUTES = 60  # Token will expire after 1 hour of inactivity


# Print warning especially if using the default key (helpful in development)
if os.getenv("SECRET_KEY") is None:
    print("WARNING: using auto-generated SECRET_KEY, set SECRET_KEY variable in production.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


# Alternative Token validation for WebSockets
# This is simple implementation for demonstration. Use a proper token store in production
_websocket_tokens = {}   # In-memory store of tokens -> user_id mappings

# Password hashing configuration
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:72])

#===============================

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    # set the token creation time
    to_encode.update({"iat": datetime.now().timestamp()})
    # set the last activity time to time of creation
    to_encode.update({"last activity": datetime.now().timestamp()})
    # set expiring time for long term token
    expire = datetime.now() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # store a mapping for a websocket (simple approach)
    if "map_email" in data:
        _websocket_tokens[token] = data["map_email"]  # Mapping the token to user email
    return token


def update_token_activity(token: str) -> str:
    """Update token last activity timestamp and return a new token string"""
    try:
        # Manually decode the token without verifying the expiration.
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_expiry": False})

        # Check if the token has expired based on the expiration field
        if datetime.fromtimestamp(token_data.get("exp")) > datetime.now():
            return None

        # Check if the token is timeout due to inactivity
        last_activity = datetime.fromtimestamp(token_data.get("last_activity"))
        if last_activity + timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES) < datetime.now():
            return None

        # Update the last activity timestamp
        token_data.update({"last_activity": datetime.now().timestamp()})

        # Now return a new token with the updated timestamp
        new_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Update the stored websocket token mapping
        if token in _websocket_tokens:
            _websocket_tokens[new_token] = _websocket_tokens[token]
            del _websocket_tokens[token]
        return new_token
    except JWTError:
        return None


def validate_token_for_websocket(token: str, db: Session) -> Optional[User]:
    """
    Purpose: validate a token for websocket connection and return a user object if it exists or None otherwise
    it has 2 different validation approaches:
    a. validate the token from in-memory storage
    b. JWT validation
    """
    # First attempt with JWT Validation
    try:
        print(f"Attempting to validate token SECRET_KEY: {SECRET_KEY[:5]}...")
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = token_data.get("sub")
        print(f"Token successfully validated/decoded. Email from token: {email}")

        if email:
            user = db.query(User).filter(User.email == email).first()
            if user:
                print(f"User already exists: {user.id}")
                return user
            else:
                print(f"No user found for email: {email}")
        else:
            print(f"Token does not contain 'sub'. Claim with email.")
    except JWTError as e:
        print(f"JWT validation failed. validation error: {str(e)}")

    # Second token validation from in-memory storage
    print(f"Checking in-memory token storage. Token in storage: {len(_websocket_tokens)}")
    if token in _websocket_tokens:
        email = _websocket_tokens[token]
        print(f"Token found in websocket storage.")
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User found in in-memory token storage: {user.id}")
            return user
        else:
            print(f"No user found in in-memory storage for email: {email}")
    else:
        print(f"Token not found in in-memory storage")


    # Print all token failed message if both methods failed
    print(f"All Token validation attempts failed.")
    return None