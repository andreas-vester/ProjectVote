"""Initial schema creation.

Revision ID: 000_initial
Revises:
Create Date: 2026-01-29 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create applications table
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("applicant_email", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=False),
        sa.Column("project_title", sa.String(), nullable=False),
        sa.Column("project_description", sa.String(), nullable=False),
        sa.Column("costs", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="applicationstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now', 'localtime')"),
            nullable=False,
        ),
        sa.Column("concluded_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_applications_id", "applications", ["id"], unique=False)

    # Create votes table
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("voter_email", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column(
            "vote",
            sa.Enum("approve", "reject", "abstain", name="voteoption"),
            nullable=True,
        ),
        sa.Column(
            "vote_status",
            sa.Enum("pending", "cast", name="votestatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("voted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_votes_id", "votes", ["id"], unique=False)
    op.create_index("ix_votes_token", "votes", ["token"], unique=False)

    # Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("filepath", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filepath"),
    )
    op.create_index("ix_attachments_id", "attachments", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_attachments_id", table_name="attachments")
    op.drop_table("attachments")
    op.drop_index("ix_votes_token", table_name="votes")
    op.drop_index("ix_votes_id", table_name="votes")
    op.drop_table("votes")
    op.drop_index("ix_applications_id", table_name="applications")
    op.drop_table("applications")
