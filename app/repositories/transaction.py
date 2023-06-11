from typing import List

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Query

from app.db import async_session
from app.models.transaction import Transaction, TrType


class TransactionRepository:

    def __init__(self):
        self.session: AsyncSession = async_session()

    async def close(self):
        if self.session is not None:
            try:
                await self.session.close()
            except Exception as ex:
                raise ex

    async def update(self, id: int, update_data: dict) -> Transaction | None:
        transaction = await self.get_transaction_by_id(id)
        if transaction is None:
            return None
        for key, value in update_data.items():
            setattr(transaction, key, value)
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

    async def get_transaction_by_hash(self, tr_hash: str) -> Transaction | None:
        query = self._get_query(tr_hash=tr_hash)
        result = await self.session.execute(query)
        transaction = result.scalars().one_or_none()
        return transaction

    async def get_transactions_by_block_id(self, block_id: int) -> List[Transaction] | None:
        query = self._get_query(block_id=block_id)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transactions_by_user_hash(self, hash: str) -> List[Transaction] | None:
        query = self._get_query(user_hash=hash).order_by(desc(Transaction.id))
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transactions_by_user_hash_and_type(self, hash: str, type: TrType) -> List[Transaction] | None:
        query = self._get_query(user_hash=hash, type=type).order_by(desc(Transaction.id))
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions

    async def get_transactions_by_hash(self, hash_list):
        query = self._get_query().\
            filter(Transaction.tr_hash.in_(hash_list))
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return transactions
