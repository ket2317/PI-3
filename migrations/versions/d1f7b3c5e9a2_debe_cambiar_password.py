"""debe_cambiar_password

Revision ID: d1f7b3c5e9a2
Revises: c9e5a1b3d7f4
Create Date: 2026-11-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1f7b3c5e9a2'
down_revision: Union[str, Sequence[str], None] = 'c9e5a1b3d7f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Los usuarios que ya existen no tienen que cambiarla; solo los que se creen de aquí en adelante
    op.add_column(
        'usuarios',
        sa.Column('debe_cambiar_password', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('usuarios', 'debe_cambiar_password')
