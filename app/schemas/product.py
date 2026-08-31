from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ProductCreate(BaseModel):
    codigo: str
    nombre: str
    precio: Decimal
    iva: Decimal
    categoria_id: int | None = None


class ProductResponse(ProductCreate):
    id: int
    created_at: datetime
    activo: bool

    model_config = {"from_attributes": True}
