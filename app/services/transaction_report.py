import hashlib
from typing import List

from app.models.transaction import TrRegionEnum
from app.repositories.transaction_report import TransactionReportRepository
from app.schemas.transaction import TransactionReportCreateSchema, TransactionReportOutSchema


class TransactionReportService:

    def __init__(self):
        self.repository: TransactionReportRepository = TransactionReportRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.repository.close()

    async def create_transaction_report(self, transaction: TransactionReportCreateSchema):
        transaction = await self.repository.create(transaction)

        return transaction

    async def get_transaction_report(self, id: int):
        return await self.repository.get_transaction_by_id(id)

    async def get_transaction_report_by_region(self, region: TrRegionEnum) -> List[TransactionReportOutSchema]:
        transactions = await self.repository.get_list_by(region=region)
        result = list(map(lambda tr: TransactionReportOutSchema.from_orm(tr), transactions))
        return result

    async def get_transaction_by_tr_id(self, tr_id: int) -> TransactionReportOutSchema:
        transaction = await self.repository.get_transaction_by_tr_id(tr_id=tr_id)
        return TransactionReportOutSchema.from_orm(transaction)

    @staticmethod
    async def hash_transaction_report(transaction: TransactionReportOutSchema):
        s = f"{transaction.destination_id} " \
            f"{transaction.executor_info}"

        hash = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return hash
