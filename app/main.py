from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import transaction, transaction_in, transaction_out, transaction_report

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:8004",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction.router)
app.include_router(transaction_in.router)
app.include_router(transaction_out.router)
app.include_router(transaction_report.router)
