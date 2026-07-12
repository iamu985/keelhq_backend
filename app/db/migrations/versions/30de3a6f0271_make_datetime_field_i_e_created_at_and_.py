"""make datetime field, i.e. created_at and updated_at with timezone

Revision ID: 30de3a6f0271
Revises: 594f982e6f5d
Create Date: 2026-07-06 21:34:37.778248

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "30de3a6f0271"
down_revision: str | Sequence[str] | None = "594f982e6f5d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.alter_column(
        "local_users",
        "created_at",
        existing_type=sa.DateTime(timezone=False),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )

    op.alter_column(
        "local_users",
        "updated_at",
        existing_type=sa.DateTime(timezone=False),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )


def downgrade():
    op.alter_column(
        "local_users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(timezone=False),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )

    op.alter_column(
        "local_users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(timezone=False),
        existing_nullable=True,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
