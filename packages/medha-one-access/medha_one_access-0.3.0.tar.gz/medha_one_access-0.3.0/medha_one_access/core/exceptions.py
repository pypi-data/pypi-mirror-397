"""
MedhaOne Access Control Exceptions

Custom exception classes for the access control system.
"""

from typing import Any, Dict, List, Optional


class MedhaAccessError(Exception):
    """Base exception class for MedhaOne Access Control system."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class UserNotFoundError(MedhaAccessError):
    """Raised when a requested user is not found."""

    def __init__(self, user_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"User not found: {user_id}"
        super().__init__(message, details)
        self.user_id = user_id


class ArtifactNotFoundError(MedhaAccessError):
    """Raised when a requested artifact/resource is not found."""

    def __init__(self, artifact_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Artifact not found: {artifact_id}"
        super().__init__(message, details)
        self.artifact_id = artifact_id


class AccessRuleNotFoundError(MedhaAccessError):
    """Raised when a requested access rule is not found."""

    def __init__(self, rule_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Access rule not found: {rule_id}"
        super().__init__(message, details)
        self.rule_id = rule_id


class ExpressionValidationError(MedhaAccessError):
    """Raised when an expression fails validation."""

    def __init__(
        self, expression: str, reason: str, details: Optional[Dict[str, Any]] = None
    ):
        message = f"Expression validation failed for '{expression}': {reason}"
        super().__init__(message, details)
        self.expression = expression
        self.reason = reason


class TimeConstraintError(MedhaAccessError):
    """Raised when time constraints are invalid or cannot be evaluated."""

    def __init__(
        self,
        constraint: Dict[str, Any],
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"Time constraint error: {reason}"
        super().__init__(message, details)
        self.constraint = constraint
        self.reason = reason


class DatabaseConnectionError(MedhaAccessError):
    """Raised when database connection issues occur."""

    def __init__(
        self, database_url: str, reason: str, details: Optional[Dict[str, Any]] = None
    ):
        message = f"Database connection error: {reason}"
        super().__init__(message, details)
        self.database_url = database_url
        self.reason = reason


class ConfigurationError(MedhaAccessError):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self, config_key: str, reason: str, details: Optional[Dict[str, Any]] = None
    ):
        message = f"Configuration error for '{config_key}': {reason}"
        super().__init__(message, details)
        self.config_key = config_key
        self.reason = reason


class PermissionDeniedError(MedhaAccessError):
    """Raised when access is explicitly denied."""

    def __init__(
        self,
        user_id: str,
        resource_id: str,
        permission: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"Permission denied: User '{user_id}' cannot '{permission}' on resource '{resource_id}'"
        super().__init__(message, details)
        self.user_id = user_id
        self.resource_id = resource_id
        self.permission = permission


class CircularDependencyError(MedhaAccessError):
    """Raised when a circular dependency is detected in hierarchies or expressions."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        path: List[str],
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"Circular dependency detected in {entity_type} '{entity_id}': {' -> '.join(path)}"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.path = path


class DataIntegrityError(MedhaAccessError):
    """Raised when data integrity violations occur."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"Data integrity error in {entity_type} '{entity_id}': {reason}"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.reason = reason
