from fastapi import APIRouter

from app.schemas.user import UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def loguin(data: UserLogin):
    return {
        "message":"login success",
        "data":data.email
    }

