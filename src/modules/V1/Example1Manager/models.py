# app/models/contact.py
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id         = Column(Integer, primary_key=True, index=True)
    outlet_id  = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name  = Column(String(255), nullable=True)
    phone_no   = Column(String(255), nullable=True, index=True)
    email      = Column(String(255), nullable=True, index=True)
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now()
    )
