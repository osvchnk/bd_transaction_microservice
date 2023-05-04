from pydantic import BaseModel

from app.models.transaction import TrType, TrRegionEnum, TrPaymentStatus

from datetime import date


class TransactionBaseSchema(BaseModel):
    type: TrType


class TransactionCreateSchema(TransactionBaseSchema):
    pass


class TransactionOutSchema(TransactionBaseSchema):
    id: int
    tr_hash: str | None
    tr_sign: str | None
    block_id: int | None
    user_hash: str

    class Config:
        orm_mode = True


class TransactionInCreateSchema(BaseModel):
    operator_hash: str
    num_tourist: int
    region: TrRegionEnum
    payment_amount: int
    period_start: date
    period_end: date


class TransactionInOutSchema(TransactionInCreateSchema):
    id: int
    payment_id: int | None
    payment_status: TrPaymentStatus
    transaction: TransactionOutSchema

    class Config:
        orm_mode = True


class TransactionOutCreateSchema(BaseModel):
    region: TrRegionEnum
    destination_id: int
    payment_amount: int


class TransactionOutOutSchema(TransactionOutCreateSchema):
    id: int
    payment_id: int | None
    payment_status: TrPaymentStatus
    transaction: TransactionOutSchema

    class Config:
        orm_mode = True


class TransactionReportCreateSchema(BaseModel):
    executor: str
    customer: str
    price: float
    destination_id: int


class TransactionReportOutSchema(TransactionReportCreateSchema):
    id: int
    transaction: TransactionOutSchema

    class Config:
        orm_mode = True
