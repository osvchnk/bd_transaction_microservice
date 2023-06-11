import hashlib
from datetime import datetime
from typing import Type

from app.models.transaction import Transaction, TrType, TransactionReport
from app.repositories.base_repository import BaseTransactionRepository
from app.schemas.transaction import TransactionReportCreateSchema, TransactionReportBaseSchema


class TransactionReportRepository(BaseTransactionRepository[TransactionReport]):

    @property
    def _model(self) -> Type[TransactionReport]:
        return TransactionReport

    async def create(self, data: TransactionReportCreateSchema):
        created_at = datetime.now().replace(microsecond=0)
        s = data.user_hash + str(created_at)
        hash = hashlib.sha256(s.encode('utf-8')).hexdigest()
        transaction = Transaction(type=TrType.REPORT,
                                  user_hash=data.user_hash,
                                  created_at=created_at,
                                  tr_hash=hash)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        try:
            tr_data = TransactionReportBaseSchema(**data.dict())
            transaction_report = TransactionReport(**tr_data.dict(),
                                                   tr_id=transaction.id,
                                                   )
            self.session.add(transaction_report)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

        return {"result": "success"}

    async def get_transaction_by_id(self, id: int) -> TransactionReport | None:
        return await self.get_by(id=id)

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionReport | None:
        return await self.get_by(tr_id=tr_id)
