# define que datos necesitamos cuanado alguien registre una sucursal

from pydantic import BaseModel
from datetime import datetime


class SucursalCreate(BaseModel):
    nombre: str
    direccion: str


class SucursalResponse(BaseModel):
    id: int
    created_at: datetime
    nombre: str
    direccion: str
    activo: bool

    model_config = {
        "from_attributes": True
    }