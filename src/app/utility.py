import sys
import httpx
import orjson
import asyncio
import logging
import traceback
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import Response
from typing import Optional, Any, Union ,Generic ,TypeVar

from src.app.settings import get_settings

logger = logging.getLogger("uvicorn.error")

# ------------------------------------------------------------ GLOBAL PROJECT TIME ----------------------------------------------

def utcnow() -> datetime:
    """
    Returns the current UTC datetime.

    NOTE:
        Always use this function throughout the project instead of
        `datetime.now()` or `datetime.utcnow()` to ensure consistent 
        UTC timestamps across all tables, services, and logs.
    """
    return datetime.now(timezone.utc)


T = TypeVar("T")

class ApiResponse(Response, Generic[T]):
    media_type = "application/json"
    def render(self, content: any) -> bytes:
        return orjson.dumps(content)
    

async def exception_handler(e: Exception,request: Optional[Request] = None,data: Optional[Union[dict, str]] = None) -> str:
    tb_str     = traceback.format_exception(type(e), e, e.__traceback__)
    tb_message = ''.join(tb_str)
    request_data: Any = None
    if request:
        try:
            if request.method == "POST":
                request_data = await request.json()
            else:
                request_data = dict(request.query_params)
        except Exception as ex:
            request_data = f"<failed to extract request data: {ex}>"
    else:
        request_data = data

    print("================================================================================")
    print("🚨 Source:\n",f"[{request.method}] {str(request.url)}")
    print("📦 Request data:\n", request_data)
    print("💥 An error occurred:\n", tb_message, file=sys.stderr)
    print("================================== ERROR =======================================")

    # logger.error("Exception caught", extra={"Source":f"[{request.method}] {str(request.url)}","request_data": request_data, "traceback": tb_message})
    return tb_message





async def get_request_data(content_type,request):
    if request.method in ["GET", "DELETE"]:
        data = dict(request.query_params)
        if "id" in data:
            try:
                data["id"] = int(data["id"])
            except ValueError:
                raise ValueError("Query param 'id' must be an integer")
        return data
    else:
        if "application/json" in content_type:
            body = await request.body()
            return orjson.loads(body) if body else {}
        elif "multipart/form-data" in content_type:
            form = await request.form()
            return dict(form)
    raise ValueError(f"Unsupported Content-Type: {content_type}")



class HttpClient:
    """
    A lightweight asynchronous HTTP client wrapper built on top of `httpx.AsyncClient`.

    This client provides:
    - Automatic retry logic with exponential backoff (2^n seconds)
    - Consistent request handling across the project
    - Connection pooling via a persistent `AsyncClient`
    - Clean context-manager interface using `async with`
    - Proper error categorization:
        ✔ Network errors → retry
        ✔ 5xx server errors → retry
        ✔ 4xx client errors → raise immediately (no retry)

    NOTE:
        Use this HttpClient for **all outbound API calls** across the project
        (Google APIs, Facebook APIs, WhatsApp Cloud API, internal microservices, etc.)
        to ensure consistent retry behavior and connection reuse.

        Do NOT create `httpx.AsyncClient()` manually in other files. Always use this class
        so that connection pooling, timeouts, and retries remain consistent everywhere.

    Usage Example:
        async with HttpClient(retries=3, timeout=10) as client:
            # GET request
            response = await client.get(
                "https://api.example.com/data",
                params={"key": "value"}
            )
            data = response.json()

        async with HttpClient() as client:
            # POST request
            response = await client.post(
                "https://api.example.com/create",
                json={"name": "John Doe", "email": "john@example.com"}
            )

        async with HttpClient() as client:
            # PUT request
            response = await client.put(
                "https://api.example.com/update/1",
                json={"name": "Updated Name"}
            )

        async with HttpClient() as client:
            # DELETE request
            response = await client.delete("https://api.example.com/delete/1")

    When to Use:
        - External API integrations
        - Internal microservice communication
        - Requests requiring resilience and retry logic
        - Any call where network reliability is a concern

    When NOT to Use:
        - For high-throughput streaming (use httpx.Stream instead)
        - For synchronous (non-async) code (use httpx.Client)

    Parameters:
        retries (int): Number of retry attempts (default: 3)
        timeout (int): Timeout for requests in seconds (default: 10)

    Returns:
        httpx.Response: The HTTP response object
    """
    def __init__(self, retries: int = 3, timeout: int = 10):
        self.retries = retries
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        for attempt in range(1, self.retries + 1):
            try:
                resp = await self.client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except httpx.RequestError as e:
                wait_time = 2 ** (attempt - 1)
                print(f"[Attempt {attempt}/{self.retries}] Network error: {e}. Retrying in {wait_time}s...")
                if attempt < self.retries:
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    raise
                wait_time = 2 ** (attempt - 1)
                print(f"[Attempt {attempt}/{self.retries}] API error: {e}. Retrying in {wait_time}s...")
                if attempt < self.retries:
                    await asyncio.sleep(wait_time)
                else:
                    raise

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("DELETE", url, **kwargs)

    async def aclose(self):
        await self.client.aclose()
