"""
FastAPI Dependencies for MedhaOne Access Control

Provides dependency injection for FastAPI route handlers.
Supports both standalone app usage and mounted route usage.
"""

from typing import Annotated, Optional, Dict, Callable
from fastapi import Depends

from medha_one_access.core.controller import AccessController


# Global registry for mounted controllers
_mounted_controllers: Dict[str, AccessController] = {}


def get_controller() -> AccessController:
    """
    Get the access controller instance.

    This works in two modes:
    1. Standalone app mode: Uses global controller from app.py
    2. Mounted route mode: Controller is injected via dependency override
    """
    # Try to get from app.py global controller (for backward compatibility)
    try:
        from medha_one_access.api.app import get_global_controller

        return get_global_controller()
    except (ImportError, RuntimeError):
        # If global controller not available, this will be overridden
        # by the mount function's dependency injection
        raise RuntimeError(
            "Controller not available. Use mount_access_control_routes() to set up dependencies."
        )


def create_controller_dependency(
    controller: AccessController,
) -> Callable[[], AccessController]:
    """
    Create a dependency function for a specific controller instance.

    Args:
        controller: The controller instance to use

    Returns:
        Dependency function that returns the controller
    """

    def controller_dependency() -> AccessController:
        return controller

    return controller_dependency


def register_controller(app_id: str, controller: AccessController) -> None:
    """
    Register a controller for a specific app ID.

    Args:
        app_id: Unique identifier for the app
        controller: Controller instance to register
    """
    _mounted_controllers[app_id] = controller


def get_registered_controller(app_id: str) -> Optional[AccessController]:
    """
    Get a registered controller by app ID.

    Args:
        app_id: App identifier

    Returns:
        Controller instance if found, None otherwise
    """
    return _mounted_controllers.get(app_id)


# Create a proper dependency function that doesn't interfere with response validation
def get_controller_dependency():
    """Get controller dependency for FastAPI route injection"""
    return Depends(get_controller)

# Note: We no longer export ControllerDep to avoid Pydantic validation conflicts
# Use: controller: AccessController = Depends(get_controller) in route functions
