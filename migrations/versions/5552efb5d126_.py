"""empty message

Revision ID: 5552efb5d126
Revises: a1fb3a58ae32
Create Date: 2024-01-19 14:20:54.642340

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5552efb5d126'
down_revision = 'a1fb3a58ae32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('logaccess',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('no_rfid', sa.String(length=50), nullable=False),
    sa.Column('waktu', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo_evidence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_time', sa.DateTime(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('image_data', mysql.MEDIUMBLOB(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('photoevidence')
    op.drop_table('log_rfid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log_rfid',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('no_rfid', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('waktu', mysql.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('photoevidence',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('access_time', mysql.DATETIME(), nullable=False),
    sa.Column('file_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('image_data', mysql.MEDIUMBLOB(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('photo_evidence')
    op.drop_table('logaccess')
    # ### end Alembic commands ###
