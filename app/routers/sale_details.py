from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sale_detail import SaleDetail
from app.schemas.sale_detail import SaleDetailCreate, SaleDetailResponse
from app.models.inventory import Inventory
from app.models.sale import Sale



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
    # Buscar la venta para saber de qué sucursal es
    sale = db.query(Sale).filter(
        Sale.id == detail.venta_id
    ).first()

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Venta no encontrada"
        )

    # Buscar el producto en el inventario de esa sucursal
    inventory = db.query(Inventory).filter(
        Inventory.sucursal_id == sale.sucursal_id,
        Inventory.producto_id == detail.producto_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado en el inventario"
        )

    # Comprobar que haya suficiente producto
    if inventory.cantidad < detail.cantidad:
        raise HTTPException(
            status_code=400,
            detail="Inventario insuficiente"
        )


    new_detail = SaleDetail(**detail.model_dump())

    db.add(new_detail)

    inventory.cantidad -= detail.cantidad
    
    db.commit()
    db.refresh(new_detail)

    return new_detail