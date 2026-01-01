# app/services/contact_service.py
from .schemas import ContactBase
from .dao import ContactDAO


class ContactService:

    @staticmethod
    async def save(**data):
        email    = data.get("email")
        phone_no = data.get("phone_no")

        existing = await ContactDAO.get_by_email_or_phone(email, phone_no)

        contact_model = ContactBase(**data)

        if existing:
            contact_model.id = existing.id
            id_ = await ContactDAO.update_contact(contact_model)
        else:
            id_ = await ContactDAO.create_contact(contact_model)

        return {"id": id_}, 200

    @staticmethod
    async def filter(**filters):
        contacts = await ContactDAO.filter(**filters)
        contacts = [ContactBase.from_orm(c).dict() for c in contacts]
        return contacts, 200

    @staticmethod
    async def update(**data):
        id_ = await ContactDAO.update_contact(ContactBase(**data))
        return {"id": id_}, 200

    @staticmethod
    async def delete(**data):
        id_ = data.get("id")
        if not id_:
            raise ValueError("Missing 'id' for delete")
        await ContactDAO.delete_contact(int(id_))
        return {"id": id_}, 200
