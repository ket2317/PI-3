from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, LargeBinary, Text

from sqlalchemy.orm import deferred 
from sqlalchemy.sql import func 
from app.database import Base   

class FotoSucursal(Base):
    __tablename__ = "fotos_sucursal"

    id = Column(BigInteger, primary_key=True, index=True)
    sucursal_id = Column(
        BigInteger,
        ForeignKey("sucursales.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Tipo de imagen: image/jpeg, image/png o image/webp
    tipo = Column(Text, nullable=False)
    # Los bytes de la imagen. deferred() hace que NO se carguen al listar
    # las fotos; solo se leen cuando alguien pide ver esa imagen.
    contenido = deferred(Column(LargeBinary, nullable=False))
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )