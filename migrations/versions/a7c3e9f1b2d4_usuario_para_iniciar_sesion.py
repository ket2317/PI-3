"""usuario_para_iniciar_sesion

Revision ID: a7c3e9f1b2d4
Revises: f6d2b0e4c8a1
Create Date: 2026-11-10 10:00:00.000000

"""
import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c3e9f1b2d4'
down_revision: Union[str, Sequence[str], None] = 'f6d2b0e4c8a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Se agrega la columna vacía para poder llenarla
    op.add_column("usuarios", sa.Column("usuario", sa.Text(), nullable=True))

    # 2. A cada usuario que ya existe se le pone como usuario la parte de su
    #    correo antes de la @ (pi3@admin.com -> pi3). Si se repite, se le
    #    agrega un número: juan, juan2, juan3...
    bind = op.get_bind()
    filas = bind.execute(sa.text("SELECT id, correo FROM usuarios ORDER BY id")).fetchall()
    usados = set()
    for id_usuario, correo in filas:
        base = re.sub(r"[^a-z0-9._-]", "", correo.split("@")[0].lower()) or "usuario"
        nombre = base
        numero = 2
        while nombre in usados:
            nombre = f"{base}{numero}"
            numero += 1
        usados.add(nombre)
        bind.execute(
            sa.text("UPDATE usuarios SET usuario = :usuario WHERE id = :id"),
            {"usuario": nombre, "id": id_usuario},
        )

    # 3. Ya con datos, se vuelve obligatoria y única
    op.alter_column("usuarios", "usuario", nullable=False)
    op.create_index("ix_usuarios_usuario", "usuarios", ["usuario"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_usuarios_usuario", table_name="usuarios")
    op.drop_column("usuarios", "usuario")
