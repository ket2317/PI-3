from datetime import datetime

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def normalizar_usuario(valor):
    # Se guarda siempre en minúsculas y sin espacios: "Juan " y "juan" son el mismo
    return valor.strip().lower() if isinstance(valor, str) else valor


# Nombre de usuario: 3 a 30 caracteres, solo letras, números, punto, guion y guion bajo
NombreUsuario = Annotated[
    str,
    BeforeValidator(normalizar_usuario),
    Field(min_length=3, max_length=30, pattern=r"^[a-z0-9._-]+$"),
]


class UserLogin(BaseModel):
    usuario: str
    password: str


class UserCreate(BaseModel):
    nombre: str
    usuario: NombreUsuario
    correo: str
    password: str
    rol_id: int
    sucursal_id: int | None = None


class AuthUser(BaseModel):
    id : int
    nombre : str
    usuario : str
    correo : str
    rol :  str
    sucursal_id : int | None
    acepto_privacidad: bool = False

class UserUpdate(BaseModel):
    nombre : str
    usuario : NombreUsuario
    correo : str
    password: str | None = None
    rol_id : int
    sucursal_id : int | None = None
    activo : bool = True


class UserResponse(BaseModel):
    id: int
    created_at: datetime
    nombre: str
    usuario: str
    correo: str
    rol_id: int
    sucursal_id: int | None
    activo: bool

    model_config = {"from_attributes": True}


