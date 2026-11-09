from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    ensure_branch_access,
    require_admin,
    require_admin_or_manager,
    require_authenticated,
)

from app.models.branch import Sucursal
from app.models.inventory import Inventory
from app.models.payment_method import PaymentMethod
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

@router.get("/dashboard")
def estadisticas_dashboard(
    periodo: str = Query(default="hoy", pattern="^(hoy|7dias|mes|anio)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    # 1. Fechas y zona horaria
    zona = ZoneInfo("America/Mexico_City")
    ahora = datetime.now(zona)
    hoy = ahora.date()

    if periodo == "hoy":
        fecha_inicio = hoy
    elif periodo == "7dias":
        fecha_inicio = hoy - timedelta(days=6)
    elif periodo == "mes":
        fecha_inicio = date(hoy.year, hoy.month, 1)
    else:
        fecha_inicio = date(hoy.year, 1, 1)

    inicio = datetime.combine(
        fecha_inicio,
        datetime.min.time(),
        tzinfo=zona
    )

    # 2. Permisos: ADMIN ve todas las sucursales;
    # GERENTE y CAJERO solamente ven la suya.
    branch_id = ensure_branch_access(current_user, None, db)

    # 3. Consulta base de ventas del periodo actual
    ventas_query = db.query(Sale).filter(
        Sale.created_at >= inicio,
        Sale.created_at <= ahora
    )

    if branch_id is not None:
        ventas_query = ventas_query.filter(
            Sale.sucursal_id == branch_id
        )

    # 4. Resumen general
    resumen = ventas_query.with_entities(
        func.count(Sale.id).label("cantidad_ventas"),
        func.coalesce(func.sum(Sale.total), 0).label("ingresos"),
        func.coalesce(func.sum(Sale.iva), 0).label("iva")
    ).first()

    cantidad_ventas = int(resumen.cantidad_ventas or 0)
    ingresos = float(resumen.ingresos or 0)
    iva = float(resumen.iva or 0)

    ticket_promedio = (
        ingresos / cantidad_ventas
        if cantidad_ventas > 0
        else 0
    )

    # 5. Crecimiento de ventas contra el periodo anterior
    # Comparamos intervalos de la misma duración.
    duracion_periodo = ahora - inicio
    inicio_anterior = inicio - duracion_periodo

    ventas_anteriores = db.query(
        func.coalesce(func.sum(Sale.total), 0)
    ).filter(
        Sale.created_at >= inicio_anterior,
        Sale.created_at < inicio
    )

    if branch_id is not None:
        ventas_anteriores = ventas_anteriores.filter(
            Sale.sucursal_id == branch_id
        )

    ingresos_anteriores = float(ventas_anteriores.scalar() or 0)

    if ingresos_anteriores > 0:
        crecimiento_ventas = (
            (ingresos - ingresos_anteriores)
            / ingresos_anteriores
        ) * 100
        crecimiento_base_cero = False
    else:
        crecimiento_ventas = 0
        crecimiento_base_cero = ingresos > 0

    # 6. Cantidad de productos vendidos
    productos_vendidos_query = (
        db.query(
            func.coalesce(func.sum(SaleDetail.cantidad), 0)
        )
        .join(Sale, Sale.id == SaleDetail.venta_id)
        .filter(
            Sale.created_at >= inicio,
            Sale.created_at <= ahora
        )
    )

    if branch_id is not None:
        productos_vendidos_query = productos_vendidos_query.filter(
            Sale.sucursal_id == branch_id
        )

    total_productos_vendidos = int(
        productos_vendidos_query.scalar() or 0
    )

    # 7. Productos activos
    productos_activos_query = db.query(
        func.count(Product.id)
    ).filter(
        Product.activo.is_(True)
    )

    if branch_id is not None:
        productos_activos_query = productos_activos_query.filter(
            Product.sucursal_id == branch_id
        )

    productos_activos = int(
        productos_activos_query.scalar() or 0
    )

    # 8. Productos más vendidos por cantidad
    top_query = (
        db.query(
            Product.id.label("producto_id"),
            Product.nombre.label("nombre"),
            func.sum(SaleDetail.cantidad).label("cantidad_vendida")
        )
        .join(SaleDetail, SaleDetail.producto_id == Product.id)
        .join(Sale, Sale.id == SaleDetail.venta_id)
        .filter(
            Sale.created_at >= inicio,
            Sale.created_at <= ahora
        )
        .group_by(Product.id, Product.nombre)
        .order_by(func.sum(SaleDetail.cantidad).desc())
    )

    if branch_id is not None:
        top_query = top_query.filter(
            Sale.sucursal_id == branch_id
        )

    top_productos = [
        {
            "producto_id": row.producto_id,
            "nombre": row.nombre,
            "cantidad_vendida": int(row.cantidad_vendida or 0)
        }
        for row in top_query.limit(5).all()
    ]

    # 9. Productos con mayores ingresos
    # Se suma subtotal + IVA para obtener el importe real generado.
    ingreso_producto = (
        SaleDetail.subtotal + SaleDetail.iva
    )

    ingresos_query = (
        db.query(
            Product.id.label("producto_id"),
            Product.nombre.label("nombre"),
            func.sum(SaleDetail.cantidad).label("cantidad_vendida"),
            func.sum(ingreso_producto).label("ingresos")
        )
        .join(SaleDetail, SaleDetail.producto_id == Product.id)
        .join(Sale, Sale.id == SaleDetail.venta_id)
        .filter(
            Sale.created_at >= inicio,
            Sale.created_at <= ahora
        )
        .group_by(Product.id, Product.nombre)
        .order_by(func.sum(ingreso_producto).desc())
    )

    if branch_id is not None:
        ingresos_query = ingresos_query.filter(
            Sale.sucursal_id == branch_id
        )

    productos_mayor_ingreso = [
        {
            "producto_id": row.producto_id,
            "nombre": row.nombre,
            "cantidad_vendida": int(row.cantidad_vendida or 0),
            "ingresos": float(row.ingresos or 0)
        }
        for row in ingresos_query.limit(5).all()
    ]

    producto_mayor_ingreso = (
        {
            "nombre": productos_mayor_ingreso[0]["nombre"],
            "ingresos": productos_mayor_ingreso[0]["ingresos"]
        }
        if productos_mayor_ingreso
        else None
    )

    # 10. Productos con inventario bajo
    inventario_query = (
        db.query(
            Inventory.id,
            Inventory.existencia,
            Inventory.stock_minimo,
            Product.nombre.label("producto"),
            Sucursal.nombre.label("sucursal")
        )
        .join(Product, Product.id == Inventory.producto_id)
        .join(Sucursal, Sucursal.id == Inventory.sucursal_id)
        .filter(
            Inventory.existencia <= Inventory.stock_minimo,
            Product.activo.is_(True)
        )
    )

    if branch_id is not None:
        inventario_query = inventario_query.filter(
            Inventory.sucursal_id == branch_id
        )

    inventario_bajo = [
        {
            "producto": row.producto,
            "sucursal": row.sucursal,
            "existencia": row.existencia,
            "stock_minimo": row.stock_minimo
        }
        for row in inventario_query.limit(10).all()
    ]

    # 11. Ventas por día o por mes para la gráfica
    granularidad = "month" if periodo == "anio" else "day"

    fecha_local = func.timezone(
        "America/Mexico_City",
        Sale.created_at
    )

    agrupacion = func.date_trunc(granularidad, fecha_local)

    grafica_query = (
        db.query(
            agrupacion.label("fecha"),
            func.sum(Sale.total).label("total")
        )
        .filter(
            Sale.created_at >= inicio,
            Sale.created_at <= ahora
        )
    )

    if branch_id is not None:
        grafica_query = grafica_query.filter(
            Sale.sucursal_id == branch_id
        )

    resultados_grafica = (
        grafica_query
        .group_by(agrupacion)
        .order_by(agrupacion)
        .all()
    )

    ventas_agrupadas = {}

    for row in resultados_grafica:
        if periodo == "anio":
            clave = row.fecha.month
        else:
            clave = row.fecha.date()

        ventas_agrupadas[clave] = float(row.total or 0)

    ventas_por_periodo = []

    if periodo == "anio":
        nombres_meses = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        for mes in range(1, 13):
            ventas_por_periodo.append({
                "periodo": nombres_meses[mes - 1],
                "total": ventas_agrupadas.get(mes, 0)
            })
    else:
        fecha = fecha_inicio

        while fecha <= hoy:
            ventas_por_periodo.append({
                "periodo": fecha.strftime("%d/%m"),
                "total": ventas_agrupadas.get(fecha, 0)
            })
            fecha += timedelta(days=1)

    # 12. Ventas por método de pago
    pagos_query = (
        db.query(
            PaymentMethod.nombre.label("metodo_pago"),
            func.count(Sale.id).label("cantidad_ventas")
        )
        .join(
            Sale,
            Sale.metodo_pago_id == PaymentMethod.id
        )
        .filter(
            Sale.created_at >= inicio,
            Sale.created_at <= ahora
        )
    )

    if branch_id is not None:
        pagos_query = pagos_query.filter(
            Sale.sucursal_id == branch_id
        )

    ventas_por_metodo_pago = [
        {
            "metodo_pago": row.metodo_pago,
            "cantidad_ventas": int(row.cantidad_ventas)
        }
        for row in (
            pagos_query
            .group_by(PaymentMethod.id, PaymentMethod.nombre)
            .order_by(func.count(Sale.id).desc())
            .all()
        )
    ]

    # 13. Comparación de sucursales (solamente ADMIN)
    ventas_por_sucursal = []

    if current_user.role_name == "ADMIN":
        sucursales_query = (
            db.query(
                Sucursal.id,
                Sucursal.nombre,
                func.count(Sale.id).label("cantidad_ventas"),
                func.coalesce(func.sum(Sale.total), 0).label("ingresos")
            )
            .outerjoin(
                Sale,
                (Sale.sucursal_id == Sucursal.id)
                & (Sale.created_at >= inicio)
                & (Sale.created_at <= ahora)
            )
            .group_by(Sucursal.id, Sucursal.nombre)
            .order_by(
                func.coalesce(func.sum(Sale.total), 0).desc()
            )
        )

        ventas_por_sucursal = [
            {
                "sucursal_id": row.id,
                "sucursal": row.nombre,
                "cantidad_ventas": int(row.cantidad_ventas),
                "ingresos": float(row.ingresos or 0)
            }
            for row in sucursales_query.all()
        ]

    # 14. Respuesta del dashboard
    return {
        "periodo": periodo,
        "rol": current_user.role_name,
        "resumen": {
            "cantidad_ventas": cantidad_ventas,
            "ingresos": ingresos,
            "iva": iva,
            "productos_vendidos": total_productos_vendidos,
            "ticket_promedio": ticket_promedio,
            "crecimiento_ventas": crecimiento_ventas,
            "crecimiento_base_cero": crecimiento_base_cero,
            "productos_activos": productos_activos,
            "producto_mayor_ingreso": producto_mayor_ingreso
        },
        "ventas_por_periodo": ventas_por_periodo,
        "productos_mas_vendidos": top_productos,
        "productos_mayor_ingreso": productos_mayor_ingreso,
        "inventario_bajo": inventario_bajo,
        "ventas_por_metodo_pago": ventas_por_metodo_pago,
        "ventas_por_sucursal": ventas_por_sucursal
    }