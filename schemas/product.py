# define que datos necesitamos cuanado alguien registre un producto

from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class ProductCreate(BaseModel):
    codigo: str
    nombre: str
    precio: Decimal
    iva: Decimal
    categoria_id: int | None = None


class ProductResponse(BaseModel):
    id: int
    created_at: datetime
    codigo: str
    nombre: str
    precio: Decimal
    iva: Decimal
    categoria_id: int | None
    activo: bool

    model_config = {
        "from_attributes": True
    }