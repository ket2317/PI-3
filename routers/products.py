from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from models.product import Product
from schemas.product import ProductCreate, ProductResponse


router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


@router.get("/", response_model=list[ProductResponse])
def obtener_productos(db: Session = Depends(get_db)):
    productos = db.query(Product).all()
    return productos


@router.post("/", response_model=ProductResponse)
def crear_producto(producto: ProductCreate, db: Session = Depends(get_db)):
    nuevo_producto = Product(
        codigo=producto.codigo,
        nombre=producto.nombre,
        precio=producto.precio,
        iva=producto.iva,
        activo=True
    )

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    return nuevo_producto