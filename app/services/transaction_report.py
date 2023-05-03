from app.repositories.transaction_report import TransactionReportRepository
from app.schemas.transaction import TransactionReportCreateSchema


class TransactionReportService:

    def __init__(self):
        self.repository: TransactionReportRepository = TransactionReportRepository()

    async def create_transaction_report(self, transaction: TransactionReportCreateSchema):
        return await self.repository.create(transaction)

    async def get_transaction_report(self, id: int):
        return await self.repository.get_transaction_by_id(id)
