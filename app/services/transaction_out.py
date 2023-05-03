from app.repositories.transaction_out import TransactionOutRepository
from app.schemas.transaction import TransactionOutCreateSchema


class TransactionOutService:

    def __init__(self):
        self.repository: TransactionOutRepository = TransactionOutRepository()

    async def create_transaction_out(self, transaction: TransactionOutCreateSchema):
        return await self.repository.create(transaction)

    async def get_transaction_out(self, id: int):
        return await self.get_transaction_out(id)
