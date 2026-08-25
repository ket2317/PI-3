# define que datos necesitamos cuanado alguien registre un producto

from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class ProductCreate(BaseModel):
    codigo: str
    nombre: str
    precio: Decimal
    iva: Decimal


class ProductResponse(BaseModel):
    id: int
    created_at: datetime
    codigo: str
    nombre: str
    precio: Decimal
    iva: Decimal
    activo: bool

    model_config = {
        "from_attributes": True
    }