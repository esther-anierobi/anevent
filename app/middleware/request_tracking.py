from uuid import uuid4
from fastapi import Request, FastAPI
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal
from app.models.requests_tracking_record import RequestsTrackingRecord


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    This middleware is to track all requests made by a user to this application.
    """
    async def dispatch(self, request: Request, call_next):
        """This tracks requests made by a user to this application."""
        database: Session = SessionLocal()
        try:
            # Extract requests client information and records
            ip_address = request.client.host if request.client else None  # extract the ip address the request was made from.
            path = request.url.path
            method = request.method
            user_agent = request.headers.get("user-agent")
            referrer = request.headers.get("referer")

            # Extract user_id from token if available
            user_id = None
            try:
                authorization_header = request.headers.get("authorization")
                if authorization_header and authorization_header.startswith("Bearer "):
                    from app.auth.auth import validate_token_for_websocket
                    token_item = authorization_header.replace("Bearer ", "")
                    user = validate_token_for_websocket(token_item, database)
                    if user:
                        user_id = user.id
            except:
                pass  # Track the request record as anonymous when token fail. To ensure app doesn't break.


            # Create each request tracking record
            made_request = RequestsTrackingRecord(
                id=str(uuid4),
                ip_address=ip_address,
                path=path,
                method=method,
                user_agent=user_agent,
                user_id=user_id,
                referrer=referrer,
            )

            # Save the requests tracking to database
            database.add(made_request)
            database.commit()
            database.refresh(made_request)

        # Now log error message without braking the requests.
        except Exception as e:
            print(f"Exception while tracking request: {str(e)}")
            database.rollback()
        finally:
            database.close()

        # Process requests
        response = await call_next(request)  # Returns a response to a made request
        return response