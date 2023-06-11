from fastapi import APIRouter

from app.models.transaction import TrRegionEnum, TrType
from app.schemas.transaction import TransactionOutCreateSchema, TransactionOutInSchema
from app.services.transaction import TransactionService
from app.services.transaction_in import TransactionInService
from app.services.transaction_out import TransactionOutService

router = APIRouter(
    prefix="/transactions/transaction_out",
    tags=["transaction out"]
)


@router.post("")
async def create_transaction_out(transaction: TransactionOutInSchema):
    async with TransactionOutService() as service:
        transaction_out = await service.create_transaction_out(transaction)
    return transaction_out


@router.get("/region")
async def get_transaction_out_by_region(region: TrRegionEnum):
    async with TransactionOutService() as service:
        return await service.get_transaction_out_by_region(region)


@router.get("/user")
async def get_transaction_out_by_user_hash(user_hash: str):
    async with TransactionService() as service:
        return await service.get_transaction_by_user_hash_and_type(user_hash=user_hash, type=TrType.OUT)
