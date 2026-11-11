from datetime import datetime

from pydantic import BaseModel, Field


class InventoryUpdate(BaseModel):
    existencia: int = Field(ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    sucursal_id: int | None = None


class InventoryResponse(BaseModel):
    # id y actualizado_at vienen vacíos si el producto aún no tiene inventario
    id: int | None = None
    sucursal_id: int
    producto_id: int
    codigo: str | None = None
    nombre: str | None = None
    existencia: int
    stock_minimo: int
    actualizado_at: datetime | None = None

    model_config = {"from_attributes": True}
