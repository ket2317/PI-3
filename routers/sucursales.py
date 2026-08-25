# 

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from models.sucursal import Sucursal
from schemas.sucursal import SucursalCreate, SucursalResponse


router = APIRouter(
    prefix="/sucursales",
    tags=["Sucursales"]
)


@router.get("/", response_model=list[SucursalResponse])
def obtener_sucursales(db: Session = Depends(get_db)):
    return db.query(Sucursal).all()


@router.post("/", response_model=SucursalResponse)
def crear_sucursal(
    sucursal: SucursalCreate,
    db: Session = Depends(get_db)
):
    nueva_sucursal = Sucursal(
        nombre=sucursal.nombre,
        direccion=sucursal.direccion,
        activo=True
    )

    db.add(nueva_sucursal)
    db.commit()
    db.refresh(nueva_sucursal)

    return nueva_sucursal