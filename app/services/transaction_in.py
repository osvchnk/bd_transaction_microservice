from app.repositories.transaction_in import TransactionInRepository
from app.schemas.transaction import TransactionInCreateSchema, TransactionInOutSchema


class TransactionInService:

    def __init__(self):
        self.repository: TransactionInRepository = TransactionInRepository()

    async def create_transaction_in(self, transaction: TransactionInCreateSchema):
        return await self.repository.create(transaction)

    async def get_transaction_in(self, id: int):
        transaction = await self.repository.get_transaction_by_id(id)
        return TransactionInOutSchema.from_orm(transaction)
