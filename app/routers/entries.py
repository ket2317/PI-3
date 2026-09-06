from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entry import Entry
from app.schemas.entry import EntryCreate, EntryResponse


router = APIRouter(
    prefix="/entradas",
    tags=["Entradas"]
)


@router.get("/", response_model=list[EntryResponse])
def get_entries(db: Session = Depends(get_db)):
    return db.query(Entry).all()


@router.post("/", response_model=EntryResponse)
def create_entry(
    entry: EntryCreate,
    db: Session = Depends(get_db)
):
    new_entry = Entry(**entry.model_dump())

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry