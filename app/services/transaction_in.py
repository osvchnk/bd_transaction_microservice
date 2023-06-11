import hashlib
import json
from datetime import datetime
from typing import List

from fastapi import HTTPException

from app.algorithms.subset_sum import subset_sum_recursive
from app.models.transaction import TrPaymentStatus, TrRegionEnum, TransactionOut
from app.repositories.transaction_in import TransactionInRepository
from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionInCreateSchema, TransactionInOutSchema


class TransactionInService:

    def __init__(self):
        self.repository: TransactionInRepository = TransactionInRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.repository.close()

    async def create_transaction_in(self, transaction: TransactionInCreateSchema):
        return await self.repository.create(transaction)

    async def get_transaction_in(self, id: int):
        transaction = await self.repository.get_transaction_by_id(id)
        return TransactionInOutSchema.from_orm(transaction)

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionInOutSchema:
        transaction = await self.repository.get_transaction_by_tr_id(tr_id=tr_id)
        return TransactionInOutSchema.from_orm(transaction)

    async def get_transaction_in_by_region(self, region: TrRegionEnum) -> List[TransactionInOutSchema]:
        result = await self.repository.get_list_by(region=region)
        transactions = list(map(lambda tr: TransactionInOutSchema.from_orm(tr), result))
        return transactions

    async def get_transaction_in_by_operator_hash(self, operator_hash: str) -> List[TransactionInOutSchema]:
        result = await self.repository.get_list_by(operator_hash=operator_hash)
        transactions = list(map(lambda tr: TransactionInOutSchema.from_orm(tr), result))
        return transactions

    async def update_payment_status(self, tr_id: int, payment_update: PaymentUpdate) -> TransactionInOutSchema:
        transaction_in = await self.repository.get_transaction_by_tr_id(tr_id=tr_id)

        if transaction_in.payment_status == TrPaymentStatus.SUCCESS:
            # raise exception if payment status is already success
            raise HTTPException(status_code=405, detail=f"Payment status already success")

        result = await self.repository.update(transaction_in.id, payment_update.dict())

        transaction_schema = TransactionInOutSchema.from_orm(result)
        return transaction_schema

    async def get_transactions_by_amount(self, region: TrRegionEnum, amount: int) -> \
            List[TransactionInOutSchema] | None:

        result = await self.repository.get_transactions_not_spent_by_region(region)
        transactions = list(map(lambda tr: TransactionInOutSchema.from_orm(tr), result))

        filtered_transactions = []
        transaction_amounts = []
        for tr in transactions:
            if tr.transaction.tr_sign is None or tr.payment_status != TrPaymentStatus.SUCCESS:
                continue
            else:
                filtered_transactions.append(tr)
                transaction_amounts.append(tr.payment_amount)

        result = subset_sum_recursive(transaction_amounts, amount)

        pay_transactions = []
        for tr in filtered_transactions:
            if tr.payment_amount in result:
                pay_transactions.append(tr)
                result.remove(tr.payment_amount)
            if result is []:
                break
        return pay_transactions

    @staticmethod
    async def hash_transaction_in(transaction: TransactionInOutSchema) -> str:
        general_transaction = transaction.transaction
        s = f"{general_transaction.type.value} {datetime.timestamp(general_transaction.created_at)} " \
            f"{general_transaction.user_hash} {transaction.operator_hash} {transaction.region.value} " \
            f"{transaction.num_tourist} {transaction.period_start} {transaction.period_end}" \
            f"{transaction.payment_amount} {transaction.payment_id}"

        hash = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return hash


if __name__ == "__main__":
    s = datetime.now().replace(microsecond=0).isoformat()
    print(s)
    j = json.dumps({'s': s})
    hash = hashlib.sha256(j.encode('utf-8')).hexdigest()
    print(hash)
