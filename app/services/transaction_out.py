import hashlib
from datetime import datetime
from typing import List

from fastapi import HTTPException

from app.models.transaction import TrPaymentStatus, TrRegionEnum
from app.repositories.transaction_out import TransactionOutRepository
from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionOutCreateSchema, TransactionOutOutSchema, TransactionOutInSchema


class TransactionOutService:

    def __init__(self):
        self.repository: TransactionOutRepository = TransactionOutRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.repository.close()

    async def create_transaction_out(self, transaction: TransactionOutInSchema):
        transaction_create_schema = TransactionOutCreateSchema(**transaction.dict(exclude={'transactions_in'}))
        transaction_out = await self.repository.create(transaction_create_schema, transaction.transactions_in)
        return transaction_out

    async def get_transaction_out(self, tr_id: int):
        return await self.get_transaction_out(tr_id)

    async def get_transaction_out_by_region(self, region: TrRegionEnum) -> List[TransactionOutOutSchema]:
        result = await self.repository.get_list_by(region=region)
        transactions = list(map(lambda tr: TransactionOutOutSchema.from_orm(tr), result))
        return transactions

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionOutOutSchema:
        transaction = await self.repository.get_transaction_by_tr_id(tr_id=tr_id)
        return TransactionOutOutSchema.from_orm(transaction)

    async def update_payment_status(self, transaction_id: int, payment_update: PaymentUpdate):
        transaction_out = await self.repository.get_transaction_by_tr_id(tr_id=transaction_id)

        if transaction_out.payment_status == TrPaymentStatus.SUCCESS:
            raise HTTPException(status_code=405, detail=f"Payment status already success")

        result = await self.repository.update(transaction_out.id, payment_update.dict())

        transaction_schema = TransactionOutOutSchema.from_orm(result)
        return transaction_schema

    @staticmethod
    async def hash_transaction_out(transaction: TransactionOutOutSchema):
        general_transaction = transaction.transaction
        s = f"{general_transaction.type.value} {datetime.timestamp(general_transaction.created_at)} " \
            f"{general_transaction.user_hash} {transaction.destination_id} {transaction.region.value} " \
            f"{transaction.payment_amount} {transaction.payment_id}"

        hash = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return hash
