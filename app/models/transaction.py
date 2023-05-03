import enum

from sqlalchemy.orm import relationship

from app.db import Base

from sqlalchemy import (
    Column,
    String,
    Integer,
    Enum,
    ForeignKey,
    Date,
    Double
)


class TrType(enum.Enum):
    IN = "in"
    OUT = "out"
    REPORT = "report"


class TrPaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"


class TrRegionEnum(enum.Enum):
    KRASNODAR = "krasnodar"
    STAVROPOL = "stavropol"
    CRIMEA = "crimea"
    ALTAI = "altai"
    PETESBURG = "petersburg"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TrType), nullable=False)
    tr_hash = Column(String)
    tr_sign = Column(String)
    block_id = Column(Integer)
    user_hash = Column(String, nullable=False)

    transaction_in = relationship("TransactionIn", uselist=False, back_populates="transaction")
    transaction_out = relationship("TransactionOut", uselist=False, back_populates="transaction")
    transaction_report = relationship("TransactionReport", uselist=False, back_populates="transaction")


class TransactionIn(Base):
    __tablename__ = "transation_in"

    id = Column(Integer, primary_key=True, index=True)
    operator_hash = Column(String, nullable=False)
    num_tourist = Column(Integer, nullable=False)
    region = Column(Enum(TrRegionEnum), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    payment_amount = Column(Integer, nullable=False)
    payment_status = Column(Enum(TrPaymentStatus), default=TrPaymentStatus.PENDING, nullable=False)
    payment_id = Column(Integer)

    tr_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship(Transaction)


class TransactionOut(Base):
    __tablename__ = "transaction_out"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(Enum(TrRegionEnum), nullable=False)
    destination_id = Column(Integer, nullable=False)
    payment_amount = Column(Integer, nullable=False)
    payment_status = Column(Enum(TrPaymentStatus), default=TrPaymentStatus.PENDING, nullable=False)
    payment_id = Column(Integer)

    tr_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship(Transaction)


class TransactionReport(Base):
    __tablename__ = "transaction_report"

    id = Column(Integer, primary_key=True, index=True)
    executor = Column(String, nullable=False)
    customer = Column(String, nullable=False)
    price = Column(Double, nullable=False)
    destination_id = Column(Integer, nullable=False)

    tr_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship(Transaction)
