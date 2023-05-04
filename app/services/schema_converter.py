from app.models.transaction import TrType, Transaction
from app.schemas.transaction import TransactionInOutSchema, TransactionOutSchema, TransactionReportOutSchema, \
    TransactionOutOutSchema


class TransactionSchemaConverter:
    @staticmethod
    def convert_schema(transaction: Transaction) -> \
            TransactionInOutSchema | TransactionOutOutSchema | TransactionReportOutSchema:

        tr_type = transaction.type
        general_transaction_schema = TransactionOutSchema.from_orm(transaction)

        if tr_type == TrType.IN:
            in_schema = TransactionInOutSchema.from_orm(transaction.transaction_in)
            in_schema.transaction = general_transaction_schema
            return in_schema

        if tr_type == TrType.OUT:
            out_schema = TransactionOutOutSchema.from_orm(transaction.transaction_out)
            out_schema.transaction = general_transaction_schema
            return out_schema

        if tr_type == TrType.REPORT:
            report_schema = TransactionReportOutSchema.from_orm(transaction.transaction_report)
            report_schema.transaction = general_transaction_schema
            return report_schema
