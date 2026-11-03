"""indices_busqueda

Revision ID: e5c1a9d3b7f2
Revises: d4b7e8a1c2f3
Create Date: 2026-11-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5c1a9d3b7f2'
down_revision: Union[str, Sequence[str], None] = 'd4b7e8a1c2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Columnas que usan las barras de búsqueda (ILIKE '%texto%')
INDICES = [
    ("ix_productos_nombre_busqueda", "productos", "nombre"),
    ("ix_productos_codigo_busqueda", "productos", "codigo"),
    ("ix_sucursales_nombre_busqueda", "sucursales", "nombre"),
]


def upgrade() -> None:
    bind = op.get_bind()

    # pg_trgm permite que ILIKE '%texto%' use el índice. Si el servidor no
    # deja instalar la extensión, se crean índices normales.
    usar_trigramas = True
    try:
        with bind.begin_nested():
            bind.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    except Exception:
        usar_trigramas = False

    for nombre, tabla, columna in INDICES:
        if usar_trigramas:
            op.execute(
                f"CREATE INDEX IF NOT EXISTS {nombre} ON {tabla} "
                f"USING gin ({columna} gin_trgm_ops)"
            )
        else:
            op.execute(f"CREATE INDEX IF NOT EXISTS {nombre} ON {tabla} (lower({columna}))")


def downgrade() -> None:
    for nombre, _tabla, _columna in INDICES:
        op.execute(f"DROP INDEX IF EXISTS {nombre}")
