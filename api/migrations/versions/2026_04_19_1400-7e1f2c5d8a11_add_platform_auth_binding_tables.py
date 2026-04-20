"""add platform auth binding tables

Revision ID: 7e1f2c5d8a11
Revises: c9f4b7e2aa01
Create Date: 2026-04-19 14:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e1f2c5d8a11"
down_revision: str | Sequence[str] | None = "c9f4b7e2aa01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "platform_auth_user_bindings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("platform_user_id", sa.String(length=64), nullable=False),
        sa.Column("system_code", sa.String(length=32), nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("platform_username", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="platform_auth_user_binding_pkey"),
        sa.UniqueConstraint("platform_user_id", "system_code", name="uniq_platform_auth_user_binding"),
    )
    op.create_index(
        "platform_auth_user_binding_account_id_idx",
        "platform_auth_user_bindings",
        ["account_id"],
        unique=False,
    )

    op.create_table(
        "platform_auth_workspace_bindings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("platform_workspace_id", sa.String(length=64), nullable=False),
        sa.Column("system_code", sa.String(length=32), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("platform_workspace_code", sa.String(length=255), nullable=True),
        sa.Column("platform_workspace_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="platform_auth_workspace_binding_pkey"),
        sa.UniqueConstraint("platform_workspace_id", "system_code", name="uniq_platform_auth_workspace_binding"),
    )
    op.create_index(
        "platform_auth_workspace_binding_tenant_id_idx",
        "platform_auth_workspace_bindings",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("platform_auth_workspace_binding_tenant_id_idx", table_name="platform_auth_workspace_bindings")
    op.drop_table("platform_auth_workspace_bindings")
    op.drop_index("platform_auth_user_binding_account_id_idx", table_name="platform_auth_user_bindings")
    op.drop_table("platform_auth_user_bindings")
