from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import SignRequest
from app.services.transaction import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get("/all")
async def get_transactions_by_user_hash(user_hash: str):
    async with TransactionService() as service:
        transactions = await service.get_transaction_by_user_hash(user_hash)
    return transactions


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: int):
    async with TransactionService() as service:
        transaction = await service.get_transaction_by_id(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail=f"Transaction not found")
    return transaction


@router.post("/{transaction_id}/sign")
async def sign_transaction(transaction_id: int, sign_data: SignRequest):
    async with TransactionService() as service:
        return await service.sign_transaction(transaction_id, sign_data.user_hash, sign_data.sign)


@router.put("/{transaction_id}/payment")
async def update_payment_info(transaction_id: int, payment_update: PaymentUpdate):
    async with TransactionService() as service:
        return await service.update_payment_status(transaction_id, payment_update)


@router.get("/block/{block_id}")
async def get_transactions_by_block_id(block_id: int):
    async with TransactionService() as service:
        transactions = await service.get_transactions_by_block_id(block_id)
    return transactions


@router.get("/all/{hashes}")
async def get_transactions_by_hash(hashes: str):
    hash_list = hashes.split(',')
    async with TransactionService() as service:
        transactions = await service.get_transactions_by_hash(hash_list)
    return transactions
