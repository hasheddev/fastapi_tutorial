from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from src.db.main import init_db
from .errors import register_errors
from .middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting")
    await init_db()
    yield
    print("Server Stoping")


version = "v1"
title = "Bookly"
description = "A Rest api for a book review webservice"

app = FastAPI(description=description, title=title, version=version)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["users"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/{version}/tags", tags=["tags"])

register_errors(app)
register_middleware(app)
