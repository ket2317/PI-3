from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventario"

    id = Column(BigInteger, primary_key=True, index=True)

    sucursal_id = Column(
        BigInteger,
        ForeignKey("sucursales.id"),
        nullable=False
    )

    producto_id = Column(
        BigInteger,
        ForeignKey("productos.id"),
        nullable=False
    )

    cantidad = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "sucursal_id",
            "producto_id",
            name="uq_inventario_sucursal_producto"
        ),
    )