"""imagen_producto

Revision ID: c9e5a1b3d7f4
Revises: b8d4f0a2c3e5
Create Date: 2026-11-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e5a1b3d7f4'
down_revision: Union[str, Sequence[str], None] = 'b8d4f0a2c3e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # La foto se guarda en la base de datos: el disco de Render se borra en cada deploy
    op.add_column('productos', sa.Column('imagen', sa.LargeBinary(), nullable=True))
    op.add_column('productos', sa.Column('imagen_tipo', sa.Text(), nullable=True))
    op.add_column('productos', sa.Column('imagen_actualizada', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('productos', 'imagen_actualizada')
    op.drop_column('productos', 'imagen_tipo')
    op.drop_column('productos', 'imagen')
