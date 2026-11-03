from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base

# Cambiar la versión hace que todos los usuarios vuelvan a ver el aviso
VERSION_AVISO_PRIVACIDAD = "1.0"


class PrivacyAcceptance(Base):
    __tablename__ = "aceptaciones_privacidad"
    __table_args__ = (
        UniqueConstraint("usuario_id", "version_aviso", name="uq_aceptacion_usuario_version"),
    )

    id = Column(BigInteger, primary_key=True)

    usuario_id = Column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_aviso = Column(Text, nullable=False)

    fecha_aceptacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
