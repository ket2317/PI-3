from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.privacy import VERSION_AVISO_PRIVACIDAD, PrivacyAcceptance
from app.models.user import User

router = APIRouter(prefix="/privacidad", tags=["Aviso de privacidad"])


def acepto_privacidad(user: User, db: Session) -> bool:
    return (
        db.query(PrivacyAcceptance.id)
        .filter(
            PrivacyAcceptance.usuario_id == user.id,
            PrivacyAcceptance.version_aviso == VERSION_AVISO_PRIVACIDAD,
        )
        .first()
        is not None
    )


@router.post("/aceptar")
def aceptar_aviso(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # El usuario se toma de la sesión, nunca del cuerpo de la petición
    if not acepto_privacidad(current_user, db):
        db.add(
            PrivacyAcceptance(
                usuario_id=current_user.id,
                version_aviso=VERSION_AVISO_PRIVACIDAD,
            )
        )
        try:
            db.commit()
        except IntegrityError:
            # Otra pestaña ya lo registró al mismo tiempo
            db.rollback()

    return {"acepto_privacidad": True, "version_aviso": VERSION_AVISO_PRIVACIDAD}
