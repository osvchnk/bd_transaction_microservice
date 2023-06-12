import enum

from sqlalchemy import (
    Column,
    String,
    Integer,
    Enum,
    ForeignKey,
    DateTime,
    Date,
    Boolean
)
from sqlalchemy.orm import relationship

from app.db import Base


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
    PETESBURG = "petesburg"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(Enum(TrType), nullable=False)
    created_at = Column(DateTime)
    tr_hash = Column(String)
    tr_sign = Column(String)
    block_id = Column(Integer)
    user_hash = Column(String, nullable=False)

    transaction_in = relationship("TransactionIn", uselist=False, back_populates="transaction", cascade="all, delete")
    transaction_out = relationship("TransactionOut", uselist=False, back_populates="transaction", cascade="all, delete")
    transaction_report = relationship("TransactionReport", uselist=False, back_populates="transaction",
                                      cascade="all, delete")


class TransactionIn(Base):
    __tablename__ = "transation_in"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    operator_hash = Column(String, nullable=False)
    num_tourist = Column(Integer, nullable=False)
    region = Column(Enum(TrRegionEnum), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    payment_amount = Column(Integer, nullable=False)
    payment_status = Column(Enum(TrPaymentStatus), default=TrPaymentStatus.PENDING, nullable=False)
    payment_id = Column(Integer)
    spent = Column(Boolean, default=False)

    transaction_out_id = Column(Integer, ForeignKey("transaction_out.id"))
    transaction_out = relationship("TransactionOut", back_populates="transactions_in")

    tr_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship(Transaction)


class TransactionOut(Base):
    __tablename__ = "transaction_out"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region = Column(Enum(TrRegionEnum), nullable=False)  # регион
    destination_id = Column(Integer, nullable=False)  # информация об объекте инфраструктуры
    payment_amount = Column(Integer, nullable=False)  # стоимость работ
    payment_status = Column(Enum(TrPaymentStatus), default=TrPaymentStatus.PENDING, nullable=False)
    payment_id = Column(Integer)
    description = Column(String, nullable=False)  # описание работ
    executor_info = Column(String, nullable=False)  # информация об организации-исполнителе
    term = Column(Date, nullable=False)  # срок исполнения

    transactions_in = relationship("TransactionIn", back_populates="transaction_out")

    tr_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship(Transaction)


class TransactionReport(Base):
    __tablename__ = "transaction_report"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region = Column(Enum(TrRegionEnum), nullable=False)  # регион
    executor_info = Column(String, nullable=False)  # информация об оргпнизации-исполнителе
    destination_id = Column(Integer, nullable=False)  # информация об объекте инфраструктуры
    tr_out_hash = Column(String, nullable=False)  # хеш транзакции, которой соответствует отчёт

    tr_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship(Transaction)
