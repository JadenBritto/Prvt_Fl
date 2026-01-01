# app/api/v1/api_docs/contacts_doc.py

contacts_handler = {
    "POST": {
        "summary": "Create or Upsert Contact",
        "description": (
            "**📩 Create Contact**\n\n"
            "Creates a new contact. If a contact with the same `email` or `phone_no` "
            "already exists, it will update that existing contact instead.\n\n"
            "**Fields accepted:**\n"
            "- `first_name` (optional)\n"
            "- `last_name` (optional)\n"
            "- `email` (optional — one of email or phone required)\n"
            "- `phone_no` (optional — one of email or phone required)\n"
            "- `description` (optional)\n\n"
            "**Context:**\n"
            "- `outlet_id` and `multiuser_id` are automatically extracted from JWT.\n\n"
            "**Returns:** Contact ID and status.\n"
        ),
        "openapi_extra": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "example": {
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john@example.com",
                            "phone_no": "+123456789",
                            "description": "Important customer"
                        }
                    }
                }
            }
        },
    },

    "GET": {
        "summary": "List / Filter Contacts",
        "description": (
            "**📄 Fetch Contacts**\n\n"
            "Returns a list of contacts. You may pass filter fields (such as email, phone_no, first_name) "
            "in request body or query params.\n\n"
            "**Context:**\n"
            "- `outlet_id` and `multiuser_id` come from JWT.\n\n"
            "**Returns:** List of contacts matching filter criteria."
        ),
        "openapi_extra": {},
    },

    "PUT": {
        "summary": "Update Contact",
        "description": (
            "**🔧 Update Contact**\n\n"
            "Updates an existing contact. Must include `id` in the request body.\n\n"
            "**Example fields:**\n"
            "- `first_name`\n"
            "- `last_name`\n"
            "- `email`\n"
            "- `phone_no`\n"
            "- `description`\n\n"
            "**Context:** Extracted from JWT.\n"
        ),
        "openapi_extra": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "example": {
                            "id": 12,
                            "first_name": "John Updated",
                            "description": "Updated notes"
                        }
                    }
                }
            }
        },
    },

    "DELETE": {
        "summary": "Delete Contact",
        "description": (
            "**🗑️ Delete Contact**\n\n"
            "Deletes a contact record. Provide the contact `id` in the body or inside "
            "query parameters.\n\n"
            "**Returns:** Deleted contact ID."
        ),
        "openapi_extra": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "example": {
                            "id": 12
                        }
                    }
                }
            }
        },
    },
}
