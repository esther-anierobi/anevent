from datetime import datetime, timedelta

from fastapi import Request, Response, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from app.auth.auth import bearer_scheme, SECRET_KEY, ALGORITHM, INACTIVITY_TIMEOUT_MINUTES, update_token_activity
from app.database import get_db
from app.models.users import User


# This function is all about Authorisation (i.e. User Permissions)
def get_current_user(
        response: Response,
        db: Session = Depends(get_db),
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> User:
    # exception handling for wrong user credentials. Authorisation error handling
    user_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Very user token
        token_data = jwt.decode(
            token.credentials,
            SECRET_KEY, algorithms=[ALGORITHM]
        )
        email = token_data.get("sub")
        if email is None:
            raise user_credentials_exception

        # Verify token inactivity timeout
        last_activity = token_data.get("last_activity")
        if last_activity is not None:
            last_activity = float(last_activity)
            last_activity = datetime.fromtimestamp(last_activity)
            if last_activity + timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token expired due to inactivity",
                    headers={"WWW-Authenticate": "Bearer"}
                )


        # Get user from the database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise user_credentials_exception


        # Update token last activity timestamp and set as a new one
        update_token = update_token_activity(token.credentials)
        if update_token:
            # Set the updated token in the response header
            response.headers["Authorization"] = f"Bearer {update_token}"

        return user

    except JWTError:
        raise user_credentials_exception