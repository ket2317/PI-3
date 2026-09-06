from sqlalchemy import BigInteger, Column, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categorias"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(Text, unique=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    productos = relationship(
        "Product",
        back_populates="categoria"
    )
