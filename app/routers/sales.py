from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleResponse


router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)


@router.get("/", response_model=list[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    return db.query(Sale).all()


@router.post("/", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
):
    new_sale = Sale(**sale.model_dump())

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    return new_sale