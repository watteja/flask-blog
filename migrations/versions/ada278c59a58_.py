"""Renamed tables, and added indices for search in admin dashboard.

Revision ID: ada278c59a58
Revises: fea9b168be5e
Create Date: 2022-12-08 18:59:54.176136

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ada278c59a58'
down_revision = 'fea9b168be5e'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("user", "users")
    op.rename_table("topic", "topics")
    op.rename_table("post", "posts")

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_posts_title'), ['title'], unique=False)

    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_topics_name'), ['name'], unique=False)
    
    # ### end Alembic commands ###


def downgrade():
    op.rename_table("users", "user")
    op.rename_table("topics", "topic")
    op.rename_table("posts", "post")

    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_topics_name'))

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_posts_title'))

    # ### end Alembic commands ###
