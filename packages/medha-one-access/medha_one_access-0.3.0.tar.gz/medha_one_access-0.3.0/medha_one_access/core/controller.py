"""
MedhaOne Access Control Library - Main Controller

This module provides the main AccessController class that serves as the
primary interface for the MedhaOne Access Control Library.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import asyncio
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, Future
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession

from medha_one_access.core.config import LibraryConfig
from medha_one_access.core.database import AsyncDatabaseManager
from medha_one_access.core.models import User, Artifact, AccessRule, AccessSummary, Base
from medha_one_access.core.background_tasks import AsyncBackgroundTaskManager, TaskPriority
from medha_one_access.core.cache import configure_caches
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
    AccessCheckRequest,
    AccessCheckResponse,
    AccessResolutionResponse,
)
from medha_one_access.core.resolver import BODMASResolver
from medha_one_access.core.expressions import ExpressionParser, ExpressionResolver
from medha_one_access.core.constraints import TimeConstraintEvaluator
from medha_one_access.core.exceptions import (
    MedhaAccessError,
    DatabaseConnectionError,
    ExpressionValidationError,
    PermissionDeniedError,
)
from medha_one_access.core.compatibility import from_orm, model_dump


class AsyncAccessController:
    """
    Main async controller class for MedhaOne Access Control Library.

    This class provides a high-level async interface for managing users, artifacts,
    access rules, and performing access resolution using the BODMAS algorithm.
    """

    def __init__(self, config: Union[LibraryConfig, Dict[str, Any], str]):
        """
        Initialize the AsyncAccessController.

        Args:
            config: Either a LibraryConfig object, a dictionary with configuration, or a database URL string
        """
        if isinstance(config, str):
            # If config is a string, treat it as database_url
            self.config = LibraryConfig(database_url=config, secret_key="default-secret-key")
        elif isinstance(config, dict):
            self.config = LibraryConfig(**config)
        else:
            self.config = config

        # Store application name for filtering
        self.application_name = self.config.application_name

        # Initialize async database manager
        self._session_manager: Optional[AsyncDatabaseManager] = None

        # Initialize background task manager
        self._task_manager: Optional[AsyncBackgroundTaskManager] = None

        # Initialize resolvers (will be set per operation with async session)
        self.expression_resolver = None
        self.bodmas_resolver = None

    async def initialize(self) -> None:
        """Initialize async database connection and test connectivity."""
        try:
            # Configure global caches from config
            configure_caches(self.config)

            # Initialize async database manager from config
            # Uses all configurable pool settings from LibraryConfig:
            # - max_pool_size, max_pool_overflow, pool_recycle_time
            # - pool_pre_ping, db_jit_enabled
            # - connection_timeout, query_timeout
            self._session_manager = AsyncDatabaseManager.from_config(self.config)

            # Test connection
            await self._session_manager.initialize()

            # Initialize and start background task manager from config
            # Uses all configurable worker settings from LibraryConfig:
            # - background_workers, background_queue_size
            # - background_shutdown_timeout, background_worker_timeout
            # - task_cleanup_max_age_hours
            self._task_manager = AsyncBackgroundTaskManager.from_config(self.config)

            # Register recalculation task handler
            self._task_manager.register_handler(
                "recalculate_access",
                self._handle_recalculation_task
            )

            # Start background task manager
            await self._task_manager.start()

        except Exception as e:
            raise DatabaseConnectionError(
                self.config.database_url,
                f"Failed to initialize async database: {str(e)}"
            )

    async def close(self) -> None:
        """Close database connections and cleanup resources."""
        # Stop background task manager first
        if self._task_manager:
            await self._task_manager.stop()
            self._task_manager = None
            
        # Close database connections
        if self._session_manager:
            await self._session_manager.close()
            self._session_manager = None

    @asynccontextmanager
    async def get_session(self):
        """Get async database session context manager."""
        if not self._session_manager:
            raise DatabaseConnectionError(
                self.config.database_url, 
                "Database not initialized. Call initialize() first."
            )
        
        async with self._session_manager.session_scope() as session:
            yield session

    def _get_async_resolvers(self, session: AsyncSession) -> tuple:
        """Get async resolvers for the given session."""
        from medha_one_access.core.expressions import AsyncExpressionResolver
        from medha_one_access.core.resolver import AsyncBODMASResolver
        
        expression_resolver = AsyncExpressionResolver(session, self.application_name)
        bodmas_resolver = AsyncBODMASResolver(session, self.application_name)
        return expression_resolver, bodmas_resolver

    def _apply_application_filter(self, query, model_class):
        """Apply application filtering to queries."""
        if hasattr(model_class, 'application') and self.application_name:
            return query.where(model_class.application == self.application_name)
        return query

    # Placeholder async methods - will be implemented in subsequent phases
    async def create_user(self, user_data: Union[UserCreate, Dict], upsert: bool = False) -> UserInDB:
        """Create a new user or update existing if upsert=True (async)."""
        try:
            async with self.get_session() as session:
                if isinstance(user_data, dict):
                    user_data = UserCreate(**user_data)

                # Check if user already exists
                result = await session.execute(
                    select(User).where(User.id == user_data.id)
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    if upsert:
                        # Update existing user
                        return await self.update_user(user_data.id, user_data)
                    else:
                        raise MedhaAccessError(f"User with ID {user_data.id} already exists")

                # Validate expression if it's a user group
                if user_data.type == "USERGROUP" and user_data.expression:
                    from medha_one_access.core.expressions import ExpressionParser
                    is_valid, error = ExpressionParser.validate_expression(
                        user_data.expression
                    )
                    if not is_valid:
                        raise ExpressionValidationError(
                            expression=user_data.expression,
                            reason=error
                        )

                # Create user
                db_user = User(**model_dump(user_data))
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)

                # Auto-recalculation: If this is a user group, recalculate member users' access
                if db_user.type == "USERGROUP" and db_user.expression:
                    affected_users = await self._get_affected_users_for_user_change(
                        db_user.id, new_expression=db_user.expression
                    )
                    if affected_users:
                        await self._trigger_auto_recalculation(affected_users)

                return from_orm(UserInDB, db_user)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to create user: {str(e)}")

    async def get_user(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID (async)."""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                return from_orm(UserInDB, user) if user else None

        except Exception as e:
            raise MedhaAccessError(f"Failed to get user: {str(e)}")

    async def update_user(self, user_id: str, user_data: Union[UserUpdate, Dict]) -> Optional[UserInDB]:
        """Update a user (async)."""
        try:
            async with self.get_session() as session:
                if isinstance(user_data, dict):
                    user_data = UserUpdate(**user_data)

                # Get existing user
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise MedhaAccessError(f"User with ID {user_id} not found")

                # Store old expression for affected user calculation
                old_expression = user.expression if user.type == "USERGROUP" else None

                # Update user fields
                update_data = model_dump(user_data, exclude_unset=True)
                for key, value in update_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

                # Validate new expression if it's a user group
                if user.type == "USERGROUP" and user.expression:
                    from medha_one_access.core.expressions import ExpressionParser
                    is_valid, error = ExpressionParser.validate_expression(user.expression)
                    if not is_valid:
                        raise ExpressionValidationError(
                            expression=user.expression,
                            reason=error
                        )

                user.updated_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(user)

                # Auto-recalculation if user group expression changed
                if user.type == "USERGROUP" and user.expression != old_expression:
                    affected_users = await self._get_affected_users_for_user_change(
                        user_id, old_expression=old_expression, new_expression=user.expression
                    )
                    if affected_users:
                        # CRITICAL: Mark summaries as stale IMMEDIATELY before background recalculation
                        await self._mark_summaries_stale(affected_users, self.application_name)

                        # Then trigger background recalculation to update the cache
                        await self._trigger_auto_recalculation(affected_users)

                return from_orm(UserInDB, user)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to update user: {str(e)}")

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user (async)."""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise MedhaAccessError(f"User with ID {user_id} not found")

                # Get affected users before deletion (for user groups)
                affected_users = []
                if user.type == "USERGROUP" and user.expression:
                    affected_users = await self._get_affected_users_for_user_change(
                        user_id, old_expression=user.expression, new_expression=None
                    )

                await session.delete(user)
                await session.commit()

                # Auto-recalculation for affected users
                if affected_users:
                    # CRITICAL: Mark summaries as stale IMMEDIATELY before background recalculation
                    await self._mark_summaries_stale(affected_users, self.application_name)

                    # Then trigger background recalculation to update the cache
                    await self._trigger_auto_recalculation(affected_users)

                return True

        except Exception as e:
            raise MedhaAccessError(f"Failed to delete user: {str(e)}")

    # Placeholder async methods - will be implemented in subsequent phases
    async def list_users(self, skip: int = 0, limit: Optional[int] = None, user_type: Optional[str] = None) -> List[UserInDB]:
        """List users with optional filtering (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                query = select(User)

                if user_type:
                    query = query.where(User.type == user_type)

                # Apply offset and limit
                query = query.offset(skip)
                if limit is not None:
                    query = query.limit(limit)

                result = await session.execute(query)
                users = result.scalars().all()
                return [from_orm(UserInDB, user) for user in users]
        except Exception as e:
            raise MedhaAccessError(f"Failed to list users: {str(e)}")

    async def get_users_bulk(self, user_ids: List[str]) -> Dict[str, UserInDB]:
        """
        Get multiple users by IDs in a single query to avoid N+1 problems (async).
        
        Args:
            user_ids: List of user IDs to retrieve
            
        Returns:
            Dictionary mapping user ID to UserInDB object
        """
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                query = select(User).where(User.id.in_(user_ids), User.active == True)
                result = await session.execute(query)
                users = result.scalars().all()
                return {user.id: from_orm(UserInDB, user) for user in users}
        except Exception as e:
            raise MedhaAccessError(f"Failed to get users in bulk: {str(e)}")

    async def create_artifact(self, artifact_data: Union[ArtifactCreate, Dict], upsert: bool = False) -> ArtifactInDB:
        """Create a new artifact or update existing if upsert=True (async)."""
        try:
            async with self.get_session() as session:
                if isinstance(artifact_data, dict):
                    artifact_data = ArtifactCreate(**artifact_data)

                # Check if artifact already exists (within application scope if configured)
                from sqlalchemy import select
                query = select(Artifact).where(Artifact.id == artifact_data.id)
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)
                result = await session.execute(query)
                existing = result.scalar_one_or_none()
                
                if existing:
                    if upsert:
                        # Update existing artifact
                        return await self.update_artifact(artifact_data.id, artifact_data)
                    else:
                        raise MedhaAccessError(
                            f"Artifact with ID {artifact_data.id} already exists in application {self.application_name or 'Default'}"
                        )

                # Validate expression if it's a resource group
                if artifact_data.type == "RESOURCEGROUP" and artifact_data.expression:
                    from medha_one_access.core.expressions import ExpressionParser
                    is_valid, error = ExpressionParser.validate_expression(
                        artifact_data.expression
                    )
                    if not is_valid:
                        raise ExpressionValidationError(
                            expression=artifact_data.expression,
                            reason=error
                        )

                # Create artifact
                artifact_dict = model_dump(artifact_data)
                
                # Set application name if configured and not already set
                if self.application_name and not artifact_dict.get('application'):
                    artifact_dict['application'] = self.application_name
                
                db_artifact = Artifact(**artifact_dict)
                session.add(db_artifact)
                await session.commit()
                await session.refresh(db_artifact)

                # Auto-recalculation: Recalculate affected user access
                affected_users = await self._get_affected_users_for_artifact_change(db_artifact.id)
                if affected_users:
                    await self._trigger_auto_recalculation(affected_users, db_artifact.application)

                return from_orm(ArtifactInDB, db_artifact)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to create artifact: {str(e)}")

    async def get_artifact(self, artifact_id: str) -> Optional[ArtifactInDB]:
        """Get artifact by ID (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                query = select(Artifact).where(Artifact.id == artifact_id)

                # Apply application filtering from config
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)

                result = await session.execute(query)
                artifact = result.scalar_one_or_none()
                if artifact:
                    return from_orm(ArtifactInDB, artifact)
                return None
        except Exception as e:
            raise MedhaAccessError(f"Failed to get artifact: {str(e)}")

    async def update_artifact(self, artifact_id: str, artifact_data: Dict[str, Any]) -> ArtifactInDB:
        """Update artifact (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select

                # Get existing artifact
                query = select(Artifact).where(Artifact.id == artifact_id)
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)

                result = await session.execute(query)
                artifact = result.scalar_one_or_none()

                if not artifact:
                    raise MedhaAccessError(f"Artifact {artifact_id} not found")

                # Get affected users before update (especially for expression changes)
                old_artifact = artifact
                affected_users = await self._get_affected_users_for_artifact_change(artifact_id, old_artifact)

                # Update fields
                for key, value in artifact_data.items():
                    if hasattr(artifact, key):
                        setattr(artifact, key, value)

                artifact.updated_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(artifact)

                # CRITICAL FIX: Expire all objects in session to force fresh queries
                # This ensures _get_affected_users_for_artifact_change() reads the updated
                # RESOURCEGROUP expressions from database, not from SQLAlchemy's identity map
                session.expire_all()

                # Auto-recalculation: Recalculate affected user access
                # Include users affected by both old and new artifact state
                new_affected_users = await self._get_affected_users_for_artifact_change(artifact_id)
                all_affected_users = list(set(affected_users + new_affected_users))
                if all_affected_users:
                    # CRITICAL: Mark summaries as stale IMMEDIATELY before background recalculation
                    # This ensures get_user_access() won't return stale cached data
                    await self._mark_summaries_stale(all_affected_users, artifact.application)

                    # Then trigger background recalculation to update the cache
                    await self._trigger_auto_recalculation(all_affected_users, artifact.application)

                return from_orm(ArtifactInDB, artifact)
        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to update artifact {artifact_id}: {str(e)}")

    async def delete_artifact(self, artifact_id: str) -> bool:
        """Delete artifact (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select, delete

                # Get artifact to delete
                query = select(Artifact).where(Artifact.id == artifact_id)
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)

                result = await session.execute(query)
                artifact = result.scalar_one_or_none()

                if not artifact:
                    return False

                # Get affected users before deletion
                affected_users = await self._get_affected_users_for_artifact_change(artifact_id, artifact)
                artifact_application = artifact.application

                # Delete artifact
                await session.delete(artifact)
                await session.commit()

                # Auto-recalculation: Recalculate affected user access
                if affected_users:
                    # CRITICAL: Mark summaries as stale IMMEDIATELY before background recalculation
                    await self._mark_summaries_stale(affected_users, artifact_application)

                    # Then trigger background recalculation to update the cache
                    await self._trigger_auto_recalculation(affected_users, artifact_application)

                return True
        except Exception as e:
            raise MedhaAccessError(f"Failed to delete artifact {artifact_id}: {str(e)}")

    async def list_artifacts(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        artifact_type: Optional[str] = None,
        application: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> List[ArtifactInDB]:
        """List artifacts with filtering and pagination (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select

                query = select(Artifact)

                # Apply application filtering from config
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)

                # Apply filters
                if artifact_type:
                    query = query.where(Artifact.type == artifact_type)
                if application:
                    query = query.where(Artifact.application == application)
                if active is not None:
                    query = query.where(Artifact.active == active)

                # Apply pagination
                query = query.offset(skip)
                if limit is not None:
                    query = query.limit(limit)

                result = await session.execute(query)
                artifacts = result.scalars().all()

                return [from_orm(ArtifactInDB, artifact) for artifact in artifacts]
        except Exception as e:
            raise MedhaAccessError(f"Failed to list artifacts: {str(e)}")

    async def resolve_user_access(self, user_id: str, evaluation_time: Optional[datetime] = None, include_audit: bool = False) -> Dict[str, Any]:
        """Resolve user access using BODMAS (async)."""
        try:
            # Use config setting if include_audit not explicitly specified
            if include_audit is None:
                include_audit = getattr(self.config, 'enable_audit_trail', True)
                
            async with self.get_session() as session:
                _, bodmas_resolver = self._get_async_resolvers(session)
                result = await bodmas_resolver.resolve_user_access(user_id, evaluation_time, include_audit)
                
                return result

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to resolve user access: {str(e)}")

    async def get_user_access(self, user_id: str, max_cache_age_minutes: int = 60, include_audit: bool = False, force_recalculate: bool = False) -> Dict[str, Any]:
        """Get user access with caching (async)."""
        try:
            cache_result = None
            used_cache = False
            
            # Check cache first (unless forced to recalculate)
            if not force_recalculate:
                cache_result = await self._get_cached_user_access(user_id, max_cache_age_minutes)
                if cache_result:
                    used_cache = True
                    # Add cache metadata
                    cache_result["cache_info"] = {
                        "used_cache": True,
                        "cache_age_minutes": cache_result.get("cache_age_minutes", 0),
                        "last_calculated": cache_result.get("last_calculated"),
                        "is_stale": cache_result.get("is_stale", False)
                    }
                    return cache_result
            
            # Cache miss or forced recalculation - do real-time calculation
            real_time_result = await self.resolve_user_access(
                user_id=user_id, 
                evaluation_time=None, 
                include_audit=include_audit
            )
            
            # Store in cache for future use
            await self._store_user_access_cache(user_id, real_time_result)
            
            # Add cache metadata
            real_time_result["cache_info"] = {
                "used_cache": False,
                "calculated_at": datetime.now(timezone.utc).isoformat(),
                "cached_for_future": True
            }
            
            return real_time_result
            
        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to get user access: {str(e)}")

    async def get_user_access_by_name(
        self,
        user_id: str,
        max_cache_age_minutes: int = 60,
        include_audit: bool = False,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Get user access with resource names instead of resource IDs (async).

        This method wraps get_user_access() and transforms the resolved_access dictionary
        to use resource names as keys instead of resource IDs.

        Args:
            user_id: The ID of the user
            max_cache_age_minutes: Maximum age of cache in minutes (default: 60)
            include_audit: Whether to include audit trail (only for real-time calculation)
            force_recalculate: Skip cache and force real-time calculation

        Returns:
            Dictionary containing resolved access with resource names and cache metadata
        """
        try:
            # Get the standard user access (with resource IDs)
            access_result = await self.get_user_access(
                user_id=user_id,
                max_cache_age_minutes=max_cache_age_minutes,
                include_audit=include_audit,
                force_recalculate=force_recalculate
            )

            resolved_access = access_result.get("resolved_access", {})

            if not resolved_access:
                # No resources, return early
                access_result["resolved_access_by_name"] = {}
                access_result["resource_name_mapping"] = {}
                return access_result

            # Get all resource IDs
            resource_ids = list(resolved_access.keys())

            # Bulk fetch artifacts to get names
            async with self.get_session() as session:
                from sqlalchemy import select
                query = select(Artifact).where(Artifact.id.in_(resource_ids))

                # Apply application filtering
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)

                result = await session.execute(query)
                artifacts = result.scalars().all()

                # Create ID to name mapping
                id_to_name = {}
                for artifact in artifacts:
                    # Use name if available, otherwise fall back to ID
                    name = artifact.name if artifact.name else artifact.id
                    id_to_name[artifact.id] = name

                # Handle missing artifacts (use ID as fallback)
                for resource_id in resource_ids:
                    if resource_id not in id_to_name:
                        id_to_name[resource_id] = f"{resource_id} (not found)"

                # Transform resolved_access to use names
                resolved_access_by_name = {}
                for resource_id, permissions in resolved_access.items():
                    resource_name = id_to_name.get(resource_id, resource_id)
                    resolved_access_by_name[resource_name] = permissions

                # Add the transformed data to result
                access_result["resolved_access_by_name"] = resolved_access_by_name
                access_result["resource_name_mapping"] = id_to_name

                return access_result

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to get user access by name: {str(e)}")

    async def resolve_resource_access(
        self,
        resource_id: str,
        evaluation_time: Optional[datetime] = None,
        include_audit: bool = False
    ) -> Dict[str, Any]:
        """
        Resolve all users who can access a resource using BODMAS algorithm (async).

        This method returns all users with access to the specified resource along with
        their permissions. Optimized for performance with a single query.

        Args:
            resource_id: The ID of the resource
            evaluation_time: Time to evaluate constraints (defaults to current time)
            include_audit: Whether to include audit trail in response (defaults to False)

        Returns:
            Dictionary containing:
            - permissions_by_user: Map of user_id -> list of permissions
            - resource_id: The resource ID
            - evaluation_time: When the access was evaluated
            - audit_trail: (optional) Step-by-step resolution details

        Example:
            {
                "resource_id": "dashboard-app",
                "permissions_by_user": {
                    "user1@example.com": ["READ", "WRITE"],
                    "user2@example.com": ["READ"]
                },
                "evaluation_time": "2025-01-15T10:30:00Z"
            }
        """
        try:
            async with self.get_session() as session:
                _, bodmas_resolver = self._get_async_resolvers(session)
                result = await bodmas_resolver.resolve_resource_access(
                    resource_id, evaluation_time
                )

                # Remove audit trail if not requested to reduce payload size
                if not include_audit and "audit_trail" in result:
                    del result["audit_trail"]

                return result

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to resolve resource access: {str(e)}")

    async def _get_cached_user_access(self, user_id: str, max_cache_age_minutes: int) -> Optional[Dict[str, Any]]:
        """Get cached user access if available and fresh (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                application_name = self.application_name or "default"
                
                # Optimized query with explicit ordering for better index usage
                result = await session.execute(
                    select(AccessSummary)
                    .where(
                        AccessSummary.user_id == user_id,
                        AccessSummary.application == application_name,
                        AccessSummary.is_stale == False
                    )
                    .order_by(AccessSummary.last_calculated.desc())  # Most recent first
                )
                summary = result.scalar_one_or_none()
                
                if not summary:
                    return None
                
                # Check cache age
                if summary.last_calculated:
                    cache_age = datetime.now(timezone.utc) - summary.last_calculated
                    cache_age_minutes = cache_age.total_seconds() / 60
                    
                    if cache_age_minutes > max_cache_age_minutes:
                        # Cache is too old, mark as stale
                        summary.is_stale = True
                        await session.commit()
                        return None
                else:
                    # No calculation time recorded, consider stale
                    return None
                
                # Extract data from summary
                summary_data = summary.summary_data or {}
                
                return {
                    "user_id": summary.user_id,
                    "application": summary.application,
                    "evaluation_time": datetime.now(timezone.utc).isoformat(),
                    "resolved_access": summary_data.get("resolved_access", {}),
                    "resolved_access_detailed": summary_data.get("resolved_access_detailed", {}),
                    "total_accessible_resources": summary.total_accessible_resources,
                    "cache_age_minutes": cache_age_minutes,
                    "last_calculated": summary.last_calculated.isoformat(),
                    "is_stale": summary.is_stale
                }
                
        except Exception:
            return None
    
    async def _store_user_access_cache(self, user_id: str, access_result: Dict[str, Any]) -> None:
        """Store user access result in cache (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                application_name = self.application_name or "default"
                resolved_access = access_result.get("resolved_access", {})
                
                # Create enhanced summary data
                summary_data = {
                    "resolved_access": resolved_access,
                    "resolved_access_detailed": access_result.get("resolved_access_detailed", {}),
                    "accessibleResourceIds": list(resolved_access.keys()),
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                }
                
                # Update or create summary
                result = await session.execute(
                    select(AccessSummary)
                    .where(
                        AccessSummary.user_id == user_id,
                        AccessSummary.application == application_name
                    )
                )
                summary = result.scalar_one_or_none()
                
                if summary:
                    summary.total_accessible_resources = len(resolved_access)
                    summary.summary_data = summary_data
                    summary.last_calculated = datetime.now(timezone.utc)
                    summary.is_stale = False
                else:
                    summary = AccessSummary(
                        id=f"summary_{user_id}_{application_name}",
                        user_id=user_id,
                        application=application_name,
                        total_accessible_resources=len(resolved_access),
                        total_groups=0,  # Simplified for caching
                        direct_permissions=0,  # Simplified for caching
                        inherited_permissions=0,  # Simplified for caching
                        summary_data=summary_data,
                        last_calculated=datetime.now(timezone.utc),
                        is_stale=False,
                    )
                    session.add(summary)
                
                await session.commit()
                
        except Exception as e:
            # Log error but don't break the main operation
            print(f"Warning: Failed to store user access cache: {str(e)}")

    # Placeholder helper methods that need async conversion
    async def _get_affected_users_for_user_change(self, user_id: str, old_expression: Optional[str] = None, new_expression: Optional[str] = None) -> List[str]:
        """Get users affected by user changes (async)."""
        try:
            async with self.get_session() as session:
                affected_users = set([user_id])  # Always include the changed user
                
                expression_resolver, _ = self._get_async_resolvers(session)
                
                # If this was a user group, get members from old and new expressions
                if old_expression:
                    try:
                        old_members = await expression_resolver.resolve_user_expression(old_expression)
                        affected_users.update(old_members)
                    except Exception:
                        pass
                        
                if new_expression:
                    try:
                        new_members = await expression_resolver.resolve_user_expression(new_expression)
                        affected_users.update(new_members)
                    except Exception:
                        pass
                
                return list(affected_users)
        except Exception:
            return [user_id]

    async def _get_affected_users_for_artifact_change(self, artifact_id: str, old_artifact=None) -> List[str]:
        """Get list of users affected by artifact creation/update/deletion (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                affected_users = set()
                
                # Find all resource groups that might include this artifact
                # Use populate_existing=True to force reload from DB and bypass SQLAlchemy cache
                result = await session.execute(
                    select(Artifact).where(
                        Artifact.type == "RESOURCEGROUP",
                        Artifact.active == True
                    ).execution_options(populate_existing=True)
                )
                resource_groups = result.scalars().all()
                
                expression_resolver, _ = self._get_async_resolvers(session)
                
                # Check each resource group to see if it includes this artifact
                for group in resource_groups:
                    if group.expression:
                        try:
                            resolved_artifacts = await expression_resolver.resolve_resource_expression(group.expression)
                            if artifact_id in resolved_artifacts:
                                # Find users with access to this resource group
                                group_result = await session.execute(
                                    select(AccessRule).where(
                                        AccessRule.resource_expression.contains(group.id),
                                        AccessRule.active == True
                                    )
                                )
                                group_rules = group_result.scalars().all()
                                
                                for rule in group_rules:
                                    rule_users = await expression_resolver.resolve_user_expression(rule.user_expression)
                                    affected_users.update(rule_users)
                        except Exception:
                            continue
                
                # Also check direct rules targeting this artifact
                direct_result = await session.execute(
                    select(AccessRule).where(
                        AccessRule.resource_expression.contains(artifact_id),
                        AccessRule.active == True
                    )
                )
                direct_rules = direct_result.scalars().all()
                
                for rule in direct_rules:
                    try:
                        rule_users = await expression_resolver.resolve_user_expression(rule.user_expression)
                        affected_users.update(rule_users)
                    except Exception:
                        continue
                        
                return list(affected_users)
        except Exception:
            return []

    async def _mark_summaries_stale(self, user_ids: List[str], application: Optional[str] = None) -> None:
        """
        Mark access summaries as stale for the given users (async).

        This method immediately invalidates cached access summaries, ensuring that
        get_user_access() will not return stale data while background recalculation
        is in progress.

        Args:
            user_ids: List of user IDs whose summaries should be marked stale
            application: Optional application context (uses controller default if not provided)
        """
        if not user_ids:
            return

        try:
            async with self.get_session() as session:
                from sqlalchemy import update
                application_name = application or self.application_name or "default"

                # Mark summaries as stale in bulk
                stmt = (
                    update(AccessSummary)
                    .where(
                        AccessSummary.user_id.in_(user_ids),
                        AccessSummary.application == application_name
                    )
                    .values(
                        is_stale=True,
                        updated_at=datetime.now(timezone.utc)
                    )
                )
                await session.execute(stmt)
                await session.commit()

                print(f"INFO: Marked {len(user_ids)} access summaries as stale for application '{application_name}'")
        except Exception as e:
            # Log error but don't break the main operation
            print(f"WARNING: Failed to mark summaries as stale: {str(e)}")

    async def _trigger_auto_recalculation(self, user_ids: List[str], application: Optional[str] = None) -> Optional[str]:
        """
        Trigger auto-recalculation for users in background (async).
        
        Args:
            user_ids: List of user IDs to recalculate
            application: Optional application context
            
        Returns:
            Task ID for tracking or None if task manager not available
        """
        if not self._task_manager:
            # Fallback: log warning but don't block the operation
            print(f"Warning: Background task manager not available. Skipping recalculation for {len(user_ids)} users")
            return None
            
        try:
            # Submit background recalculation task with high priority
            task_id = await self._task_manager.submit_recalculation_task(
                user_ids=user_ids,
                application=application or self.application_name,
                priority=TaskPriority.HIGH
            )
            print(f"Submitted background recalculation task {task_id} for {len(user_ids)} users")
            return task_id
            
        except Exception as e:
            print(f"Failed to submit background recalculation task: {str(e)}")
            return None

    async def _handle_recalculation_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle background recalculation task.
        
        Args:
            payload: Task payload containing user_ids and application
            
        Returns:
            Task result with processing statistics
        """
        user_ids = payload.get("user_ids", [])
        application = payload.get("application")
        
        if not user_ids:
            return {"status": "skipped", "reason": "No user IDs provided"}
            
        try:
            processed_count = 0
            failed_count = 0
            results = []
            
            # Process each user's access recalculation
            for user_id in user_ids:
                try:
                    # Perform actual access resolution and cache the result
                    access_result = await self.resolve_user_access(user_id, include_audit=False)
                    
                    # Store the resolved access in cache (AccessSummary)
                    await self._store_user_access_cache(user_id, access_result)
                    
                    results.append({
                        "user_id": user_id,
                        "status": "completed",
                        "resources_count": len(access_result.get("resolved_access", {})),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    processed_count += 1
                    
                except Exception as user_error:
                    results.append({
                        "user_id": user_id,
                        "status": "failed",
                        "error": str(user_error),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    failed_count += 1
            
            return {
                "status": "completed",
                "processed_count": processed_count,
                "failed_count": failed_count,
                "total_users": len(user_ids),
                "application": application,
                "results": results,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "total_users": len(user_ids),
                "application": application,
                "failed_at": datetime.now(timezone.utc).isoformat()
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform async health check."""
        try:
            if not self._session_manager:
                return {
                    "status": "unhealthy",
                    "error": "Database not initialized"
                }

            # Test database connection
            async with self.get_session() as session:
                await session.execute(select(1))

            # Get some basic stats
            async with self.get_session() as session:
                user_count_result = await session.execute(select(func.count()).select_from(User))
                artifact_count_result = await session.execute(select(func.count()).select_from(Artifact))
                rule_count_result = await session.execute(select(func.count()).select_from(AccessRule))
                
                # Get cache statistics
                application_name = self.application_name or "default"
                total_summaries_result = await session.execute(
                    select(func.count()).select_from(AccessSummary).where(
                        AccessSummary.application == application_name
                    )
                )
                stale_summaries_result = await session.execute(
                    select(func.count()).select_from(AccessSummary).where(
                        AccessSummary.application == application_name,
                        AccessSummary.is_stale == True
                    )
                )
                
                user_count = user_count_result.scalar()
                artifact_count = artifact_count_result.scalar()
                rule_count = rule_count_result.scalar()
                total_summaries = total_summaries_result.scalar()
                stale_summaries = stale_summaries_result.scalar()
                fresh_summaries = total_summaries - stale_summaries

            return {
                "status": "healthy",
                "database": "connected",
                "statistics": {
                    "users": user_count,
                    "artifacts": artifact_count,
                    "access_rules": rule_count,
                    "cache_summaries": {
                        "total": total_summaries,
                        "fresh": fresh_summaries,
                        "stale": stale_summaries,
                        "cache_hit_rate": round((fresh_summaries / total_summaries * 100) if total_summaries > 0 else 0, 2)
                    }
                },
                "configuration": {
                    "api_prefix": self.config.api_prefix,
                    "application_name": self.application_name,
                    "debug": self.config.debug,
                    "auto_recalculation": {
                        "enabled": getattr(self.config, 'enable_auto_recalculation', True),
                        "mode": getattr(self.config, 'auto_recalc_mode', 'immediate'),
                        "batch_size": getattr(self.config, 'auto_recalc_batch_size', 50),
                    }
                },
                "background_tasks": await self.get_background_queue_stats(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "connection_failed",
                "error": str(e),
            }

    async def get_background_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a background task."""
        if not self._task_manager:
            return None
        return await self._task_manager.get_task_status(task_id)

    async def get_background_queue_stats(self) -> Dict[str, Any]:
        """Get background task queue statistics."""
        if not self._task_manager:
            return {
                "status": "disabled",
                "message": "Background task manager not available"
            }
        return await self._task_manager.get_queue_stats()

    async def cleanup_old_background_tasks(self, max_age_hours: int = 24) -> None:
        """Clean up old background tasks from memory."""
        if self._task_manager:
            await self._task_manager.cleanup_old_tasks(max_age_hours)

    # Access Rule Management Methods (Async)

    async def create_access_rule(
        self, rule_data: Union[AccessRuleCreate, Dict]
    ) -> AccessRuleInDB:
        """Create a new access rule (async)."""
        try:
            async with self.get_session() as session:
                if isinstance(rule_data, dict):
                    rule_data = AccessRuleCreate(**rule_data)

                # Check if access rule already exists (within application scope if configured)
                from sqlalchemy import select
                query = select(AccessRule).where(AccessRule.id == rule_data.id)
                if self.application_name:
                    query = query.where(AccessRule.application == self.application_name)
                result = await session.execute(query)
                existing = result.scalar_one_or_none()

                if existing:
                    raise MedhaAccessError(
                        f"Access rule with ID {rule_data.id} already exists in application {self.application_name or 'Default'}"
                    )

                # Validate expressions
                user_valid, user_error = ExpressionParser.validate_expression(
                    rule_data.user_expression
                )
                if not user_valid:
                    raise ExpressionValidationError(
                        expression=rule_data.user_expression,
                        reason=user_error
                    )

                resource_valid, resource_error = ExpressionParser.validate_expression(
                    rule_data.resource_expression
                )
                if not resource_valid:
                    raise ExpressionValidationError(
                        expression=rule_data.resource_expression,
                        reason=resource_error
                    )

                # Create rule
                rule_dict = model_dump(rule_data)

                # Set application name if configured and not already set
                if self.application_name and not rule_dict.get('application'):
                    rule_dict['application'] = self.application_name

                db_rule = AccessRule(**rule_dict)
                session.add(db_rule)
                await session.commit()
                await session.refresh(db_rule)

                # Auto-recalculation: Recalculate affected user access
                affected_users = await self._get_affected_users_for_access_rule(db_rule)
                if affected_users:
                    await self._trigger_auto_recalculation(affected_users, db_rule.application)

                return from_orm(AccessRuleInDB, db_rule)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to create access rule: {str(e)}")

    async def get_access_rule(self, rule_id: str) -> Optional[AccessRuleInDB]:
        """Get access rule by ID (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                query = select(AccessRule).where(AccessRule.id == rule_id)

                # Apply application filtering from config
                if self.application_name:
                    query = query.where(AccessRule.application == self.application_name)

                result = await session.execute(query)
                rule = result.scalar_one_or_none()

                if rule:
                    return from_orm(AccessRuleInDB, rule)
                return None
        except Exception as e:
            raise MedhaAccessError(f"Failed to get access rule {rule_id}: {str(e)}")

    async def update_access_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> AccessRuleInDB:
        """Update access rule (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(AccessRule).where(AccessRule.id == rule_id)
                )
                rule = result.scalar_one_or_none()

                if not rule:
                    raise MedhaAccessError(f"Access rule {rule_id} not found")

                # Get affected users before and after update
                old_affected_users = await self._get_affected_users_for_access_rule(rule)

                # Update fields
                for key, value in rule_data.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)

                rule.updated_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(rule)

                # Get new affected users and combine with old ones
                new_affected_users = await self._get_affected_users_for_access_rule(rule)
                all_affected_users = list(set(old_affected_users + new_affected_users))

                # Auto-recalculation: Recalculate affected user access
                if all_affected_users:
                    # CRITICAL: Mark summaries as stale IMMEDIATELY before background recalculation
                    await self._mark_summaries_stale(all_affected_users, rule.application)

                    # Then trigger background recalculation to update the cache
                    await self._trigger_auto_recalculation(all_affected_users, rule.application)

                return from_orm(AccessRuleInDB, rule)
        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to update access rule {rule_id}: {str(e)}")

    async def delete_access_rule(self, rule_id: str) -> bool:
        """Delete access rule (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(AccessRule).where(AccessRule.id == rule_id)
                )
                rule = result.scalar_one_or_none()

                if not rule:
                    return False

                # Get affected users before deletion
                affected_users = await self._get_affected_users_for_access_rule(rule)
                rule_application = rule.application

                await session.delete(rule)
                await session.commit()

                # Auto-recalculation: Recalculate affected user access
                if affected_users:
                    # CRITICAL: Mark summaries as stale IMMEDIATELY before background recalculation
                    await self._mark_summaries_stale(affected_users, rule_application)

                    # Then trigger background recalculation to update the cache
                    await self._trigger_auto_recalculation(affected_users, rule_application)

                return True
        except Exception as e:
            raise MedhaAccessError(f"Failed to delete access rule {rule_id}: {str(e)}")

    async def list_access_rules(
        self,
        user_expression: Optional[str] = None,
        resource_expression: Optional[str] = None,
        application: Optional[str] = None,
        active: Optional[bool] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[AccessRuleInDB]:
        """List access rules with filtering and pagination (async)."""
        try:
            async with self.get_session() as session:
                from sqlalchemy import select

                query = select(AccessRule)

                # Apply application filtering from config
                if self.application_name:
                    query = query.where(AccessRule.application == self.application_name)

                # Apply filters
                if user_expression:
                    query = query.where(AccessRule.user_expression == user_expression)
                if resource_expression:
                    query = query.where(AccessRule.resource_expression == resource_expression)
                if application:
                    query = query.where(AccessRule.application == application)
                if active is not None:
                    query = query.where(AccessRule.active == active)

                # Apply pagination
                query = query.offset(skip)
                if limit is not None:
                    query = query.limit(limit)

                result = await session.execute(query)
                rules = result.scalars().all()

                return [from_orm(AccessRuleInDB, rule) for rule in rules]
        except Exception as e:
            raise MedhaAccessError(f"Failed to list access rules: {str(e)}")

    async def check_access(
        self,
        user_id: str,
        resource_id: str,
        permission: str,
        evaluation_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Check if a user has a specific permission for a resource (async).

        Args:
            user_id: The ID of the user
            resource_id: The ID of the resource
            permission: The permission to check
            evaluation_time: Time to evaluate constraints

        Returns:
            Dictionary with access decision and audit trail
        """
        try:
            async with self.get_session() as session:
                _, bodmas_resolver = self._get_async_resolvers(session)
                return await bodmas_resolver.check_access(
                    user_id, resource_id, permission, evaluation_time
                )

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to check access: {str(e)}")

    async def get_resource_permissions_by_name(
        self,
        user_id: str,
        resource_name: str,
        max_cache_age_minutes: int = 60,
        include_audit: bool = False,
        force_recalculate: bool = False,
        evaluation_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get all permissions a user has for a specific resource by resource name (async).

        Args:
            user_id: The ID of the user (required)
            resource_name: The name of the resource (required)
            max_cache_age_minutes: Maximum age of cache in minutes (default: 60)
            include_audit: Whether to include audit trail (default: False)
            force_recalculate: Skip cache and force real-time calculation (default: False)
            evaluation_time: Time to evaluate access (default: None)

        Returns:
            Dictionary containing user permissions for the specific resource
        """
        try:
            # Find the resource by name
            async with self.get_session() as session:
                from sqlalchemy import select
                query = select(Artifact).where(Artifact.name == resource_name)

                # Apply application filtering
                if self.application_name:
                    query = query.where(Artifact.application == self.application_name)

                result = await session.execute(query)
                artifact = result.scalar_one_or_none()

                if not artifact:
                    return {
                        "user_id": user_id,
                        "resource_name": resource_name,
                        "resource_id": None,
                        "permissions": [],
                        "found": False,
                        "error": f"Resource with name '{resource_name}' not found",
                        "evaluation_time": (evaluation_time or datetime.now(timezone.utc)).isoformat()
                    }

                resource_id = artifact.id

            # Get all user access using cache
            user_access = await self.get_user_access(
                user_id=user_id,
                max_cache_age_minutes=max_cache_age_minutes,
                include_audit=include_audit,
                force_recalculate=force_recalculate
            )

            # Extract permissions for this specific resource
            resolved_access = user_access.get("resolved_access", {})
            permissions = resolved_access.get(resource_id, [])

            # Build response
            response = {
                "user_id": user_id,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "permissions": permissions,
                "found": True,
                "evaluation_time": user_access.get("evaluation_time"),
                "cache_info": user_access.get("cache_info", {})
            }

            if include_audit:
                response["audit_trail"] = user_access.get("audit_trail", [])

            return response

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to get resource permissions by name: {str(e)}")

    async def _get_affected_users_for_access_rule(self, rule: AccessRule) -> List[str]:
        """Get list of users affected by an access rule change (async)."""
        try:
            async with self.get_session() as session:
                expression_resolver, _ = self._get_async_resolvers(session)
                # Resolve user expression to get affected user IDs
                affected_users = await expression_resolver.resolve_user_expression(rule.user_expression)
                return list(affected_users)
        except Exception:
            return []


class AccessController:
    """
    Main controller class for MedhaOne Access Control Library.

    This class provides a high-level interface for managing users, artifacts,
    access rules, and performing access resolution using the BODMAS algorithm.
    """

    def __init__(self, config: Union[LibraryConfig, Dict[str, Any], str]):
        """
        Initialize the AccessController.

        Args:
            config: Either a LibraryConfig object, a dictionary with configuration, or a database URL string
        """
        if isinstance(config, str):
            # If config is a string, treat it as database_url
            self.config = LibraryConfig(database_url=config, secret_key="default-secret-key")
        elif isinstance(config, dict):
            self.config = LibraryConfig(**config)
        else:
            self.config = config

        # Store application name for filtering
        self.application_name = self.config.application_name

        # Configure global caches from config
        configure_caches(self.config)

        # Initialize database
        self._init_database()

        # Initialize background thread pool for async recalculation
        # Uses background_workers from config for thread count
        self._background_executor = ThreadPoolExecutor(
            max_workers=self.config.background_workers,
            thread_name_prefix="medha_recalc"
        )
        self._background_tasks: Dict[str, Future] = {}

        # Initialize resolvers
        self.expression_resolver = None
        self.bodmas_resolver = None

    def _init_database(self) -> None:
        """Initialize database connection and session factory."""
        try:
            # Determine if using SQLite or other database
            is_sqlite = "sqlite" in self.config.database_url

            # Optimized engine configuration using config settings
            engine_kwargs = {
                "echo": self.config.debug,
                "pool_pre_ping": self.config.pool_pre_ping,
            }

            if is_sqlite:
                # SQLite-specific optimizations
                engine_kwargs.update({
                    "poolclass": StaticPool,
                    "connect_args": {
                        "check_same_thread": False,
                        "timeout": self.config.connection_timeout,
                    },
                })
            else:
                # PostgreSQL/other database optimizations using config settings
                engine_kwargs.update({
                    "pool_size": self.config.max_pool_size,
                    "max_overflow": self.config.max_pool_overflow,
                    "pool_recycle": self.config.pool_recycle_time,
                    "pool_timeout": self.config.connection_timeout,
                    "connect_args": {
                        "connect_timeout": self.config.connection_timeout,
                        "application_name": self.config.project_name.replace(" ", "_").lower(),
                        # PostgreSQL performance settings
                        "options": f"-c statement_timeout={self.config.query_timeout * 1000}",
                    },
                })

            # Create engine with optimized settings
            self.engine = create_engine(self.config.database_url, **engine_kwargs)

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)

        except Exception as e:
            raise DatabaseConnectionError(
                database_url=str(self.config.database_url),
                reason=f"Failed to initialize database: {str(e)}"
            )

    def close(self) -> None:
        """Close database connections and cleanup background resources."""
        try:
            # Shutdown background thread pool
            if hasattr(self, '_background_executor') and self._background_executor:
                print("INFO: Shutting down background task executor...")
                self._background_executor.shutdown(wait=True, timeout=30)
                self._background_executor = None
                
            # Clear background tasks tracking
            if hasattr(self, '_background_tasks'):
                self._background_tasks.clear()
                
            # Close database engine if it exists
            if hasattr(self, 'engine') and self.engine:
                self.engine.dispose()
                
        except Exception as e:
            print(f"Warning: Error during AccessController cleanup: {str(e)}")

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def _get_resolvers(self, session: Session) -> tuple:
        """Get expression and BODMAS resolvers for the session."""
        if not self.expression_resolver:
            self.expression_resolver = ExpressionResolver(session, self.application_name)
        if not self.bodmas_resolver:
            self.bodmas_resolver = BODMASResolver(session, self.application_name)
        return self.expression_resolver, self.bodmas_resolver

    def _apply_application_filter(self, query, model_class):
        """Apply application name filtering to a query if application_name is configured."""
        if self.application_name and hasattr(model_class, 'application'):
            query = query.filter(model_class.application == self.application_name)
        return query

    def get_users_bulk(self, user_ids: List[str]) -> Dict[str, UserInDB]:
        """
        Get multiple users by IDs in a single query to avoid N+1 problems.
        
        Args:
            user_ids: List of user IDs to retrieve
            
        Returns:
            Dictionary mapping user ID to UserInDB object
        """
        try:
            with self.get_session() as session:
                users = session.query(User).filter(User.id.in_(user_ids), User.active == True).all()
                return {user.id: from_orm(UserInDB, user) for user in users}
        except Exception as e:
            raise MedhaAccessError(f"Failed to get users in bulk: {str(e)}")

    def get_artifacts_bulk(self, artifact_ids: List[str]) -> Dict[str, ArtifactInDB]:
        """
        Get multiple artifacts by IDs in a single query to avoid N+1 problems.
        
        Args:
            artifact_ids: List of artifact IDs to retrieve
            
        Returns:
            Dictionary mapping artifact ID to ArtifactInDB object
        """
        try:
            with self.get_session() as session:
                query = session.query(Artifact).filter(Artifact.id.in_(artifact_ids), Artifact.active == True)
                query = self._apply_application_filter(query, Artifact)
                artifacts = query.all()
                return {artifact.id: from_orm(ArtifactInDB, artifact) for artifact in artifacts}
        except Exception as e:
            raise MedhaAccessError(f"Failed to get artifacts in bulk: {str(e)}")

    def get_access_rules_bulk(self, rule_ids: List[str]) -> Dict[str, AccessRuleInDB]:
        """
        Get multiple access rules by IDs in a single query to avoid N+1 problems.
        
        Args:
            rule_ids: List of rule IDs to retrieve
            
        Returns:
            Dictionary mapping rule ID to AccessRuleInDB object
        """
        try:
            with self.get_session() as session:
                query = session.query(AccessRule).filter(AccessRule.id.in_(rule_ids), AccessRule.active == True)
                query = self._apply_application_filter(query, AccessRule)
                rules = query.all()
                return {rule.id: from_orm(AccessRuleInDB, rule) for rule in rules}
        except Exception as e:
            raise MedhaAccessError(f"Failed to get access rules in bulk: {str(e)}")

    # User Management Methods

    def create_user(self, user_data: Union[UserCreate, Dict], upsert: bool = False) -> UserInDB:
        """Create a new user or update existing if upsert=True."""
        try:
            with self.get_session() as session:
                if isinstance(user_data, dict):
                    user_data = UserCreate(**user_data)

                # Check if user already exists
                existing_user = (
                    session.query(User).filter(User.id == user_data.id).first()
                )
                if existing_user:
                    if upsert:
                        # Update existing user
                        return self.update_user(user_data.id, user_data)
                    else:
                        raise MedhaAccessError(f"User with ID {user_data.id} already exists")

                # Validate expression if it's a user group
                if user_data.type == "USERGROUP" and user_data.expression:
                    is_valid, error = ExpressionParser.validate_expression(
                        user_data.expression
                    )
                    if not is_valid:
                        raise ExpressionValidationError(
                            expression=user_data.expression,
                            reason=error
                        )

                # Create user
                db_user = User(**model_dump(user_data))
                session.add(db_user)
                session.commit()
                session.refresh(db_user)

                # Auto-recalculation: If this is a user group, recalculate member users' access
                if db_user.type == "USERGROUP" and db_user.expression:
                    affected_users = self._get_affected_users_for_user_change(
                        db_user.id, new_expression=db_user.expression
                    )
                    if affected_users:
                        self._trigger_auto_recalculation(affected_users)

                return from_orm(UserInDB, db_user)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to create user: {str(e)}")

    def get_user(self, user_id: str) -> Optional[UserInDB]:
        """Get a user by ID."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                return from_orm(UserInDB, user) if user else None

        except Exception as e:
            raise MedhaAccessError(f"Failed to get user: {str(e)}")

    def update_user(
        self, user_id: str, user_data: Union[UserUpdate, Dict]
    ) -> Optional[UserInDB]:
        """Update a user."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return None

                if isinstance(user_data, dict):
                    user_data = UserUpdate(**user_data)

                # Store old expression for affected user calculation
                old_expression = user.expression if user.type == "USERGROUP" else None

                # Validate expression if updating a user group
                if hasattr(user_data, "expression") and user_data.expression:
                    is_valid, error = ExpressionParser.validate_expression(
                        user_data.expression
                    )
                    if not is_valid:
                        raise ExpressionValidationError(
                            expression=user_data.expression,
                            reason=error
                        )

                # Update fields
                for field, value in model_dump(user_data, exclude_unset=True).items():
                    setattr(user, field, value)

                session.commit()
                session.refresh(user)

                # Auto-recalculation if user group expression changed
                if user.type == "USERGROUP" and user.expression != old_expression:
                    affected_users = self._get_affected_users_for_user_change(
                        user_id, old_expression=old_expression, new_expression=user.expression
                    )
                    if affected_users:
                        self._trigger_auto_recalculation(affected_users)

                return from_orm(UserInDB, user)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to update user: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False

                # Get affected users before deletion (for user groups)
                affected_users = []
                if user.type == "USERGROUP" and user.expression:
                    affected_users = self._get_affected_users_for_user_change(
                        user_id, old_expression=user.expression, new_expression=None
                    )

                session.delete(user)
                session.commit()

                # Auto-recalculation for affected users
                if affected_users:
                    self._trigger_auto_recalculation(affected_users)

                return True

        except Exception as e:
            raise MedhaAccessError(f"Failed to delete user: {str(e)}")

    def list_users(
        self, skip: int = 0, limit: Optional[int] = None, user_type: Optional[str] = None
    ) -> List[UserInDB]:
        """List users with optional filtering."""
        try:
            with self.get_session() as session:
                query = session.query(User)

                if user_type:
                    query = query.filter(User.type == user_type)

                if limit is not None:
                    users = query.offset(skip).limit(limit).all()
                else:
                    users = query.offset(skip).all()
                return [from_orm(UserInDB, user) for user in users]

        except Exception as e:
            raise MedhaAccessError(f"Failed to list users: {str(e)}")

    # Artifact Management Methods

    def create_artifact(
        self, artifact_data: Union[ArtifactCreate, Dict]
    ) -> ArtifactInDB:
        """Create a new artifact."""
        try:
            with self.get_session() as session:
                if isinstance(artifact_data, dict):
                    artifact_data = ArtifactCreate(**artifact_data)

                # Check if artifact already exists (within application scope if configured)
                query = session.query(Artifact).filter(Artifact.id == artifact_data.id)
                if self.application_name:
                    query = query.filter(Artifact.application == self.application_name)
                existing = query.first()
                if existing:
                    raise MedhaAccessError(
                        f"Artifact with ID {artifact_data.id} already exists in application {self.application_name or 'Default'}"
                    )

                # Validate expression if it's a resource group
                if artifact_data.type == "RESOURCEGROUP" and artifact_data.expression:
                    from medha_one_access.core.expressions import ExpressionParser
                    is_valid, error = ExpressionParser.validate_expression(
                        artifact_data.expression
                    )
                    if not is_valid:
                        raise ExpressionValidationError(
                            expression=artifact_data.expression,
                            reason=error
                        )

                # Create artifact
                artifact_dict = model_dump(artifact_data)
                
                # Set application name if configured and not already set
                if self.application_name and not artifact_dict.get('application'):
                    artifact_dict['application'] = self.application_name
                
                db_artifact = Artifact(**artifact_dict)
                session.add(db_artifact)
                session.commit()
                session.refresh(db_artifact)

                # Auto-recalculation: Recalculate affected user access
                # New artifacts can affect users if they're added to existing resource groups
                affected_users = self._get_affected_users_for_artifact_change(db_artifact.id)
                if affected_users:
                    self._trigger_auto_recalculation(affected_users, db_artifact.application)

                return from_orm(ArtifactInDB, db_artifact)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to create artifact: {str(e)}")

    # Access Rule Management Methods

    def create_access_rule(
        self, rule_data: Union[AccessRuleCreate, Dict]
    ) -> AccessRuleInDB:
        """Create a new access rule."""
        try:
            with self.get_session() as session:
                if isinstance(rule_data, dict):
                    rule_data = AccessRuleCreate(**rule_data)

                # Check if access rule already exists (within application scope if configured)
                query = session.query(AccessRule).filter(AccessRule.id == rule_data.id)
                if self.application_name:
                    query = query.filter(AccessRule.application == self.application_name)
                existing = query.first()
                if existing:
                    raise MedhaAccessError(
                        f"Access rule with ID {rule_data.id} already exists in application {self.application_name or 'Default'}"
                    )

                # Validate expressions
                user_valid, user_error = ExpressionParser.validate_expression(
                    rule_data.user_expression
                )
                if not user_valid:
                    raise ExpressionValidationError(
                            expression=rule_data.user_expression,
                            reason=user_error
                        )

                resource_valid, resource_error = ExpressionParser.validate_expression(
                    rule_data.resource_expression
                )
                if not resource_valid:
                    raise ExpressionValidationError(
                        expression=rule_data.resource_expression,
                        reason=resource_error
                    )

                # Create rule
                rule_dict = model_dump(rule_data)
                
                # Set application name if configured and not already set
                if self.application_name and not rule_dict.get('application'):
                    rule_dict['application'] = self.application_name
                
                db_rule = AccessRule(**rule_dict)
                session.add(db_rule)
                session.commit()
                session.refresh(db_rule)

                # Auto-recalculation: Recalculate affected user access
                affected_users = self._get_affected_users_for_access_rule(db_rule)
                if affected_users:
                    self._trigger_auto_recalculation(affected_users, db_rule.application)

                return from_orm(AccessRuleInDB, db_rule)

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to create access rule: {str(e)}")

    # Access Resolution Methods

    def resolve_user_access(
        self, user_id: str, evaluation_time: Optional[datetime] = None, include_audit: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Resolve all access permissions for a user using BODMAS algorithm.

        Args:
            user_id: The ID of the user
            evaluation_time: Time to evaluate constraints (defaults to current time)
            include_audit: Whether to include audit trail in response (defaults to True)

        Returns:
            Dictionary containing resolved access with optional audit trail
        """
        try:
            # Use config setting if include_audit not explicitly specified
            if include_audit is None:
                include_audit = getattr(self.config, 'enable_audit_trail', True)
                
            with self.get_session() as session:
                _, bodmas_resolver = self._get_resolvers(session)
                result = bodmas_resolver.resolve_user_access(user_id, evaluation_time, include_audit)
                
                return result

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to resolve user access: {str(e)}")

    def resolve_resource_access(
        self, resource_id: str, evaluation_time: Optional[datetime] = None, include_audit: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve all users who can access a resource using BODMAS algorithm.

        Args:
            resource_id: The ID of the resource
            evaluation_time: Time to evaluate constraints (defaults to current time)
            include_audit: Whether to include audit trail in response (defaults to True)

        Returns:
            Dictionary containing users with access and optional audit trail
        """
        try:
            with self.get_session() as session:
                _, bodmas_resolver = self._get_resolvers(session)
                result = bodmas_resolver.resolve_resource_access(
                    resource_id, evaluation_time
                )
                
                # If include_audit is False, remove audit trail from response
                if not include_audit and isinstance(result, dict) and 'audit_trail' in result:
                    result = dict(result)  # Make a copy
                    del result['audit_trail']
                
                return result

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to resolve resource access: {str(e)}")

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
            user_id: The ID of the user
            resource_id: The ID of the resource
            permission: The permission to check
            evaluation_time: Time to evaluate constraints

        Returns:
            Dictionary with access decision and audit trail
        """
        try:
            with self.get_session() as session:
                _, bodmas_resolver = self._get_resolvers(session)
                return bodmas_resolver.check_access(
                    user_id, resource_id, permission, evaluation_time
                )

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to check access: {str(e)}")

    def get_resource_permissions_by_name(
        self,
        user_id: str,
        resource_name: str,
        max_cache_age_minutes: int = 60,
        include_audit: bool = False,
        force_recalculate: bool = False,
        evaluation_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get all permissions a user has for a specific resource by resource name (sync).

        Args:
            user_id: The ID of the user (required)
            resource_name: The name of the resource (required)
            max_cache_age_minutes: Maximum age of cache in minutes (default: 60)
            include_audit: Whether to include audit trail (default: False)
            force_recalculate: Skip cache and force real-time calculation (default: False)
            evaluation_time: Time to evaluate access (default: None)

        Returns:
            Dictionary containing user permissions for the specific resource
        """
        try:
            # Find the resource by name
            with self.get_session() as session:
                query = session.query(Artifact).filter(Artifact.name == resource_name)

                # Apply application filtering
                query = self._apply_application_filter(query, Artifact)

                artifact = query.first()

                if not artifact:
                    return {
                        "user_id": user_id,
                        "resource_name": resource_name,
                        "resource_id": None,
                        "permissions": [],
                        "found": False,
                        "error": f"Resource with name '{resource_name}' not found",
                        "evaluation_time": (evaluation_time or datetime.now(timezone.utc)).isoformat()
                    }

                resource_id = artifact.id

            # Get all user access using cache
            user_access = self.get_user_access(
                user_id=user_id,
                max_cache_age_minutes=max_cache_age_minutes,
                include_audit=include_audit,
                force_recalculate=force_recalculate
            )

            # Extract permissions for this specific resource
            resolved_access = user_access.get("resolved_access", {})
            permissions = resolved_access.get(resource_id, [])

            # Build response
            response = {
                "user_id": user_id,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "permissions": permissions,
                "found": True,
                "evaluation_time": user_access.get("evaluation_time"),
                "cache_info": user_access.get("cache_info", {})
            }

            if include_audit:
                response["audit_trail"] = user_access.get("audit_trail", [])

            return response

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to get resource permissions by name: {str(e)}")

    def get_user_access(
        self,
        user_id: str,
        max_cache_age_minutes: int = 60,
        include_audit: bool = False,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Get user access with cache-first logic.
        
        This method first checks for cached access summaries and returns them if fresh.
        If cache is stale, missing, or force_recalculate=True, it falls back to real-time calculation.
        
        Args:
            user_id: The ID of the user
            max_cache_age_minutes: Maximum age of cache in minutes (default: 60)
            include_audit: Whether to include audit trail (only for real-time calculation)
            force_recalculate: Skip cache and force real-time calculation
            
        Returns:
            Dictionary containing resolved access with cache metadata
        """
        try:
            cache_result = None
            used_cache = False
            
            # Check cache first (unless forced to recalculate)
            if not force_recalculate:
                cache_result = self._get_cached_user_access(user_id, max_cache_age_minutes)
                if cache_result:
                    used_cache = True
                    # Add cache metadata
                    cache_result["cache_info"] = {
                        "used_cache": True,
                        "cache_age_minutes": cache_result.get("cache_age_minutes", 0),
                        "last_calculated": cache_result.get("last_calculated"),
                        "is_stale": cache_result.get("is_stale", False)
                    }
                    return cache_result
            
            # Cache miss or forced recalculation - do real-time calculation
            real_time_result = self.resolve_user_access(
                user_id=user_id, 
                evaluation_time=None, 
                include_audit=include_audit
            )
            
            # Store in cache for future use
            self._store_user_access_cache(user_id, real_time_result)
            
            # Add cache metadata
            real_time_result["cache_info"] = {
                "used_cache": False,
                "calculated_at": datetime.now(timezone.utc).isoformat(),
                "cached_for_future": True
            }
            
            return real_time_result
            
        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to get user access: {str(e)}")

    def get_user_access_by_name(
        self,
        user_id: str,
        max_cache_age_minutes: int = 60,
        include_audit: bool = False,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Get user access with resource names instead of resource IDs (sync).

        This method wraps get_user_access() and transforms the resolved_access dictionary
        to use resource names as keys instead of resource IDs.

        Args:
            user_id: The ID of the user
            max_cache_age_minutes: Maximum age of cache in minutes (default: 60)
            include_audit: Whether to include audit trail (only for real-time calculation)
            force_recalculate: Skip cache and force real-time calculation

        Returns:
            Dictionary containing resolved access with resource names and cache metadata
        """
        try:
            # Get the standard user access (with resource IDs)
            access_result = self.get_user_access(
                user_id=user_id,
                max_cache_age_minutes=max_cache_age_minutes,
                include_audit=include_audit,
                force_recalculate=force_recalculate
            )

            resolved_access = access_result.get("resolved_access", {})

            if not resolved_access:
                # No resources, return early
                access_result["resolved_access_by_name"] = {}
                access_result["resource_name_mapping"] = {}
                return access_result

            # Get all resource IDs
            resource_ids = list(resolved_access.keys())

            # Bulk fetch artifacts to get names
            with self.get_session() as session:
                query = session.query(Artifact).filter(Artifact.id.in_(resource_ids))

                # Apply application filtering
                query = self._apply_application_filter(query, Artifact)

                artifacts = query.all()

                # Create ID to name mapping
                id_to_name = {}
                for artifact in artifacts:
                    # Use name if available, otherwise fall back to ID
                    name = artifact.name if artifact.name else artifact.id
                    id_to_name[artifact.id] = name

                # Handle missing artifacts (use ID as fallback)
                for resource_id in resource_ids:
                    if resource_id not in id_to_name:
                        id_to_name[resource_id] = f"{resource_id} (not found)"

                # Transform resolved_access to use names
                resolved_access_by_name = {}
                for resource_id, permissions in resolved_access.items():
                    resource_name = id_to_name.get(resource_id, resource_id)
                    resolved_access_by_name[resource_name] = permissions

                # Add the transformed data to result
                access_result["resolved_access_by_name"] = resolved_access_by_name
                access_result["resource_name_mapping"] = id_to_name

                return access_result

        except Exception as e:
            if isinstance(e, MedhaAccessError):
                raise
            raise MedhaAccessError(f"Failed to get user access by name: {str(e)}")

    def _get_cached_user_access(self, user_id: str, max_cache_age_minutes: int) -> Optional[Dict[str, Any]]:
        """Get cached user access if available and fresh."""
        try:
            with self.get_session() as session:
                application_name = self.application_name or "default"
                
                # Optimized query with explicit ordering for better index usage
                summary = (
                    session.query(AccessSummary)
                    .filter(
                        AccessSummary.user_id == user_id,
                        AccessSummary.application == application_name,
                        AccessSummary.is_stale == False
                    )
                    .order_by(AccessSummary.last_calculated.desc())  # Most recent first
                    .first()
                )
                
                if not summary:
                    return None
                
                # Check cache age
                if summary.last_calculated:
                    cache_age = datetime.now(timezone.utc) - summary.last_calculated
                    cache_age_minutes = cache_age.total_seconds() / 60
                    
                    if cache_age_minutes > max_cache_age_minutes:
                        # Cache is too old, mark as stale
                        summary.is_stale = True
                        session.commit()
                        return None
                else:
                    # No calculation time recorded, consider stale
                    return None
                
                # Extract data from summary
                summary_data = summary.summary_data or {}
                
                return {
                    "user_id": summary.user_id,
                    "application": summary.application,
                    "evaluation_time": datetime.now(timezone.utc).isoformat(),
                    "resolved_access": summary_data.get("resolved_access", {}),
                    "resolved_access_detailed": summary_data.get("resolved_access_detailed", {}),
                    "total_accessible_resources": summary.total_accessible_resources,
                    "cache_age_minutes": cache_age_minutes,
                    "last_calculated": summary.last_calculated.isoformat(),
                    "is_stale": summary.is_stale
                }
                
        except Exception:
            return None
    
    def _store_user_access_cache(self, user_id: str, access_result: Dict[str, Any]) -> None:
        """Store user access result in cache."""
        try:
            with self.get_session() as session:
                application_name = self.application_name or "default"
                resolved_access = access_result.get("resolved_access", {})
                
                # Create enhanced summary data
                summary_data = {
                    "resolved_access": resolved_access,
                    "resolved_access_detailed": access_result.get("resolved_access_detailed", {}),
                    "accessibleResourceIds": list(resolved_access.keys()),
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                }
                
                # Update or create summary
                summary = (
                    session.query(AccessSummary)
                    .filter(
                        AccessSummary.user_id == user_id,
                        AccessSummary.application == application_name
                    )
                    .first()
                )
                
                if summary:
                    summary.total_accessible_resources = len(resolved_access)
                    summary.summary_data = summary_data
                    summary.last_calculated = datetime.now(timezone.utc)
                    summary.is_stale = False
                else:
                    summary = AccessSummary(
                        id=f"summary_{user_id}_{application_name}",
                        user_id=user_id,
                        application=application_name,
                        total_accessible_resources=len(resolved_access),
                        total_groups=0,  # Simplified for caching
                        direct_permissions=0,  # Simplified for caching
                        inherited_permissions=0,  # Simplified for caching
                        summary_data=summary_data,
                        last_calculated=datetime.now(timezone.utc),
                        is_stale=False,
                    )
                    session.add(summary)
                
                session.commit()
                
        except Exception as e:
            # Log error but don't break the main operation
            print(f"Warning: Failed to store user access cache: {str(e)}")

    # Validation Methods

    def validate_expression(
        self, expression: str, expression_type: str = "user"
    ) -> Dict[str, Any]:
        """
        Validate an expression and return details about its structure.

        Args:
            expression: The expression to validate
            expression_type: Type of expression ("user" or "resource")

        Returns:
            Dictionary with validation results and details
        """
        try:
            # Parse and validate syntax
            is_valid, error = ExpressionParser.validate_expression(expression)

            result = {
                "valid": is_valid,
                "error": error,
                "expression": expression,
                "type": expression_type,
            }

            if is_valid:
                # Parse operations
                operations = ExpressionParser.parse_expression(expression)
                result["operations"] = operations

                # Try to resolve if database connection available
                try:
                    with self.get_session() as session:
                        expression_resolver, _ = self._get_resolvers(session)

                        if expression_type == "user":
                            resolved_ids = expression_resolver.resolve_user_expression(
                                expression
                            )
                        else:
                            resolved_ids = (
                                expression_resolver.resolve_resource_expression(
                                    expression
                                )
                            )

                        result["resolved_entities"] = list(resolved_ids)
                        result["resolved_count"] = len(resolved_ids)

                except Exception as e:
                    result["resolution_error"] = str(e)

            return result

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "expression": expression,
                "type": expression_type,
            }

    # Utility Methods

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the system."""
        try:
            with self.get_session() as session:
                # Test database connection
                from sqlalchemy import text
                session.execute(text("SELECT 1"))

                # Get some basic stats
                user_count = session.query(User).count()
                artifact_count = session.query(Artifact).count()
                rule_count = session.query(AccessRule).count()
                
                # Get cache statistics
                application_name = self.application_name or "default"
                total_summaries = session.query(AccessSummary).filter(
                    AccessSummary.application == application_name
                ).count()
                stale_summaries = session.query(AccessSummary).filter(
                    AccessSummary.application == application_name,
                    AccessSummary.is_stale == True
                ).count()
                fresh_summaries = total_summaries - stale_summaries

                return {
                    "status": "healthy",
                    "database": "connected",
                    "statistics": {
                        "users": user_count,
                        "artifacts": artifact_count,
                        "access_rules": rule_count,
                        "cache_summaries": {
                            "total": total_summaries,
                            "fresh": fresh_summaries,
                            "stale": stale_summaries,
                            "cache_hit_rate": round((fresh_summaries / total_summaries * 100) if total_summaries > 0 else 0, 2)
                        }
                    },
                    "configuration": {
                        "api_prefix": self.config.api_prefix,
                        "application_name": self.application_name,
                        "debug": self.config.debug,
                        "auto_recalculation": {
                            "enabled": getattr(self.config, 'enable_auto_recalculation', True),
                            "mode": getattr(self.config, 'auto_recalc_mode', 'immediate'),
                            "batch_size": getattr(self.config, 'auto_recalc_batch_size', 50),
                        }
                    },
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            }

    # Access Rule Management Methods

    def get_access_rule(self, rule_id: str) -> Optional[AccessRuleInDB]:
        """Get access rule by ID."""
        try:
            with self.get_session() as session:
                query = session.query(AccessRule).filter(AccessRule.id == rule_id)
                
                # Apply application filtering from config
                query = self._apply_application_filter(query, AccessRule)
                
                rule = query.first()
                if rule:
                    return from_orm(AccessRuleInDB, rule)
                return None
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url, 
                reason=f"Failed to get access rule {rule_id}: {str(e)}"
            )

    def update_access_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> AccessRuleInDB:
        """Update access rule."""
        try:
            with self.get_session() as session:
                rule = session.query(AccessRule).filter(AccessRule.id == rule_id).first()
                if not rule:
                    raise PermissionDeniedError(f"Access rule {rule_id} not found")
                
                # Get affected users before and after update
                old_affected_users = self._get_affected_users_for_access_rule(rule)
                
                # Update fields
                for key, value in rule_data.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                
                rule.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(rule)
                
                # Get new affected users and combine with old ones
                new_affected_users = self._get_affected_users_for_access_rule(rule)
                all_affected_users = list(set(old_affected_users + new_affected_users))
                
                # Auto-recalculation: Recalculate affected user access
                if all_affected_users:
                    self._trigger_auto_recalculation(all_affected_users, rule.application)
                
                return from_orm(AccessRuleInDB, rule)
        except Exception as e:
            if "not found" in str(e):
                raise
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to update access rule {rule_id}: {str(e)}"
            )

    def delete_access_rule(self, rule_id: str) -> bool:
        """Delete access rule."""
        try:
            with self.get_session() as session:
                rule = session.query(AccessRule).filter(AccessRule.id == rule_id).first()
                if not rule:
                    return False
                
                # Get affected users before deletion
                affected_users = self._get_affected_users_for_access_rule(rule)
                rule_application = rule.application
                
                session.delete(rule)
                session.commit()
                
                # Auto-recalculation: Recalculate affected user access
                if affected_users:
                    self._trigger_auto_recalculation(affected_users, rule_application)
                
                return True
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to delete access rule {rule_id}: {str(e)}"
            )

    def list_access_rules(
        self,
        user_expression: Optional[str] = None,
        resource_expression: Optional[str] = None,
        application: Optional[str] = None,
        active: Optional[bool] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[AccessRuleInDB]:
        """List access rules with filtering."""
        try:
            with self.get_session() as session:
                query = session.query(AccessRule)
                
                # Apply application filtering from config
                query = self._apply_application_filter(query, AccessRule)
                
                # Apply filters
                if user_expression:
                    query = query.filter(AccessRule.user_expression.ilike(f"%{user_expression}%"))
                if resource_expression:
                    query = query.filter(AccessRule.resource_expression.ilike(f"%{resource_expression}%"))
                if application:
                    query = query.filter(AccessRule.application == application)
                if active is not None:
                    query = query.filter(AccessRule.active == active)
                
                # Apply pagination
                if limit is not None:
                    rules = query.offset(skip).limit(limit).all()
                else:
                    rules = query.offset(skip).all()
                return [from_orm(AccessRuleInDB, rule) for rule in rules]
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to list access rules: {str(e)}"
            )

    # Artifact Management Methods

    def get_artifact(self, artifact_id: str) -> Optional[ArtifactInDB]:
        """Get artifact by ID."""
        try:
            with self.get_session() as session:
                query = session.query(Artifact).filter(Artifact.id == artifact_id)
                
                # Apply application filtering from config
                query = self._apply_application_filter(query, Artifact)
                
                artifact = query.first()
                if artifact:
                    return from_orm(ArtifactInDB, artifact)
                return None
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to get artifact {artifact_id}: {str(e)}"
            )

    def update_artifact(self, artifact_id: str, artifact_data: Dict[str, Any]) -> ArtifactInDB:
        """Update artifact."""
        try:
            with self.get_session() as session:
                artifact = session.query(Artifact).filter(Artifact.id == artifact_id).first()
                if not artifact:
                    raise PermissionDeniedError(f"Artifact {artifact_id} not found")
                
                # Get affected users before update (especially for expression changes)
                old_artifact = artifact
                affected_users = self._get_affected_users_for_artifact_change(artifact_id, old_artifact)
                
                # Update fields
                for key, value in artifact_data.items():
                    if hasattr(artifact, key):
                        setattr(artifact, key, value)
                
                artifact.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(artifact)

                # CRITICAL FIX: Expire all objects in session to force fresh queries
                # This ensures _get_affected_users_for_artifact_change() reads the updated
                # RESOURCEGROUP expressions from database, not from SQLAlchemy's identity map
                session.expire_all()

                # Auto-recalculation: Recalculate affected user access
                # Include users affected by both old and new artifact state
                new_affected_users = self._get_affected_users_for_artifact_change(artifact_id)
                all_affected_users = list(set(affected_users + new_affected_users))
                if all_affected_users:
                    # CRITICAL FIX: Mark summaries as stale IMMEDIATELY before background recalculation
                    # This ensures get_user_access() won't return stale cached data
                    self._mark_summaries_stale(all_affected_users, artifact.application)

                    # Then trigger background recalculation to update the cache
                    self._trigger_auto_recalculation(all_affected_users, artifact.application)
                
                return from_orm(ArtifactInDB, artifact)
        except Exception as e:
            if "not found" in str(e):
                raise
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to update artifact {artifact_id}: {str(e)}"
            )

    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete artifact."""
        try:
            with self.get_session() as session:
                artifact = session.query(Artifact).filter(Artifact.id == artifact_id).first()
                if not artifact:
                    return False
                
                # Get affected users before deletion
                affected_users = self._get_affected_users_for_artifact_change(artifact_id, artifact)
                artifact_application = artifact.application
                
                session.delete(artifact)
                session.commit()
                
                # Auto-recalculation: Recalculate affected user access
                if affected_users:
                    self._trigger_auto_recalculation(affected_users, artifact_application)
                
                return True
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to delete artifact {artifact_id}: {str(e)}"
            )

    def list_artifacts(
        self, 
        skip: int = 0, 
        limit: Optional[int] = None,
        artifact_type: Optional[str] = None,
        application: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> List[ArtifactInDB]:
        """List artifacts with filtering and pagination."""
        try:
            with self.get_session() as session:
                query = session.query(Artifact)
                
                # Apply application filtering from config
                query = self._apply_application_filter(query, Artifact)
                
                # Apply filters
                if artifact_type:
                    query = query.filter(Artifact.type == artifact_type)
                if application:
                    query = query.filter(Artifact.application == application)
                if active is not None:
                    query = query.filter(Artifact.active == active)
                
                # Apply pagination
                if limit is not None:
                    artifacts = query.offset(skip).limit(limit).all()
                else:
                    artifacts = query.offset(skip).all()
                return [from_orm(ArtifactInDB, artifact) for artifact in artifacts]
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to list artifacts: {str(e)}"
            )

    # Access Summary Methods

    def get_access_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get access summary for a user (application-scoped)."""
        try:
            with self.get_session() as session:
                application_name = self.application_name or "default"
                
                summary = (
                    session.query(AccessSummary)
                    .filter(
                        AccessSummary.user_id == user_id,
                        AccessSummary.application == application_name
                    )
                    .first()
                )
                if summary:
                    # Extract detailed permissions from summary_data
                    summary_data = summary.summary_data or {}
                    return {
                        "user_id": summary.user_id,
                        "application": summary.application,
                        "resolved_access": summary_data.get("resolved_access", {}),
                        "resolved_access_detailed": summary_data.get("resolved_access_detailed", {}),
                        "audit_trail": summary_data.get("calculationDetails", {}).get("auditTrail", []),
                        "last_calculated": summary.last_calculated.isoformat() if summary.last_calculated else None,
                        "is_stale": summary.is_stale,
                        "total_accessible_resources": summary.total_accessible_resources,
                    }
                return None
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to get access summary for {user_id}: {str(e)}"
            )

    # User Group Methods

    def get_user_groups(self, user_id: str) -> Optional[List[UserInDB]]:
        """Get groups that a user belongs to."""
        try:
            with self.get_session() as session:
                
                # Check if user exists
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    print(f"DEBUG: User {user_id} not found in database")
                    return None
                
                
                # Get all user groups where this user appears in the expression
                groups = session.query(User).filter(
                    User.type == "USERGROUP",
                    User.active == True
                ).all()
                
                
                user_groups = []
                for group in groups:
                    if group.expression:
                        # Parse the expression to see if this user is included
                        expression_resolver, _ = self._get_resolvers(session)
                        try:
                            # Use the correct method name for user expressions
                            resolved_users = expression_resolver.resolve_user_expression(
                                group.expression
                            )
                            if user_id in resolved_users:
                                user_groups.append(from_orm(UserInDB, group))
                        except Exception as e:
                            print(f"DEBUG: Error resolving expression for group {group.id}: {str(e)}")
                            # Skip groups with invalid expressions
                            continue
                    else:
                        print(f"DEBUG: Group {group.id} has no expression")
                
                return user_groups
        except Exception as e:
            print(f"DEBUG: Exception in get_user_groups: {str(e)}")
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to get user groups for {user_id}: {str(e)}"
            )

    def get_artifact_groups(self, artifact_id: str) -> Optional[List[str]]:
        """Get resource groups that an artifact belongs to."""
        try:
            with self.get_session() as session:
                # Check if artifact exists
                artifact = session.query(Artifact).filter(Artifact.id == artifact_id).first()
                if not artifact:
                    return None
                
                # Get all resource groups where this artifact appears in the expression
                groups = session.query(Artifact).filter(
                    Artifact.type == "RESOURCEGROUP",
                    Artifact.active == True
                ).all()
                
                artifact_groups = []
                for group in groups:
                    if group.expression:
                        # Parse the expression to see if this artifact is included
                        expression_resolver, _ = self._get_resolvers(session)
                        try:
                            resolved_artifacts = expression_resolver.resolve_expression(
                                group.expression, "resource", session
                            )
                            if artifact_id in resolved_artifacts:
                                artifact_groups.append(group.id)
                        except Exception:
                            # Skip groups with invalid expressions
                            continue
                
                return artifact_groups
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to get artifact groups for {artifact_id}: {str(e)}"
            )

    def get_usergroup_members(self, group_id: str) -> Optional[List[UserInDB]]:
        """Get members of a user group."""
        try:
            with self.get_session() as session:
                # Check if group exists
                group = session.query(User).filter(
                    User.id == group_id, 
                    User.type == "USERGROUP"
                ).first()
                if not group:
                    return None
                
                if not group.expression:
                    return []
                
                # Parse the expression to get members
                expression_resolver, _ = self._get_resolvers(session)
                try:
                    resolved_users = expression_resolver.resolve_user_expression(
                        group.expression
                    )
                    
                    # Get full user objects
                    members = []
                    for user_id in resolved_users:
                        user = session.query(User).filter(User.id == user_id).first()
                        if user:
                            members.append(from_orm(UserInDB, user))
                    
                    return members
                except Exception:
                    return []
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to get usergroup members for {group_id}: {str(e)}"
            )

    def get_resourcegroup_contents(self, group_id: str) -> Optional[List[ArtifactInDB]]:
        """Get contents of a resource group."""
        try:
            with self.get_session() as session:
                # Check if group exists
                group = session.query(Artifact).filter(
                    Artifact.id == group_id,
                    Artifact.type == "RESOURCEGROUP"
                ).first()
                if not group:
                    return None
                
                if not group.expression:
                    return []
                
                # Parse the expression to get contents
                expression_resolver, _ = self._get_resolvers(session)
                try:
                    resolved_artifacts = expression_resolver.resolve_expression(
                        group.expression, "resource", session
                    )
                    
                    # Get full artifact objects
                    contents = []
                    for artifact_id in resolved_artifacts:
                        artifact = session.query(Artifact).filter(Artifact.id == artifact_id).first()
                        if artifact:
                            contents.append(from_orm(ArtifactInDB, artifact))
                    
                    return contents
                except Exception:
                    return []
        except Exception as e:
            raise DatabaseConnectionError(
                database_url=self.config.database_url,
                reason=f"Failed to get resourcegroup contents for {group_id}: {str(e)}"
            )

    # Auto-Recalculation Helper Methods

    def _get_affected_users_for_access_rule(self, rule: AccessRule) -> List[str]:
        """Get list of users affected by an access rule change."""
        try:
            with self.get_session() as session:
                expression_resolver, _ = self._get_resolvers(session)
                # Resolve user expression to get affected user IDs
                affected_users = expression_resolver.resolve_user_expression(rule.user_expression)
                return list(affected_users)
        except Exception:
            return []

    def _get_affected_users_for_artifact_change(self, artifact_id: str, old_artifact: Optional[Artifact] = None) -> List[str]:
        """Get list of users affected by artifact creation/update/deletion."""
        try:
            with self.get_session() as session:
                affected_users = set()
                
                # Find all resource groups that might include this artifact
                resource_groups = session.query(Artifact).filter(
                    Artifact.type == "RESOURCEGROUP",
                    Artifact.active == True
                ).all()
                
                expression_resolver, _ = self._get_resolvers(session)
                
                # Check each resource group to see if it includes this artifact
                for group in resource_groups:
                    if group.expression:
                        try:
                            resolved_artifacts = expression_resolver.resolve_resource_expression(group.expression)
                            if artifact_id in resolved_artifacts:
                                # Find users with access to this resource group
                                group_rules = session.query(AccessRule).filter(
                                    AccessRule.resource_expression.contains(group.id),
                                    AccessRule.active == True
                                ).all()
                                
                                for rule in group_rules:
                                    rule_users = expression_resolver.resolve_user_expression(rule.user_expression)
                                    affected_users.update(rule_users)
                        except Exception:
                            continue
                
                # Also check direct rules targeting this artifact
                direct_rules = session.query(AccessRule).filter(
                    AccessRule.resource_expression.contains(artifact_id),
                    AccessRule.active == True
                ).all()
                
                for rule in direct_rules:
                    try:
                        rule_users = expression_resolver.resolve_user_expression(rule.user_expression)
                        affected_users.update(rule_users)
                    except Exception:
                        continue
                        
                return list(affected_users)
        except Exception:
            return []

    def _get_affected_users_for_user_change(self, user_id: str, old_expression: Optional[str] = None, new_expression: Optional[str] = None) -> List[str]:
        """Get list of users affected by user/usergroup changes."""
        try:
            with self.get_session() as session:
                affected_users = set([user_id])  # Always include the changed user
                
                expression_resolver, _ = self._get_resolvers(session)
                
                # If this was a user group, get members from old and new expressions
                if old_expression:
                    try:
                        old_members = expression_resolver.resolve_user_expression(old_expression)
                        affected_users.update(old_members)
                    except Exception:
                        pass
                        
                if new_expression:
                    try:
                        new_members = expression_resolver.resolve_user_expression(new_expression)
                        affected_users.update(new_members)
                    except Exception:
                        pass
                
                return list(affected_users)
        except Exception:
            return [user_id]

    def _mark_summaries_stale(self, user_ids: List[str], application: Optional[str] = None) -> None:
        """Mark access summaries as stale for the given users."""
        if not user_ids:
            return
            
        try:
            with self.get_session() as session:
                application_name = application or self.application_name or "default"
                
                # Mark summaries as stale
                session.query(AccessSummary).filter(
                    AccessSummary.user_id.in_(user_ids),
                    AccessSummary.application == application_name
                ).update(
                    {"is_stale": True, "updated_at": datetime.now(timezone.utc)},
                    synchronize_session=False
                )
                session.commit()
        except Exception as e:
            # Log error but don't break the main operation
            print(f"Warning: Failed to mark summaries as stale: {str(e)}")

    def _trigger_auto_recalculation(self, user_ids: List[str], application: Optional[str] = None) -> None:
        """
        Trigger auto-recalculation based on configuration settings.
        
        Args:
            user_ids: List of user IDs to recalculate
            application: Application name (optional, uses config default)
        """
        if not user_ids or not getattr(self.config, 'enable_auto_recalculation', True):
            return
            
        mode = getattr(self.config, 'auto_recalc_mode', 'immediate')
        
        try:
            if mode == 'immediate':
                # Submit to background thread and return immediately
                app_name = application or self.application_name or 'default'
                print(f"INFO: Submitting background recalculation for {len(user_ids)} users in application '{app_name}'")
                
                # Submit task to background thread pool
                future = self._background_executor.submit(
                    self._recalculate_user_summaries_with_logging, 
                    user_ids, 
                    application
                )
                
                # Track the task with a unique ID for monitoring
                import uuid
                task_id = f"recalc_{uuid.uuid4().hex[:8]}"
                self._background_tasks[task_id] = future
                
                # Clean up completed tasks (optional cleanup)
                self._cleanup_completed_tasks()
                
                print(f"INFO: Background recalculation task {task_id} submitted successfully")
                
            elif mode == 'batched':
                # Background batched recalculation
                batch_size = getattr(self.config, 'auto_recalc_batch_size', 50)
                batch_users = user_ids[:batch_size]
                app_name = application or self.application_name or 'default'
                print(f"INFO: Submitting background batch recalculation for {len(batch_users)} users in application '{app_name}'")
                
                # Submit batch to background thread pool
                future = self._background_executor.submit(
                    self._recalculate_user_summaries_with_logging, 
                    batch_users, 
                    application
                )
                
                # Track the task
                import uuid
                task_id = f"batch_recalc_{uuid.uuid4().hex[:8]}"
                self._background_tasks[task_id] = future
                
                # Handle remaining users - mark as stale for later processing
                if len(user_ids) > batch_size:
                    print(f"INFO: Batch processing {len(batch_users)} of {len(user_ids)} users. Remaining users marked as stale.")
                    self._mark_summaries_stale(user_ids[batch_size:], application)
                
                self._cleanup_completed_tasks()
                print(f"INFO: Background batch recalculation task {task_id} submitted successfully")
            # If mode == 'disabled', do nothing
                
        except Exception as e:
            # Log error but don't break the main operation
            print(f"ERROR: Auto-recalculation failed: {str(e)}")
            # Fall back to marking as stale
            self._mark_summaries_stale(user_ids, application)

    def _recalculate_user_summaries(self, user_ids: List[str], application: Optional[str] = None) -> None:
        """Recalculate access summaries for the given users."""
        if not user_ids:
            return
            
        application_name = application or self.application_name or "default"
        
        for user_id in user_ids:
            try:
                # Use the same logic as the calculate endpoint
                with self.get_session() as session:
                    # Check if user exists and is active
                    user = session.query(User).filter(
                        User.id == user_id, 
                        User.active == True
                    ).first()
                    if not user:
                        continue
                    
                    # Get resolvers and calculate access
                    _, bodmas_resolver = self._get_resolvers(session)
                    user_access = bodmas_resolver.resolve_user_access(user_id, include_audit=False)
                    
                    # Extract data
                    resolved_access = user_access.get("resolved_access", {})
                    
                    # Create enhanced summary data
                    summary_data = {
                        "resolved_access": resolved_access,
                        "resolved_access_detailed": user_access.get("resolved_access_detailed", {}),
                        "accessibleResourceIds": list(resolved_access.keys()),
                        "last_auto_calculated": datetime.now(timezone.utc).isoformat(),
                    }
                    
                    # Update or create summary
                    db_summary = session.query(AccessSummary).filter(
                        AccessSummary.user_id == user_id,
                        AccessSummary.application == application_name
                    ).first()
                    
                    if db_summary:
                        db_summary.total_accessible_resources = len(resolved_access)
                        db_summary.summary_data = summary_data
                        db_summary.last_calculated = datetime.now(timezone.utc)
                        db_summary.is_stale = False
                    else:
                        db_summary = AccessSummary(
                            id=f"summary_{user_id}_{application_name}",
                            user_id=user_id,
                            application=application_name,
                            total_accessible_resources=len(resolved_access),
                            total_groups=0,  # Simplified for auto-calculation
                            direct_permissions=0,  # Simplified for auto-calculation
                            inherited_permissions=0,  # Simplified for auto-calculation
                            summary_data=summary_data,
                            last_calculated=datetime.now(timezone.utc),
                            is_stale=False,
                        )
                        session.add(db_summary)
                    
                    session.commit()
                    
            except Exception as e:
                # Log error but continue with other users
                print(f"Warning: Failed to recalculate summary for user {user_id}: {str(e)}")
                continue

    def get_background_task_count(self) -> int:
        """Get the number of active background tasks."""
        if not hasattr(self, '_background_tasks'):
            return 0
        return len(self._background_tasks)

    def get_background_task_status(self) -> Dict[str, Any]:
        """Get status information about background tasks."""
        if not hasattr(self, '_background_tasks'):
            return {
                "total_tasks": 0,
                "running_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "tasks": []
            }
        
        running = 0
        completed = 0
        failed = 0
        task_details = []
        
        for task_id, future in self._background_tasks.items():
            if future.done():
                try:
                    future.result()  # Check if it completed successfully
                    completed += 1
                    status = "completed"
                except Exception as e:
                    failed += 1
                    status = f"failed: {str(e)}"
            else:
                running += 1
                status = "running"
            
            task_details.append({
                "task_id": task_id,
                "status": status
            })
        
        return {
            "total_tasks": len(self._background_tasks),
            "running_tasks": running,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "tasks": task_details
        }

    def wait_for_background_tasks(self, timeout: Optional[float] = None) -> bool:
        """Wait for all background tasks to complete. Returns True if all completed, False if timeout."""
        if not hasattr(self, '_background_tasks') or not self._background_tasks:
            return True
            
        from concurrent.futures import as_completed
        
        try:
            # Wait for all futures to complete
            list(as_completed(self._background_tasks.values(), timeout=timeout))
            return True
        except TimeoutError:
            return False

    def _recalculate_user_summaries_with_logging(self, user_ids: List[str], application: Optional[str] = None) -> None:
        """Wrapper for _recalculate_user_summaries with enhanced logging for background execution."""
        app_name = application or self.application_name or "default"
        start_time = datetime.now(timezone.utc)
        
        try:
            print(f"INFO: Starting background recalculation for {len(user_ids)} users in application '{app_name}'")
            self._recalculate_user_summaries(user_ids, application)
            
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            print(f"INFO: Background recalculation completed successfully for {len(user_ids)} users in {elapsed:.2f}s")
            
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            print(f"ERROR: Background recalculation failed after {elapsed:.2f}s for {len(user_ids)} users: {str(e)}")
            
            # Fall back to marking as stale
            try:
                self._mark_summaries_stale(user_ids, application)
                print(f"INFO: Marked {len(user_ids)} user summaries as stale as fallback")
            except Exception as fallback_error:
                print(f"ERROR: Failed to mark summaries as stale: {str(fallback_error)}")
            
            raise  # Re-raise for Future.result() to capture

    def _cleanup_completed_tasks(self) -> None:
        """Remove completed background tasks from tracking."""
        if not hasattr(self, '_background_tasks'):
            return
            
        completed_tasks = []
        for task_id, future in self._background_tasks.items():
            if future.done():
                completed_tasks.append(task_id)
                
        for task_id in completed_tasks:
            del self._background_tasks[task_id]
            
        if completed_tasks:
            print(f"DEBUG: Cleaned up {len(completed_tasks)} completed background tasks")


# Export both sync and async controllers
__all__ = [
    "AsyncAccessController",  # New async controller
    "AccessController",       # Legacy sync controller
]
