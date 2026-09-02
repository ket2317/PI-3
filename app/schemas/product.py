from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from pydantic import BaseModel


class ProductCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=80)
    nombre: str = Field(min_length=2, max_length=150)
    precio: Decimal = Field(gt=0)
    iva: Decimal = Field(ge=0, le=1)
    categoria_id: int | None = None


class ProductResponse(ProductCreate):
    id: int
    created_at: datetime
    activo: bool

    model_config = {"from_attributes": True}
