from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func

from app.database import Base


class EntryDetail(Base):
    __tablename__ = "detalle_entradas"

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    entrada_id = Column(
        BigInteger,
        ForeignKey("entradas.id"),
        nullable=False
    )

    producto_id = Column(
        BigInteger,
        ForeignKey("productos.id"),
        nullable=False
    )

    cantidad = Column(BigInteger, nullable=False)

    costo_unitario = Column(Numeric(10, 2), nullable=False)