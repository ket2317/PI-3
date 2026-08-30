from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)



@router.get("/", response_model=list[UserResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/", response_model=UserResponse)
def crear_usuario(
    usuario: UserCreate,
    db: Session = Depends(get_db)
):
    password_encriptada = bcrypt.hashpw(
    usuario.password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

    nuevo_usuario = User(
        nombre=usuario.nombre,
        correo=usuario.correo,
        password_hash=password_encriptada,
        rol_id=usuario.rol_id,
        sucursal_id=usuario.sucursal_id,
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.put("/{usuario_id}", response_model=UserResponse)
def actualizar_usuario(
    usuario_id: int,
    usuario: UserCreate,
    db: Session = Depends(get_db)
):
    usuario_db = db.query(User).filter(
        User.id == usuario_id
    ).first()

    if not usuario_db:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    password_encriptada = bcrypt.hashpw(
        usuario.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    usuario_db.nombre = usuario.nombre
    usuario_db.correo = usuario.correo
    usuario_db.password_hash = password_encriptada
    usuario_db.rol_id = usuario.rol_id
    usuario_db.sucursal_id = usuario.sucursal_id

    db.commit()
    db.refresh(usuario_db)

    return usuario_db


@router.delete("/{usuario_id}")
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario_db = db.query(User).filter(
        User.id == usuario_id
    ).first()

    if not usuario_db:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario_db.activo = False
    db.commit()

    return {"message": "Usuario desactivado correctamente"}