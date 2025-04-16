"""add nombre to promocion

Revision ID: 4f44440c0699
Revises: b2dadbb70624
Create Date: 2025-04-16 10:53:50.320960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f44440c0699'
down_revision = 'b2dadbb70624'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('promociones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nombre', sa.String(length=100), nullable=False, server_default='Sin nombre'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('promociones', schema=None) as batch_op:
        batch_op.drop_column('nombre')

    # ### end Alembic commands ###
