"""empty message

Revision ID: e6ea4c3bf968
Revises: 129f33627e6d
Create Date: 2020-01-11 20:33:07.898217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6ea4c3bf968'
down_revision = '129f33627e6d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exercise', sa.Column('type', sa.String(length=15), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('exercise', 'type')
    # ### end Alembic commands ###