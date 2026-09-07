from datetime import datetime

from pydantic import BaseModel, Field


class InventoryUpdate(BaseModel):
    cantidad: int = Field(ge=0)
    sucursal_id: int | None = None


class InventoryResponse(BaseModel):
    id: int
    sucursal_id: int
    producto_id: int
    cantidad: int
    created_at: datetime

    model_config = {"from_attributes": True}
