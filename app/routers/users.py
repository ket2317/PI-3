import bcrypt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin
from app.models.branch import Sucursal
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserResponse, UserUpdate


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def validate_role_and_branch(
    rol_id: int,
    sucursal_id: int | None,
    db: Session,
) -> Role:
    role = db.query(Role).filter(Role.id == rol_id).first()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Rol no encontrado",
        )

    if role.nombre == "ADMIN":
        if sucursal_id is not None:
            raise HTTPException(
                status_code=422,
                detail="El administrador general no debe tener sucursal",
            )

        return role

    if sucursal_id is None:
        raise HTTPException(
            status_code=422,
            detail="Gerentes y cajeros deben tener sucursal",
        )

    branch = (
        db.query(Sucursal)
        .filter(
            Sucursal.id == sucursal_id,
            Sucursal.activo.is_(True),
        )
        .first()
    )

    if branch is None:
        raise HTTPException(
            status_code=404,
            detail="Sucursal no encontrada o inactiva",
        )

    return role


@router.get("/", response_model=list[UserResponse])
def obtener_usuarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return db.query(User).all()


@router.get("/{usuario_id}", response_model=UserResponse)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = (
        db.query(User)
        .filter(User.id == usuario_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    return user


@router.post("/", response_model=UserResponse)
def crear_usuario(
    usuario: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    validate_role_and_branch(
        usuario.rol_id,
        usuario.sucursal_id,
        db,
    )

    existing_user = (
        db.query(User)
        .filter(User.correo == usuario.correo)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado",
        )

    datos = usuario.model_dump(exclude={"password"})

    datos["password_hash"] = bcrypt.hashpw(
        usuario.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    nuevo_usuario = User(
        **datos,
        activo=True,
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="No se pudo crear el usuario por datos duplicados",
        )

    return nuevo_usuario


@router.put("/{usuario_id}", response_model=UserResponse)
def actualizar_usuario(
    usuario_id: int,
    usuario: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    usuario_db = (
        db.query(User)
        .filter(User.id == usuario_id)
        .first()
    )

    if usuario_db is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    validate_role_and_branch(
        usuario.rol_id,
        usuario.sucursal_id,
        db,
    )

    existing_user = (
        db.query(User)
        .filter(
            User.correo == usuario.correo,
            User.id != usuario_id,
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado",
        )

    usuario_db.nombre = usuario.nombre
    usuario_db.correo = usuario.correo
    usuario_db.rol_id = usuario.rol_id
    usuario_db.sucursal_id = usuario.sucursal_id
    usuario_db.activo = usuario.activo

    if usuario.password:
        usuario_db.password_hash = bcrypt.hashpw(
            usuario.password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    try:
        db.commit()
        db.refresh(usuario_db)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="No se pudo actualizar el usuario por datos duplicados",
        )

    return usuario_db


@router.delete("/{usuario_id}")
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    usuario_db = (
        db.query(User)
        .filter(User.id == usuario_id)
        .first()
    )

    if usuario_db is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    usuario_db.activo = False

    db.commit()

    return {
        "message": "Usuario desactivado correctamente"
    }