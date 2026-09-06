from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

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

    telefono = Column(Text, nullable=True)
    contacto = Column(Text, nullable=True)

    gerente_id = Column(
        BigInteger,
        ForeignKey(
            "usuarios.id",
            name="fk_sucursales_gerente",
            use_alter=True
        ),
        nullable=True
    )

    activo = Column(Boolean, default=True, nullable=False)

    usuarios = relationship(
        "User",
        foreign_keys="User.sucursal_id",
        back_populates="sucursal"
    )

    gerente = relationship(
        "User",
        foreign_keys=[gerente_id]
    )

    inventarios = relationship(
        "Inventory",
        back_populates="sucursal"
    )