"""indices_para_reportes_de_ventas

Revision ID: 8d7268152246
Revises: 091c63ac5145
Create Date: 2026-09-15 08:47:26.948455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d7268152246'
down_revision: Union[str, Sequence[str], None] = '091c63ac5145'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_ventas_sucursal_created",
        "ventas",
        ["sucursal_id", "created_at"],
    )
    op.create_index(
        "ix_detalle_ventas_venta_id",
        "detalle_ventas",
        ["venta_id"],
    )
    op.create_index(
        "ix_detalle_ventas_producto_id",
        "detalle_ventas",
        ["producto_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_detalle_ventas_producto_id",
        table_name="detalle_ventas",
    )
    op.drop_index(
        "ix_detalle_ventas_venta_id",
        table_name="detalle_ventas",
    )
    op.drop_index(
        "ix_ventas_sucursal_created",
        table_name="ventas",
    )
