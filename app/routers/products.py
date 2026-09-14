from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    ensure_branch_access,
    get_current_user,
    require_admin_or_manager,
)

from app.models.branch import Sucursal
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)


def get_product_or_404(
    producto_id: int,
    db: Session,
) -> Product:
    product = (
        db.query(Product)
        .filter(
            Product.id == producto_id,
            Product.activo.is_(True),
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return product


def validate_category(
    categoria_id: int | None,
    db: Session,
) -> None:
    if categoria_id is None:
        return

    category = (
        db.query(Category)
        .filter(Category.id == categoria_id)
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Categoría no encontrada",
        )


def validate_branch(
    sucursal_id: int,
    db: Session,
) -> None:
    branch = (
        db.query(Sucursal)
        .filter(
            Sucursal.id == sucursal_id,
            Sucursal.activo.is_(True),
        )
        .first()
    )

    if branch is None:
        raise HTTPException(
            status_code=404,
            detail="Sucursal no encontrada o inactiva",
        )


def ensure_unique_code(
    codigo: str,
    sucursal_id: int,
    db: Session,
    producto_id: int | None = None,
) -> None:
    query = (
        db.query(Product)
        .filter(
            Product.codigo == codigo,
            Product.sucursal_id == sucursal_id,
        )
    )

    if producto_id is not None:
        query = query.filter(
            Product.id != producto_id,
        )

    if query.first() is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un producto con ese código en la sucursal",
        )


@router.get(
    "/",
    response_model=list[ProductResponse],
)
def obtener_productos(
    sucursal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    allowed_branch_id = ensure_branch_access(
        current_user,
        sucursal_id,
        db,
    )

    query = (
        db.query(Product)
        .filter(Product.activo.is_(True))
    )

    if allowed_branch_id is not None:
        query = query.filter(
            Product.sucursal_id == allowed_branch_id,
        )

    return query.order_by(Product.nombre).all()


@router.get(
    "/{producto_id}",
    response_model=ProductResponse,
)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    product = get_product_or_404(
        producto_id,
        db,
    )

    ensure_branch_access(
        current_user,
        product.sucursal_id,
        db,
    )

    return product


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=201,
)
def crear_producto(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    branch_id = ensure_branch_access(
        current_user,
        data.sucursal_id,
        db,
    )

    if branch_id is None:
        raise HTTPException(
            status_code=422,
            detail="Debes indicar sucursal_id",
        )

    validate_branch(
        branch_id,
        db,
    )

    codigo = data.codigo.strip()

    ensure_unique_code(
        codigo,
        branch_id,
        db,
    )

    validate_category(
        data.categoria_id,
        db,
    )

    product = Product(
        sucursal_id=branch_id,
        codigo=codigo,
        nombre=data.nombre.strip(),
        precio=data.precio,
        iva=data.iva,
        categoria_id=data.categoria_id,
        activo=True,
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflicto al crear el producto",
        )

    return product


@router.put(
    "/{producto_id}",
    response_model=ProductResponse,
)
def actualizar_producto(
    producto_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    product = get_product_or_404(
        producto_id,
        db,
    )

    ensure_branch_access(
        current_user,
        product.sucursal_id,
        db,
    )

    branch_id = ensure_branch_access(
        current_user,
        data.sucursal_id,
        db,
    )

    if branch_id != product.sucursal_id:
        raise HTTPException(
            status_code=403,
            detail="No puedes mover un producto a otra sucursal",
        )

    codigo = data.codigo.strip()

    ensure_unique_code(
        codigo,
        branch_id,
        db,
        producto_id,
    )

    validate_category(
        data.categoria_id,
        db,
    )

    product.codigo = codigo
    product.nombre = data.nombre.strip()
    product.precio = data.precio
    product.iva = data.iva
    product.categoria_id = data.categoria_id

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflicto al actualizar el producto",
        )

    return product


@router.delete(
    "/{producto_id}",
)
def desactivar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    product = get_product_or_404(
        producto_id,
        db,
    )

    ensure_branch_access(
        current_user,
        product.sucursal_id,
        db,
    )

    product.activo = False
    db.commit()

    return {
        "message": "Producto desactivado correctamente",
    }