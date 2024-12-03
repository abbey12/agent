"""Add user profile fields

Revision ID: 72109e20cef2
Revises: cc4a8d5476b1
Create Date: 2024-11-11 00:53:51.432048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72109e20cef2'
down_revision = 'cc4a8d5476b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('facility_name', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('clinical_position', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('years_of_experience', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('country')
        batch_op.drop_column('gender')
        batch_op.drop_column('years_of_experience')
        batch_op.drop_column('clinical_position')
        batch_op.drop_column('facility_name')
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###
