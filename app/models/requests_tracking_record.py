from datetime import datetime

from sqlalchemy import Column, String, DateTime

from app.database import Base


class RequestsTrackingRecord(Base):
    __tablename__ = "requests_tracking_record"

    id = Column(String, primary_key=True, index=True)
    ip_address = Column(String, nullable=True)
    path = Column(String, nullable=True)
    method = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), index=True)

    def __repr__(self):
        return f"<RequestsTrackingRecord {self.id} - {self.path}, {str(self.ip_address)}>"

