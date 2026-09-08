"""Ajustes de los modelos del Sprint 3 sin perder inventario existente.

Revision ID: b6c4d6ad9596
Revises: be2f873c9a46
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b6c4d6ad9596"
down_revision: Union[str, Sequence[str], None] = "be2f873c9a46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("inventario", "inventarios")
    op.drop_index("ix_inventario_id", table_name="inventarios")
    op.alter_column(
        "inventarios",
        "cantidad",
        new_column_name="existencia",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "inventarios",
        "stock_minimo",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "inventarios",
        "created_at",
        new_column_name="actualizado_at",
        existing_type=sa.DateTime(timezone=True),
        existing_server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.execute(
        "ALTER TABLE inventarios RENAME CONSTRAINT "
        "uq_inventario_sucursal_producto TO uq_inventarios_sucursal_producto"
    )
    op.execute(
        "ALTER TABLE inventarios RENAME CONSTRAINT "
        "ck_inventario_cantidad_no_negativa TO ck_inventarios_existencia_no_negativa"
    )
    op.execute(
        "ALTER TABLE inventarios RENAME CONSTRAINT "
        "ck_inventario_stock_minimo_no_negativo "
        "TO ck_inventarios_stock_minimo_no_negativo"
    )
    op.create_index("ix_inventarios_id", "inventarios", ["id"])
    op.create_index("ix_inventarios_sucursal_id", "inventarios", ["sucursal_id"])
    op.create_index("ix_inventarios_producto_id", "inventarios", ["producto_id"])

    op.alter_column(
        "productos",
        "precio",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
    )
    op.alter_column(
        "productos",
        "iva",
        existing_type=sa.Numeric(5, 2),
        type_=sa.Numeric(5, 4),
        existing_nullable=False,
    )
    op.execute("UPDATE sucursales SET telefono = '' WHERE telefono IS NULL")
    op.alter_column(
        "sucursales", "telefono", existing_type=sa.Text(), nullable=False
    )
    op.create_unique_constraint(
        "uq_sucursales_gerente_id", "sucursales", ["gerente_id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_sucursales_gerente_id", "sucursales", type_="unique"
    )
    op.alter_column(
        "sucursales", "telefono", existing_type=sa.Text(), nullable=True
    )
    op.alter_column(
        "productos",
        "iva",
        existing_type=sa.Numeric(5, 4),
        type_=sa.Numeric(5, 2),
        existing_nullable=False,
    )
    op.alter_column(
        "productos",
        "precio",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Numeric(10, 2),
        existing_nullable=False,
    )

    op.drop_index("ix_inventarios_producto_id", table_name="inventarios")
    op.drop_index("ix_inventarios_sucursal_id", table_name="inventarios")
    op.drop_index("ix_inventarios_id", table_name="inventarios")
    op.execute(
        "ALTER TABLE inventarios RENAME CONSTRAINT "
        "uq_inventarios_sucursal_producto TO uq_inventario_sucursal_producto"
    )
    op.execute(
        "ALTER TABLE inventarios RENAME CONSTRAINT "
        "ck_inventarios_existencia_no_negativa TO ck_inventario_cantidad_no_negativa"
    )
    op.execute(
        "ALTER TABLE inventarios RENAME CONSTRAINT "
        "ck_inventarios_stock_minimo_no_negativo "
        "TO ck_inventario_stock_minimo_no_negativo"
    )
    op.alter_column(
        "inventarios",
        "actualizado_at",
        new_column_name="created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.alter_column(
        "inventarios",
        "stock_minimo",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        "inventarios",
        "existencia",
        new_column_name="cantidad",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.rename_table("inventarios", "inventario")
    op.create_index("ix_inventario_id", "inventario", ["id"])
