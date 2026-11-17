from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, LargeBinary, Numeric, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred, relationship

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

    # Foto del producto. deferred() evita cargar los bytes al listar productos
    imagen = deferred(Column(LargeBinary, nullable=True))
    imagen_tipo = Column(Text, nullable=True)
    imagen_actualizada = Column(DateTime(timezone=True), nullable=True)

    @property
    def imagen_url(self):
        if not self.imagen_tipo:
            return None
        # ?v= cambia al subir otra foto para que el navegador no muestre la vieja
        version = int(self.imagen_actualizada.timestamp()) if self.imagen_actualizada else 0
        return f"/productos/{self.id}/imagen?v={version}"

    inventarios = relationship(
        "Inventory",
        back_populates="producto",
        cascade="all, delete-orphan"
    )
