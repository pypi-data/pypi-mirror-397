"""
MedhaOne Access Control Expression System

Expression parser and resolver for user and resource expressions.
Supports mathematical-style expressions with + (include) and - (exclude) operators.
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from functools import lru_cache
from sqlalchemy.orm import Session

from medha_one_access.core.models import User, Artifact
from medha_one_access.core.exceptions import ExpressionValidationError


class ExpressionParser:
    """Parser for user and resource expressions."""

    @staticmethod
    @lru_cache(maxsize=1000)  # Cache parsed expressions
    def parse_expression(expression: str) -> List[Dict[str, str]]:
        """
        Parse an expression into a list of operations.

        Args:
            expression: Expression string like "user1+group1-user2"

        Returns:
            List of operations: [
                {"type": "include", "entity": "user1"},
                {"type": "include", "entity": "group1"},
                {"type": "exclude", "entity": "user2"}
            ]
        """
        if not expression:
            return []

        operations = []

        # Split by operators while preserving operator
        # Support quoted entities: "entity-with-hyphens"
        tokens = re.findall(r'([+-]?)(".*?"|[^+-]+)', expression)

        for i, (op, entity) in enumerate(tokens):
            entity = entity.strip()
            
            # Remove quotes if present
            if entity.startswith('"') and entity.endswith('"'):
                entity = entity[1:-1]

            # First token is always include even if no operator specified
            if i == 0 and not op:
                op = "+"

            if op == "+" or not op:
                operations.append({"type": "include", "entity": entity})
            elif op == "-":
                operations.append({"type": "exclude", "entity": entity})

        return tuple(operations)  # Return tuple for caching

    @staticmethod
    @lru_cache(maxsize=500)  # Cache validation results
    def validate_expression(expression: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an expression's syntax.

        Args:
            expression: Expression string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not expression:
            return True, None

        # Check for invalid characters (allowing common characters in entity names: alphanumeric, _, +, -, |, ., @, &, #, quotes, parentheses, colons, commas, apostrophes, and spaces)
        if re.search(r"[^a-zA-Z0-9_+\-|.\s@&#\"():,']", expression):
            return (
                False,
                "Expression contains invalid characters. Only alphanumeric, _, +, -, |, ., @, &, #, quotes, parentheses, colons, commas, apostrophes, and spaces are allowed",
            )

        # Check for unmatched quotes
        quote_count = expression.count('"')
        if quote_count % 2 != 0:
            return False, "Expression contains unmatched quotes"

        # Check for consecutive operators
        if re.search(r"[+-][+-]", expression):
            return False, "Expression contains consecutive operators"

        # Check for leading/trailing operators
        if expression.startswith("+") or expression.startswith("-"):
            return False, "Expression cannot start with an operator"

        if expression.endswith("+") or expression.endswith("-"):
            return False, "Expression cannot end with an operator"

        # Check for empty entities
        parts = re.split(r"[+-]", expression)
        for part in parts:
            if not part.strip():
                return False, "Expression contains empty entities"

        return True, None


class ExpressionResolver:
    """Resolver for user and resource expressions."""

    def __init__(self, db: Session, application_name: Optional[str] = None):
        self.db = db
        self.application_name = application_name
        # Session-level caches for repeated queries within single operation
        self._user_cache = {}  # id -> User
        self._artifact_cache = {}  # id -> Artifact
        self._resolution_cache = {}  # expression -> resolved_ids

    def resolve_user_expression(self, expression: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a user expression to a set of user IDs.
        Process operations sequentially from left to right.

        Args:
            expression: User expression to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of resolved user IDs

        Raises:
            ExpressionValidationError: If expression is invalid
        """
        # Check cache first
        cache_key = f"user:{expression}:{tuple(sorted(visited)) if visited else 'none'}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]
        
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
        
        # Validate expression first
        is_valid, error = ExpressionParser.validate_expression(expression)
        if not is_valid:
            raise ExpressionValidationError(expression, error)

        operations = list(ExpressionParser.parse_expression(expression))

        # Start with empty result set
        result_users = set()

        # Process operations in order
        for operation in operations:
            op_type = operation["type"]  # "include" or "exclude"
            entity_id = operation["entity"]

            # Resolve the entity
            if op_type == "include":
                # Get users from this entity
                users = self._resolve_user_entity(entity_id, visited)
                # Add to result set (union)
                result_users.update(users)
            elif op_type == "exclude":
                # Get users from this entity
                users = self._resolve_user_entity(entity_id, visited)
                # Remove from result set (difference)
                result_users.difference_update(users)

        # Cache the result
        self._resolution_cache[cache_key] = result_users
        return result_users

    def resolve_resource_expression(self, expression: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a resource expression to a set of artifact IDs.
        Process operations sequentially from left to right.

        Args:
            expression: Resource expression to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of resolved artifact IDs

        Raises:
            ExpressionValidationError: If expression is invalid
        """
        # Check cache first
        cache_key = f"resource:{expression}:{tuple(sorted(visited)) if visited else 'none'}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]
            
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Validate expression first
        is_valid, error = ExpressionParser.validate_expression(expression)
        if not is_valid:
            raise ExpressionValidationError(expression, error)

        operations = list(ExpressionParser.parse_expression(expression))

        # Start with empty result set
        result_resources = set()

        # Process operations in order
        for operation in operations:
            op_type = operation["type"]  # "include" or "exclude"
            entity_id = operation["entity"]

            # Resolve the entity
            if op_type == "include":
                # Get resources from this entity
                resources = self._resolve_resource_entity(entity_id, visited)
                # Add to result set (union)
                result_resources.update(resources)
            elif op_type == "exclude":
                # Get resources from this entity
                resources = self._resolve_resource_entity(entity_id, visited)
                # Remove from result set (difference)
                result_resources.difference_update(resources)

        # Cache the result
        self._resolution_cache[cache_key] = result_resources
        return result_resources

    def _resolve_user_entity(self, entity_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a user entity to a set of user IDs.
        Handles both individual users and user groups.

        Args:
            entity_id: ID of user or user group to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of user IDs
        """
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Check for circular dependency
        if entity_id in visited:
            # Log warning about circular reference and return empty set to break the cycle
            print(f"WARNING: Circular reference detected in user group resolution for entity '{entity_id}'. Breaking cycle.")
            return set()
        
        # Check cache first
        if entity_id in self._user_cache:
            entity = self._user_cache[entity_id]
        else:
            # Get the entity from database
            entity = (
                self.db.query(User)
                .filter(User.id == entity_id, User.active == True)
                .first()
            )
            # Cache the entity (including None for not found)
            self._user_cache[entity_id] = entity

        # If entity doesn't exist or is inactive, return empty set
        if not entity:
            return set()

        # If it's an individual user
        if entity.type == "USER":
            return {entity.id}

        # If it's a user group with an expression
        if entity.type == "USERGROUP" and entity.expression:
            # Add this entity to visited set before recursion
            new_visited = visited.copy()
            new_visited.add(entity_id)
            # Recursively resolve the expression
            return self.resolve_user_expression(entity.expression, new_visited)

        # Otherwise it's a user group without an expression
        return {entity.id}

    def _resolve_resource_entity(self, entity_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a resource entity to a set of artifact IDs.
        Handles both individual resources and resource groups.

        Args:
            entity_id: ID of artifact or resource group to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of artifact IDs
        """
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Check for circular dependency
        if entity_id in visited:
            # Log warning about circular reference and return empty set to break the cycle
            print(f"WARNING: Circular reference detected in resource group resolution for entity '{entity_id}'. Breaking cycle.")
            return set()
            
        # Check cache first
        if entity_id in self._artifact_cache:
            entity = self._artifact_cache[entity_id]
        else:
            # Get the entity from database
            query = self.db.query(Artifact).filter(Artifact.id == entity_id, Artifact.active == True)
            if self.application_name:
                query = query.filter(Artifact.application == self.application_name)
            entity = query.first()
            # Cache the entity (including None for not found)
            self._artifact_cache[entity_id] = entity

        # If entity doesn't exist or is inactive, return empty set
        if not entity:
            return set()

        # If it's an individual resource
        if entity.type == "RESOURCE":
            return {entity.id}

        # If it's a resource group with an expression
        if entity.type == "RESOURCEGROUP" and entity.expression:
            # Add this entity to visited set before recursion
            new_visited = visited.copy()
            new_visited.add(entity_id)
            # Recursively resolve the expression
            return self.resolve_resource_expression(entity.expression, new_visited)

        # Otherwise it's a resource group without an expression
        # Resource groups without expressions should not grant access to any resources
        return set()

    def validate_expression_with_database(
        self, expression: str, expression_type: str
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate expression syntax and check if all entities exist in the database.

        Args:
            expression: Expression to validate
            expression_type: Type of expression ("USER" or "RESOURCE")

        Returns:
            Tuple of (is_valid, errors, resolved_entities)
        """
        # First validate the syntax
        is_valid, error = ExpressionParser.validate_expression(expression)
        if not is_valid:
            return False, [error], []

        # Then check if all entities exist in the database
        try:
            # Parse the expression
            operations = list(ExpressionParser.parse_expression(expression))

            # Check each entity
            missing_entities = []
            resolved_entities = []

            for operation in operations:
                entity_id = operation["entity"]

                if expression_type.upper() == "USER":
                    # Check if user/group exists
                    entity = self.db.query(User).filter(User.id == entity_id).first()
                    if not entity:
                        missing_entities.append(entity_id)
                    else:
                        resolved_entities.append(entity_id)

                elif expression_type.upper() == "RESOURCE":
                    # Check if resource/group exists
                    query = self.db.query(Artifact).filter(Artifact.id == entity_id)
                    if self.application_name:
                        query = query.filter(Artifact.application == self.application_name)
                    entity = query.first()
                    if not entity:
                        missing_entities.append(entity_id)
                    else:
                        resolved_entities.append(entity_id)
                else:
                    return False, [f"Unknown expression type: {expression_type}"], []

            # If there are missing entities, return error
            if missing_entities:
                return (
                    False,
                    [f"Missing entities: {', '.join(missing_entities)}"],
                    resolved_entities,
                )

            return True, [], resolved_entities

        except Exception as e:
            return False, [f"Error evaluating expression: {str(e)}"], []


class AsyncExpressionResolver:
    """Async resolver for user and resource expressions."""

    def __init__(self, db_session, application_name: Optional[str] = None):
        self.db = db_session
        self.application_name = application_name
        # Session-level caches for repeated queries within single operation
        self._user_cache = {}  # id -> User
        self._artifact_cache = {}  # id -> Artifact
        self._resolution_cache = {}  # expression -> resolved_ids

    async def resolve_user_expression(self, expression: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a user expression to a set of user IDs.
        Process operations sequentially from left to right.

        Args:
            expression: User expression to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of resolved user IDs

        Raises:
            ExpressionValidationError: If expression is invalid
        """
        # Check cache first
        cache_key = f"user:{expression}:{tuple(sorted(visited)) if visited else 'none'}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]
        
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
        
        # Validate expression first
        is_valid, error = ExpressionParser.validate_expression(expression)
        if not is_valid:
            raise ExpressionValidationError(expression, error)

        operations = list(ExpressionParser.parse_expression(expression))

        # Start with empty result set
        result_users = set()

        # Process operations in order
        for operation in operations:
            op_type = operation["type"]  # "include" or "exclude"
            entity_id = operation["entity"]

            # Resolve the entity
            if op_type == "include":
                # Get users from this entity
                users = await self._resolve_user_entity(entity_id, visited)
                # Add to result set (union)
                result_users.update(users)
            elif op_type == "exclude":
                # Get users from this entity
                users = await self._resolve_user_entity(entity_id, visited)
                # Remove from result set (difference)
                result_users.difference_update(users)

        # Cache the result
        self._resolution_cache[cache_key] = result_users
        return result_users

    async def resolve_resource_expression(self, expression: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a resource expression to a set of artifact IDs.
        Process operations sequentially from left to right.

        Args:
            expression: Resource expression to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of resolved artifact IDs

        Raises:
            ExpressionValidationError: If expression is invalid
        """
        # Check cache first
        cache_key = f"resource:{expression}:{tuple(sorted(visited)) if visited else 'none'}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]
            
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Validate expression first
        is_valid, error = ExpressionParser.validate_expression(expression)
        if not is_valid:
            raise ExpressionValidationError(expression, error)

        operations = list(ExpressionParser.parse_expression(expression))

        # Start with empty result set
        result_resources = set()

        # Process operations in order
        for operation in operations:
            op_type = operation["type"]  # "include" or "exclude"
            entity_id = operation["entity"]

            # Resolve the entity
            if op_type == "include":
                # Get resources from this entity
                resources = await self._resolve_resource_entity(entity_id, visited)
                # Add to result set (union)
                result_resources.update(resources)
            elif op_type == "exclude":
                # Get resources from this entity
                resources = await self._resolve_resource_entity(entity_id, visited)
                # Remove from result set (difference)
                result_resources.difference_update(resources)

        # Cache the result
        self._resolution_cache[cache_key] = result_resources
        return result_resources

    async def _resolve_user_entity(self, entity_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a user entity to a set of user IDs.
        Handles both individual users and user groups.

        Args:
            entity_id: ID of user or user group to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of user IDs
        """
        from sqlalchemy import select
        
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Check for circular dependency
        if entity_id in visited:
            # Log warning about circular reference and return empty set to break the cycle
            print(f"WARNING: Circular reference detected in user group resolution for entity '{entity_id}'. Breaking cycle.")
            return set()
        
        # Check cache first
        if entity_id in self._user_cache:
            entity = self._user_cache[entity_id]
        else:
            # Get the entity from database using async query
            result = await self.db.execute(
                select(User).where(User.id == entity_id, User.active == True)
            )
            entity = result.scalar_one_or_none()
            # Cache the entity (including None for not found)
            self._user_cache[entity_id] = entity

        # If entity doesn't exist or is inactive, return empty set
        if not entity:
            return set()

        # If it's an individual user
        if entity.type == "USER":
            return {entity.id}

        # If it's a user group with an expression
        if entity.type == "USERGROUP" and entity.expression:
            # Add this entity to visited set before recursion
            new_visited = visited.copy()
            new_visited.add(entity_id)
            # Recursively resolve the expression
            return await self.resolve_user_expression(entity.expression, new_visited)

        # Otherwise it's a user group without an expression
        return {entity.id}

    async def _resolve_resource_entity(self, entity_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Resolve a resource entity to a set of artifact IDs.
        Handles both individual resources and resource groups.

        Args:
            entity_id: ID of artifact or resource group to resolve
            visited: Set of entity IDs already being resolved (for cycle detection)

        Returns:
            Set of artifact IDs
        """
        from sqlalchemy import select
        
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
            
        # Check for circular dependency
        if entity_id in visited:
            # Log warning about circular reference and return empty set to break the cycle
            print(f"WARNING: Circular reference detected in resource group resolution for entity '{entity_id}'. Breaking cycle.")
            return set()
            
        # Check cache first
        if entity_id in self._artifact_cache:
            entity = self._artifact_cache[entity_id]
        else:
            # Get the entity from database using async query
            query = select(Artifact).where(Artifact.id == entity_id, Artifact.active == True)
            if self.application_name:
                query = query.where(Artifact.application == self.application_name)
            result = await self.db.execute(query)
            entity = result.scalar_one_or_none()
            # Cache the entity (including None for not found)
            self._artifact_cache[entity_id] = entity

        # If entity doesn't exist or is inactive, return empty set
        if not entity:
            return set()

        # If it's an individual resource
        if entity.type == "RESOURCE":
            return {entity.id}

        # If it's a resource group with an expression
        if entity.type == "RESOURCEGROUP" and entity.expression:
            # Add this entity to visited set before recursion
            new_visited = visited.copy()
            new_visited.add(entity_id)
            # Recursively resolve the expression
            return await self.resolve_resource_expression(entity.expression, new_visited)

        # Otherwise it's a resource group without an expression
        # Resource groups without expressions should not grant access to any resources
        return set()

    async def validate_expression_with_database(
        self, expression: str, expression_type: str
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate expression syntax and check if all entities exist in the database.

        Args:
            expression: Expression to validate
            expression_type: Type of expression ("USER" or "RESOURCE")

        Returns:
            Tuple of (is_valid, errors, resolved_entities)
        """
        from sqlalchemy import select
        
        # First validate the syntax
        is_valid, error = ExpressionParser.validate_expression(expression)
        if not is_valid:
            return False, [error], []

        # Then check if all entities exist in the database
        try:
            # Parse the expression
            operations = list(ExpressionParser.parse_expression(expression))

            # Check each entity
            missing_entities = []
            resolved_entities = []

            for operation in operations:
                entity_id = operation["entity"]

                if expression_type.upper() == "USER":
                    # Check if user/group exists
                    result = await self.db.execute(
                        select(User).where(User.id == entity_id)
                    )
                    entity = result.scalar_one_or_none()
                    if not entity:
                        missing_entities.append(entity_id)
                    else:
                        resolved_entities.append(entity_id)

                elif expression_type.upper() == "RESOURCE":
                    # Check if resource/group exists
                    query = select(Artifact).where(Artifact.id == entity_id)
                    if self.application_name:
                        query = query.where(Artifact.application == self.application_name)
                    result = await self.db.execute(query)
                    entity = result.scalar_one_or_none()
                    if not entity:
                        missing_entities.append(entity_id)
                    else:
                        resolved_entities.append(entity_id)
                else:
                    return False, [f"Unknown expression type: {expression_type}"], []

            # If there are missing entities, return error
            if missing_entities:
                return (
                    False,
                    [f"Missing entities: {', '.join(missing_entities)}"],
                    resolved_entities,
                )

            return True, [], resolved_entities

        except Exception as e:
            return False, [f"Error evaluating expression: {str(e)}"], []


# Export classes
__all__ = [
    "ExpressionParser",
    "ExpressionResolver",
    "AsyncExpressionResolver",
]
