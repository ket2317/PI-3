from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    nombre: str
    correo: str
    password: str
    rol_id: int
    sucursal_id: int | None = None


class UserResponse(BaseModel):
    id: int
    created_at: datetime
    nombre: str
    correo: str
    rol_id: int
    sucursal_id: int | None
    activo: bool

    model_config = {
        "from_attributes": True
    }