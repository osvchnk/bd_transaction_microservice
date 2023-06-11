from datetime import datetime
from typing import List

from fastapi import HTTPException

from app.models.transaction import TrPaymentStatus, TrType
from app.rabbit.pika_client import PikaPublisher
from app.repositories import *
from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionOutOutSchema, TransactionInOutSchema, TransactionReportOutSchema
from app.services.schema_converter import TransactionSchemaConverter
from app.services.transaction_in import TransactionInService
from app.services.transaction_out import TransactionOutService
from app.services.transaction_report import TransactionReportService


class TransactionService:

    def __init__(self):
        self.repository: TransactionRepository = TransactionRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.repository.close()

    @staticmethod
    def get_service_and_schema(tr_type: TrType):
        if tr_type == TrType.IN:
            return TransactionInService(), TransactionInOutSchema
        elif tr_type == TrType.OUT:
            return TransactionOutService(), TransactionOutOutSchema
        elif tr_type == TrType.REPORT:
            return TransactionReportService(), TransactionReportOutSchema
        else:
            raise ValueError(f"Invalid transaction type: {tr_type}")

    async def add_hash_transaction(
            self,
            transaction: TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema
    ):
        general_transaction = transaction.transaction
        tr_type = general_transaction.type
        service, schema = self.get_service_and_schema(tr_type)

        if tr_type == TrType.IN:
            async with service as service:
                tr_hash = await service.hash_transaction_in(transaction)
        elif tr_type == TrType.OUT:
            async with service as service:
                tr_hash = await service.hash_transaction_out(transaction)
        else:
            async with service as service:
                tr_hash = await service.hash_transaction_report(transaction)

        await self.repository.update(id=general_transaction.id, update_data={"tr_hash": tr_hash})
        return tr_hash

    async def get_transaction_by_id(self, transaction_id: int) -> \
            None | TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema:
        transaction = await self.repository.get_transaction_by_id(transaction_id)
        if transaction is None:
            return None
        return TransactionSchemaConverter.convert_schema(transaction)

    async def get_transaction_by_user_hash(self, user_hash: str) -> \
            list[TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema] | None:
        transactions = await self.repository.get_transactions_by_user_hash(hash=user_hash)
        result = list(map(lambda tr: TransactionSchemaConverter.convert_schema(tr), transactions))
        return result

    async def get_transaction_by_user_hash_and_type(self, user_hash: str, type: TrType) -> \
            list[TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema] | None:
        transactions = await self.repository.get_transactions_by_user_hash_and_type(hash=user_hash, type=type)
        result = list(map(lambda tr: TransactionSchemaConverter.convert_schema(tr), transactions))
        return result

    async def get_transactions_by_block_id(self, block_id: int) -> \
            list[TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema] | None:

        transactions = await self.repository.get_transactions_by_block_id(block_id)
        result = list(map(lambda tr: TransactionSchemaConverter.convert_schema(tr), transactions))
        return result

    async def update_payment_status(self, transaction_id: int, payment_update: PaymentUpdate) -> \
            TransactionInOutSchema | TransactionOutOutSchema:
        general_transaction = await self.repository.get_transaction_by_id(transaction_id)
        tr_type = general_transaction.type

        if general_transaction is None:
            raise HTTPException(status_code=404, detail=f"Transaction not found")

        if tr_type is TrType.REPORT:
            raise HTTPException(status_code=405, detail=f"Method not allowed for the transaction type")

        service, schema = self.get_service_and_schema(tr_type)
        async with service as service:
            result = await service.update_payment_status(transaction_id, payment_update)

        if payment_update.payment_status == TrPaymentStatus.SUCCESS:
            await self.add_hash_transaction(transaction=result)
        return result

    async def sign_transaction(self, transaction_id: int, user_hash: str, sign: str) -> \
            TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema:
        general_transaction = await self.repository.get_transaction_by_id(transaction_id)

        if general_transaction.user_hash != user_hash:
            raise HTTPException(status_code=405, detail=f"Method not allowed. User hash doesn't match")

        if general_transaction.tr_sign is not None and general_transaction.tr_sign != "":
            raise HTTPException(status_code=405, detail="Method not allowed. Transaction is already signed")

        service, schema = self.get_service_and_schema(general_transaction.type)

        async with service as service:
            transaction = await service.get_transaction_by_tr_id(tr_id=transaction_id)

        if general_transaction.type != TrType.REPORT:
            if transaction.payment_status != TrPaymentStatus.SUCCESS:
                raise HTTPException(status_code=405, detail=f"Method not allowed. Not paid")

        result = await self.repository.update(general_transaction.id, {"tr_sign": sign})

        await self.send_to_blockchain(result.tr_hash)

        return TransactionSchemaConverter.convert_schema(result)

    async def send_to_blockchain(self, transaction_hash: str):
        with PikaPublisher() as producer:
            producer.send_message({"tr_hash": transaction_hash})

    async def get_transactions_by_hash(self, hash_list) -> \
            List[TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema]:
        result = await self.repository.get_transactions_by_hash(hash_list)
        transactions = []
        for tr in result:
            transactions.append(TransactionSchemaConverter.convert_schema(tr))
        return transactions
