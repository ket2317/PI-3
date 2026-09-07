from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categorias", tags=["Categorías"])


def get_category_or_404(categoria_id: int, db: Session) -> Category:
    category = db.query(Category).filter(Category.id == categoria_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


def ensure_unique_name(nombre: str, db: Session, categoria_id: int | None = None) -> None:
    query = db.query(Category).filter(Category.nombre == nombre)
    if categoria_id is not None:
        query = query.filter(Category.id != categoria_id)
    if query.first() is not None:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")


@router.get("/", response_model=list[CategoryResponse])
def obtener_categorias(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Category).order_by(Category.nombre).all()


@router.get("/{categoria_id}", response_model=CategoryResponse)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_category_or_404(categoria_id, db)


@router.post("/", response_model=CategoryResponse, status_code=201)
def crear_categoria(data: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    nombre = data.nombre.strip()
    ensure_unique_name(nombre, db)
    category = Category(nombre=nombre)
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al crear la categoría")
    return category


@router.put("/{categoria_id}", response_model=CategoryResponse)
def actualizar_categoria(categoria_id: int, data: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    category = get_category_or_404(categoria_id, db)
    nombre = data.nombre.strip()
    ensure_unique_name(nombre, db, categoria_id)
    category.nombre = nombre
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al actualizar la categoría")
    return category


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    category = get_category_or_404(categoria_id, db)
    if db.query(Product.id).filter(Product.categoria_id == categoria_id).first() is not None:
        raise HTTPException(status_code=409, detail="No se puede eliminar una categoría que tiene productos")
    db.delete(category)
    db.commit()
    return {"message": "Categoría eliminada correctamente"}
