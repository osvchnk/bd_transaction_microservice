from pydantic import BaseModel

from app.models.transaction import TrPaymentStatus


class PaymentUpdate(BaseModel):
    payment_id: int
    status: TrPaymentStatus
