"""convert_blogpost_to_article_add_affiliate_fields

Revision ID: 2023051401
Revises: 
Create Date: 2023-05-14 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '2023051401'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create article table
    op.create_table(
        'article',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=80), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('tags', sa.String(length=80), nullable=False),
        sa.Column('affiliate_url', sa.String(), nullable=False, server_default='https://example.com'),
        sa.Column('commission_rate', sa.Float(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_clicked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_category'), 'article', ['category'], unique=False)
    op.create_index(op.f('ix_article_owner_id'), 'article', ['owner_id'], unique=False)
    
    # Add new columns to users table
    op.add_column('users', sa.Column('commission_balance', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))


def downgrade():
    # Drop new columns from users table
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'commission_balance')
    
    # Drop article table
    op.drop_index(op.f('ix_article_owner_id'), table_name='article')
    op.drop_index(op.f('ix_article_category'), table_name='article')
    op.drop_table('article')
