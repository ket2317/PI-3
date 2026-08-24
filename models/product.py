from sqlalchemy import Column, BigInteger, Text, Numeric, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "productos"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    codigo = Column(Text, unique=True, nullable=False)
    nombre = Column(Text, nullable=False)
    precio = Column(Numeric, nullable=False)
    iva = Column(Numeric, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)