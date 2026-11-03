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
from app.models.payment_method import PaymentMethod
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_detail import SaleDetail
from app.models.user import User
from app.routers.sales import filtrar_ventas

# Las ventas se agrupan por día según la hora de México, no la del servidor
ZONA_HORARIA = "America/Mexico_City"

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/ventas")
def historial_ventas(
    sucursal_id: int | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    q: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = ensure_branch_access(current_user, sucursal_id, db)

    query = filtrar_ventas(db.query(Sale), q)
    query = filtrar_periodo(query, branch_id, desde, hasta)
    ventas = query.order_by(Sale.created_at.desc()).all()

    sucursales = dict(db.query(Sucursal.id, Sucursal.nombre).all())
    usuarios = dict(db.query(User.id, User.nombre).all())
    metodos = dict(db.query(PaymentMethod.id, PaymentMethod.nombre).all())

    return [
        {
            "id": venta.id,
            "created_at": venta.created_at,
            "sucursal_id": venta.sucursal_id,
            "sucursal": sucursales.get(venta.sucursal_id),
            "usuario": usuarios.get(venta.usuario_id),
            "metodo_pago": metodos.get(venta.metodo_pago_id),
            "subtotal": venta.subtotal,
            "iva": venta.iva,
            "total": venta.total,
        }
        for venta in ventas
    ]


def filtrar_periodo(query, branch_id: int | None, desde: date | None, hasta: date | None):
    if branch_id is not None:
        query = query.filter(Sale.sucursal_id == branch_id)
    if desde is not None:
        query = query.filter(Sale.created_at >= datetime.combine(desde, datetime.min.time()))
    if hasta is not None:
        query = query.filter(Sale.created_at <= datetime.combine(hasta, datetime.max.time()))
    return query


@router.get("/estadisticas")
def estadisticas_ventas(
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    sucursal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = ensure_branch_access(current_user, sucursal_id, db)

    # Total vendido, número de ventas y ticket promedio (SUM, COUNT, AVG)
    totales = filtrar_periodo(
        db.query(
            func.coalesce(func.sum(Sale.total), 0).label("total_vendido"),
            func.count(Sale.id).label("numero_ventas"),
            func.coalesce(func.avg(Sale.total), 0).label("ticket_promedio"),
        ),
        branch_id,
        desde,
        hasta,
    ).one()

    # Los 5 productos más vendidos (GROUP BY producto, ORDER BY, LIMIT 5)
    cantidad = func.sum(SaleDetail.cantidad)
    mas_vendidos = filtrar_periodo(
        db.query(
            Product.id,
            Product.codigo,
            Product.nombre,
            cantidad.label("cantidad_vendida"),
            func.sum(SaleDetail.subtotal).label("importe"),
        )
        .join(SaleDetail, SaleDetail.producto_id == Product.id)
        .join(Sale, Sale.id == SaleDetail.venta_id),
        branch_id,
        desde,
        hasta,
    ).group_by(Product.id, Product.codigo, Product.nombre).order_by(cantidad.desc()).limit(5).all()

    # Ventas por día (GROUP BY fecha)
    dia = func.date(func.timezone(ZONA_HORARIA, Sale.created_at))
    por_dia = filtrar_periodo(
        db.query(
            dia.label("fecha"),
            func.count(Sale.id).label("numero_ventas"),
            func.sum(Sale.total).label("total"),
        ),
        branch_id,
        desde,
        hasta,
    ).group_by(dia).order_by(dia).all()

    # Ventas por sucursal (GROUP BY sucursal)
    por_sucursal = filtrar_periodo(
        db.query(
            Sucursal.id,
            Sucursal.nombre,
            func.count(Sale.id).label("numero_ventas"),
            func.sum(Sale.total).label("total"),
        ).join(Sale, Sale.sucursal_id == Sucursal.id),
        branch_id,
        desde,
        hasta,
    ).group_by(Sucursal.id, Sucursal.nombre).order_by(func.sum(Sale.total).desc()).all()

    return {
        "desde": desde,
        "hasta": hasta,
        "total_vendido": round(float(totales.total_vendido), 2),
        "numero_ventas": totales.numero_ventas,
        "ticket_promedio": round(float(totales.ticket_promedio), 2),
        "productos_mas_vendidos": [
            {
                "producto_id": row.id,
                "codigo": row.codigo,
                "nombre": row.nombre,
                "cantidad_vendida": int(row.cantidad_vendida),
                "importe": round(float(row.importe), 2),
            }
            for row in mas_vendidos
        ],
        "ventas_por_dia": [
            {
                "fecha": row.fecha,
                "numero_ventas": row.numero_ventas,
                "total": round(float(row.total), 2),
            }
            for row in por_dia
        ],
        "ventas_por_sucursal": [
            {
                "sucursal_id": row.id,
                "sucursal": row.nombre,
                "numero_ventas": row.numero_ventas,
                "total": round(float(row.total), 2),
            }
            for row in por_sucursal
        ],
    }


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
