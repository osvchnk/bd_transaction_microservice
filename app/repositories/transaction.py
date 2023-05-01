from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import async_session
from app.models.transaction import TransactionIn, Transaction, TrType, TransactionOut, TransactionReport, \
    TrPaymentStatus
from app.schemas.transaction import TransactionInCreateSchema, TransactionOutCreateSchema, \
    TransactionReportCreateSchema, TransactionOutSchema


class TransactionRepository:

    def __init__(self):
        self.session: AsyncSession = async_session()

    @staticmethod
    def get_model(tr_type: TrType):
        if tr_type == TrType.IN:
            return TransactionIn
        elif tr_type == TrType.OUT:
            return TransactionOut
        elif tr_type == TrType.REPORT:
            return TransactionReport

    async def get_transactions(self) -> List[Transaction] | None:
        query = (
            select(Transaction).options(selectinload(Transaction.transaction_in),
                                        selectinload(Transaction.transaction_out),
                                        selectinload(Transaction.transaction_report))
        )
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transactions_by_tourist_hash(self, hash: str) -> list[TransactionIn] | None:
        query = select(TransactionIn, Transaction).join(Transaction).filter(TransactionIn.tourist_hash == hash)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transaction_by_id(self, tr_id: int) -> Transaction | None:
        query = select(Transaction).where(Transaction.id == tr_id)
        result = await self.session.execute(query)
        transaction = result.scalars().one_or_none()
        return transaction

    async def get_full_transaction_by_id(self, tr_id: int, tr_type: TrType):
        model = self.get_model(tr_type)
        query = (
            select(model).
            options(selectinload(model.transaction)).
            where(model.tr_id == tr_id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one()
        return transaction

    async def create_transaction(self, tr_type: TrType, data: TransactionInCreateSchema |
                                                              TransactionOutCreateSchema |
                                                              TransactionReportCreateSchema):
        transaction = Transaction(type=tr_type)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        transaction_schema = TransactionOutSchema.from_orm(transaction)

        model = self.get_model(tr_type)

        try:
            transaction_extra = model(**data.dict(), tr_id=transaction_schema.id)
            self.session.add(transaction_extra)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return {"result": "success"}

    async def add_sign(self, transaction: TransactionIn, sign: str):
        stmt = (
            update(Transaction).
            where(Transaction.id == transaction.tr_id).
            values(tr_sign=sign)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def update_payment_info(self, transaction: Transaction,
                                  payment_status: TrPaymentStatus,
                                  payment_id: int) -> Transaction:
        model = self.get_model(transaction.type)
        stmt = (
            update(model).
            where(model.tr_id == transaction.id).
            values(payment_status=payment_status, payment_id=payment_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_transaction_in_by_id(self, tr_id: int) -> TransactionIn | None:
        query = select(TransactionIn).filter(TransactionIn.tr_id == tr_id)
        result = await self.session.execute(query)
        transaction_in = result.scalars().one_or_none()
        return transaction_in
