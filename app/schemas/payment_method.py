from datetime import datetime
from pydantic import BaseModel


class PaymentMethodCreate(BaseModel):
    nombre: str


class PaymentMethodResponse(PaymentMethodCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}