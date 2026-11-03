"""aceptaciones_privacidad

Revision ID: f6d2b0e4c8a1
Revises: e5c1a9d3b7f2
Create Date: 2026-11-03 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6d2b0e4c8a1'
down_revision: Union[str, Sequence[str], None] = 'e5c1a9d3b7f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'aceptaciones_privacidad',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('version_aviso', sa.Text(), nullable=False),
        sa.Column(
            'fecha_aceptacion',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'version_aviso', name='uq_aceptacion_usuario_version'),
    )
    op.create_index(
        op.f('ix_aceptaciones_privacidad_usuario_id'),
        'aceptaciones_privacidad',
        ['usuario_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_aceptaciones_privacidad_usuario_id'), table_name='aceptaciones_privacidad')
    op.drop_table('aceptaciones_privacidad')
