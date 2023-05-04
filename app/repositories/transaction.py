from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Query

from app.db import async_session
from app.models.transaction import Transaction


class TransactionRepository:

    def __init__(self):
        self.session: AsyncSession = async_session()

    async def update(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    def _get_query(self, *args, **kwargs) -> Query:
        query = (select(Transaction).
                 options(selectinload(Transaction.transaction_in),
                         selectinload(Transaction.transaction_out),
                         selectinload(Transaction.transaction_report))
                 )
        for key, value in kwargs.items():
            query = query.filter(getattr(Transaction, key) == value)
        return query

    async def get_transactions(self) -> List[Transaction] | None:
        query = self._get_query()
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transaction_by_id(self, tr_id: int) -> Transaction | None:
        query = self._get_query(id=tr_id)
        result = await self.session.execute(query)
        transaction = result.scalars().one_or_none()
        return transaction

    async def get_transactions_by_block_id(self, block_id: int) -> List[Transaction] | None:
        query = self._get_query(block_id=block_id)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transactions_by_user_hash(self, hash: str) -> List[Transaction] | None:
        query = self._get_query(user_hash=hash)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions
