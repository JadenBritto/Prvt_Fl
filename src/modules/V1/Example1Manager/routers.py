# app/api/v1/routes/contacts.py

from fastapi import APIRouter, Depends, Request
from app.project_schemas import APIResponse
from app.utility import ApiResponse
from app.auth import verify_jwt_token

from .controller import contact_controller
from .api_docs import contacts_handler

router = APIRouter()

# -------------------- CREATE (POST) --------------------
@router.api_route(
    "/contacts",
    methods=["POST"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=contacts_handler["POST"]["summary"],
    description=contacts_handler["POST"]["description"],
    openapi_extra=contacts_handler["POST"]["openapi_extra"],
)
async def create_contact(
    request: Request,
    auth_data: dict = Depends(verify_jwt_token),
):
    return await contact_controller(request, auth_data)


# -------------------- LIST / FILTER (GET) --------------------
@router.api_route(
    "/contacts",
    methods=["GET"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=contacts_handler["GET"]["summary"],
    description=contacts_handler["GET"]["description"],
    openapi_extra=contacts_handler["GET"]["openapi_extra"],
)
async def list_contacts(
    request: Request,
    auth_data: dict = Depends(verify_jwt_token),
):
    return await contact_controller(request, auth_data)


# -------------------- UPDATE (PUT) --------------------
@router.api_route(
    "/contacts",
    methods=["PUT"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=contacts_handler["PUT"]["summary"],
    description=contacts_handler["PUT"]["description"],
    openapi_extra=contacts_handler["PUT"]["openapi_extra"],
)
async def update_contact(
    request: Request,
    auth_data: dict = Depends(verify_jwt_token),
):
    return await contact_controller(request, auth_data)


# -------------------- DELETE (DELETE) --------------------
@router.api_route(
    "/contacts",
    methods=["DELETE"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=contacts_handler["DELETE"]["summary"],
    description=contacts_handler["DELETE"]["description"],
    openapi_extra=contacts_handler["DELETE"]["openapi_extra"],
)
async def delete_contact(
    request: Request,
    auth_data: dict = Depends(verify_jwt_token),
):
    return await contact_controller(request, auth_data)
