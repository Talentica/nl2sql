import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.services.get_analytics import get_analytics

app = FastAPI()

origins = os.getenv("CORS_ORIGINS").split(",")
allow_methods = os.getenv("CORS_ALLOW_METHODS").split(",")
allow_headers = os.getenv("CORS_ALLOW_HEADERS").split(",")
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS") == "True"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)


class RequestData(BaseModel):
    question: str
    request_id: str


@app.post("/answer")
async def answer(request_data: RequestData):
    return get_analytics(request_data.question, request_data.request_id)
