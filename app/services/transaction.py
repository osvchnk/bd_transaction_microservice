from fastapi import HTTPException

from app.models.transaction import TrPaymentStatus, TrType, Transaction
from app.repositories import *
from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionOutOutSchema, TransactionOutSchema, \
    TransactionInOutSchema, TransactionReportOutSchema
from app.services.schema_converter import TransactionSchemaConverter


class TransactionService:

    def __init__(self):
        self.repository: TransactionRepository = TransactionRepository()

    @staticmethod
    def hash_transaction(transaction: Transaction):
        pass

    @staticmethod
    def get_repo_and_schema(tr_type: TrType):
        if tr_type == TrType.IN:
            return TransactionInRepository, TransactionInOutSchema
        elif tr_type == TrType.OUT:
            return TransactionOutRepository, TransactionOutOutSchema
        elif tr_type == TrType.REPORT:
            return TransactionReportRepository, TransactionReportOutSchema
        else:
            raise ValueError(f"Invalid transaction type: {tr_type}")

    async def get_transaction_by_id(self, transaction_id: int) -> \
            None | TransactionInOutSchema | TransactionOutSchema | TransactionReportOutSchema:
        transaction = await self.repository.get_transaction_by_id(transaction_id)
        if transaction is None:
            return None
        return TransactionSchemaConverter.convert_schema(transaction)

    async def get_transaction_by_user_hash(self, user_hash: str) -> \
            list[TransactionInOutSchema | TransactionOutSchema | TransactionReportOutSchema] | None:
        transactions = await self.repository.get_transactions_by_user_hash(hash=user_hash)
        result = []
        for transaction in transactions:
            result.append(TransactionSchemaConverter.convert_schema(transaction))
        return result

    async def get_transactions_by_block_id(self, block_id: int) -> \
            list[TransactionInOutSchema | TransactionOutSchema | TransactionReportOutSchema] | None:

        transactions = await self.repository.get_transactions_by_block_id(block_id)
        result = []
        for transaction in transactions:
            result.append(TransactionSchemaConverter.convert_schema(transaction))
        return result

    async def update_payment_status(self, transaction_id: int, payment_update: PaymentUpdate):
        general_transaction = await self.repository.get_transaction_by_id(transaction_id)

        if general_transaction is None:
            raise HTTPException(status_code=404, detail=f"Transaction not found")

        if general_transaction.type is TrType.REPORT:
            raise HTTPException(status_code=405, detail=f"Method not allowed for the transaction type")

        repo, schema = self.get_repo_and_schema(tr_type=general_transaction.type)
        repo_obj = repo()
        # create repository instance so that requests to get and update will have one db session.
        # It is necessary for working with one object from db.

        transaction = await repo_obj.get_transaction_by_tr_id(tr_id=transaction_id)

        if transaction.payment_status == TrPaymentStatus.SUCCESS:
            # raise exception if payment status is already success
            raise HTTPException(status_code=405, detail=f"Payment status already success")

        transaction.payment_status = payment_update.status
        transaction.payment_id = payment_update.payment_id
        result = await repo_obj.update(transaction)

        # if PaymentUpdate.status == TrPaymentStatus.SUCCESS:
        #     self.hash_transaction()

        return schema.from_orm(result)

    async def sign_transaction(self, transaction_id: int, user_hash: str, sign: str):
        general_transaction = await self.repository.get_transaction_by_id(transaction_id)

        if general_transaction.user_hash != user_hash:
            raise HTTPException(status_code=405, detail=f"Method not allowed. User hash doesn't match")

        repo, schema = self.get_repo_and_schema(general_transaction.type)
        transaction = await repo().get_transaction_by_tr_id(tr_id=transaction_id)

        if general_transaction.type != TrType.REPORT:
            if transaction.payment_status != TrPaymentStatus.SUCCESS:
                raise HTTPException(status_code=405, detail=f"Method not allowed. Not paid")

        general_transaction.tr_sign = sign
        result = await self.repository.update(general_transaction)

        return TransactionSchemaConverter.convert_schema(result)
