# apps/V1/routers.py
from fastapi import APIRouter

# Import each module router
from apps.V1.Example1Manager.routers import router as example_manager_router


router = APIRouter()

# Attach module routes
router.include_router(example_manager_router, prefix="/example_manager", tags=["example_manager"])
