from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8d4f0a2c3e5'
down_revision: Union[str, Sequence[str], None] = 'a7c3e9f1b2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'fotos_sucursal',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('sucursal_id', sa.BigInteger(), nullable=False),
        sa.Column('tipo', sa.Text(), nullable=False),
        sa.Column('contenido', sa.LargeBinary(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(['sucursal_id'], ['sucursales.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fotos_sucursal_sucursal_id', 'fotos_sucursal', ['sucursal_id'])


def downgrade() -> None:
    op.drop_index('ix_fotos_sucursal_sucursal_id', table_name='fotos_sucursal')
    op.drop_table('fotos_sucursal')