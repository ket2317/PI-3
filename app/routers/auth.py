import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, get_role_name
from app.models.user import User
from app.schemas.user import AuthUser, UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def to_auth_user(
    user: User,
    db: Session,
) -> AuthUser:
    return AuthUser(
        id=user.id,
        nombre=user.nombre,
        correo=user.correo,
        rol=get_role_name(user, db),
        sucursal_id=user.sucursal_id,
    )


@router.post(
    "/login",
    response_model=AuthUser,
)
def login(
    data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.correo == data.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
        )

    if not user.activo:
        raise HTTPException(
            status_code=401,
            detail="Usuario inactivo",
        )

    valid_password = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
        )

    request.session.clear()
    request.session["user_id"] = user.id

    return to_auth_user(user, db)


@router.get(
    "/me",
    response_model=AuthUser,
)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return to_auth_user(current_user, db)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {
        "message": "Sesión cerrada",
    }
