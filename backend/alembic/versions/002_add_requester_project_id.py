"""add requester_project_id to match_requests

Revision ID: 002
Revises: 001
Create Date: 2026-06-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("match_requests", sa.Column("requester_project_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_match_requests_requester_project_id"),
        "match_requests",
        ["requester_project_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_match_requests_requester_project_id",
        "match_requests",
        "projects",
        ["requester_project_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_match_requests_requester_project_id", "match_requests", type_="foreignkey")
    op.drop_index(op.f("ix_match_requests_requester_project_id"), table_name="match_requests")
    op.drop_column("match_requests", "requester_project_id")
