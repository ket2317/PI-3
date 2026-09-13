from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "productos"

    __table_args__ = (
        UniqueConstraint(
            "sucursal_id",
            "codigo",
            name="uq_productos_sucursal_codigo"
        ),
    )

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    codigo = Column(Text, nullable=False)
    nombre = Column(Text, nullable=False)

    precio = Column(
        Numeric(12, 2),
        nullable=False
    )
    iva = Column(
        Numeric(5, 4),
        nullable=False
    )
    categoria_id = Column(
        BigInteger,
        ForeignKey("categorias.id"),
        nullable=True
    )

    # NUEVO: sucursal propietaria del producto
    sucursal_id = Column(
        BigInteger,
        ForeignKey("sucursales.id"),
        nullable=False
    )

    categoria = relationship(
        "Category",
        back_populates="productos"
    )

    sucursal = relationship(
        "Sucursal",
        back_populates="productos"
    )

    activo = Column(Boolean, default=True, nullable=False)

    inventarios = relationship(
        "Inventory",
        back_populates="producto",
        cascade="all, delete-orphan"
    )
