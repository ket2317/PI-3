from fastapi import APIRouter
from app.schemas.branch import BranchCreate

router = APIRouter(
    prefix="/branches",
    tags=["Branches"],
)

@router.get("/")
def get_branches():
    return {
        "message":"Lista de Sucursales"
    }

@router.post("/")
def create_branches(branch: BranchCreate):
    return {
        "message":"Sucursal recibida",
        "branch": branch
    }