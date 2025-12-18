"""
MedhaOne Access Control Database Models

SQLAlchemy models for the access control system.
Simple, clean models with only essential fields.
"""

from sqlalchemy import (
    Boolean,
    Column,
    String,
    DateTime,
    JSON,
    Integer,
    Index,
)
from sqlalchemy.sql import func

from medha_one_access.core.base import Base


class User(Base):
    """
    User model for individual users and user groups.
    
    Supports both individual users (type="USER") and user groups (type="USERGROUP").
    User groups use expressions to define membership dynamically.
    """

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)  # "USER" or "USERGROUP"
    expression = Column(String, nullable=True)  # Only for USERGROUP
    active = Column(Boolean, default=True)

    # Basic user fields
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    department = Column(String, nullable=True)
    role = Column(String, nullable=True)
    description = Column(String, nullable=True)  # Description for groups
    
    # Hierarchy fields
    manager_id = Column(String, nullable=True)  # ID of manager
    parent_group_id = Column(String, nullable=True)  # ID of parent group
    owner_id = Column(String, nullable=True)  # ID of owner

    # Metadata
    user_metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(id='{self.id}', type='{self.type}', active={self.active})>"

    # Performance indexes
    __table_args__ = (
        Index('idx_user_id_active', 'id', 'active'),  # Most common lookup pattern
        Index('idx_user_type_active', 'type', 'active'),  # Filter by type and active
        Index('idx_user_email', 'email'),  # Email lookups
        Index('idx_user_manager', 'manager_id'),  # Hierarchy queries
    )


class Artifact(Base):
    """
    Artifact model for resources and resource groups.
    
    Supports both individual resources (type="RESOURCE") and resource groups (type="RESOURCEGROUP").
    Resource groups use expressions to define contents dynamically.
    """

    __tablename__ = "artifacts"
    pk_id = Column(Integer, primary_key=True, autoincrement=True)  # Surrogate PK
    id = Column(String, nullable=False)  # Business ID (can be duplicate across applications)
    type = Column(String, nullable=False)  # "RESOURCE" or "RESOURCEGROUP"
    name = Column(String, nullable=True)
    description = Column(String, nullable=False)
    expression = Column(String, nullable=True)  # Only for RESOURCEGROUP
    application = Column(String, nullable=False)  # Application name
    owner_id = Column(String, nullable=True)  # ID of artifact owner
    parent_group_id = Column(String, nullable=True)  # ID of parent group
    active = Column(Boolean, default=True)

    # Metadata
    artifact_metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Artifact(id='{self.id}', application='{self.application}', type='{self.type}', active={self.active})>"

    # Performance indexes
    __table_args__ = (
        Index('idx_artifact_id_app_active', 'id', 'application', 'active'),  # Primary lookup pattern
        Index('idx_artifact_type_app_active', 'type', 'application', 'active'),  # Filter by type
        Index('idx_artifact_application', 'application'),  # Application filtering
        Index('idx_artifact_owner', 'owner_id'),  # Owner queries
        Index('idx_artifact_parent_group', 'parent_group_id'),  # Hierarchy queries
    )


class AccessRule(Base):
    """
    Access rule model defining permissions between users and resources.
    
    Uses expressions to define which users have which permissions on which resources.
    Supports time constraints for conditional access.
    """

    __tablename__ = "access_rules"

    pk_id = Column(Integer, primary_key=True, autoincrement=True)  # Surrogate PK
    id = Column(String, nullable=False)  # Business ID (can be duplicate across applications)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    user_expression = Column(String, nullable=False)
    resource_expression = Column(String, nullable=False)
    permissions = Column(JSON, nullable=False)  # Array of permission strings
    application = Column(String, nullable=False)  # Application name (required for composite PK)
    time_constraints = Column(JSON, nullable=True)  # Time constraint object
    active = Column(Boolean, default=True)
    
    # Additional fields from schema
    is_direct = Column(Boolean, default=True)  # Whether this is a direct rule or inherited
    parent_rule_id = Column(String, nullable=True)  # ID of parent rule (for inheritance)
    owner_id = Column(String, nullable=True)  # ID of rule owner

    # Metadata
    rule_metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<AccessRule(id='{self.id}', application='{self.application}', active={self.active}, permissions={self.permissions})>"

    # Performance indexes
    __table_args__ = (
        Index('idx_accessrule_id_app_active', 'id', 'application', 'active'),  # Primary lookup
        Index('idx_accessrule_active_app', 'active', 'application'),  # Most common filter
        Index('idx_accessrule_user_expr', 'user_expression'),  # Expression searches
        Index('idx_accessrule_resource_expr', 'resource_expression'),  # Expression searches
        Index('idx_accessrule_owner', 'owner_id'),  # Owner queries
    )


class AccessSummary(Base):
    """
    Pre-calculated access summaries for performance optimization.
    
    Stores aggregated access information for users to avoid expensive real-time calculations.
    Application-scoped for multi-tenant support.
    """

    __tablename__ = "access_summaries"

    pk_id = Column(Integer, primary_key=True, autoincrement=True)  # Surrogate PK
    id = Column(String, nullable=False)  # Business ID (can be duplicate across applications)
    user_id = Column(String, nullable=False)  # ID of user this summary is for
    application = Column(String, nullable=False)  # Application name for isolation
    total_accessible_resources = Column(Integer, default=0)
    total_groups = Column(Integer, default=0)
    direct_permissions = Column(Integer, default=0)
    inherited_permissions = Column(Integer, default=0)
    last_calculated = Column(DateTime(timezone=True), server_default=func.now())
    is_stale = Column(Boolean, default=False)  # Mark for recalculation when data changes

    # Summary data - stores detailed permissions and metadata
    summary_data = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<AccessSummary(user_id='{self.user_id}', application='{self.application}', resources={self.total_accessible_resources})>"

    # Performance indexes
    __table_args__ = (
        Index('idx_accesssummary_user_app', 'user_id', 'application'),  # Primary lookup pattern
        Index('idx_accesssummary_user_app_stale', 'user_id', 'application', 'is_stale'),  # Optimized cache lookup
        Index('idx_accesssummary_last_calc', 'last_calculated'),  # For cache invalidation
        Index('idx_accesssummary_stale', 'is_stale', 'application'),  # Find stale summaries
    )


# Export all models
__all__ = [
    "User",
    "Artifact", 
    "AccessRule",
    "AccessSummary",
]