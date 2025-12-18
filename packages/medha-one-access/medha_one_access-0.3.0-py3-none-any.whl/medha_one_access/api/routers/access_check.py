"""
Access Control API Routes

FastAPI routes for access resolution and permission checking.
"""

from typing import Optional
from datetime import datetime
import inspect

from fastapi import APIRouter, Query, Path, Depends
from pydantic import BaseModel

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import AccessResolutionResponse, AccessCheckResponse

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


class AccessCheckRequest(BaseModel):
    """Request model for access checking."""

    user_id: str
    resource_id: str
    permission: str
    evaluation_time: Optional[datetime] = None


@router.get("/resolve/{user_id}", response_model=AccessResolutionResponse)
async def resolve_user_access(
    user_id: str = Path(..., description="User ID"),
    evaluation_time: Optional[datetime] = Query(
        None, description="Time to evaluate access (ISO format)"
    ),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    controller: AccessController = Depends(get_controller),
):
    """Resolve all access permissions for a user using BODMAS methodology."""
    return await _await_if_needed(controller.resolve_user_access(
        user_id=user_id, evaluation_time=evaluation_time, include_audit=include_audit
    ))


@router.post("/check", response_model=AccessCheckResponse)
async def check_access(request: AccessCheckRequest, controller: AccessController = Depends(get_controller)):
    """Check if a user has a specific permission on a resource."""
    return await _await_if_needed(controller.check_access(
        user_id=request.user_id,
        resource_id=request.resource_id,
        permission=request.permission,
        evaluation_time=request.evaluation_time,
    ))


@router.get(
    "/check/{user_id}/{resource_id}/{permission}", response_model=AccessCheckResponse
)
async def check_access_get(
    user_id: str = Path(..., description="User ID"),
    resource_id: str = Path(..., description="Resource ID"),
    permission: str = Path(..., description="Permission to check"),
    evaluation_time: Optional[datetime] = Query(
        None, description="Time to evaluate access (ISO format)"
    ),
    controller: AccessController = Depends(get_controller),
):
    """Check if a user has a specific permission on a resource (GET version)."""
    return await _await_if_needed(controller.check_access(
        user_id=user_id,
        resource_id=resource_id,
        permission=permission,
        evaluation_time=evaluation_time,
    ))


@router.get("/user/{user_id}", response_model=AccessResolutionResponse)
async def get_user_access(
    user_id: str = Path(..., description="User ID"),
    evaluation_time: Optional[datetime] = Query(
        None, description="Time to evaluate access (ISO format)"
    ),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    controller: AccessController = Depends(get_controller),
):
    """Get all access permissions for a user (alias for resolve_user_access)."""
    return await _await_if_needed(controller.resolve_user_access(
        user_id=user_id, evaluation_time=evaluation_time, include_audit=include_audit
    ))


@router.get("/user/{user_id}/cached", response_model=AccessResolutionResponse)
async def get_user_access_cached(
    user_id: str = Path(..., description="User ID"),
    max_cache_age_minutes: int = Query(60, description="Maximum cache age in minutes"),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    force_recalculate: bool = Query(False, description="Force real-time calculation"),
    controller: AccessController = Depends(get_controller),
):
    """Get user access with cache-first logic (faster response, may use cached data)."""
    return await _await_if_needed(controller.get_user_access(
        user_id=user_id,
        max_cache_age_minutes=max_cache_age_minutes,
        include_audit=include_audit,
        force_recalculate=force_recalculate
    ))


@router.get("/user/{user_id}/cached/by-name")
async def get_user_access_cached_by_name(
    user_id: str = Path(..., description="User ID"),
    max_cache_age_minutes: int = Query(60, description="Maximum cache age in minutes"),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    force_recalculate: bool = Query(False, description="Force real-time calculation"),
    controller: AccessController = Depends(get_controller),
):
    """
    Get user access with resource names instead of IDs (cache-first logic).

    Returns the same data as /user/{user_id}/cached but with an additional
    'resolved_access_by_name' field that maps resource names to permissions
    instead of resource IDs to permissions.
    """
    return await _await_if_needed(controller.get_user_access_by_name(
        user_id=user_id,
        max_cache_age_minutes=max_cache_age_minutes,
        include_audit=include_audit,
        force_recalculate=force_recalculate
    ))


@router.get("/user/{user_id}/resource-name/{resource_name}/permissions")
async def get_resource_permissions_by_name(
    user_id: str = Path(..., description="User ID"),
    resource_name: str = Path(..., description="Resource name"),
    max_cache_age_minutes: int = Query(60, description="Maximum cache age in minutes"),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    force_recalculate: bool = Query(False, description="Force real-time calculation"),
    evaluation_time: Optional[datetime] = Query(None, description="Time to evaluate access (ISO format)"),
    controller: AccessController = Depends(get_controller),
):
    """
    Get all permissions a user has for a specific resource by resource name.

    This endpoint allows you to query permissions using a human-readable resource name
    instead of a resource ID. Only user_id and resource_name are required; all other
    parameters are optional.

    Returns:
        - permissions: List of permissions the user has on the resource
        - resource_id: The ID of the matched resource
        - resource_name: The name of the resource
        - cache_info: Information about cache usage
    """
    return await _await_if_needed(controller.get_resource_permissions_by_name(
        user_id=user_id,
        resource_name=resource_name,
        max_cache_age_minutes=max_cache_age_minutes,
        include_audit=include_audit,
        force_recalculate=force_recalculate,
        evaluation_time=evaluation_time
    ))


@router.get("/resource/{resource_id}")
async def get_resource_access(
    resource_id: str = Path(..., description="Resource ID"),
    evaluation_time: Optional[datetime] = Query(
        None, description="Time to evaluate access (ISO format)"
    ),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    controller: AccessController = Depends(get_controller),
):
    """Get all access permissions for a resource."""
    return await _await_if_needed(controller.resolve_resource_access(
        resource_id=resource_id, evaluation_time=evaluation_time, include_audit=include_audit
    ))


@router.get("/usergroup/{group_id}", response_model=AccessResolutionResponse)
async def get_usergroup_access(
    group_id: str = Path(..., description="User Group ID"),
    evaluation_time: Optional[datetime] = Query(
        None, description="Time to evaluate access (ISO format)"
    ),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    controller: AccessController = Depends(get_controller),
):
    """Get all access permissions for a user group."""
    return await _await_if_needed(controller.resolve_user_access(
        user_id=group_id, evaluation_time=evaluation_time, include_audit=include_audit
    ))


@router.get("/resourcegroup/{group_id}")
async def get_resourcegroup_access(
    group_id: str = Path(..., description="Resource Group ID"),
    evaluation_time: Optional[datetime] = Query(
        None, description="Time to evaluate access (ISO format)"
    ),
    include_audit: bool = Query(False, description="Include audit trail in response"),
    controller: AccessController = Depends(get_controller),
):
    """Get all access permissions for a resource group."""
    return await _await_if_needed(controller.resolve_resource_access(
        resource_id=group_id, evaluation_time=evaluation_time, include_audit=include_audit
    ))


@router.get("/summary/{user_id}")
async def get_user_access_summary(
    user_id: str = Path(..., description="User ID"), controller: AccessController = Depends(get_controller)
):
    """Get access summary for a user."""
    summary = await _await_if_needed(controller.get_access_summary(user_id))
    if not summary:
        return {"message": "No access summary found. Run access resolution first."}
    return summary
