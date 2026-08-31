from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductResponse])
def obtener_productos(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.post("/", response_model=ProductResponse)
def crear_producto(producto: ProductCreate, db: Session = Depends(get_db)):
    nuevo_producto = Product(**producto.model_dump(), activo=True)
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


@router.put("/{producto_id}", response_model=ProductResponse)
def actualizar_producto(
    producto_id: int, producto: ProductCreate, db: Session = Depends(get_db)
):
    producto_db = db.query(Product).filter(Product.id == producto_id).first()
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in producto.model_dump().items():
        setattr(producto_db, campo, valor)
    db.commit()
    db.refresh(producto_db)
    return producto_db


@router.delete("/{producto_id}")
def desactivar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto_db = db.query(Product).filter(Product.id == producto_id).first()
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto_db.activo = False
    db.commit()
    return {"message": "Producto desactivado correctamente"}
