"""Init

Revision ID: 62969d08b73e
Revises: 
Create Date: 2024-07-04 01:17:04.248912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62969d08b73e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_staff', sa.Boolean(), nullable=False),
    sa.Column('joined', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('data', sa.Text(), nullable=True),
    sa.Column('added_at', sa.DateTime(), nullable=False),
    sa.Column('added_by', sa.Integer(), nullable=False),
    sa.Column('site', sa.String(), nullable=False),
    sa.Column('is_complete', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['added_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('products')
    op.drop_table('users')
    # ### end Alembic commands ###
