from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import async_session
from app.models.transaction import Transaction, TrType, TransactionReport
from app.schemas.transaction import TransactionReportCreateSchema


class TransactionReportRepository:

    def __init__(self):
        self.session: AsyncSession = async_session()

    async def create(self, data: TransactionReportCreateSchema):
        transaction = Transaction(type=TrType.REPORT)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        try:
            transaction_report = TransactionReport(**data.dict(), tr_id=transaction.id)
            self.session.add(transaction_report)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return {"result": "success"}

    async def get_transaction_by_id(self, id: int) -> TransactionReport | None:
        query = (
            select(TransactionReport).
            options(selectinload(TransactionReport.transaction)).
            where(TransactionReport.id == id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one_or_none()
        return transaction

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionReport | None:
        query = (
            select(TransactionReport).
            options(selectinload(TransactionReport.transaction)).
            where(TransactionReport.tr_id == tr_id)
        )
        result = await self.session.execute(query)
        transaction = result.scalars().one()
        return transaction