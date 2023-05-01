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

    class Config:
        orm_mode = True


class TransactionInCreateSchema(BaseModel):
    operator_hash: str
    tourist_hash: str
    num_tourist: int
    region: TrRegionEnum
    payment_amount: int
    period_start: date
    period_end: date


class TransactionInOutSchema(TransactionInCreateSchema):
    # tr_id: int
    payment_id: int | None
    payment_status: TrPaymentStatus

    class Config:
        orm_mode = True


class TransactionOutCreateSchema(BaseModel):
    region: TrRegionEnum
    destination_id: int
    payment_amount: int


class TransactionOutOutSchema(TransactionOutCreateSchema):
    tr_id: int
    payment_id: int | None
    payment_status: TrPaymentStatus

    class Config:
        orm_mode = True


class TransactionReportCreateSchema(BaseModel):
    executor: str
    customer: str
    price: float
    destination_id: int


class TransactionReportOutSchema(TransactionReportCreateSchema):
    tr_id: int

    class Config:
        orm_mode = True


class TransactionAllInfoSchema(BaseModel):
    transaction: TransactionOutSchema
    info: TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema

    class Config:
        orm_mode = True
