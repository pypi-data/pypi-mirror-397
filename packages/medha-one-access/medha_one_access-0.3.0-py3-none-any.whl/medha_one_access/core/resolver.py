"""
MedhaOne Access Control BODMAS Resolver

Implementation of BODMAS-based resolution for access control.
Processes access rules using mathematical precedence for predictable results.
"""

from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Any
from sqlalchemy.orm import Session

from medha_one_access.core.models import User, Artifact, AccessRule
from medha_one_access.core.expressions import ExpressionResolver
from medha_one_access.core.constraints import TimeConstraintEvaluator
from medha_one_access.core.exceptions import (
    UserNotFoundError,
    ArtifactNotFoundError,
    MedhaAccessError,
)


class BODMASResolver:
    """
    Implementation of BODMAS-based resolution for access control.

    BODMAS resolution follows these steps:
    1. [UserGroup × ResourceGroup] (Highest Priority)
    2. [UserGroup × Individual Resource]
    3. [Individual User × ResourceGroup]
    4. [Individual User × Individual Resource] (Lowest Priority)
    5. Union all results (additive permissions)
    """

    def __init__(self, db: Session, application_name: Optional[str] = None):
        self.db = db
        self.application_name = application_name
        self.expression_resolver = ExpressionResolver(db, application_name)

    def resolve_user_access(
        self, user_id: str, evaluation_time: Optional[datetime] = None, include_audit: bool = False
    ) -> Dict[str, Any]:
        """
        Determine what resources a user can access.

        Args:
            user_id: ID of user to resolve access for
            evaluation_time: Time to evaluate access (defaults to current time)
            include_audit: Whether to include detailed audit trail (defaults to False for performance)

        Returns:
            Dictionary with resolved access and optional audit trail

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        # Use current time if not provided
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        # Check if user exists and is active
        user = (
            self.db.query(User).filter(User.id == user_id, User.active == True).first()
        )
        if not user:
            raise UserNotFoundError(user_id)

        # Get all active access rules with optimized filtering
        active_rules = self._get_relevant_rules_for_user(user_id)

        # Results structure
        permissions_by_artifact = {}
        audit_trail = [] if include_audit else None

        # Step 1: [UserGroup × ResourceGroup]
        step1_results = self._process_usergroup_resourcegroup(
            user_id, active_rules, evaluation_time, include_audit
        )
        self._update_permissions(permissions_by_artifact, step1_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "UserGroup × ResourceGroup",
                    "appliedRules": step1_results["rules"],
                    "result": step1_results["permissions"],
                }
            )

        # Step 2: [UserGroup × Individual Resource]
        step2_results = self._process_usergroup_resource(
            user_id, active_rules, evaluation_time, include_audit
        )
        self._update_permissions(permissions_by_artifact, step2_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "UserGroup × Individual Resource",
                    "appliedRules": step2_results["rules"],
                    "result": step2_results["permissions"],
                }
            )

        # Step 3: [Individual User × ResourceGroup]
        step3_results = self._process_user_resourcegroup(
            user_id, active_rules, evaluation_time, include_audit
        )
        self._update_permissions(permissions_by_artifact, step3_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "Individual User × ResourceGroup",
                    "appliedRules": step3_results["rules"],
                    "result": step3_results["permissions"],
                }
            )

        # Step 4: [Individual User × Individual Resource]
        step4_results = self._process_user_resource(
            user_id, active_rules, evaluation_time, include_audit
        )
        self._update_permissions(permissions_by_artifact, step4_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "Individual User × Individual Resource",
                    "appliedRules": step4_results["rules"],
                    "result": step4_results["permissions"],
                }
            )

        # Enhance the response with artifact names and metadata
        enhanced_access = {}
        for artifact_id, permissions in permissions_by_artifact.items():
            # Get artifact details from database
            artifact = self.db.query(Artifact).filter(Artifact.id == artifact_id).first()
            artifact_name = (artifact.name if artifact and artifact.name else artifact_id)
            
            # Include all artifact metadata
            artifact_data = {
                "artifact_id": artifact_id,
                "artifact_name": artifact_name,
                "permissions": permissions
            }
            
            # Add all artifact properties if artifact exists
            if artifact:
                artifact_data.update({
                    "type": artifact.type,
                    "description": artifact.description,
                    "active": artifact.active,
                    "application": artifact.application,
                    "owner_id": artifact.owner_id,
                    "parent_group_id": artifact.parent_group_id,
                    "expression": artifact.expression,
                    "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
                    "updated_at": artifact.updated_at.isoformat() if artifact.updated_at else None,
                    "artifact_metadata": artifact.artifact_metadata
                })
            
            enhanced_access[artifact_id] = artifact_data

        # Return final result with optional audit trail
        result = {
            "user_id": user_id,
            "evaluation_time": evaluation_time.isoformat(),
            "resolved_access": permissions_by_artifact,  # Keep original format for compatibility
            "resolved_access_detailed": enhanced_access,  # New detailed format
        }
        
        # Only include audit trail if requested
        if include_audit:
            result["audit_trail"] = audit_trail
            
        return result

    def resolve_user_group_access(
        self, user_group_id: str, evaluation_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Determine what resources a user group can access by expanding the group
        to individual users and aggregating their access.

        Args:
            user_group_id: ID of user group to resolve access for
            evaluation_time: Time to evaluate access (defaults to current time)

        Returns:
            Dictionary with resolved access and audit trail

        Raises:
            UserNotFoundError: If user group doesn't exist
        """
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        # Fetch the user group and its expression
        group = (
            self.db.query(User)
            .filter(
                User.id == user_group_id, User.type == "USERGROUP", User.active == True
            )
            .first()
        )

        if not group:
            raise UserNotFoundError(
                user_group_id, {"reason": "User group not found or not a USERGROUP"}
            )

        if not group.expression:
            return {
                "user_group_id": user_group_id,
                "evaluation_time": evaluation_time.isoformat(),
                "resolved_access": {},
                "audit_trail": [],
            }

        # Resolve member user IDs from the group's expression
        member_user_ids = self.expression_resolver.resolve_user_expression(
            group.expression
        )
        if not member_user_ids:
            return {
                "user_group_id": user_group_id,
                "evaluation_time": evaluation_time.isoformat(),
                "resolved_access": {},
                "audit_trail": [],
            }

        # Aggregate permissions across all group members
        permissions_by_artifact: Dict[str, List[str]] = {}
        audit_trail: List[Dict[str, Any]] = []
        processed_users: Set[str] = set()

        for member_user_id in member_user_ids:
            if member_user_id in processed_users:
                continue
            processed_users.add(member_user_id)

            try:
                # Reuse existing user-centric resolver
                member_result = self.resolve_user_access(
                    member_user_id, evaluation_time
                )

                # Merge member permissions into group-level permissions
                member_access = member_result.get("resolved_access", {})
                self._update_permissions(permissions_by_artifact, member_access)

                # Record per-member audit for traceability
                audit_trail.append(
                    {
                        "memberUserId": member_user_id,
                        "resolved_access": member_access,
                        "memberAudit": member_result.get("audit_trail", []),
                    }
                )

            except UserNotFoundError:
                # Skip non-existent users in group
                audit_trail.append(
                    {
                        "memberUserId": member_user_id,
                        "error": "User not found",
                        "resolved_access": {},
                        "memberAudit": [],
                    }
                )
                continue

        return {
            "user_group_id": user_group_id,
            "evaluation_time": evaluation_time.isoformat(),
            "resolved_access": permissions_by_artifact,
            "audit_trail": audit_trail,
        }

    def resolve_resource_access(
        self, resource_id: str, evaluation_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Determine who can access a resource.

        Args:
            resource_id: ID of resource to resolve access for
            evaluation_time: Time to evaluate access (defaults to current time)

        Returns:
            Dictionary with users and their permissions

        Raises:
            ArtifactNotFoundError: If resource doesn't exist
        """
        # Use current time if not provided
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        # Check if resource exists and is active
        resource = (
            self.db.query(Artifact)
            .filter(Artifact.id == resource_id, Artifact.active == True)
            .first()
        )
        if not resource:
            raise ArtifactNotFoundError(resource_id)

        # Get all active access rules with optimized filtering
        active_rules = self._get_relevant_rules_for_resource(resource_id)

        # Results structure
        permissions_by_user = {}
        audit_trail = []

        # Apply BODMAS steps in reverse for resource-centric view

        # Step 1: [Individual User × Individual Resource]
        step1_results = self._process_resource_user(
            resource_id, active_rules, evaluation_time
        )
        self._update_permissions(permissions_by_user, step1_results["permissions"])
        audit_trail.append(
            {
                "step": "Individual User × Individual Resource",
                "appliedRules": step1_results["rules"],
                "result": step1_results["permissions"],
            }
        )

        # Step 2: [ResourceGroup × Individual User]
        step2_results = self._process_resourcegroup_user(
            resource_id, active_rules, evaluation_time
        )
        self._update_permissions(permissions_by_user, step2_results["permissions"])
        audit_trail.append(
            {
                "step": "ResourceGroup × Individual User",
                "appliedRules": step2_results["rules"],
                "result": step2_results["permissions"],
            }
        )

        # Step 3: [Individual Resource × UserGroup]
        step3_results = self._process_resource_usergroup(
            resource_id, active_rules, evaluation_time
        )
        self._update_permissions(permissions_by_user, step3_results["permissions"])
        audit_trail.append(
            {
                "step": "Individual Resource × UserGroup",
                "appliedRules": step3_results["rules"],
                "result": step3_results["permissions"],
            }
        )

        # Step 4: [ResourceGroup × UserGroup]
        step4_results = self._process_resourcegroup_usergroup(
            resource_id, active_rules, evaluation_time
        )
        self._update_permissions(permissions_by_user, step4_results["permissions"])
        audit_trail.append(
            {
                "step": "ResourceGroup × UserGroup",
                "appliedRules": step4_results["rules"],
                "result": step4_results["permissions"],
            }
        )

        # Return final result with audit trail
        return {
            "resource_id": resource_id,
            "evaluation_time": evaluation_time.isoformat(),
            "users_with_access": permissions_by_user,
            "audit_trail": audit_trail,
        }

    def resolve_resource_group_access(
        self, resource_group_id: str, evaluation_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Determine which users can access a resource group by expanding the group
        to individual resources and aggregating access.

        Args:
            resource_group_id: ID of resource group to resolve access for
            evaluation_time: Time to evaluate access (defaults to current time)

        Returns:
            Dictionary with users and their permissions

        Raises:
            ArtifactNotFoundError: If resource group doesn't exist
        """
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        # Fetch the resource group and its expression
        resource_group = (
            self.db.query(Artifact)
            .filter(
                Artifact.id == resource_group_id,
                Artifact.type == "RESOURCEGROUP",
                Artifact.active == True,
            )
            .first()
        )

        if not resource_group:
            raise ArtifactNotFoundError(
                resource_group_id,
                {"reason": "Resource group not found or not a RESOURCEGROUP"},
            )

        if not resource_group.expression:
            return {
                "resource_group_id": resource_group_id,
                "evaluation_time": evaluation_time.isoformat(),
                "users_with_access": {},
                "audit_trail": [],
            }

        # Resolve concrete resource IDs from the group's expression
        member_resource_ids = self.expression_resolver.resolve_resource_expression(
            resource_group.expression
        )
        if not member_resource_ids:
            return {
                "resource_group_id": resource_group_id,
                "evaluation_time": evaluation_time.isoformat(),
                "users_with_access": {},
                "audit_trail": [],
            }

        # Aggregate permissions across all resources in the group
        permissions_by_user: Dict[str, List[str]] = {}
        audit_trail: List[Dict[str, Any]] = []
        processed_resources: Set[str] = set()

        for member_resource_id in member_resource_ids:
            if member_resource_id in processed_resources:
                continue
            processed_resources.add(member_resource_id)

            try:
                # Reuse existing resource-centric resolver
                member_result = self.resolve_resource_access(
                    member_resource_id, evaluation_time
                )

                # Merge member resource's users -> permissions into group-level map
                member_users_access = member_result.get("users_with_access", {})
                self._update_permissions(permissions_by_user, member_users_access)

                # Record per-resource audit for traceability
                audit_trail.append(
                    {
                        "memberResourceId": member_resource_id,
                        "users_with_access": member_users_access,
                        "resourceAudit": member_result.get("audit_trail", []),
                    }
                )

            except ArtifactNotFoundError:
                # Skip non-existent resources in group
                audit_trail.append(
                    {
                        "memberResourceId": member_resource_id,
                        "error": "Resource not found",
                        "users_with_access": {},
                        "resourceAudit": [],
                    }
                )
                continue

        return {
            "resource_group_id": resource_group_id,
            "evaluation_time": evaluation_time.isoformat(),
            "users_with_access": permissions_by_user,
            "audit_trail": audit_trail,
        }

    def check_access(
        self,
        user_id: str,
        resource_id: str,
        permission: str,
        evaluation_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Check if a user has a specific permission for a resource.

        Args:
            user_id: ID of user to check
            resource_id: ID of resource to check
            permission: Permission to check for
            evaluation_time: Time to evaluate access (defaults to current time)

        Returns:
            Dictionary with access result and audit trail
        """
        try:
            # Get all permissions for this user and resource
            user_access = self.resolve_user_access(user_id, evaluation_time)

            # Check if the resource is in the resolved access
            resource_permissions = user_access["resolved_access"].get(resource_id, [])
            has_permission = permission in resource_permissions

            return {
                "userId": user_id,
                "resource_id": resource_id,
                "permission": permission,
                "has_access": has_permission,
                "evaluation_time": user_access["evaluation_time"],
                "audit_trail": user_access["audit_trail"],
            }

        except (UserNotFoundError, ArtifactNotFoundError) as e:
            return {
                "userId": user_id,
                "resource_id": resource_id,
                "permission": permission,
                "has_access": False,
                "evaluation_time": (evaluation_time or datetime.now(timezone.utc)).isoformat(),
                "error": str(e),
                "audit_trail": [],
            }

    # BODMAS Step Processing Methods

    def _process_usergroup_resourcegroup(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving user groups and resource groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves user groups
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves resource groups
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    def _process_usergroup_resource(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving user groups and individual resources."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves user groups
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves individual resources (not resource groups)
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    def _process_user_resourcegroup(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving individual users and resource groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves individual users (not user groups)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves resource groups
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    def _process_user_resource(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving individual users and individual resources."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves individual users (not user groups)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves individual resources (not resource groups)
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    # Resource-centric resolution methods

    def _process_resource_user(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime
    ) -> Dict[str, Any]:
        """Process rules involving individual resources and individual users."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be individual (not a resource group)
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            # Check if this resource is included
            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # Resolve individual users (not user groups)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    def _process_resourcegroup_user(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime
    ) -> Dict[str, Any]:
        """Process rules involving resource groups and individual users."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be group
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            # Check if this resource is in the group's resolved list
            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # User must be individual (not a group)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    def _process_resource_usergroup(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime
    ) -> Dict[str, Any]:
        """Process rules involving individual resources and user groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be individual
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # User must be group
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    def _process_resourcegroup_usergroup(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime
    ) -> Dict[str, Any]:
        """Process rules involving resource groups and user groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be group
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            resolved_resources = self.expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # User must be group
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            resolved_users = self.expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    # Helper methods

    def _involves_user_groups(self, expression: str) -> bool:
        """
        Check if an expression involves user groups.

        This is a heuristic check - in a more sophisticated implementation,
        we could parse the expression and check each entity type.
        """
        # Simple heuristic: check if expression contains typical group identifiers
        group_indicators = ["group", "team", "department", "role"]
        expression_lower = expression.lower()
        return any(indicator in expression_lower for indicator in group_indicators)

    def _involves_resource_groups(self, expression: str) -> bool:
        """
        Check if an expression involves resource groups.

        This is a heuristic check - in a more sophisticated implementation,
        we could parse the expression and check each entity type.
        """
        # Simple heuristic: check if expression contains typical group identifiers
        group_indicators = ["group", "cluster", "pool", "collection"]
        expression_lower = expression.lower()
        return any(indicator in expression_lower for indicator in group_indicators)

    def _get_relevant_rules_for_user(self, user_id: str) -> List[AccessRule]:
        """
        Get access rules that could potentially apply to this user.
        Pre-filters rules to avoid processing irrelevant ones.
        """
        # First, get all user groups this user belongs to
        user_groups = []
        try:
            # Get direct user groups containing this user
            groups = self.db.query(User).filter(
                User.type == "USERGROUP", 
                User.active == True
            ).all()
            
            for group in groups:
                if group.expression:
                    try:
                        resolved_users = self.expression_resolver.resolve_user_expression(group.expression)
                        if user_id in resolved_users:
                            user_groups.append(group.id)
                    except Exception:
                        continue  # Skip problematic groups
        except Exception:
            pass  # Fall back to all rules if group resolution fails
        
        # Get rules that match this user or any of their groups (with application filtering)
        query = self.db.query(AccessRule).filter(AccessRule.active == True)
        if self.application_name:
            query = query.filter(AccessRule.application == self.application_name)
        all_rules = query.all()
        relevant_rules = []
        
        for rule in all_rules:
            # Quick check: if rule mentions user directly or any of their groups
            user_expr = rule.user_expression.lower()
            if (user_id.lower() in user_expr or 
                any(group.lower() in user_expr for group in user_groups)):
                relevant_rules.append(rule)
            else:
                # More expensive check: resolve the expression
                try:
                    resolved_users = self.expression_resolver.resolve_user_expression(rule.user_expression)
                    if user_id in resolved_users:
                        relevant_rules.append(rule)
                except Exception:
                    # If resolution fails, include rule to be safe
                    relevant_rules.append(rule)
        
        return relevant_rules

    def _get_relevant_rules_for_resource(self, resource_id: str) -> List[AccessRule]:
        """
        Get access rules that could potentially apply to this resource.
        Pre-filters rules to avoid processing irrelevant ones.
        """
        # First, get all resource groups this resource belongs to
        resource_groups = []
        try:
            # Get direct resource groups containing this resource
            groups = self.db.query(Artifact).filter(
                Artifact.type == "RESOURCEGROUP",
                Artifact.active == True
            ).all()
            
            for group in groups:
                if group.expression:
                    try:
                        resolved_resources = self.expression_resolver.resolve_resource_expression(group.expression)
                        if resource_id in resolved_resources:
                            resource_groups.append(group.id)
                    except Exception:
                        continue  # Skip problematic groups
        except Exception:
            pass  # Fall back to all rules if group resolution fails
        
        # Get rules that match this resource or any of their groups (with application filtering)
        query = self.db.query(AccessRule).filter(AccessRule.active == True)
        if self.application_name:
            query = query.filter(AccessRule.application == self.application_name)
        all_rules = query.all()
        relevant_rules = []
        
        for rule in all_rules:
            # Quick check: if rule mentions resource directly or any of their groups
            resource_expr = rule.resource_expression.lower()
            if (resource_id.lower() in resource_expr or 
                any(group.lower() in resource_expr for group in resource_groups)):
                relevant_rules.append(rule)
            else:
                # More expensive check: resolve the expression
                try:
                    resolved_resources = self.expression_resolver.resolve_resource_expression(rule.resource_expression)
                    if resource_id in resolved_resources:
                        relevant_rules.append(rule)
                except Exception:
                    # If resolution fails, include rule to be safe
                    relevant_rules.append(rule)
        
        return relevant_rules

    def _update_permissions(
        self,
        permission_dict: Dict[str, List[str]],
        new_permissions: Dict[str, List[str]],
    ) -> None:
        """
        Update the permissions dictionary with new permissions.
        Permissions are additive - we union the permission sets.

        Args:
            permission_dict: Existing permissions dictionary to update
            new_permissions: New permissions to add
        """
        for entity_id, permissions in new_permissions.items():
            if entity_id not in permission_dict:
                permission_dict[entity_id] = []

            # Add each permission if not already present
            for permission in permissions:
                if permission not in permission_dict[entity_id]:
                    permission_dict[entity_id].append(permission)


class AsyncBODMASResolver:
    """
    Async implementation of BODMAS-based resolution for access control.

    BODMAS resolution follows these steps:
    1. [UserGroup × ResourceGroup] (Highest Priority)
    2. [UserGroup × Individual Resource]
    3. [Individual User × ResourceGroup]
    4. [Individual User × Individual Resource] (Lowest Priority)
    5. Union all results (additive permissions)
    """

    def __init__(self, db_session, application_name: Optional[str] = None):
        self.db = db_session
        self.application_name = application_name

    async def resolve_user_access(
        self, user_id: str, evaluation_time: Optional[datetime] = None, include_audit: bool = False
    ) -> Dict[str, Any]:
        """
        Determine what resources a user can access.

        Args:
            user_id: ID of user to resolve access for
            evaluation_time: Time to evaluate access (defaults to current time)
            include_audit: Whether to include detailed audit trail (defaults to False for performance)

        Returns:
            Dictionary with resolved access and optional audit trail

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        from sqlalchemy import select
        from medha_one_access.core.expressions import AsyncExpressionResolver
        
        # Use current time if not provided
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        # Check if user exists and is active
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.active == True)
        )
        
        try:
            user = result.scalar_one_or_none()
        except Exception as e:
            # Handle "Multiple rows were found" error with better diagnostics
            if "Multiple rows were found" in str(e):
                # Get all matching users for debugging
                debug_result = await self.db.execute(
                    select(User).where(User.id == user_id, User.active == True)
                )
                all_users = debug_result.scalars().all()
                raise MedhaAccessError(
                    f"Multiple users found with ID '{user_id}': Found {len(all_users)} users. "
                    f"This indicates a database integrity issue. "
                    f"User IDs should be unique. Please check your database for duplicate user records."
                )
            else:
                # Re-raise other exceptions
                raise
        
        if not user:
            raise UserNotFoundError(user_id)

        # Initialize async expression resolver
        expression_resolver = AsyncExpressionResolver(self.db, self.application_name)

        # Get all active access rules with optimized filtering
        active_rules = await self._get_relevant_rules_for_user(user_id, expression_resolver)

        # Results structure
        permissions_by_artifact = {}
        audit_trail = [] if include_audit else None

        # Step 1: [UserGroup × ResourceGroup]
        step1_results = await self._process_usergroup_resourcegroup(
            user_id, active_rules, evaluation_time, expression_resolver, include_audit
        )
        self._update_permissions(permissions_by_artifact, step1_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "UserGroup × ResourceGroup",
                    "appliedRules": step1_results["rules"],
                    "result": step1_results["permissions"],
                }
            )

        # Step 2: [UserGroup × Individual Resource]
        step2_results = await self._process_usergroup_resource(
            user_id, active_rules, evaluation_time, expression_resolver, include_audit
        )
        self._update_permissions(permissions_by_artifact, step2_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "UserGroup × Individual Resource",
                    "appliedRules": step2_results["rules"],
                    "result": step2_results["permissions"],
                }
            )

        # Step 3: [Individual User × ResourceGroup]
        step3_results = await self._process_user_resourcegroup(
            user_id, active_rules, evaluation_time, expression_resolver, include_audit
        )
        self._update_permissions(permissions_by_artifact, step3_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "Individual User × ResourceGroup",
                    "appliedRules": step3_results["rules"],
                    "result": step3_results["permissions"],
                }
            )

        # Step 4: [Individual User × Individual Resource]
        step4_results = await self._process_user_resource(
            user_id, active_rules, evaluation_time, expression_resolver, include_audit
        )
        self._update_permissions(permissions_by_artifact, step4_results["permissions"])
        if include_audit:
            audit_trail.append(
                {
                    "step": "Individual User × Individual Resource",
                    "appliedRules": step4_results["rules"],
                    "result": step4_results["permissions"],
                }
            )

        # Enhance the response with artifact names and metadata
        enhanced_access = {}
        for artifact_id, permissions in permissions_by_artifact.items():
            # Get artifact details from database (with application filtering)
            query = select(Artifact).where(Artifact.id == artifact_id)
            if self.application_name:
                query = query.where(Artifact.application == self.application_name)
            result = await self.db.execute(query)
            
            try:
                artifact = result.scalar_one_or_none()
            except Exception as e:
                # Handle "Multiple rows were found" error with better diagnostics
                if "Multiple rows were found" in str(e):
                    # Get all matching artifacts for debugging
                    debug_query = select(Artifact).where(Artifact.id == artifact_id)
                    debug_result = await self.db.execute(debug_query)
                    all_artifacts = debug_result.scalars().all()
                    applications = [a.application for a in all_artifacts] if all_artifacts else ['unknown']
                    raise MedhaAccessError(
                        f"Multiple artifacts found with ID '{artifact_id}' during access resolution: "
                        f"Found {len(all_artifacts)} artifacts across applications: {applications}. "
                        f"Current application filter: {self.application_name}. "
                        f"This indicates duplicate artifact IDs across applications."
                    )
                else:
                    # Re-raise other exceptions
                    raise
            artifact_name = (artifact.name if artifact and artifact.name else artifact_id)
            
            # Include all artifact metadata
            artifact_data = {
                "artifact_id": artifact_id,
                "artifact_name": artifact_name,
                "permissions": permissions
            }
            
            # Add all artifact properties if artifact exists
            if artifact:
                artifact_data.update({
                    "type": artifact.type,
                    "description": artifact.description,
                    "active": artifact.active,
                    "application": artifact.application,
                    "owner_id": artifact.owner_id,
                    "parent_group_id": artifact.parent_group_id,
                    "expression": artifact.expression,
                    "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
                    "updated_at": artifact.updated_at.isoformat() if artifact.updated_at else None,
                    "artifact_metadata": artifact.artifact_metadata
                })
            
            enhanced_access[artifact_id] = artifact_data

        # Return final result with optional audit trail
        result = {
            "user_id": user_id,
            "evaluation_time": evaluation_time.isoformat(),
            "resolved_access": permissions_by_artifact,  # Keep original format for compatibility
            "resolved_access_detailed": enhanced_access,  # New detailed format
        }
        
        # Only include audit trail if requested
        if include_audit:
            result["audit_trail"] = audit_trail
            
        return result

    async def resolve_resource_access(
        self, resource_id: str, evaluation_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Determine who can access a resource.

        Args:
            resource_id: ID of resource to resolve access for
            evaluation_time: Time to evaluate access (defaults to current time)

        Returns:
            Dictionary with users and their permissions

        Raises:
            ArtifactNotFoundError: If resource doesn't exist
        """
        from sqlalchemy import select
        from medha_one_access.core.expressions import AsyncExpressionResolver
        
        # Use current time if not provided
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        # Check if resource exists and is active (with application filtering)
        query = select(Artifact).where(Artifact.id == resource_id, Artifact.active == True)
        if self.application_name:
            query = query.where(Artifact.application == self.application_name)
        result = await self.db.execute(query)
        
        try:
            resource = result.scalar_one_or_none()
        except Exception as e:
            # Handle "Multiple rows were found" error with better diagnostics
            if "Multiple rows were found" in str(e):
                # Get all matching resources for debugging
                debug_query = select(Artifact).where(Artifact.id == resource_id, Artifact.active == True)
                if self.application_name:
                    debug_query = debug_query.where(Artifact.application == self.application_name)
                debug_result = await self.db.execute(debug_query)
                all_resources = debug_result.scalars().all()
                applications = [r.application for r in all_resources] if hasattr(all_resources[0], 'application') else ['unknown']
                raise MedhaAccessError(
                    f"Multiple resources found with ID '{resource_id}': Found {len(all_resources)} resources "
                    f"across applications: {applications}. This might indicate duplicate resource IDs across applications. "
                    f"Current application filter: {self.application_name}"
                )
            else:
                # Re-raise other exceptions
                raise
        
        if not resource:
            raise ArtifactNotFoundError(resource_id)

        # Initialize async expression resolver
        expression_resolver = AsyncExpressionResolver(self.db, self.application_name)

        # Get all active access rules with optimized filtering
        active_rules = await self._get_relevant_rules_for_resource(resource_id, expression_resolver)

        # Results structure
        permissions_by_user = {}
        audit_trail = []

        # Apply BODMAS steps in reverse for resource-centric view

        # Step 1: [Individual User × Individual Resource]
        step1_results = await self._process_resource_user(
            resource_id, active_rules, evaluation_time, expression_resolver
        )
        self._update_permissions(permissions_by_user, step1_results["permissions"])
        audit_trail.append(
            {
                "step": "Individual User × Individual Resource",
                "appliedRules": step1_results["rules"],
                "result": step1_results["permissions"],
            }
        )

        # Step 2: [ResourceGroup × Individual User]
        step2_results = await self._process_resourcegroup_user(
            resource_id, active_rules, evaluation_time, expression_resolver
        )
        self._update_permissions(permissions_by_user, step2_results["permissions"])
        audit_trail.append(
            {
                "step": "ResourceGroup × Individual User",
                "appliedRules": step2_results["rules"],
                "result": step2_results["permissions"],
            }
        )

        # Step 3: [Individual Resource × UserGroup]
        step3_results = await self._process_resource_usergroup(
            resource_id, active_rules, evaluation_time, expression_resolver
        )
        self._update_permissions(permissions_by_user, step3_results["permissions"])
        audit_trail.append(
            {
                "step": "Individual Resource × UserGroup",
                "appliedRules": step3_results["rules"],
                "result": step3_results["permissions"],
            }
        )

        # Step 4: [ResourceGroup × UserGroup]
        step4_results = await self._process_resourcegroup_usergroup(
            resource_id, active_rules, evaluation_time, expression_resolver
        )
        self._update_permissions(permissions_by_user, step4_results["permissions"])
        audit_trail.append(
            {
                "step": "ResourceGroup × UserGroup",
                "appliedRules": step4_results["rules"],
                "result": step4_results["permissions"],
            }
        )

        # Return final result with audit trail
        return {
            "resource_id": resource_id,
            "evaluation_time": evaluation_time.isoformat(),
            "users_with_access": permissions_by_user,
            "audit_trail": audit_trail,
        }

    async def check_access(
        self,
        user_id: str,
        resource_id: str,
        permission: str,
        evaluation_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Check if a user has a specific permission for a resource.

        Args:
            user_id: ID of user to check
            resource_id: ID of resource to check
            permission: Permission to check for
            evaluation_time: Time to evaluate access (defaults to current time)

        Returns:
            Dictionary with access result and audit trail
        """
        try:
            # Get all permissions for this user and resource
            user_access = await self.resolve_user_access(user_id, evaluation_time)

            # Check if the resource is in the resolved access
            resource_permissions = user_access["resolved_access"].get(resource_id, [])
            has_permission = permission in resource_permissions

            return {
                "userId": user_id,
                "resource_id": resource_id,
                "permission": permission,
                "has_access": has_permission,
                "evaluation_time": user_access["evaluation_time"],
                "audit_trail": user_access.get("audit_trail", []),
            }

        except (UserNotFoundError, ArtifactNotFoundError) as e:
            return {
                "userId": user_id,
                "resource_id": resource_id,
                "permission": permission,
                "has_access": False,
                "evaluation_time": (evaluation_time or datetime.now(timezone.utc)).isoformat(),
                "error": str(e),
                "audit_trail": [],
            }

    # BODMAS Step Processing Methods (Async)

    async def _process_usergroup_resourcegroup(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving user groups and resource groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves user groups
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves resource groups
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    async def _process_usergroup_resource(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving user groups and individual resources."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves user groups
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves individual resources (not resource groups)
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    async def _process_user_resourcegroup(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving individual users and resource groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves individual users (not user groups)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves resource groups
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    async def _process_user_resource(
        self, user_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver, include_audit: bool = False
    ) -> Dict[str, Any]:
        """Process rules involving individual users and individual resources."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            # Skip rules that don't satisfy time constraints
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Check if this rule involves individual users (not user groups)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            # Check if this rule involves individual resources (not resource groups)
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            # Check if this user is included in the user expression
            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )
            if user_id not in resolved_users:
                continue

            # Get all concrete resources from the resource expression
            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )

            # Add permissions for these resources
            for resource_id in resolved_resources:
                if resource_id not in permissions:
                    permissions[resource_id] = []

                # Add permissions (avoiding duplicates)
                for permission in rule.permissions:
                    if permission not in permissions[resource_id]:
                        permissions[resource_id].append(permission)

            # Record the rule that was applied
            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    # Resource-centric resolution methods (async)

    async def _process_resource_user(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver
    ) -> Dict[str, Any]:
        """Process rules involving individual resources and individual users."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be individual (not a resource group)
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            # Check if this resource is included
            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # Resolve individual users (not user groups)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    async def _process_resourcegroup_user(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver
    ) -> Dict[str, Any]:
        """Process rules involving resource groups and individual users."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be group
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            # Check if this resource is in the group's resolved list
            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # User must be individual (not a group)
            user_expression = rule.user_expression
            if self._involves_user_groups(user_expression):
                continue

            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    async def _process_resource_usergroup(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver
    ) -> Dict[str, Any]:
        """Process rules involving individual resources and user groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be individual
            resource_expression = rule.resource_expression
            if self._involves_resource_groups(resource_expression):
                continue

            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # User must be group
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    async def _process_resourcegroup_usergroup(
        self, resource_id: str, rules: List[AccessRule], evaluation_time: datetime, expression_resolver
    ) -> Dict[str, Any]:
        """Process rules involving resource groups and user groups."""
        permissions = {}
        applied_rules = []

        for rule in rules:
            if not TimeConstraintEvaluator.is_satisfied(
                rule.time_constraints, evaluation_time
            ):
                continue

            # Resource must be group
            resource_expression = rule.resource_expression
            if not self._involves_resource_groups(resource_expression):
                continue

            resolved_resources = await expression_resolver.resolve_resource_expression(
                resource_expression
            )
            if resource_id not in resolved_resources:
                continue

            # User must be group
            user_expression = rule.user_expression
            if not self._involves_user_groups(user_expression):
                continue

            resolved_users = await expression_resolver.resolve_user_expression(
                user_expression
            )

            for user_id in resolved_users:
                if user_id not in permissions:
                    permissions[user_id] = []
                for permission in rule.permissions:
                    if permission not in permissions[user_id]:
                        permissions[user_id].append(permission)

            applied_rules.append(
                {
                    "ruleId": rule.id,
                    "userExpression": rule.user_expression,
                    "resourceExpression": rule.resource_expression,
                    "permissions": rule.permissions,
                }
            )

        return {"permissions": permissions, "rules": applied_rules}

    # Helper methods

    def _involves_user_groups(self, expression: str) -> bool:
        """
        Check if an expression involves user groups.

        This is a heuristic check - in a more sophisticated implementation,
        we could parse the expression and check each entity type.
        """
        # Simple heuristic: check if expression contains typical group identifiers
        group_indicators = ["group", "team", "department", "role"]
        expression_lower = expression.lower()
        return any(indicator in expression_lower for indicator in group_indicators)

    def _involves_resource_groups(self, expression: str) -> bool:
        """
        Check if an expression involves resource groups.

        This is a heuristic check - in a more sophisticated implementation,
        we could parse the expression and check each entity type.
        """
        # Simple heuristic: check if expression contains typical group identifiers
        group_indicators = ["group", "cluster", "pool", "collection"]
        expression_lower = expression.lower()
        return any(indicator in expression_lower for indicator in group_indicators)

    async def _get_relevant_rules_for_user(self, user_id: str, expression_resolver) -> List[AccessRule]:
        """
        Get access rules that could potentially apply to this user.
        Pre-filters rules to avoid processing irrelevant ones.
        """
        from sqlalchemy import select
        
        # First, get all user groups this user belongs to
        user_groups = []
        try:
            # Get direct user groups containing this user
            result = await self.db.execute(
                select(User).where(User.type == "USERGROUP", User.active == True)
            )
            groups = result.scalars().all()
            
            for group in groups:
                if group.expression:
                    try:
                        resolved_users = await expression_resolver.resolve_user_expression(group.expression)
                        if user_id in resolved_users:
                            user_groups.append(group.id)
                    except Exception:
                        continue  # Skip problematic groups
        except Exception:
            pass  # Fall back to all rules if group resolution fails
        
        # Get rules that match this user or any of their groups (with application filtering)
        query = select(AccessRule).where(AccessRule.active == True)
        if self.application_name:
            query = query.where(AccessRule.application == self.application_name)
        
        result = await self.db.execute(query)
        all_rules = result.scalars().all()
        relevant_rules = []
        
        for rule in all_rules:
            # Quick check: if rule mentions user directly or any of their groups
            user_expr = rule.user_expression.lower()
            if (user_id.lower() in user_expr or 
                any(group.lower() in user_expr for group in user_groups)):
                relevant_rules.append(rule)
            else:
                # More expensive check: resolve the expression
                try:
                    resolved_users = await expression_resolver.resolve_user_expression(rule.user_expression)
                    if user_id in resolved_users:
                        relevant_rules.append(rule)
                except Exception:
                    # If resolution fails, include rule to be safe
                    relevant_rules.append(rule)
        
        return relevant_rules

    async def _get_relevant_rules_for_resource(self, resource_id: str, expression_resolver) -> List[AccessRule]:
        """
        Get access rules that could potentially apply to this resource.
        Pre-filters rules to avoid processing irrelevant ones.
        """
        from sqlalchemy import select
        
        # First, get all resource groups this resource belongs to
        resource_groups = []
        try:
            # Get direct resource groups containing this resource
            result = await self.db.execute(
                select(Artifact).where(Artifact.type == "RESOURCEGROUP", Artifact.active == True)
            )
            groups = result.scalars().all()
            
            for group in groups:
                if group.expression:
                    try:
                        resolved_resources = await expression_resolver.resolve_resource_expression(group.expression)
                        if resource_id in resolved_resources:
                            resource_groups.append(group.id)
                    except Exception:
                        continue  # Skip problematic groups
        except Exception:
            pass  # Fall back to all rules if group resolution fails
        
        # Get rules that match this resource or any of their groups (with application filtering)
        query = select(AccessRule).where(AccessRule.active == True)
        if self.application_name:
            query = query.where(AccessRule.application == self.application_name)
        
        result = await self.db.execute(query)
        all_rules = result.scalars().all()
        relevant_rules = []
        
        for rule in all_rules:
            # Quick check: if rule mentions resource directly or any of their groups
            resource_expr = rule.resource_expression.lower()
            if (resource_id.lower() in resource_expr or 
                any(group.lower() in resource_expr for group in resource_groups)):
                relevant_rules.append(rule)
            else:
                # More expensive check: resolve the expression
                try:
                    resolved_resources = await expression_resolver.resolve_resource_expression(rule.resource_expression)
                    if resource_id in resolved_resources:
                        relevant_rules.append(rule)
                except Exception:
                    # If resolution fails, include rule to be safe
                    relevant_rules.append(rule)
        
        return relevant_rules

    def _update_permissions(
        self,
        permission_dict: Dict[str, List[str]],
        new_permissions: Dict[str, List[str]],
    ) -> None:
        """
        Update the permissions dictionary with new permissions.
        Permissions are additive - we union the permission sets.

        Args:
            permission_dict: Existing permissions dictionary to update
            new_permissions: New permissions to add
        """
        for entity_id, permissions in new_permissions.items():
            if entity_id not in permission_dict:
                permission_dict[entity_id] = []

            # Add each permission if not already present
            for permission in permissions:
                if permission not in permission_dict[entity_id]:
                    permission_dict[entity_id].append(permission)


# Export the resolver
__all__ = [
    "BODMASResolver",
    "AsyncBODMASResolver",
]
