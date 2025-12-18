"""
MedhaOne Access Control Pydantic Schemas

Data validation and serialization schemas for the access control system.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import time
import re
from pydantic import BaseModel, Field, validator, root_validator


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        orm_mode = True
        from_attributes = True


# User schemas
class UserBase(BaseSchema):
    """Base user schema with common fields."""

    type: str = Field(..., description="User type (USER or USERGROUP)")
    active: bool = Field(True, description="Whether the user is active")
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("type")
    def validate_type(cls, v):
        if v not in ["USER", "USERGROUP"]:
            raise ValueError("Type must be either USER or USERGROUP")
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""

    id: str = Field(..., description="User ID", min_length=1, max_length=255)
    first_name: Optional[str] = Field(
        None, description="First name (for individual users)", max_length=255
    )
    last_name: Optional[str] = Field(
        None, description="Last name (for individual users)", max_length=255
    )
    email: Optional[str] = Field(None, description="Email address", max_length=255)
    department: Optional[str] = Field(None, description="Department", max_length=255)
    role: Optional[str] = Field(None, description="Job role/title", max_length=255)
    expression: Optional[str] = Field(None, description="Expression for user groups")
    manager_id: Optional[str] = Field(
        None, description="ID of user's manager", max_length=255
    )
    parent_group_id: Optional[str] = Field(
        None, description="ID of parent group (for user groups)", max_length=255
    )
    owner_id: Optional[str] = Field(
        None, description="ID of group owner", max_length=255
    )
    description: Optional[str] = Field(None, description="Description (for groups)")

    @validator("email")
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    type: Optional[str] = Field(None, description="User type (USER or USERGROUP)")
    first_name: Optional[str] = Field(
        None, description="First name (for individual users)", max_length=255
    )
    last_name: Optional[str] = Field(
        None, description="Last name (for individual users)", max_length=255
    )
    email: Optional[str] = Field(None, description="Email address", max_length=255)
    department: Optional[str] = Field(None, description="Department", max_length=255)
    role: Optional[str] = Field(None, description="Job role/title", max_length=255)
    expression: Optional[str] = Field(None, description="Expression for user groups")
    manager_id: Optional[str] = Field(
        None, description="ID of user's manager", max_length=255
    )
    parent_group_id: Optional[str] = Field(
        None, description="ID of parent group (for user groups)", max_length=255
    )
    owner_id: Optional[str] = Field(
        None, description="ID of group owner", max_length=255
    )
    description: Optional[str] = Field(None, description="Description (for groups)")
    active: Optional[bool] = Field(None, description="Whether the user is active")
    user_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )

    @validator("type")
    def validate_type(cls, v):
        if v and v not in ["USER", "USERGROUP"]:
            raise ValueError("Type must be either USER or USERGROUP")
        return v

    @validator("email")
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class UserInDB(UserBase):
    """Schema for user data from database."""

    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    expression: Optional[str] = None
    manager_id: Optional[str] = None
    parent_group_id: Optional[str] = None
    owner_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserGroupMember(BaseSchema):
    """Schema for user group membership."""

    user_id: str = Field(..., description="ID of user to add to group")
    group_id: str = Field(..., description="ID of group to add user to")


class UserGroupMembersList(BaseSchema):
    """Schema for list of group members."""

    members: List[str] = Field(
        ..., description="List of user IDs that are members of the group"
    )
    group_id: str = Field(..., description="ID of the group")


# Artifact schemas
class ArtifactBase(BaseSchema):
    """Base artifact schema with common fields."""

    type: str = Field(..., description="Artifact type (RESOURCE or RESOURCEGROUP)")
    description: str = Field(default="", description="Artifact description")
    active: bool = Field(True, description="Whether the artifact is active")
    artifact_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("type")
    def validate_type(cls, v):
        if v not in ["RESOURCE", "RESOURCEGROUP"]:
            raise ValueError("Type must be either RESOURCE or RESOURCEGROUP")
        return v


class ArtifactCreate(ArtifactBase):
    """Schema for creating a new artifact."""

    id: str = Field(default="", description="Artifact ID", max_length=255)
    name: Optional[str] = Field(
        None, description="Name of the artifact", max_length=255
    )
    application: Optional[str] = Field(
        None, description="Application name", max_length=255
    )
    owner_id: Optional[str] = Field(
        None, description="ID of artifact owner", max_length=255
    )
    parent_group_id: Optional[str] = Field(
        None,
        description="ID of parent group (for resource hierarchies)",
        max_length=255,
    )
    expression: Optional[str] = Field(
        None, description="Expression for resource groups"
    )

    @validator("description", pre=True, always=True)
    def ensure_description_not_none(cls, v):
        """Ensure description is not None and provide default if empty."""
        if v is None:
            return ""
        return str(v).strip()

    @root_validator(pre=True)
    def generate_id_if_empty(cls, values):
        """Auto-generate ID if empty using name and timestamp."""
        if isinstance(values, dict):
            artifact_id = values.get("id", "")
            if not artifact_id or artifact_id.strip() == "":
                name = values.get("name", "")
                if name and name.strip():
                    # Create ID from name: lowercase, replace spaces/special chars with underscores
                    base_id = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip().lower())
                    base_id = re.sub(r'_+', '_', base_id).strip('_')  # Remove multiple underscores
                    # Add timestamp to ensure uniqueness
                    timestamp = str(int(time.time() * 1000))[-6:]  # Last 6 digits
                    values["id"] = f"{base_id}_{timestamp}"
                else:
                    # If no name, use timestamp
                    values["id"] = f"artifact_{int(time.time() * 1000)}"
        return values


class ArtifactUpdate(BaseSchema):
    """Schema for updating an artifact."""

    type: Optional[str] = Field(
        None, description="Artifact type (RESOURCE or RESOURCEGROUP)"
    )
    name: Optional[str] = Field(
        None, description="Name of the artifact", max_length=255
    )
    description: Optional[str] = Field(
        None, description="Artifact description", min_length=1
    )
    application: Optional[str] = Field(
        None, description="Application name", max_length=255
    )
    owner_id: Optional[str] = Field(
        None, description="ID of artifact owner", max_length=255
    )
    parent_group_id: Optional[str] = Field(
        None,
        description="ID of parent group (for resource hierarchies)",
        max_length=255,
    )
    expression: Optional[str] = Field(
        None, description="Expression for resource groups"
    )
    active: Optional[bool] = Field(None, description="Whether the artifact is active")
    artifact_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )

    @validator("type")
    def validate_type(cls, v):
        if v and v not in ["RESOURCE", "RESOURCEGROUP"]:
            raise ValueError("Type must be either RESOURCE or RESOURCEGROUP")
        return v


class ArtifactInDB(ArtifactBase):
    """Schema for artifact data from database."""

    id: str
    name: Optional[str] = None
    application: Optional[str] = None
    owner_id: Optional[str] = None
    parent_group_id: Optional[str] = None
    expression: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ArtifactGroupMember(BaseSchema):
    """Schema for artifact group membership."""

    artifact_id: str = Field(..., description="ID of resource to add to group")
    group_id: str = Field(..., description="ID of group to add resource to")


class ArtifactGroupMembersList(BaseSchema):
    """Schema for list of group members."""

    members: List[str] = Field(
        ..., description="List of artifact IDs that are members of the group"
    )
    group_id: str = Field(..., description="ID of the group")


# Access rule schemas
class AccessRuleBase(BaseSchema):
    """Base access rule schema with common fields."""

    user_expression: str = Field(..., description="User expression", min_length=1)
    resource_expression: str = Field(
        ..., description="Resource expression", min_length=1
    )
    permissions: List[str] = Field(..., description="List of permissions", min_items=1)
    active: bool = Field(True, description="Whether the rule is active")
    time_constraints: Optional[Dict[str, Any]] = Field(
        None, description="Time constraints"
    )
    rule_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("permissions")
    def validate_permissions(cls, v):
        if not v:
            raise ValueError("At least one permission must be specified")
        # Common permission validation
        valid_permissions = {
            "READ",
            "WRITE",
            "DELETE",
            "EXECUTE",
            "ADMIN",
            "EXPORT",
            "IMPORT",
        }
        for perm in v:
            if perm not in valid_permissions:
                # Allow custom permissions but warn
                pass
        return v


class AccessRuleCreate(AccessRuleBase):
    """Schema for creating a new access rule."""

    id: str = Field(..., description="Access rule ID", min_length=1, max_length=255)
    name: Optional[str] = Field(
        None, description="Name of the access rule", max_length=255
    )
    description: Optional[str] = Field(None, description="Description of the rule")
    application: Optional[str] = Field(
        None, description="Application name", max_length=255
    )
    is_direct: Optional[bool] = Field(
        True, description="Whether this is a direct rule or inherited"
    )
    parent_rule_id: Optional[str] = Field(
        None, description="ID of parent rule (for inheritance)", max_length=255
    )
    owner_id: Optional[str] = Field(
        None, description="ID of rule owner", max_length=255
    )


class AccessRuleUpdate(BaseSchema):
    """Schema for updating an access rule."""

    name: Optional[str] = Field(
        None, description="Name of the access rule", max_length=255
    )
    description: Optional[str] = Field(None, description="Description of the rule")
    user_expression: Optional[str] = Field(
        None, description="User expression", min_length=1
    )
    resource_expression: Optional[str] = Field(
        None, description="Resource expression", min_length=1
    )
    permissions: Optional[List[str]] = Field(
        None, description="List of permissions", min_items=1
    )
    application: Optional[str] = Field(
        None, description="Application name", max_length=255
    )
    active: Optional[bool] = Field(None, description="Whether the rule is active")
    time_constraints: Optional[Dict[str, Any]] = Field(
        None, description="Time constraints"
    )
    is_direct: Optional[bool] = Field(
        None, description="Whether this is a direct rule or inherited"
    )
    parent_rule_id: Optional[str] = Field(
        None, description="ID of parent rule (for inheritance)", max_length=255
    )
    owner_id: Optional[str] = Field(
        None, description="ID of rule owner", max_length=255
    )
    rule_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )

    @validator("permissions")
    def validate_permissions(cls, v):
        if v is not None and not v:
            raise ValueError("At least one permission must be specified")
        return v


class AccessRuleInDB(AccessRuleBase):
    """Schema for access rule data from database."""

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    application: Optional[str] = None
    is_direct: bool = True
    parent_rule_id: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Access summary schemas
class AccessSummaryBase(BaseSchema):
    """Base access summary schema."""

    user_id: str = Field(..., description="ID of the user")
    application: str = Field(..., description="Application name for isolation")
    total_accessible_resources: int = Field(
        0, description="Total number of accessible resources"
    )
    total_groups: int = Field(
        0, description="Total number of groups the user belongs to"
    )
    direct_permissions: int = Field(0, description="Number of direct permissions")
    inherited_permissions: int = Field(0, description="Number of inherited permissions")
    is_stale: bool = Field(False, description="Whether the summary needs recalculation")
    summary_data: Dict[str, Any] = Field(
        default_factory=dict, description="Additional summary data including detailed permissions"
    )


class AccessSummaryCreate(AccessSummaryBase):
    """Schema for creating an access summary."""

    pass


class AccessSummaryUpdate(BaseSchema):
    """Schema for updating an access summary."""

    application: Optional[str] = Field(None, description="Application name for isolation")
    total_accessible_resources: Optional[int] = Field(
        None, description="Total number of accessible resources"
    )
    total_groups: Optional[int] = Field(
        None, description="Total number of groups the user belongs to"
    )
    direct_permissions: Optional[int] = Field(
        None, description="Number of direct permissions"
    )
    inherited_permissions: Optional[int] = Field(
        None, description="Number of inherited permissions"
    )
    is_stale: Optional[bool] = Field(None, description="Whether the summary needs recalculation")
    summary_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional summary data including detailed permissions"
    )


class AccessSummaryInDB(AccessSummaryBase):
    """Schema for access summary data from database."""

    id: str
    last_calculated: datetime
    created_at: datetime
    updated_at: datetime


# Expression schemas
class ExpressionValidateRequest(BaseSchema):
    """Schema for expression validation requests."""

    expression: str = Field(..., description="Expression to validate", min_length=1)
    expression_type: str = Field(
        ..., description="Type of expression (USER or RESOURCE)"
    )

    @validator("expression_type")
    def validate_expression_type(cls, v):
        if v not in ["USER", "RESOURCE"]:
            raise ValueError("Expression type must be either USER or RESOURCE")
        return v


class ExpressionResolveRequest(BaseSchema):
    """Schema for expression resolution requests."""

    expression: str = Field(..., description="Expression to resolve", min_length=1)
    expression_type: str = Field(
        ..., description="Type of expression (USER or RESOURCE)"
    )

    @validator("expression_type")
    def validate_expression_type(cls, v):
        if v not in ["USER", "RESOURCE"]:
            raise ValueError("Expression type must be either USER or RESOURCE")
        return v


# Access resolution schemas
class AccessCheckRequest(BaseSchema):
    """Schema for access check requests."""

    user_id: str = Field(..., description="User ID", min_length=1)
    resource_id: str = Field(..., description="Resource ID", min_length=1)
    permission: str = Field(..., description="Permission to check", min_length=1)
    evaluation_time: Optional[str] = Field(
        None, description="Evaluation time (ISO format)"
    )


class AccessCheckResponse(BaseSchema):
    """Schema for access check responses."""

    user_id: str
    resource_id: str
    permission: str
    has_access: bool
    evaluation_time: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)


class AccessResolutionResponse(BaseSchema):
    """Schema for access resolution responses."""

    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    evaluation_time: Optional[str] = None
    resolved_access: Dict[str, List[str]] = Field(
        default_factory=dict, description="Map of resource/user IDs to permissions"
    )
    resolved_access_detailed: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Enhanced access map with artifact names and details"
    )
    users_with_access: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of user IDs to permissions (resource-centric)",
    )
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)


# Data import/export schemas
class ImportData(BaseSchema):
    """Schema for data import requests."""

    users: Optional[List[UserCreate]] = Field(None, description="Users to import")
    artifacts: Optional[List[ArtifactCreate]] = Field(
        None, description="Artifacts to import"
    )
    access_rules: Optional[List[AccessRuleCreate]] = Field(
        None, description="Access rules to import"
    )


class ExportRequest(BaseSchema):
    """Schema for data export requests."""

    include_users: bool = Field(True, description="Whether to include users in export")
    include_artifacts: bool = Field(
        True, description="Whether to include artifacts in export"
    )
    include_access_rules: bool = Field(
        True, description="Whether to include access rules in export"
    )
    user_ids: Optional[List[str]] = Field(
        None, description="Specific user IDs to export"
    )
    artifact_ids: Optional[List[str]] = Field(
        None, description="Specific artifact IDs to export"
    )
    rule_ids: Optional[List[str]] = Field(
        None, description="Specific rule IDs to export"
    )


# Export all schemas
__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserGroupMember",
    "UserGroupMembersList",
    # Artifact schemas
    "ArtifactBase",
    "ArtifactCreate",
    "ArtifactUpdate",
    "ArtifactInDB",
    "ArtifactGroupMember",
    "ArtifactGroupMembersList",
    # Access rule schemas
    "AccessRuleBase",
    "AccessRuleCreate",
    "AccessRuleUpdate",
    "AccessRuleInDB",
    # Access summary schemas
    "AccessSummaryBase",
    "AccessSummaryCreate",
    "AccessSummaryUpdate",
    "AccessSummaryInDB",
    # Expression schemas
    "ExpressionValidateRequest",
    "ExpressionResolveRequest",
    # Access resolution schemas
    "AccessCheckRequest",
    "AccessCheckResponse",
    "AccessResolutionResponse",
    # Data I/O schemas
    "ImportData",
    "ExpressionRequest",
]
