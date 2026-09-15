from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    ensure_branch_access,
    require_admin,
    require_admin_or_manager,
)
from app.models.branch import Sucursal
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_detail import SaleDetail
from app.models.user import User

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/ventas")
def historial_ventas(
    sucursal_id: int | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = ensure_branch_access(current_user, sucursal_id, db)

    query = db.query(Sale)
    if branch_id is not None:
        query = query.filter(Sale.sucursal_id == branch_id)
    if desde is not None:
        query = query.filter(Sale.created_at >= datetime.combine(desde, datetime.min.time()))
    if hasta is not None:
        query = query.filter(Sale.created_at <= datetime.combine(hasta, datetime.max.time()))

    return query.order_by(Sale.created_at.desc()).all()


@router.get("/resumen")
def resumen_sistema(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    total_sucursales = (
        db.query(func.count(Sucursal.id))
        .filter(Sucursal.activo.is_(True))
        .scalar()
    )
    total_productos = (
        db.query(func.count(Product.id))
        .filter(Product.activo.is_(True))
        .scalar()
    )
    total_ventas = db.query(func.count(Sale.id)).scalar()
    monto_total_vendido = db.query(func.coalesce(func.sum(Sale.total), 0)).scalar()

    return {
        "sucursales_activas": total_sucursales,
        "productos_activos": total_productos,
        "ventas_totales": total_ventas,
        "monto_total_vendido": monto_total_vendido,
    }


@router.get("/productos-mas-vendidos")
def productos_mas_vendidos(
    sucursal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = ensure_branch_access(current_user, sucursal_id, db)

    query = (
        db.query(
            SaleDetail.producto_id,
            func.sum(SaleDetail.cantidad).label("cantidad_vendida"),
        )
        .join(Sale, Sale.id == SaleDetail.venta_id)
        .group_by(SaleDetail.producto_id)
        .order_by(func.sum(SaleDetail.cantidad).desc())
    )

    if branch_id is not None:
        query = query.filter(Sale.sucursal_id == branch_id)

    return [
        {"producto_id": row.producto_id, "cantidad_vendida": row.cantidad_vendida}
        for row in query.limit(10).all()
    ]
