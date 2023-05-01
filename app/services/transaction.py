from fastapi import HTTPException

from app.models.transaction import TrPaymentStatus, TrType, Transaction, TransactionIn, TransactionOut, \
    TransactionReport
from app.repositories.transaction import TransactionRepository
from app.schemas.payment import PaymentUpdate
from app.schemas.transaction import TransactionInCreateSchema, TransactionOutCreateSchema, \
    TransactionReportCreateSchema, TransactionOutOutSchema, TransactionAllInfoSchema, TransactionOutSchema, \
    TransactionInOutSchema, TransactionReportOutSchema


class TransactionService:

    def __init__(self):
        self.repository: TransactionRepository = TransactionRepository()

    @staticmethod
    def get_schema(tr_type: TrType):
        if tr_type == TrType.IN:
            return TransactionInOutSchema
        elif tr_type == TrType.OUT:
            return TransactionOutOutSchema
        elif tr_type == TrType.REPORT:
            return TransactionReportOutSchema
        else:
            raise ValueError(f"Invalid transaction type: {tr_type}")

    @staticmethod
    def hash_transaction(transaction: Transaction):
        pass

    @staticmethod
    async def transaction_to_schema(transaction: Transaction):
        tr_type = transaction.type
        transaction_out_schema = TransactionOutSchema.from_orm(transaction)

        if tr_type == TrType.IN:
            return TransactionAllInfoSchema(
                transaction=transaction_out_schema,
                info=TransactionInOutSchema.from_orm(transaction.transaction_in))
        if tr_type == TrType.OUT:
            return TransactionAllInfoSchema(
                transaction=transaction_out_schema,
                info=TransactionOutOutSchema.from_orm(transaction.transaction_out))
        if tr_type == TrType.REPORT:
            return TransactionAllInfoSchema(
                transaction=transaction_out_schema,
                info=TransactionReportOutSchema.from_orm(transaction.transaction_report))

    async def get_transactions(self) -> list[TransactionAllInfoSchema]:
        transactions = await self.repository.get_transactions()
        response = []
        for transaction in transactions:
            response.append(await self.transaction_to_schema(transaction))
        return response

    async def create_transaction_in(self, transaction: TransactionInCreateSchema):
        return await self.repository.create_transaction(TrType.IN, transaction)

    async def create_transaction_out(self, transaction: TransactionOutCreateSchema):
        return await self.repository.create_transaction(TrType.OUT, transaction)

    async def create_transaction_report(self, transaction: TransactionReportCreateSchema):
        return await self.repository.create_transaction(TrType.REPORT, transaction)

    async def update_payment_status(self, transaction_id: int, payment_update: PaymentUpdate):
        transaction = await self.repository.get_transaction_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail=f"Transaction not found")
        if transaction.type is TrType.REPORT:
            raise HTTPException(status_code=405, detail=f"Method not allowed for the transaction type")
        schema = self.get_schema(tr_type=transaction.type)
        await self.repository.update_payment_info(transaction,
                                                  payment_status=payment_update.status,
                                                  payment_id=payment_update.payment_id)

        # if PaymentUpdate.status == TrPaymentStatus.SUCCESS:
        #     self.hash_transaction()

        full_transaction = await self.repository.get_full_transaction_by_id(transaction_id, transaction.type)
        return TransactionAllInfoSchema(transaction=TransactionOutSchema.from_orm(transaction),
                                        info=schema.from_orm(full_transaction))

    async def get_transaction_by_id(self, transaction_id) -> TransactionAllInfoSchema | None:
        transaction = await self.repository.get_transaction_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail=f"Transaction not found")

        tr_type = transaction.type
        transaction_out_schema = TransactionOutSchema.from_orm(transaction)
        schema = self.get_schema(tr_type=tr_type)
        full_transaction = await self.repository.get_full_transaction_by_id(transaction_id, tr_type)
        return TransactionAllInfoSchema(transaction=transaction_out_schema, info=schema.from_orm(full_transaction))

    async def sign_transaction(self, transaction_id: int, user_hash: str, sign: str):
        transaction = await self.repository.get_transaction_in_by_id(transaction_id)
        if transaction.tourist_hash != user_hash:
            raise HTTPException(status_code=405, detail=f"Method not allowed. User hash doesn't match")
        if transaction.payment_status != TrPaymentStatus.SUCCESS:
            raise HTTPException(status_code=405, detail=f"Method not allowed. Not paid")
        return await self.repository.add_sign(transaction, sign)
