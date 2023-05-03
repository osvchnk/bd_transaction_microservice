from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import async_session
from app.models.transaction import Transaction, TrType, TransactionOut, TrPaymentStatus
from app.schemas.transaction import TransactionOutCreateSchema


class TransactionOutRepository:

    def __init__(self):
        self.session: AsyncSession = async_session()

    async def create(self, data: TransactionOutCreateSchema):
        transaction = Transaction(type=TrType.OUT)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        try:
            transaction_out = TransactionOut(**data.dict(), tr_id=transaction.id)
            self.session.add(transaction_out)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return {"result": "success"}

    async def update(self, transaction: TransactionOut) -> TransactionOut:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_transaction_by_id(self, id: int) -> TransactionOut | None:
        query = (
            select(TransactionOut).
            options(selectinload(TransactionOut.transaction)).
            where(TransactionOut.id == id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one_or_none()
        return transaction

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionOut | None:
        query = (
            select(TransactionOut).
            options(selectinload(TransactionOut.transaction)).
            where(TransactionOut.tr_id == tr_id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one()
        return transaction

