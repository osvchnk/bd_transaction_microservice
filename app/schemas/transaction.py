from typing import List

from pydantic import BaseModel

from app.models.transaction import TrType, TrRegionEnum, TrPaymentStatus

from datetime import date, datetime


class TransactionBaseSchema(BaseModel):
    type: TrType


class TransactionCreateSchema(TransactionBaseSchema):
    user_hash: str


class TransactionOutSchema(TransactionCreateSchema):
    id: int
    created_at: datetime
    tr_hash: str | None
    tr_sign: str | None
    block_id: int | None

    class Config:
        orm_mode = True


class TransactionInBaseSchema(BaseModel):
    operator_hash: str
    num_tourist: int
    region: TrRegionEnum
    payment_amount: int
    period_start: date
    period_end: date


class TransactionInCreateSchema(TransactionInBaseSchema):
    user_hash: str


class TransactionInOutSchema(TransactionInBaseSchema):
    id: int
    payment_id: int | None
    payment_status: TrPaymentStatus
    transaction: TransactionOutSchema

    class Config:
        orm_mode = True


class TransactionOutBaseSchema(BaseModel):
    region: TrRegionEnum
    destination_id: int
    payment_amount: int
    description: str
    executor_info: str
    term: date


class TransactionOutCreateSchema(TransactionOutBaseSchema):
    user_hash: str


class TransactionOutInSchema(TransactionOutCreateSchema):
    transactions_in: List[int]


class TransactionOutOutSchema(TransactionOutBaseSchema):
    id: int
    payment_id: int | None
    payment_status: TrPaymentStatus
    transaction: TransactionOutSchema

    class Config:
        orm_mode = True


class TransactionReportBaseSchema(BaseModel):
    executor_info: str
    tr_out_hash: str
    destination_id: int
    region: TrRegionEnum


class TransactionReportCreateSchema(TransactionReportBaseSchema):
    user_hash: str


class TransactionReportOutSchema(TransactionReportBaseSchema):
    id: int
    transaction: TransactionOutSchema

    class Config:
        orm_mode = True


class SignRequest(BaseModel):
    user_hash: str
    sign: str
