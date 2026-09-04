from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sale_detail import SaleDetail
from app.schemas.sale_detail import SaleDetailCreate, SaleDetailResponse


router = APIRouter(
    prefix="/detalle-ventas",
    tags=["Detalle de Ventas"]
)


@router.get("/", response_model=list[SaleDetailResponse])
def get_sale_details(db: Session = Depends(get_db)):
    return db.query(SaleDetail).all()


@router.post("/", response_model=SaleDetailResponse)
def create_sale_detail(
    detail: SaleDetailCreate,
    db: Session = Depends(get_db)
):
    new_detail = SaleDetail(**detail.model_dump())

    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)

    return new_detail