from fastapi import APIRouter

from app.models.transaction import TrRegionEnum, TrType
from app.schemas.transaction import TransactionReportCreateSchema
from app.services.transaction import TransactionService
from app.services.transaction_report import TransactionReportService


router = APIRouter(
    prefix="/transactions/transaction_report",
    tags=["transaction report"]
)


@router.post("")
async def create_transaction_report(transaction: TransactionReportCreateSchema):
    async with TransactionReportService() as service:
        return await service.create_transaction_report(transaction)


@router.get("/region")
async def get_transaction_report_by_region(region: TrRegionEnum):
    async with TransactionReportService() as service:
        return await service.get_transaction_report_by_region(region)


@router.get("/user")
async def get_transaction_report_by_user_hash(user_hash: str):
    async with TransactionService() as service:
        return await service.get_transaction_by_user_hash_and_type(user_hash=user_hash, type=TrType.REPORT)
