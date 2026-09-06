from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entry_detail import EntryDetail
from app.schemas.entry_detail import EntryDetailCreate, EntryDetailResponse


router = APIRouter(
    prefix="/detalle-entradas",
    tags=["Detalle de Entradas"]
)


@router.get("/", response_model=list[EntryDetailResponse])
def get_entry_details(db: Session = Depends(get_db)):
    return db.query(EntryDetail).all()


@router.post("/", response_model=EntryDetailResponse)
def create_entry_detail(
    detail: EntryDetailCreate,
    db: Session = Depends(get_db)
):
    new_detail = EntryDetail(**detail.model_dump())

    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)

    return new_detail