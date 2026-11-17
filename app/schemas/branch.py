from datetime import datetime

from pydantic import BaseModel, Field


class SucursalCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    direccion: str = Field(min_length=3, max_length=250)
    telefono: str = Field(default="", max_length=30)
    contacto: str | None = Field(default=None, max_length=120)
    gerente_id: int | None = None


class SucursalUpdate(SucursalCreate):
    activo: bool = True


class FotoSucursalResponse(BaseModel):
    id: int
    model_config = {"from_attributes": True}

class SucursalResponse(SucursalCreate):
    id: int
    created_at: datetime
    activo: bool
    # Solo los id; cada imagen se pide aparte en /sucursales/{id}/fotos/{foto_id}
    fotos: list[FotoSucursalResponse] = []

    model_config = {"from_attributes": True}
