from sqlalchemy import BigInteger, Column, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base


class PaymentMethod(Base):
    __tablename__ = "metodos_pago"

    id = Column(BigInteger, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    nombre = Column(Text, nullable=False)