from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin, require_admin_or_manager
from app.models.branch import Sucursal
from app.models.user import User
from app.schemas.branch import SucursalCreate, SucursalResponse, SucursalUpdate


router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


def get_branch_or_404(sucursal_id: int, db: Session) -> Sucursal:
    branch = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return branch


def ensure_branch_access(user: User, sucursal_id: int) -> None:
    if user.role_name == "GERENTE" and user.sucursal_id != sucursal_id:
        raise HTTPException(status_code=403, detail="No puedes acceder a otra sucursal")


@router.get("/", response_model=list[SucursalResponse])
def obtener_sucursales(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    query = db.query(Sucursal).filter(Sucursal.activo.is_(True))
    if current_user.role_name == "GERENTE":
        query = query.filter(Sucursal.id == current_user.sucursal_id)
    return query.all()


@router.get("/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    ensure_branch_access(current_user, sucursal_id)
    return get_branch_or_404(sucursal_id, db)


@router.post("/", response_model=SucursalResponse, status_code=201)
def crear_sucursal(
    data: SucursalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    branch = Sucursal(**data.model_dump(), activo=True)
    db.add(branch)
    try:
        db.commit()
        db.refresh(branch)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al crear la sucursal")
    return branch


@router.put("/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(
    sucursal_id: int,
    data: SucursalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    ensure_branch_access(current_user, sucursal_id)
    branch = get_branch_or_404(sucursal_id, db)
    branch.nombre = data.nombre
    branch.direccion = data.direccion
    branch.telefono = data.telefono
    branch.contacto = data.contacto
    if current_user.role_name == "ADMIN":
        branch.activo = data.activo
        branch.gerente_id = data.gerente_id
    try:
        db.commit()
        db.refresh(branch)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al actualizar la sucursal")
    return branch


@router.delete("/{sucursal_id}")
def desactivar_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    branch = get_branch_or_404(sucursal_id, db)
    branch.activo = False
    db.commit()
    return {"message": "Sucursal desactivada correctamente"}
