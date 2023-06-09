"""add relationship

Revision ID: 10875dbe3c12
Revises: b0df8d13567a
Create Date: 2023-06-20 15:33:48.902566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10875dbe3c12'
down_revision = 'b0df8d13567a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transation_in', sa.Column('transaction_out_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'transation_in', 'transaction_out', ['transaction_out_id'], ['id'])
    op.drop_column('transation_in', 'transaction_out_hash')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transation_in', sa.Column('transaction_out_hash', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'transation_in', type_='foreignkey')
    op.drop_column('transation_in', 'transaction_out_id')
    # ### end Alembic commands ###
