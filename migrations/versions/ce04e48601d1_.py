"""empty message

Revision ID: ce04e48601d1
Revises: 
Create Date: 2020-07-14 13:33:34.829903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce04e48601d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=24), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('image_file', sa.String(length=40), nullable=True),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.Column('view', sa.Integer(), nullable=True),
    sa.Column('current_account', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('current_account', sa.Integer(), nullable=False),
    sa.Column('safe_bal', sa.Integer(), nullable=True),
    sa.Column('crit_bal', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deposits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=40), nullable=False),
    sa.Column('acct_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['acct_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('expenses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('payee', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('comment', sa.Text(length=40), nullable=True),
    sa.Column('acct_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['acct_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('expenses')
    op.drop_table('deposits')
    op.drop_table('accounts')
    op.drop_table('users')
    # ### end Alembic commands ###
