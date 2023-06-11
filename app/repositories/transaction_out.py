from datetime import datetime
from typing import Type, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction, TrType, TransactionOut, TransactionIn
from app.repositories.base_repository import BaseTransactionRepository
from app.schemas.transaction import TransactionOutCreateSchema, TransactionOutBaseSchema


class TransactionOutRepository(BaseTransactionRepository[TransactionOut]):

    @property
    def _model(self) -> Type[TransactionOut]:
        return TransactionOut

    async def create(self, data: TransactionOutCreateSchema, transaction_in_list):
        transaction = Transaction(type=TrType.OUT,
                                  user_hash=data.user_hash,
                                  created_at=datetime.now().replace(microsecond=0))
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        try:
            tr_data = TransactionOutBaseSchema(**data.dict())
            transaction_out = TransactionOut(**tr_data.dict(), tr_id=transaction.id)

            query = select(TransactionIn).where(TransactionIn.id.in_(transaction_in_list))
            result = await self.session.execute(query)
            tr_in_objects = result.scalars().all()
            transaction_out.transactions_in = tr_in_objects

            self.session.add(transaction_out)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return transaction

    async def get_transaction_by_id(self, id: int) -> TransactionOut | None:
        return await self.get_by(id=id)

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionOut | None:
        return await self.get_by(tr_id=tr_id)


