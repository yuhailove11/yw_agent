"""add_platform_governance_tables

Revision ID: a1b2c3d4e5f6
Revises: 8bcc02c9bd07
Create Date: 2026-04-18 22:30:00.000000

"""

from alembic import op
import models as models
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "8bcc02c9bd07"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "dify_registry_app_bindings",
        sa.Column("id", models.types.StringUUID(), nullable=False),
        sa.Column("app_id", models.types.StringUUID(), nullable=False),
        sa.Column("tenant_id", models.types.StringUUID(), nullable=False),
        sa.Column("resource_code", sa.String(length=255), nullable=False),
        sa.Column("sync_status", sa.String(length=32), server_default="synced", nullable=False),
        sa.Column("last_payload", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="dify_registry_app_binding_pkey"),
    )
    with op.batch_alter_table("dify_registry_app_bindings") as batch_op:
        batch_op.create_index("dify_registry_app_binding_app_id_idx", ["app_id"])
        batch_op.create_index("dify_registry_app_binding_resource_code_idx", ["resource_code"])

    op.create_table(
        "dify_shadow_dataset_bindings",
        sa.Column("id", models.types.StringUUID(), nullable=False),
        sa.Column("dataset_id", models.types.StringUUID(), nullable=False),
        sa.Column("tenant_id", models.types.StringUUID(), nullable=False),
        sa.Column("resource_code", sa.String(length=255), nullable=False),
        sa.Column("source_system", sa.String(length=32), server_default="ragflow", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="dify_shadow_dataset_binding_pkey"),
    )
    with op.batch_alter_table("dify_shadow_dataset_bindings") as batch_op:
        batch_op.create_index("dify_shadow_dataset_binding_dataset_idx", ["dataset_id"])
        batch_op.create_index("dify_shadow_dataset_binding_resource_code_idx", ["resource_code"])

    op.create_table(
        "dify_sync_outbox",
        sa.Column("id", models.types.StringUUID(), nullable=False),
        sa.Column("tenant_id", models.types.StringUUID(), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", models.types.StringUUID(), nullable=False),
        sa.Column("operation", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.Text(), server_default="{}", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="dify_sync_outbox_pkey"),
    )
    with op.batch_alter_table("dify_sync_outbox") as batch_op:
        batch_op.create_index("dify_sync_outbox_resource_type_idx", ["resource_type"])
        batch_op.create_index("dify_sync_outbox_status_idx", ["status"])


def downgrade():
    op.drop_table("dify_sync_outbox")
    op.drop_table("dify_shadow_dataset_bindings")
    op.drop_table("dify_registry_app_bindings")
