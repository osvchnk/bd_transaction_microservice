from fastapi import APIRouter, HTTPException

from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionInCreateSchema, TransactionOutCreateSchema, \
    TransactionReportCreateSchema, TransactionAllInfoSchema
from app.services.transaction import TransactionService


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get("/")
async def get_transactions():
    return await TransactionService().get_transactions()


@router.get("/{transaction_id}")
async def get_transactions(transaction_id: int) -> TransactionAllInfoSchema:
    transaction = await TransactionService().get_transaction_by_id(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail=f"Transaction not found")
    return transaction


@router.post("/sign")
async def sign_transaction(tr_id: int, user_hash: str, sign: str):
    return await TransactionService().sign_transaction(tr_id, user_hash, sign)


@router.post("/transaction_in")
async def create_transaction_in(transaction: TransactionInCreateSchema):
    return await TransactionService().create_transaction_in(transaction)


@router.post("/transaction_out")
async def create_transaction_out(transaction: TransactionOutCreateSchema):
    return await TransactionService().create_transaction_out(transaction)


@router.post("/transaction_report")
async def create_transaction_report(transaction: TransactionReportCreateSchema):
    return await TransactionService().create_transaction_report(transaction)


@router.put("/{transaction_id}/payment")
async def update_payment_info(transaction_id: int, payment_update: PaymentUpdate):
    return await TransactionService().update_payment_status(transaction_id, payment_update)
