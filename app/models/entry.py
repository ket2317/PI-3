from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Entry(Base):
    __tablename__ = "entradas"

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    sucursal_id = Column(
        BigInteger,
        ForeignKey("sucursales.id"),
        nullable=False
    )

    usuario_id = Column(
        BigInteger,
        ForeignKey("usuarios.id"),
        nullable=False
    )