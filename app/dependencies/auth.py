from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Role, User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión",
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.activo.is_(True),
        )
        .first()
    )

    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o usuario inactivo",
        )

    return user


def get_role_name(
    current_user: User,
    db: Session,
) -> str:
    role = (
        db.query(Role)
        .filter(Role.id == current_user.rol_id)
        .first()
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene un rol válido",
        )

    return role.nombre


def require_roles(*allowed_roles: str) -> Callable:
    def check_role(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        role_name = get_role_name(
            current_user,
            db,
        )

        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para esta operación",
            )

        current_user.role_name = role_name
        return current_user

    return check_role


def ensure_branch_access(
    current_user: User,
    requested_branch_id: int | None,
    db: Session,
) -> int | None:
    role_name = get_role_name(
        current_user,
        db,
    )

    if role_name == "ADMIN":
        return requested_branch_id

    if role_name != "GERENTE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para esta operación",
        )

    if current_user.sucursal_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes una sucursal asignada",
        )

    if requested_branch_id not in (
        None,
        current_user.sucursal_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes acceder a otra sucursal",
        )

    return current_user.sucursal_id


require_admin = require_roles("ADMIN")
require_admin_or_manager = require_roles(
    "ADMIN",
    "GERENTE",
)
require_authenticated = require_roles(
    "ADMIN",
    "GERENTE",
    "CAJERO",
)
