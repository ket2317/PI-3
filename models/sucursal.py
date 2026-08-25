# explica al programa como esta estructurada la tabla sucursales en la base de datos

from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Sucursal(Base):
    __tablename__ = "sucursales"

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    nombre = Column(Text, nullable=False)
    direccion = Column(Text, nullable=False)
    activo = Column(Boolean, default=True)
    