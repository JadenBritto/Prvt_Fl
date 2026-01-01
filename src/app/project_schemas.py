from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, Field
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional, Dict, Any

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    code: int
    message: str
    status: str
    data: Optional[T] = None

    @classmethod
    def success(cls, message: str = "Success", data: Optional[T] = None, code: int = 200):
        return cls(code=code, message=message, status="success", data=data)

    @classmethod
    def error(cls, message: str = "Something went wrong", code: int = 400):
        return cls(code=code, message=message, status="error", data=None)

