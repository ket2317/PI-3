from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "usuarios"

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    nombre = Column(Text, nullable=False)
    correo = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    rol_id = Column(
    BigInteger,
    ForeignKey("roles.id"),
    nullable=False
)

    sucursal_id = Column(
        BigInteger,
        ForeignKey("sucursales.id"),
        nullable=True
    )

    activo = Column(Boolean, default=True, nullable=False)