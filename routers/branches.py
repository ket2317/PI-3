# 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.branch  import Sucursal
from schemas.branch import SucursalCreate, SucursalResponse


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


@router.put("/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(
    sucursal_id: int,
    sucursal: SucursalCreate,
    db: Session = Depends(get_db)
):
    sucursal_db = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()

    if not sucursal_db:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    sucursal_db.nombre = sucursal.nombre
    sucursal_db.direccion = sucursal.direccion

    db.commit()
    db.refresh(sucursal_db)

    return sucursal_db


@router.delete("/{sucursal_id}")
def desactivar_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db)
):
    sucursal_db = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id
    ).first()

    if not sucursal_db:
        raise HTTPException(
            status_code=404,
            detail="Sucursal no encontrada"
        )

    sucursal_db.activo = False
    db.commit()

    return {"message": "Sucursal desactivada correctamente"}