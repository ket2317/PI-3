from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventarios"

    id = Column(BigInteger, primary_key=True, index=True)

    sucursal_id = Column(
        BigInteger,
        ForeignKey("sucursales.id"),
        nullable=False,
        index=True
    )

    producto_id = Column(
        BigInteger,
        ForeignKey("productos.id"),
        nullable=False,
        index=True
    )

    existencia = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)

    actualizado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
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
            name="uq_inventarios_sucursal_producto"
        ),
        CheckConstraint(
            "existencia >= 0",
            name="ck_inventarios_existencia_no_negativa"
        ),
        CheckConstraint(
            "stock_minimo >= 0",
            name="ck_inventarios_stock_minimo_no_negativo"
        ),
    )
