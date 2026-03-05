from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
import logging
from time import time
from typing import Callable, Awaitable


logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        start_time = time()

        response = await call_next(request)
        processing_time = time() - start_time
        host_port = (
            f"{request.client.host}:{request.client.port} - " if request.client else ""
        )
        message = f"{host_port}{request.method} - {request.url.path} - {response.status_code} - completed after {processing_time}s"
        print(message)
        return response

    # app.add_middleware(CORSMiddleware, allow_credentials = True, allow_headers = ["*"], allow_methods = ["*"], allow_origins = ["*"])
