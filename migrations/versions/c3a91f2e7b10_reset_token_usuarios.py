"""reset_token_usuarios

Revision ID: c3a91f2e7b10
Revises: 8d7268152246
Create Date: 2026-10-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a91f2e7b10'
down_revision: Union[str, Sequence[str], None] = '8d7268152246'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Algunas bases locales ya tienen la columna creada a mano
    columnas = [c["name"] for c in sa.inspect(op.get_bind()).get_columns("usuarios")]
    if "reset_token" not in columnas:
        op.add_column("usuarios", sa.Column("reset_token", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "reset_token")
