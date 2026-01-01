# app/api/v1/controller/contact_controller.py

from fastapi import Request
from app.utility import ApiResponse, get_request_data
from .services import ContactService


# ------------------------ CONTACT CRUD CONTROLLER ------------------------
async def contact_controller(
    request: Request,
    auth_data
) -> ApiResponse:

    data = await get_request_data(request.headers.get("content-type", ""), request)
    outlet_id = auth_data.get("outlet_id")
    multiuser_id = auth_data.get("multiuser_id")
    data.update({
        "outlet_id": outlet_id,
        "multiuser_id": multiuser_id
    })

    method = request.method

    match method:
        case "POST":
            result, status_code = await ContactService.save(**data)
            message = "Contact saved successfully"

        case "GET":
            result, status_code = await ContactService.filter(**data)
            message = "Contacts fetched successfully"

        case "DELETE":
            result, status_code = await ContactService.delete(**data)
            message = "Contact deleted successfully"

        case "PUT":
            result, status_code = await ContactService.update(**data)
            message = "Contact updated successfully"

        case _:
            return ApiResponse(
                content={
                    "status": "error",
                    "message": "Method not allowed",
                    "code": 405,
                    "data": None
                },
                status_code=405
            )

    return ApiResponse.success(
        data=result,
        message=message,
        code=status_code
    )
