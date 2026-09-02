from datetime import datetime
from pydantic import BaseModel,Field

class InventoryUpdate(BaseModel):
    existencia: int = Field(ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    sucursal_id: int | None = None

class InventoryResponse(BaseModel):
    id: int
    sucursal_id: int
    producto_id: int
    existencia: int
    stock_minimo: int
    actualizado_at: datetime

    model_config = {"from_attributes": True}