from fastapi import APIRouter, Depends, HTTPException
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
        categoria_id=producto.categoria_id,
        activo=True
    )

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    return nuevo_producto


@router.put("/{producto_id}", response_model=ProductResponse)
def actualizar_producto(
    producto_id: int,
    producto: ProductCreate,
    db: Session = Depends(get_db)
):
    producto_db = db.query(Product).filter(
        Product.id == producto_id
    ).first()

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto_db.codigo = producto.codigo
    producto_db.nombre = producto.nombre
    producto_db.precio = producto.precio
    producto_db.iva = producto.iva
    producto_db.categoria_id = producto.categoria_id

    db.commit()
    db.refresh(producto_db)

    return producto_db


@router.delete("/{producto_id}")
def desactivar_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    producto_db = db.query(Product).filter(
        Product.id == producto_id
    ).first()

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto_db.activo = False
    db.commit()

    return {"message": "Producto desactivado correctamente"}