"""Added first_name and last_name to user model

Revision ID: a2d1826237ab
Revises: 7d5b07cb2050
Create Date: 2024-11-11 10:40:00.182045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2d1826237ab'
down_revision = '7d5b07cb2050'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_profile')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('facility_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('clinical_position', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('years_of_experience', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(length=100), nullable=True))
        batch_op.drop_column('history_count')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('history_count', sa.INTEGER(), nullable=True))
        batch_op.drop_column('country')
        batch_op.drop_column('gender')
        batch_op.drop_column('years_of_experience')
        batch_op.drop_column('clinical_position')
        batch_op.drop_column('facility_name')
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    op.create_table('user_profile',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=True),
    sa.Column('facility_name', sa.VARCHAR(length=100), nullable=True),
    sa.Column('clinical_position', sa.VARCHAR(length=100), nullable=True),
    sa.Column('years_of_experience', sa.INTEGER(), nullable=True),
    sa.Column('gender', sa.VARCHAR(length=10), nullable=True),
    sa.Column('country', sa.VARCHAR(length=100), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
