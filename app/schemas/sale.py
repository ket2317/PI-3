from datetime import datetime
from pydantic import BaseModel


class SaleCreate(BaseModel):
    sucursal_id: int
    usuario_id: int
    metodo_pago_id: int
    subtotal: float
    iva: float
    total: float


class SaleResponse(SaleCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}