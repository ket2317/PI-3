from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func

from app.database import Base


class Sale(Base):
    __tablename__ = "ventas"

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

    metodo_pago_id = Column(
        BigInteger,
        ForeignKey("metodos_pago.id"),
        nullable=False
    )

    subtotal = Column(Numeric(10, 2), nullable=False)
    iva = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)