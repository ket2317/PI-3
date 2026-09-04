from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodResponse


router = APIRouter(
    prefix="/metodos-pago",
    tags=["Métodos de Pago"]
)


@router.get("/", response_model=list[PaymentMethodResponse])
def get_payment_methods(db: Session = Depends(get_db)):
    return db.query(PaymentMethod).all()


@router.post("/", response_model=PaymentMethodResponse)
def create_payment_method(
    payment_method: PaymentMethodCreate,
    db: Session = Depends(get_db)
):
    new_payment_method = PaymentMethod(**payment_method.model_dump())

    db.add(new_payment_method)
    db.commit()
    db.refresh(new_payment_method)

    return new_payment_method