"""Add time_of_day and features to Survey model

Revision ID: 94e81a2497ff
Revises: 51ecf25f4244
Create Date: 2024-12-18 16:49:21.273655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94e81a2497ff'
down_revision = '51ecf25f4244'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('survey', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_of_day', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('features', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('survey', schema=None) as batch_op:
        batch_op.drop_column('features')
        batch_op.drop_column('time_of_day')

    # ### end Alembic commands ###
