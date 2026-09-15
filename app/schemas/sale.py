from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class SaleCreate(BaseModel):
    sucursal_id: int
    metodo_pago_id: int
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleDetailResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    iva: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    id: int
    created_at: datetime
    sucursal_id: int
    usuario_id: int
    metodo_pago_id: int
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    detalles: list[SaleDetailResponse]

    model_config = {"from_attributes": True}
