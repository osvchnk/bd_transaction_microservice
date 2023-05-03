from fastapi import APIRouter, HTTPException

from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionInCreateSchema, TransactionOutCreateSchema, \
    TransactionReportCreateSchema
from app.services import *

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: int):
    transaction = await TransactionService().get_transaction_by_id(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail=f"Transaction not found")
    return transaction


@router.get("/block/{block_id}")
async def get_transactions_by_block_id(block_id: int):
    transactions = await TransactionService().get_transactions_by_block_id(block_id)
    return transactions


@router.get("")
async def get_transactions_by_user_hash(user_hash: str):
    transactions = await TransactionService().get_transaction_by_user_hash(user_hash)
    return transactions


@router.post("{transaction_id}/sign")
async def sign_transaction(transaction_id: int, user_hash: str, sign: str):
    return await TransactionService().sign_transaction(transaction_id, user_hash, sign)


@router.post("/transaction_in")
async def create_transaction_in(transaction: TransactionInCreateSchema):
    return await TransactionInService().create_transaction_in(transaction)


@router.post("/transaction_out")
async def create_transaction_out(transaction: TransactionOutCreateSchema):
    return await TransactionOutService().create_transaction_out(transaction)


@router.post("/transaction_report")
async def create_transaction_report(transaction: TransactionReportCreateSchema):
    return await TransactionReportService().create_transaction_report(transaction)


@router.put("/{transaction_id}/payment")
async def update_payment_info(transaction_id: int, payment_update: PaymentUpdate):
    return await TransactionService().update_payment_status(transaction_id, payment_update)
