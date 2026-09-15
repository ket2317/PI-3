from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import ensure_branch_access, require_authenticated
from app.models.inventory import Inventory
from app.models.payment_method import PaymentMethod
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_detail import SaleDetail
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/", response_model=list[SaleResponse])
def obtener_ventas(
    sucursal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    branch_id = ensure_branch_access(current_user, sucursal_id, db)

    query = db.query(Sale)
    if branch_id is not None:
        query = query.filter(Sale.sucursal_id == branch_id)

    return query.order_by(Sale.created_at.desc()).all()


@router.get("/{venta_id}", response_model=SaleResponse)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    venta = db.query(Sale).filter(Sale.id == venta_id).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    ensure_branch_access(current_user, venta.sucursal_id, db)
    return venta


@router.post("/", response_model=SaleResponse, status_code=201)
def crear_venta(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    branch_id = ensure_branch_access(current_user, data.sucursal_id, db)
    if branch_id is None:
        raise HTTPException(status_code=422, detail="Debes indicar sucursal_id")

    metodo = (
        db.query(PaymentMethod)
        .filter(PaymentMethod.id == data.metodo_pago_id)
        .first()
    )
    if metodo is None:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")

    subtotal_total = 0
    iva_total = 0
    detalles: list[SaleDetail] = []

    for item in data.items:
        product = (
            db.query(Product)
            .filter(Product.id == item.producto_id, Product.activo.is_(True))
            .first()
        )
        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {item.producto_id} no encontrado",
            )

        if product.sucursal_id != branch_id:
            raise HTTPException(
                status_code=422,
                detail="El producto no pertenece a la sucursal de la venta",
            )

        inventario = (
            db.query(Inventory)
            .filter(
                Inventory.sucursal_id == branch_id,
                Inventory.producto_id == product.id,
            )
            .with_for_update()
            .first()
        )
        if inventario is None or inventario.existencia < item.cantidad:
            raise HTTPException(
                status_code=409,
                detail=f"Existencia insuficiente para {product.nombre}",
            )

        precio_unitario = product.precio
        iva_unitario = precio_unitario * product.iva
        subtotal_item = precio_unitario * item.cantidad

        subtotal_total += subtotal_item
        iva_total += iva_unitario * item.cantidad

        inventario.existencia -= item.cantidad

        detalles.append(
            SaleDetail(
                producto_id=product.id,
                cantidad=item.cantidad,
                precio_unitario=precio_unitario,
                iva=iva_unitario,
                subtotal=subtotal_item,
            )
        )

    venta = Sale(
        sucursal_id=branch_id,
        usuario_id=current_user.id,
        metodo_pago_id=data.metodo_pago_id,
        subtotal=subtotal_total,
        iva=iva_total,
        total=subtotal_total + iva_total,
    )
    venta.detalles = detalles

    db.add(venta)
    db.commit()
    db.refresh(venta)

    return venta
