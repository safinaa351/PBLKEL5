"""empty message

Revision ID: 83b16ae9cc88
Revises: 6592ab898097
Create Date: 2024-01-16 16:56:31.648257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83b16ae9cc88'
down_revision = '6592ab898097'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('image_data', sa.LargeBinary(), nullable=False),
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('images')
    # ### end Alembic commands ###