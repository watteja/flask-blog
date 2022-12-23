"""Boolean field for public topics.

Revision ID: 2dcc319aa502
Revises: f2e85849f360
Create Date: 2022-12-23 09:17:38.348097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2dcc319aa502'
down_revision = 'f2e85849f360'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_public', sa.Boolean(), server_default=sa.text('false'), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.drop_column('is_public')

    # ### end Alembic commands ###
