"""empty message

Revision ID: 89d6401b7f62
Revises: 77e0a79fc278
Create Date: 2020-09-16 20:00:08.787868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89d6401b7f62'
down_revision = '77e0a79fc278'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('keywords', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'keywords')
    # ### end Alembic commands ###
