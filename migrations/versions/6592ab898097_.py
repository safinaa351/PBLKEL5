"""empty message

Revision ID: 6592ab898097
Revises: d1ad81579a63
Create Date: 2024-01-16 16:55:58.941267

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6592ab898097'
down_revision = 'd1ad81579a63'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('images')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('file_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('image_data', sa.BLOB(), nullable=False),
    sa.Column('uid', mysql.INTEGER(display_width=50), autoincrement=False, nullable=False),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
