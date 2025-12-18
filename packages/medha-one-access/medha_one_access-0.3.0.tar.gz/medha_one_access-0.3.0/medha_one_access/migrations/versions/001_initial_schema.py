"""Initial schema creation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-08-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create initial tables."""
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('expression', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, default=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('manager_id', sa.String(), nullable=True),
        sa.Column('parent_group_id', sa.String(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('user_metadata', sa.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key constraints for users
    op.create_foreign_key(None, 'users', 'users', ['manager_id'], ['id'])
    op.create_foreign_key(None, 'users', 'users', ['parent_group_id'], ['id'])
    op.create_foreign_key(None, 'users', 'users', ['owner_id'], ['id'])
    
    # Add unique constraint on email
    op.create_unique_constraint(None, 'users', ['email'])
    
    # Create artifacts table
    op.create_table('artifacts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('expression', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, default=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('application', sa.String(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('parent_group_id', sa.String(), nullable=True),
        sa.Column('artifact_metadata', sa.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key constraints for artifacts
    op.create_foreign_key(None, 'artifacts', 'users', ['owner_id'], ['id'])
    op.create_foreign_key(None, 'artifacts', 'artifacts', ['parent_group_id'], ['id'])
    
    # Create access_rules table
    op.create_table('access_rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_expression', sa.String(), nullable=False),
        sa.Column('resource_expression', sa.String(), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=False),
        sa.Column('time_constraints', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, default=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('application', sa.String(), nullable=True),
        sa.Column('is_direct', sa.Boolean(), nullable=True, default=True),
        sa.Column('parent_rule_id', sa.String(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('rule_metadata', sa.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key constraints for access_rules
    op.create_foreign_key(None, 'access_rules', 'users', ['owner_id'], ['id'])
    op.create_foreign_key(None, 'access_rules', 'access_rules', ['parent_rule_id'], ['id'])
    
    # Create access_summaries table
    op.create_table('access_summaries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('total_accessible_resources', sa.Integer(), nullable=True, default=0),
        sa.Column('total_groups', sa.Integer(), nullable=True, default=0),
        sa.Column('direct_permissions', sa.Integer(), nullable=True, default=0),
        sa.Column('inherited_permissions', sa.Integer(), nullable=True, default=0),
        sa.Column('last_calculated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('summary_data', sa.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key constraint for access_summaries
    op.create_foreign_key(None, 'access_summaries', 'users', ['user_id'], ['id'])
    
    # Create association tables
    
    # User group membership association table
    op.create_table('user_group_membership',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.create_foreign_key(None, 'user_group_membership', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'user_group_membership', 'users', ['group_id'], ['id'])
    
    # Artifact group membership association table
    op.create_table('artifact_group_membership',
        sa.Column('artifact_id', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('artifact_id', 'group_id')
    )
    op.create_foreign_key(None, 'artifact_group_membership', 'artifacts', ['artifact_id'], ['id'])
    op.create_foreign_key(None, 'artifact_group_membership', 'artifacts', ['group_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema - Drop all tables."""
    
    # Drop association tables first (to avoid foreign key issues)
    op.drop_table('artifact_group_membership')
    op.drop_table('user_group_membership')
    
    # Drop main tables
    op.drop_table('access_summaries')
    op.drop_table('access_rules')
    op.drop_table('artifacts')
    op.drop_table('users')