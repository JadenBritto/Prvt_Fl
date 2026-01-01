# app/dao/contact_dao.py
from sqlalchemy import select, or_
from typing import Optional, Any, List

from app.database import fetch_one, fetch_all, create, update, delete_by_id
from .models import Contact
from app.schemas.contact_schema import ContactBase


class ContactDAO:

    @staticmethod
    async def get_by_id(contact_id: int) -> Optional[Contact]:
        query = select(Contact).where(Contact.id == contact_id)
        return await fetch_one(query)

    @staticmethod
    async def get_by_email_or_phone(email: str, phone: str) -> Optional[Contact]:
        query = select(Contact).where(
            or_(Contact.email == email, Contact.phone_no == phone)
        )
        return await fetch_one(query)

    @staticmethod
    async def filter(**filters: Any) -> List[Contact]:
        conditions = [
            getattr(Contact, key) == value for key, value in filters.items()
        ]
        query = select(Contact).where(*conditions)
        return await fetch_all(query)

    @staticmethod
    async def get_all() -> List[Contact]:
        query = select(Contact)
        return await fetch_all(query)

    @staticmethod
    async def create_contact(contact: ContactBase) -> int:
        model = Contact(**contact.dict())
        return await create(model)

    @staticmethod
    async def update_contact(contact: ContactBase) -> int:
        model = Contact(**contact.dict())
        return await update(model)

    @staticmethod
    async def delete_contact(contact_id: int) -> None:
        await delete_by_id(Contact, id=contact_id)
