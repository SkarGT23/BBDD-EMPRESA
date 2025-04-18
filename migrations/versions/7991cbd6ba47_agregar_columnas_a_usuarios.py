"""Agregar columnas a usuarios

Revision ID: 7991cbd6ba47
Revises: 
Create Date: 2025-04-11 14:46:25.923467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7991cbd6ba47'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('localidad', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('direccion', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('telefono', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('dni', sa.String(length=9), nullable=True))
        batch_op.add_column(sa.Column('cuenta_bancaria', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('cuenta_bancaria')
        batch_op.drop_column('dni')
        batch_op.drop_column('telefono')
        batch_op.drop_column('direccion')
        batch_op.drop_column('localidad')

    # ### end Alembic commands ###
