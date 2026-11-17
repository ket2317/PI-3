from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.database import get_db
from app.dependencies.auth import (
    ensure_branch_access,
    get_current_user,
    require_admin_or_manager,
    require_authenticated,
)

from app.models.branch import Sucursal
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.utils.search import ilike_any, like_term
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
    q: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
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

    pattern = like_term(q)
    if pattern is not None:
        query = query.filter(ilike_any(pattern, Product.nombre, Product.codigo))

    return query.order_by(Product.nombre).all()


@router.get(
    "/{producto_id}",
    response_model=ProductResponse,
)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
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


TAMANO_MAXIMO_IMAGEN = 2 * 1024 * 1024  # 2 MB

# Los primeros bytes de cada formato: confirman que el archivo de verdad es una imagen
FIRMAS_IMAGEN = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


def es_imagen_valida(tipo: str | None, contenido: bytes) -> bool:
    if tipo not in FIRMAS_IMAGEN:
        return False
    if tipo == "image/webp" and contenido[8:12] != b"WEBP":
        return False
    return any(contenido.startswith(firma) for firma in FIRMAS_IMAGEN[tipo])


@router.put(
    "/{producto_id}/imagen",
    response_model=ProductResponse,
)
async def subir_imagen(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    product = get_product_or_404(producto_id, db)
    ensure_branch_access(current_user, product.sucursal_id, db)

    # Se lee un byte de más para saber si el archivo rebasa el límite
    contenido = await archivo.read(TAMANO_MAXIMO_IMAGEN + 1)
    if len(contenido) > TAMANO_MAXIMO_IMAGEN:
        raise HTTPException(status_code=413, detail="La imagen no puede pesar más de 2 MB")

    if not es_imagen_valida(archivo.content_type, contenido):
        raise HTTPException(status_code=415, detail="Solo se permiten imágenes JPG, PNG o WEBP")

    product.imagen = contenido
    product.imagen_tipo = archivo.content_type
    product.imagen_actualizada = func.now()
    db.commit()
    db.refresh(product)
    return product


@router.get("/{producto_id}/imagen")
def ver_imagen(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    product = get_product_or_404(producto_id, db)
    ensure_branch_access(current_user, product.sucursal_id, db)

    if not product.imagen_tipo or product.imagen is None:
        raise HTTPException(status_code=404, detail="El producto no tiene imagen")

    # La URL cambia con cada foto nueva, así que el navegador puede guardarla un día
    return Response(
        content=product.imagen,
        media_type=product.imagen_tipo,
        headers={"Cache-Control": "private, max-age=86400"},
    )


@router.delete(
    "/{producto_id}/imagen",
    response_model=ProductResponse,
)
def eliminar_imagen(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    product = get_product_or_404(producto_id, db)
    ensure_branch_access(current_user, product.sucursal_id, db)

    product.imagen = None
    product.imagen_tipo = None
    product.imagen_actualizada = func.now()
    db.commit()
    db.refresh(product)
    return product
