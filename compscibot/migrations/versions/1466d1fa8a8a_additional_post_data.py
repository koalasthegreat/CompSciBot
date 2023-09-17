"""Add additional post data

Revision ID: 1466d1fa8a8a
Revises: 52b5dd47f84e
Create Date: 2022-11-14 20:28:19.747580

"""
import sqlalchemy as sa
from alembic import op

revision = "1466d1fa8a8a"
down_revision = "52b5dd47f84e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("channel_id", sa.BigInteger(), nullable=True))
    op.add_column("posts", sa.Column("content", sa.Text(), nullable=True))
    op.add_column("posts", sa.Column("star_count", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("posts", "star_count")
    op.drop_column("posts", "content")
    op.drop_column("posts", "channel_id")
