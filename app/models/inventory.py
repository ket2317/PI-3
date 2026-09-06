from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

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

    cantidad = Column(BigInteger, nullable=False, default=0)
    stock_minimo = Column(BigInteger, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    producto = relationship(
        "Product",
        back_populates="inventarios"
    )

    sucursal = relationship(
        "Sucursal",
        back_populates="inventarios"
    )

    __table_args__ = (
        UniqueConstraint(
            "sucursal_id",
            "producto_id",
            name="uq_inventario_sucursal_producto"
        ),
        CheckConstraint(
            "cantidad >= 0",
            name="ck_inventario_cantidad_no_negativa"
        ),
        CheckConstraint(
            "stock_minimo >= 0",
            name="ck_inventario_stock_minimo_no_negativo"
        ),
    )