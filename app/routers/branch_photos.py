from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import require_admin, require_authenticated
from app.models.branch_photo import FotoSucursal
from app.models.user import User
from app.routers.branches import ensure_branch_access, get_branch_or_404
from app.schemas.branch import FotoSucursalResponse

router = APIRouter(prefix="/sucursales", tags=["Fotos de sucursales"])

TAMANO_MAXIMO = 2 * 1024 * 1024  # 2 MB por foto
FOTOS_MAXIMAS = 6  # por sucursal

# Los primeros bytes de cada formato. Sirven para comprobar que el archivo
# de verdad es una imagen y no solo que se llame ".jpg".
FIRMAS = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


def es_imagen_valida(tipo: str, contenido: bytes) -> bool:
    if tipo not in FIRMAS:
        return False
    if tipo == "image/webp" and contenido[8:12] != b"WEBP":
        return False
    return any(contenido.startswith(firma) for firma in FIRMAS[tipo])


@router.post("/{sucursal_id}/fotos", response_model=FotoSucursalResponse, status_code=201)
async def subir_foto(
    sucursal_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    sucursal = get_branch_or_404(sucursal_id, db)

    if len(sucursal.fotos) >= FOTOS_MAXIMAS:
        raise HTTPException(
            status_code=422,
            detail=f"Cada sucursal puede tener máximo {FOTOS_MAXIMAS} fotos",
        )

    # Se lee un byte de más para saber si el archivo rebasa el límite
    contenido = await archivo.read(TAMANO_MAXIMO + 1)
    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(status_code=413, detail="La foto no puede pesar más de 2 MB")

    if not es_imagen_valida(archivo.content_type, contenido):
        raise HTTPException(status_code=415, detail="Solo se permiten fotos JPG, PNG o WEBP")

    foto = FotoSucursal(
        sucursal_id=sucursal.id,
        tipo=archivo.content_type,
        contenido=contenido,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


@router.get("/{sucursal_id}/fotos/{foto_id}")
def ver_foto(
    sucursal_id: int,
    foto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    ensure_branch_access(current_user, sucursal_id)
    foto = (
        db.query(FotoSucursal)
        .filter(FotoSucursal.id == foto_id, FotoSucursal.sucursal_id == sucursal_id)
        .first()
    )
    if foto is None:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    # El navegador guarda la foto un día para no volver a pedirla
    return Response(
        content=foto.contenido,
        media_type=foto.tipo,
        headers={"Cache-Control": "private, max-age=86400"},
    )


@router.delete("/{sucursal_id}/fotos/{foto_id}")
def eliminar_foto(
    sucursal_id: int,
    foto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    foto = (
        db.query(FotoSucursal)
        .filter(FotoSucursal.id == foto_id, FotoSucursal.sucursal_id == sucursal_id)
        .first()
    )
    if foto is None:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    db.delete(foto)
    db.commit()
    return {"message": "Foto eliminada"}