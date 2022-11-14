"""Initial migration

Revision ID: 52b5dd47f84e
Revises: 
Create Date: 2022-11-14 19:07:51.232839

"""
import sqlalchemy as sa
from alembic import op

revision = "52b5dd47f84e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("guild_id", sa.BigInteger(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("posts")
