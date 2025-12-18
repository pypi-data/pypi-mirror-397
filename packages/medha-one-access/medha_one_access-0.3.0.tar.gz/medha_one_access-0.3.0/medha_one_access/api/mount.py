"""
FastAPI Route Mount Function for MedhaOne Access Control

This module provides the main integration function for mounting access control routes
into an existing FastAPI application.
"""

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute

from medha_one_access.core.config import LibraryConfig
from medha_one_access.core.controller import AccessController
from medha_one_access.core.exceptions import MedhaAccessError


def mount_access_control_routes(
    app: FastAPI,
    config: LibraryConfig,
    controller: Optional[AccessController] = None,
    include_routers: Optional[List[str]] = None,
    add_exception_handlers: bool = True,
) -> AccessController:
    """
    Mount all access control routes into an existing FastAPI application.

    This function adds all MedhaOne Access Control API endpoints to your existing
    FastAPI application using your preferred API prefix.

    Args:
        app: User's existing FastAPI application
        config: Library configuration with api_prefix, database_url, secret_key
        controller: Optional pre-created controller (creates new if None)
        include_routers: Optional list of router names to include (includes all if None)
        add_exception_handlers: Whether to add MedhaOne exception handlers

    Returns:
        AccessController instance for optional direct usage

    Example:
        ```python
        from fastapi import FastAPI
        from medha_one_access import LibraryConfig, mount_access_control_routes

        app = FastAPI()

        controller = mount_access_control_routes(app, LibraryConfig(
            database_url="postgresql://user:pass@host/db",
            secret_key="your_secret_key",
            api_prefix="/oneAccess"
        ))

        # Now your app has all these endpoints:
        # GET  /oneAccess/users
        # POST /oneAccess/users
        # GET  /oneAccess/artifacts
        # POST /oneAccess/access/check
        # ... and many more
        ```
    """

    # Create controller if not provided
    if controller is None:
        controller = AccessController(config)

    # Create controller dependency function
    def get_controller() -> AccessController:
        return controller

    # Add exception handlers if requested
    if add_exception_handlers:
        _add_exception_handlers(app)

    # Import all available routers
    from medha_one_access.api.routers import (
        users,
        artifacts,
        access_rules,
        access_check,
        usergroups,
        resourcegroups,
        expressions,
    )

    # Define available routers
    available_routers = {
        "users": (users.router, "/users", ["Users"]),
        "artifacts": (artifacts.router, "/artifacts", ["Artifacts"]),
        "access_rules": (access_rules.router, "/access-rules", ["Access Rules"]),
        "access_check": (access_check.router, "/access", ["Access Control"]),
        "usergroups": (usergroups.router, "/usergroups", ["User Groups"]),
        "resourcegroups": (resourcegroups.router, "/resourcegroups", ["Resource Groups"]),
        "expressions": (expressions.router, "/expressions", ["Expression Validation"]),
    }

    # Try to import optional routers (they might not exist yet)
    try:
        from medha_one_access.api.routers import access_summary

        available_routers["access_summary"] = (
            access_summary.router,
            "/access-summary",
            ["Access Summary"],
        )
    except ImportError:
        pass

    try:
        from medha_one_access.api.routers import reporting

        available_routers["reporting"] = (reporting.router, "/reporting", ["Reporting"])
    except ImportError:
        pass

    try:
        from medha_one_access.api.routers import data_io

        available_routers["data_io"] = (
            data_io.router,
            "/data-io",
            ["Data Import/Export"],
        )
    except ImportError:
        pass

    # Determine which routers to include
    if include_routers is None:
        routers_to_include = available_routers.keys()
    else:
        routers_to_include = [
            name for name in include_routers if name in available_routers
        ]

    # Override the get_controller dependency for all routers
    from medha_one_access.api.dependencies import get_controller as original_get_controller
    app.dependency_overrides[original_get_controller] = get_controller
    
    # Mount each router with custom prefix
    for router_name in routers_to_include:
        router, path_suffix, tags = available_routers[router_name]

        app.include_router(
            router, prefix=f"{config.api_prefix}{path_suffix}", tags=tags
        )

    # Add health check endpoint if not already present
    _add_health_check(app, controller, config.api_prefix)

    return controller


async def mount_async_access_control_routes(
    app: FastAPI,
    config: LibraryConfig,
    controller: Optional['AsyncAccessController'] = None,
    include_routers: Optional[List[str]] = None,
    add_exception_handlers: bool = True,
) -> 'AsyncAccessController':
    """
    Mount all access control routes into an existing FastAPI application with async controller support.

    This function adds all MedhaOne Access Control API endpoints to your existing
    FastAPI application using async controller methods for better performance.

    Args:
        app: User's existing FastAPI application
        config: Library configuration with api_prefix, database_url, secret_key
        controller: Optional pre-created async controller (creates new if None)
        include_routers: Optional list of router names to include (includes all if None)
        add_exception_handlers: Whether to add MedhaOne exception handlers

    Returns:
        AsyncAccessController instance for optional direct usage

    Example:
        ```python
        from fastapi import FastAPI
        from medha_one_access import LibraryConfig, mount_async_access_control_routes

        app = FastAPI()

        # Note: This function is async and must be awaited
        async_controller = await mount_async_access_control_routes(app, LibraryConfig(
            database_url="postgresql://user:pass@host/db",
            secret_key="your_secret_key",
            api_prefix="/oneAccess"
        ))

        # Now you can use async methods:
        @app.get("/my-endpoint")
        async def my_endpoint():
            access = await async_controller.get_user_access("user123")
            return access
        ```
    """
    from medha_one_access.core.controller import AsyncAccessController

    # Create async controller if not provided
    if controller is None:
        controller = AsyncAccessController(config)
    
    # Initialize the async controller's database connection if not already initialized
    if not hasattr(controller, '_session_manager') or controller._session_manager is None:
        await controller.initialize()

    # Create async controller dependency function
    def get_async_controller() -> AsyncAccessController:
        return controller

    # Add exception handlers if requested
    if add_exception_handlers:
        _add_exception_handlers(app)

    # Import all available routers
    from medha_one_access.api.routers import (
        users,
        artifacts,
        access_rules,
        access_check,
        usergroups,
        resourcegroups,
        expressions,
    )

    # Define available routers
    available_routers = {
        "users": (users.router, "/users", ["Users"]),
        "artifacts": (artifacts.router, "/artifacts", ["Artifacts"]),
        "access_rules": (access_rules.router, "/access-rules", ["Access Rules"]),
        "access_check": (access_check.router, "/access", ["Access Control"]),
        "usergroups": (usergroups.router, "/usergroups", ["User Groups"]),
        "resourcegroups": (resourcegroups.router, "/resourcegroups", ["Resource Groups"]),
        "expressions": (expressions.router, "/expressions", ["Expression Validation"]),
    }

    # Try to import optional routers (they might not exist yet)
    try:
        from medha_one_access.api.routers import access_summary

        available_routers["access_summary"] = (
            access_summary.router,
            "/access-summary",
            ["Access Summary"],
        )
    except ImportError:
        pass

    try:
        from medha_one_access.api.routers import reporting

        available_routers["reporting"] = (reporting.router, "/reporting", ["Reporting"])
    except ImportError:
        pass

    try:
        from medha_one_access.api.routers import data_io

        available_routers["data_io"] = (
            data_io.router,
            "/data-io",
            ["Data Import/Export"],
        )
    except ImportError:
        pass

    # Determine which routers to include
    if include_routers is None:
        routers_to_include = available_routers.keys()
    else:
        routers_to_include = [
            name for name in include_routers if name in available_routers
        ]

    # Override the get_controller dependency for all routers to use async controller
    from medha_one_access.api.dependencies import get_controller as original_get_controller
    
    # Note: This creates a wrapper that makes the async controller compatible with sync dependency injection
    # The routes themselves will still be async-compatible
    def sync_wrapper() -> AccessController:
        # Return the async controller but cast it for dependency injection compatibility
        # The actual route handlers will determine whether to use sync or async methods
        return controller
    
    app.dependency_overrides[original_get_controller] = sync_wrapper
    
    # Mount each router with custom prefix
    for router_name in routers_to_include:
        router, path_suffix, tags = available_routers[router_name]

        app.include_router(
            router, prefix=f"{config.api_prefix}{path_suffix}", tags=tags
        )

    # Add async health check endpoint
    _add_async_health_check(app, controller, config.api_prefix)

    return controller


def _add_exception_handlers(app: FastAPI):
    """Add MedhaOne exception handlers to the FastAPI app."""
    from fastapi.responses import JSONResponse
    from fastapi import Request

    @app.exception_handler(MedhaAccessError)
    async def medha_access_exception_handler(request: Request, exc: MedhaAccessError):
        # Determine appropriate status code based on error type
        status_code = 400
        if "already exists" in str(exc):
            status_code = 409  # Conflict
        elif "not found" in str(exc).lower():
            status_code = 404  # Not Found
        elif "permission denied" in str(exc).lower():
            status_code = 403  # Forbidden
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": exc.__class__.__name__,
                "message": str(exc),
                "details": getattr(exc, "details", {}),
            },
        )


def _add_health_check(app: FastAPI, controller: AccessController, api_prefix: str):
    """Add a health check endpoint for the access control system."""

    @app.get(f"{api_prefix}/health")
    async def access_control_health():
        """Health check endpoint for MedhaOne Access Control."""
        try:
            health_result = controller.health_check()
            return health_result
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "component": "access_control",
            }


def _add_async_health_check(app: FastAPI, controller: 'AsyncAccessController', api_prefix: str):
    """Add an async health check endpoint for the access control system."""

    @app.get(f"{api_prefix}/health")
    async def access_control_health():
        """Async health check endpoint for MedhaOne Access Control."""
        try:
            # Use async health check if available, otherwise fall back to sync
            if hasattr(controller, 'health_check') and hasattr(controller.health_check, '__await__'):
                health_result = await controller.health_check()
            else:
                # Fallback to sync method
                health_result = controller.health_check()
            return health_result
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "component": "access_control",
            }


def get_mounted_routers(config: LibraryConfig) -> Dict[str, str]:
    """
    Get information about available routers and their mount paths.

    Args:
        config: Library configuration

    Returns:
        Dictionary mapping router names to their full mount paths
    """
    routers = {
        "users": f"{config.api_prefix}/users",
        "artifacts": f"{config.api_prefix}/artifacts",
        "access_rules": f"{config.api_prefix}/access-rules",
        "access_check": f"{config.api_prefix}/access",
        "usergroups": f"{config.api_prefix}/usergroups",
        "resourcegroups": f"{config.api_prefix}/resourcegroups",
        "expressions": f"{config.api_prefix}/expressions",
        "health": f"{config.api_prefix}/health",
    }

    # Add optional routers
    optional_routers = ["access_summary", "reporting", "data_io"]
    for router_name in optional_routers:
        try:
            # Try to import to see if it exists
            exec(f"from medha_one_access.api.routers import {router_name}")
            path_mapping = {
                "access_summary": "/access-summary",
                "reporting": "/reporting",
                "data_io": "/data-io",
            }
            routers[router_name] = f"{config.api_prefix}{path_mapping[router_name]}"
        except ImportError:
            continue

    return routers
