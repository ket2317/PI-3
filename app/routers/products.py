from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/productos", tags=["Productos"])


def get_product_or_404(producto_id: int, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == producto_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


def validate_category(categoria_id: int | None, db: Session) -> None:
    if categoria_id is not None and db.query(Category).filter(Category.id == categoria_id).first() is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


def ensure_unique_code(codigo: str, db: Session, producto_id: int | None = None) -> None:
    query = db.query(Product).filter(Product.codigo == codigo)
    if producto_id is not None:
        query = query.filter(Product.id != producto_id)
    if query.first() is not None:
        raise HTTPException(status_code=409, detail="Ya existe un producto con ese código")


@router.get("/", response_model=list[ProductResponse])
def obtener_productos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Product).filter(Product.activo.is_(True)).order_by(Product.nombre).all()


@router.get("/{producto_id}", response_model=ProductResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = get_product_or_404(producto_id, db)
    if not product.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
def crear_producto(data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    codigo = data.codigo.strip()
    ensure_unique_code(codigo, db)
    validate_category(data.categoria_id, db)
    values = data.model_dump()
    values.update(codigo=codigo, nombre=data.nombre.strip())
    product = Product(**values, activo=True)
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al crear el producto")
    return product


@router.put("/{producto_id}", response_model=ProductResponse)
def actualizar_producto(producto_id: int, data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    product = get_product_or_404(producto_id, db)
    codigo = data.codigo.strip()
    ensure_unique_code(codigo, db, producto_id)
    validate_category(data.categoria_id, db)
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    product.codigo = codigo
    product.nombre = data.nombre.strip()
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al actualizar el producto")
    return product


@router.delete("/{producto_id}")
def desactivar_producto(producto_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    product = get_product_or_404(producto_id, db)
    product.activo = False
    db.commit()
    return {"message": "Producto desactivado correctamente"}
