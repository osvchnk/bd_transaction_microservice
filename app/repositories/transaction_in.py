from datetime import datetime
from typing import Type, List

from app.models.transaction import Transaction, TransactionIn, TrType, TrRegionEnum, TransactionOut
from app.repositories.base_repository import BaseTransactionRepository
from app.schemas.transaction import TransactionInCreateSchema, TransactionInBaseSchema


class TransactionInRepository(BaseTransactionRepository[TransactionIn]):

    @property
    def _model(self) -> Type[TransactionIn]:
        return TransactionIn

    async def create(self, data: TransactionInCreateSchema):
        transaction = Transaction(type=TrType.IN,
                                  user_hash=data.user_hash,
                                  created_at=datetime.now().replace(microsecond=0))
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        try:
            tr_data = TransactionInBaseSchema(**data.dict())
            transaction_in = TransactionIn(**tr_data.dict(), tr_id=transaction.id)
            self.session.add(transaction_in)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return {"result": "success"}

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionIn | None:
        return await self.get_by(tr_id=tr_id)

    async def get_transaction_by_id(self, id: int) -> TransactionIn | None:
        return await self.get_by(id=id)

    async def get_transactions_not_spent_by_region(self, region: TrRegionEnum) -> List[TransactionIn] | None:
        return await self.get_list_by(region=region, spent=False)

    async def add_transaction_out(self, id: int, transaction_out: TransactionOut):
        tr = await self.get(id)
        tr.transaction_out = transaction_out
        self.session.add(tr)
        await self.session.commit()
        await self.session.refresh(tr)
        print(tr)
        return tr
