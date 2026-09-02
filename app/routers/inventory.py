from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryResponse

router = APIRouter(
    prefix="/inventario",
    tags=["Inventario"]
)


@router.get("/", response_model=list[InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(Inventory).all()


@router.post("/", response_model=InventoryResponse)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):
    new_inventory = Inventory(**inventory.model_dump())

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory



@router.put("/{inventario_id}", response_model=InventoryResponse)
def update_inventory(
    inventario_id: int,
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):
    inventory_db = (
        db.query(Inventory)
        .filter(Inventory.id == inventario_id)
        .first()
    )

    if not inventory_db:
        raise HTTPException(
            status_code=404,
            detail="Inventario no encontrado"
        )

    inventory_db.sucursal_id = inventory.sucursal_id
    inventory_db.producto_id = inventory.producto_id
    inventory_db.cantidad = inventory.cantidad

    db.commit()
    db.refresh(inventory_db)

    return inventory_db