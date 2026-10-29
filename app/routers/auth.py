import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, get_role_name
from app.models.user import User
from app.schemas.user import AuthUser, UserLogin
from app.services.email import enviar_correo_recuperacion
import uuid

# Esquema para validar los datos que vienen del formulario de nueva contraseña
class ResetPasswordSchema(BaseModel):
    token: str
    nueva_password: str

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# Configuración de las plantillas HTML
templates = Jinja2Templates(directory="app/templates")

# Esquema para recibir el correo
class ResetRequest(BaseModel):
    email: str


def to_auth_user(
    user: User,
    db: Session,
) -> AuthUser:
    return AuthUser(
        id=user.id,
        nombre=user.nombre,
        correo=user.correo,
        rol=get_role_name(user, db),
        sucursal_id=user.sucursal_id,
    )


@router.post(
    "/login",
    response_model=AuthUser,
)
def login(
    data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.correo == data.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
        )

    if not user.activo:
        raise HTTPException(
            status_code=401,
            detail="Usuario inactivo",
        )

    valid_password = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
        )

    request.session.clear()
    request.session["user_id"] = user.id

    return to_auth_user(user, db)


@router.get(
    "/me",
    response_model=AuthUser,
)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return to_auth_user(current_user, db)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {
        "message": "Sesión cerrada",
    }


# ruta para recuperacion de contraseña

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="forgot-password.html")


@router.post("/recuperar-password")
async def process_forgot_password(
    payload: ResetRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. Buscar si el correo existe en la base de datos de usuarios
    user = db.query(User).filter(User.correo == payload.email).first()

    if user:
        # 2. Generar un token único para el restablecimiento
        token = str(uuid.uuid4())

        user.reset_token = token
        db.commit()

        # 3. Enviar el correo electrónico mediante Gmail
        enlace = str(request.url_for("vista_reset_password").include_query_params(token=token))
        try:
            await enviar_correo_recuperacion(user.correo, enlace)
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            raise HTTPException(status_code=500, detail="No se pudo enviar el correo de recuperación")

    # Por seguridad, respondemos siempre con éxito para no filtrar qué correos están registrados
    return {"message": "Si el correo existe, se enviaron las instrucciones."}


# 1. Muestra la vista HTML de nueva contraseña (al hacer clic en el enlace del correo)
@router.get("/reset-password", response_class=HTMLResponse)
async def vista_reset_password(request: Request, token: str):
    return templates.TemplateResponse(
        request=request,
        name="reset-password.html",
        context={"token": token},
    )


# 2. Recibe la nueva contraseña y la actualiza en la base de datos
@router.post("/actualizar-password")
async def actualizar_password(payload: ResetPasswordSchema, db: Session = Depends(get_db)):
    # Buscamos al usuario que tenga este token exacto en la base de datos
    user = None
    if payload.token:
        user = db.query(User).filter(User.reset_token == payload.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="El enlace es inválido o ha expirado.")

    # Generamos el hash seguro con bcrypt de la nueva contraseña
    hashed_bytes = bcrypt.hashpw(payload.nueva_password.encode("utf-8"), bcrypt.gensalt())

    # Actualizamos la contraseña y BORRAMOS el token para que no se pueda volver a usar
    user.password_hash = hashed_bytes.decode("utf-8")
    user.reset_token = None
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")
