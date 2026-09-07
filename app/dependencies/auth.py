from collections.abc import Callable
from fastapi import Depends, HTTPException,Request,status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User



def get_current_user (
        request: Request,
        db: Session = Depends(get_db),

) -> User:
    user_id = request.session.get("user_id")

    if user_id is None :
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = " debes iniciar sesion",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id, User.activo.is_(True))
        .first()
    )

    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "sesion invalida o usuario inactivo"
        )
    return user

def require_roloes (*allowed_roles) -> Callable:
    def check_role (
            current_user : User = Depends(get_current_user),

    ) -> User:
        if current_user.rol is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail= " El usuario no tiene un rol valido"
            )

        if current_user.rol not in allowed_roles:
            raise  HTTPException(status_code= status.HTTP_403_FORBIDDEN,
            detail= "No tienes permiso para esta operacion")

        return current_user

    return  check_role
require_admin = require_roloes("ADMIN")
require_admin_or_manager = require_roloes("ADMIN","GERENTE")
require_authenticated = require_roloes("ADMIN","GERENTE","CAJERO")
