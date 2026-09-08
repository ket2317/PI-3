from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func

from app.database import Base


class SaleDetail(Base):
    __tablename__ = "detalle_ventas"

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    venta_id = Column(
        BigInteger,
        ForeignKey("ventas.id"),
        nullable=False
    )

    producto_id = Column(
        BigInteger,
        ForeignKey("productos.id"),
        nullable=False
    )

    cantidad = Column(BigInteger, nullable=False)

    precio_unitario = Column(Numeric(10, 2), nullable=False)
    iva = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)