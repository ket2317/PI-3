"""metodos_pago_iniciales

Revision ID: d4b7e8a1c2f3
Revises: c3a91f2e7b10
Create Date: 2026-10-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4b7e8a1c2f3'
down_revision: Union[str, Sequence[str], None] = 'c3a91f2e7b10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

METODOS = ["Efectivo", "Terminal", "Transferencia"]


def upgrade() -> None:
    # Solo agrega los que falten; algunas bases ya los tienen capturados a mano
    bind = op.get_bind()
    for nombre in METODOS:
        existe = bind.execute(
            sa.text("SELECT 1 FROM metodos_pago WHERE lower(nombre) = lower(:nombre)"),
            {"nombre": nombre},
        ).first()
        if not existe:
            bind.execute(
                sa.text("INSERT INTO metodos_pago (nombre) VALUES (:nombre)"),
                {"nombre": nombre},
            )


def downgrade() -> None:
    # No se borran: puede haber ventas que ya los usan
    pass
