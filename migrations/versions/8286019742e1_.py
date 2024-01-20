"""empty message

Revision ID: 8286019742e1
Revises: 5552efb5d126
Create Date: 2024-01-19 15:21:24.467656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8286019742e1'
down_revision = '5552efb5d126'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('logaccess', schema=None) as batch_op:
        batch_op.add_column(sa.Column('access', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('logaccess', schema=None) as batch_op:
        batch_op.drop_column('access')

    # ### end Alembic commands ###
