from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entry_detail import EntryDetail
from app.models.entry import Entry
from app.models.inventory import Inventory
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
    # Buscar la entrada para saber a qué sucursal pertenece
    entry = db.query(Entry).filter(
        Entry.id == detail.entrada_id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entrada no encontrada"
        )

    # Guardar el detalle de entrada
    new_detail = EntryDetail(**detail.model_dump())

    db.add(new_detail)
    # Buscar el producto en el inventario de esa sucursal
    inventory = db.query(Inventory).filter(
        Inventory.sucursal_id == entry.sucursal_id,
        Inventory.producto_id == detail.producto_id
    ).first()

    if inventory:
        # Si ya existe, aumentar cantidad
        inventory.cantidad += detail.cantidad
    else:
        # Si todavía no existe, crear registro de inventario
        inventory = Inventory(
            sucursal_id=entry.sucursal_id,
            producto_id=detail.producto_id,
            cantidad=detail.cantidad
        )

        db.add(inventory)


    db.commit()
    db.refresh(new_detail)

    return new_detail