from datetime import datetime
from pydantic import BaseModel


class SaleDetailCreate(BaseModel):
    venta_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    iva: float
    subtotal: float


class SaleDetailResponse(SaleDetailCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}