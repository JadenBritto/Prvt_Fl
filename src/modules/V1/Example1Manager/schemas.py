# app/schemas/contact_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ContactBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_no: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    outlet_id: str

    class Config:
        from_attributes = True


class ContactRead(ContactBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
