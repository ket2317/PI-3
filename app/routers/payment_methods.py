from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_authenticated
from app.models.payment_method import PaymentMethod
from app.models.user import User
from app.schemas.payment_method import PaymentMethodResponse

router = APIRouter(prefix="/metodos-pago", tags=["Métodos de pago"])


@router.get("/", response_model=list[PaymentMethodResponse])
def obtener_metodos_pago(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    return db.query(PaymentMethod).order_by(PaymentMethod.nombre).all()
