"""empty message

Revision ID: 071da0ae7735
Revises: d176237399bc
Create Date: 2024-11-12 14:52:41.388450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '071da0ae7735'
down_revision = 'd176237399bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hospital', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interaction_count', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('interaction_count')

    with op.batch_alter_table('hospital', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)

    # ### end Alembic commands ###
