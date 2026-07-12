"""fixing timezone issue

Revision ID: 7e09cefa2baa
Revises: 467df3a539ab
Create Date: 2026-07-06 22:32:43.740590

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e09cefa2baa"
down_revision: str | Sequence[str] | None = "467df3a539ab"
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
