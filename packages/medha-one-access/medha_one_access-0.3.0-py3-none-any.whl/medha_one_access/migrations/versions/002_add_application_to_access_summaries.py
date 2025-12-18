"""Add application field to access_summaries

Revision ID: 002
Revises: 001
Create Date: 2025-08-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add application field and is_stale field to access_summaries table"""
    
    # Add new columns
    op.add_column('access_summaries', sa.Column('application', sa.String(), nullable=True))
    op.add_column('access_summaries', sa.Column('is_stale', sa.Boolean(), nullable=True, default=False))
    op.add_column('access_summaries', sa.Column('pk_id', sa.Integer(), autoincrement=True, nullable=True))
    
    # Set default values for existing records (if any)
    # Note: In production, you might want to set a meaningful default application name
    op.execute("UPDATE access_summaries SET application = 'default', is_stale = false WHERE application IS NULL")
    op.execute("UPDATE access_summaries SET pk_id = ROW_NUMBER() OVER (ORDER BY created_at) WHERE pk_id IS NULL")
    
    # Make columns non-nullable after setting defaults
    op.alter_column('access_summaries', 'application', nullable=False)
    op.alter_column('access_summaries', 'is_stale', nullable=False)
    op.alter_column('access_summaries', 'pk_id', nullable=False)
    
    # Drop old indexes
    op.drop_index('idx_accesssummary_user_id', table_name='access_summaries')
    op.drop_index('idx_accesssummary_last_calc', table_name='access_summaries')
    
    # Add new primary key (drop old first)
    op.drop_constraint('access_summaries_pkey', 'access_summaries', type_='primary')
    op.create_primary_key('access_summaries_pkey', 'access_summaries', ['pk_id'])
    
    # Create new indexes
    op.create_index('idx_accesssummary_user_app', 'access_summaries', ['user_id', 'application'])
    op.create_index('idx_accesssummary_last_calc', 'access_summaries', ['last_calculated'])
    op.create_index('idx_accesssummary_stale', 'access_summaries', ['is_stale', 'application'])


def downgrade():
    """Remove application field and is_stale field from access_summaries table"""
    
    # Drop new indexes
    op.drop_index('idx_accesssummary_user_app', table_name='access_summaries')
    op.drop_index('idx_accesssummary_last_calc', table_name='access_summaries')
    op.drop_index('idx_accesssummary_stale', table_name='access_summaries')
    
    # Restore old primary key
    op.drop_constraint('access_summaries_pkey', 'access_summaries', type_='primary')
    op.create_primary_key('access_summaries_pkey', 'access_summaries', ['id'])
    
    # Recreate old indexes
    op.create_index('idx_accesssummary_user_id', 'access_summaries', ['user_id'])
    op.create_index('idx_accesssummary_last_calc', 'access_summaries', ['last_calculated'])
    
    # Remove new columns
    op.drop_column('access_summaries', 'pk_id')
    op.drop_column('access_summaries', 'is_stale')
    op.drop_column('access_summaries', 'application')