from fastapi import FastAPI, Header
from typing import Optional
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def home_root():
    return {"message": "Hello World"}


@app.get("/greet/{name}")
async def greet_name(name: str):
    return {"message": f"Hello {name}"}


# /greetq?name=value   as query parameter
@app.get("/greetq")
async def greet_name_query(name: str):
    return {"message": f"Hello {name}"}


# /greetq/name?age=value  mixing path and query parameters
@app.get("/greetm/{name}")
async def greet_name_mixed(name: str, age: int):
    return {"message": f"Hello {name} your age is {age}"}


# /greetq/name?age=value&age=value  for optional query parameters
@app.get("/greeto")
async def greet_name_optional(name: Optional[str] = "User", age: int = 0):
    return {"message": f"Hello {name} your age is {age}"}


class BookCreateModel(BaseModel):
    title: str
    author: str


@app.post("/create_book")
async def create_book(book_data: BookCreateModel):
    return book_data.model_dump()


# Headers use snake case
@app.get("/headers", status_code=200)
async def headers(
    accept: str = Header(None),
    accept_encoding: str = Header(None),
    host: str = Header(None),
    user_agent: str = Header(None),
):
    request_headers = {}

    request_headers["Accept"] = accept
    request_headers["Accept-Encoding"] = accept_encoding
    request_headers["User-Agent"] = user_agent
    request_headers["Host"] = host

    return request_headers
