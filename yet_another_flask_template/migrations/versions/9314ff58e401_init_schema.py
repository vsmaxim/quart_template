"""Init schema

Revision ID: 9314ff58e401
Revises: 
Create Date: 2023-04-30 20:07:14.717756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9314ff58e401'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('education.category',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('education.user',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('date_joined', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('education.entry',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('keywords', sa.String(), nullable=False),
    sa.Column('links', sa.String(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('entry')
    op.drop_table('user')
    op.drop_table('category')
