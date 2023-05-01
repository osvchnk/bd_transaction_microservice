from fastapi import FastAPI

from app.routers import transaction


app = FastAPI()

app.include_router(transaction.router)
