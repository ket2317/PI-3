from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.category import Category


router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)


@router.get("/")
def obtener_categorias(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/")
def crear_categoria(
    nombre: str,
    db: Session = Depends(get_db)
):
    nueva_categoria = Category(
        nombre=nombre
    )

    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)

    return nueva_categoria


@router.put("/{categoria_id}")
def actualizar_categoria(
    categoria_id: int,
    nombre: str,
    db: Session = Depends(get_db)
):
    categoria_db = db.query(Category).filter(
        Category.id == categoria_id
    ).first()

    if not categoria_db:
        raise HTTPException(
            status_code=404,
            detail="Categoría no encontrada"
        )

    categoria_db.nombre = nombre

    db.commit()
    db.refresh(categoria_db)

    return categoria_db


@router.delete("/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db)
):
    categoria_db = db.query(Category).filter(
        Category.id == categoria_id
    ).first()

    if not categoria_db:
        raise HTTPException(
            status_code=404,
            detail="Categoría no encontrada"
        )

    db.delete(categoria_db)
    db.commit()

    return {"message": "Categoría eliminada correctamente"}