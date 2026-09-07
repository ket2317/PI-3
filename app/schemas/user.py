from datetime import datetime

from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    nombre: str
    correo: str
    password: str
    rol_id: int
    sucursal_id: int | None = None

class AuthUser(BaseModel):
    id : int
    nombre : str
    correo : str
    rol :  str
    sucursal_id : int | None

class UserUpdate(BaseModel):
    nombre : str
    correo : str
    password: str | None = None
    rol_id : int
    sucursal_id : int | None = None
    activo : bool = True


class UserResponse(BaseModel):
    id: int
    created_at: datetime
    nombre: str
    correo: str
    rol_id: int
    sucursal_id: int | None
    activo: bool

    model_config = {"from_attributes": True}


