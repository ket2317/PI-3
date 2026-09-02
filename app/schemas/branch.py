from datetime import datetime
from pydantic import BaseModel, Field

class SucursalCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    direccion: str = Field(min_length=3, max_length=250)
    telefono: str = Field(min_length=7, max_length=30)
    contacto: str | None = Field(default=None, max_length=200)
    gerente_id: int | None = None

class SucursalUpdate(SucursalCreate):
    activo: bool = True

class SucursalResponse(SucursalCreate):
    id : int
    created_at: datetime
    activo: bool

    model_config = {"from_attributes": True}


