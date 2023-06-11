from fastapi import APIRouter

from app.models.transaction import TrRegionEnum, TrType
from app.schemas.transaction import TransactionInCreateSchema
from app.services.transaction import TransactionService
from app.services.transaction_in import TransactionInService

router = APIRouter(
    prefix="/transactions/transaction_in",
    tags=["transaction in"]
)


@router.post("")
async def create_transaction_in(transaction: TransactionInCreateSchema):
    async with TransactionInService() as service:
        return await service.create_transaction_in(transaction)


@router.get("/region")
async def get_transaction_in_by_region(region: TrRegionEnum):
    print(region)
    async with TransactionInService() as service:
        result = await service.get_transaction_in_by_region(region)
        print(result)
        return await service.get_transaction_in_by_region(region)


@router.get("/operator")
async def get_transaction_in_by_operator_hash(operator_hash: str):
    async with TransactionInService() as service:
        return await service.get_transaction_in_by_operator_hash(operator_hash)


@router.get("/user")
async def get_transaction_in_by_user_hash(user_hash: str):
    async with TransactionService() as service:
        return await service.get_transaction_by_user_hash_and_type(user_hash=user_hash, type=TrType.IN)


@router.get("/{region}")
async def get_transactions_in_by_region_and_amount(region: TrRegionEnum, amount: int):
    async with TransactionInService() as service:
        return await service.get_transactions_by_amount(region, amount)
