"""empty message

Revision ID: 1e5b445ac946
Revises: 34f3a20c806b
Create Date: 2023-09-06 20:41:13.579252

"""
from alembic import op
import sqlalchemy as sa


revision = '1e5b445ac946'
down_revision = '34f3a20c806b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('piece', schema=None) as batch_op:
        batch_op.alter_column('midi',
               existing_type=sa.VARCHAR(),
               type_=sa.LargeBinary(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('piece', schema=None) as batch_op:
        batch_op.alter_column('midi',
               existing_type=sa.LargeBinary(),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    # ### end Alembic commands ###