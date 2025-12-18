"""
MedhaOne Access Control Library

A comprehensive access control system with BODMAS-based resolution for managing
users, resources, and permissions with sophisticated expression-based rules.

Features:
- BODMAS-based access resolution
- Expression-based user and resource grouping
- Time-based access constraints
- Hierarchical organization structures
- FastAPI integration support
- CLI tools for management

Example usage:
    from medha_one_access import AccessController, LibraryConfig

    # Option 1: Direct configuration
    config = LibraryConfig(
        database_url="postgresql://user:pass@localhost/db",
        secret_key="your_secret_key",
        api_prefix="/oneAccess",
        application_name="MyApp"  # Optional: filters all operations by application
    )

    # Option 2: From environment variables
    config = LibraryConfig.from_env()

    # Initialize controller
    controller = AccessController(config)

    # Create users and resources
    controller.create_user({"id": "john", "type": "USER"})
    controller.create_artifact({"id": "doc1", "type": "RESOURCE", "description": "Document 1"})

    # Create access rule
    controller.create_access_rule({
        "id": "rule1",
        "user_expression": "john",
        "resource_expression": "doc1",
        "permissions": ["READ", "WRITE"]
    })

    # Check access
    result = controller.check_access("john", "doc1", "READ")
"""

__version__ = "0.1.0"
__author__ = "MedhaOne Analytics"
__description__ = "Enterprise access control system with BODMAS resolution"

# Import main classes for easy access
from medha_one_access.core.controller import AccessController, AsyncAccessController
from medha_one_access.core.config import LibraryConfig, AccessControlConfig
from medha_one_access.core.models import User, Artifact, AccessRule, AccessSummary
from medha_one_access.core.schemas import (
    UserCreate,
    UserUpdate,
    UserInDB,
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactInDB,
    AccessRuleCreate,
    AccessRuleUpdate,
    AccessRuleInDB,
)

# Import API integration
try:
    from medha_one_access.api import mount_access_control_routes, mount_async_access_control_routes, create_app

    _has_api = True
except ImportError:
    _has_api = False

# Exception classes
from medha_one_access.core.exceptions import (
    MedhaAccessError,
    UserNotFoundError,
    ArtifactNotFoundError,
    AccessRuleNotFoundError,
    ExpressionValidationError,
    TimeConstraintError,
)

__all__ = [
    # Main controller and configuration
    "AccessController",
    "AsyncAccessController",
    "LibraryConfig",
    "AccessControlConfig",
    # Models
    "User",
    "Artifact",
    "AccessRule",
    "AccessSummary",
    # Schemas
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "ArtifactCreate",
    "ArtifactUpdate",
    "ArtifactInDB",
    "AccessRuleCreate",
    "AccessRuleUpdate",
    "AccessRuleInDB",
    # Exceptions
    "MedhaAccessError",
    "UserNotFoundError",
    "ArtifactNotFoundError",
    "AccessRuleNotFoundError",
    "ExpressionValidationError",
    "TimeConstraintError",
]

# Add API functions to exports if available
if _has_api:
    __all__.extend(["mount_access_control_routes", "mount_async_access_control_routes", "create_app"])
