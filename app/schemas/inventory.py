from pydantic import BaseModel
from datetime import datetime


class InventoryCreate(BaseModel):
    sucursal_id: int
    producto_id: int
    cantidad: int


class InventoryResponse(BaseModel):
    id: int
    sucursal_id: int
    producto_id: int
    cantidad: int
    created_at: datetime

    model_config = {"from_attributes": True}