from datetime import datetime

from pydantic import BaseModel

class BranchCreate(BaseModel):
    name: str
    address: str
    phone: str


class SucursalCreate(BaseModel):
    nombre: str
    direccion: str


class SucursalResponse(SucursalCreate):
    id: int
    created_at: datetime
    activo: bool

    model_config = {"from_attributes": True}

