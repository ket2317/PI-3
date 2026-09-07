from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin_or_manager
from app.models.branch import Sucursal
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import Role, User
from app.schemas.inventory import InventoryResponse, InventoryUpdate


router = APIRouter(prefix="/inventario", tags=["Inventario"])


def get_role_name(user: User, db: Session) -> str:
    role = db.query(Role).filter(Role.id == user.rol_id).first()
    if role is None:
        raise HTTPException(status_code=403, detail="El usuario no tiene un rol valido")
    return role.nombre


def resolve_read_branch(user: User, requested: int | None, db: Session) -> int | None:
    if get_role_name(user, db) == "ADMIN":
        return requested
    if user.sucursal_id is None:
        raise HTTPException(status_code=403, detail="No tienes una sucursal asignada")
    if requested not in (None, user.sucursal_id):
        raise HTTPException(status_code=403, detail="No puedes consultar otra sucursal")
    return user.sucursal_id


def resolve_write_branch(user: User, requested: int | None, db: Session) -> int:
    if get_role_name(user, db) == "ADMIN":
        if requested is None:
            raise HTTPException(status_code=422, detail="El administrador debe indicar sucursal_id")
        return requested
    if user.sucursal_id is None:
        raise HTTPException(status_code=403, detail="No tienes una sucursal asignada")
    if requested not in (None, user.sucursal_id):
        raise HTTPException(status_code=403, detail="No puedes modificar otra sucursal")
    return user.sucursal_id


@router.get("/", response_model=list[InventoryResponse])
def obtener_inventario(
    sucursal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = resolve_read_branch(current_user, sucursal_id, db)
    query = db.query(Inventory)
    if branch_id is not None:
        query = query.filter(Inventory.sucursal_id == branch_id)
    return query.order_by(Inventory.sucursal_id, Inventory.producto_id).all()


@router.get("/bajo-stock", response_model=list[InventoryResponse])
def obtener_bajo_stock(
    limite: int = Query(default=5, ge=0),
    sucursal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = resolve_read_branch(current_user, sucursal_id, db)
    query = db.query(Inventory).filter(Inventory.cantidad <= limite)
    if branch_id is not None:
        query = query.filter(Inventory.sucursal_id == branch_id)
    return query.all()


@router.put("/{producto_id}", response_model=InventoryResponse)
def actualizar_inventario(
    producto_id: int,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = resolve_write_branch(current_user, data.sucursal_id, db)

    branch = db.query(Sucursal).filter(Sucursal.id == branch_id, Sucursal.activo.is_(True)).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o inactiva")

    product = db.query(Product).filter(Product.id == producto_id, Product.activo.is_(True)).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    inventory = db.query(Inventory).filter(
        Inventory.sucursal_id == branch_id,
        Inventory.producto_id == producto_id,
    ).first()

    if inventory is None:
        inventory = Inventory(
            sucursal_id=branch_id,
            producto_id=producto_id,
            cantidad=data.cantidad,
        )
        db.add(inventory)
    else:
        inventory.cantidad = data.cantidad

    try:
        db.commit()
        db.refresh(inventory)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al actualizar el inventario")

    return inventory
