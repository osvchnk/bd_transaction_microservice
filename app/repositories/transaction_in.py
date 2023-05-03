import asyncio

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import async_session
from app.models.transaction import Transaction, TransactionIn, TrType, TrPaymentStatus
from app.schemas.transaction import TransactionInCreateSchema


class TransactionInRepository:

    def __init__(self):
        self.session: AsyncSession = async_session()

    async def create(self, data: TransactionInCreateSchema):
        transaction = Transaction(type=TrType.IN)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        try:
            transaction_in = TransactionIn(**data.dict(), tr_id=transaction.id)
            self.session.add(transaction_in)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return {"result": "success"}

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionIn | None:
        query = (
            select(TransactionIn).
            options(selectinload(TransactionIn.transaction)).
            where(TransactionIn.tr_id == tr_id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one()
        return transaction

    async def update(self, transaction: TransactionIn) -> TransactionIn:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_transaction_by_id(self, id: int) -> TransactionIn | None:
        query = (
            select(TransactionIn).
            options(selectinload(TransactionIn.transaction)).
            where(TransactionIn.id == id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one_or_none()
        return transaction

