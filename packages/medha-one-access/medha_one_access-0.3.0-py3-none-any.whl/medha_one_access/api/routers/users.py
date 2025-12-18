"""
User Management API Routes

FastAPI routes for managing users and user groups.
"""

from typing import Optional, List
from datetime import datetime
import inspect

from fastapi import APIRouter, Query, Path, HTTPException, Depends
from pydantic import Field

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import UserCreate, UserUpdate, UserInDB
from medha_one_access.core.compatibility import model_dump

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


@router.post("/", response_model=UserInDB)
async def create_user(
    user_data: UserCreate,
    upsert: bool = Query(False, description="Update if user already exists"),
    controller: AccessController = Depends(get_controller)
):
    """Create a new user or user group."""
    return await _await_if_needed(controller.create_user(model_dump(user_data), upsert=upsert))


@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str = Path(..., description="User ID"),
    controller: AccessController = Depends(get_controller)
):
    """Get user details by ID."""
    user = await _await_if_needed(controller.get_user(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_data: UserUpdate,
    controller: AccessController = Depends(get_controller),
    user_id: str = Path(..., description="User ID"),
):
    """Update user details."""
    updated_user = await _await_if_needed(controller.update_user(user_id, model_dump(user_data, exclude_unset=True)))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str = Path(..., description="User ID"),
    controller: AccessController = Depends(get_controller)
):
    """Delete a user."""
    success = await _await_if_needed(controller.delete_user(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get("/", response_model=List[UserInDB])
async def list_users(
    user_type: Optional[str] = Query(
        None, description="Filter by user type (USER/USERGROUP)"
    ),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Number of users to return"),
    controller: AccessController = Depends(get_controller),
):
    """List users with filtering and pagination."""
    return await _await_if_needed(controller.list_users(user_type=user_type, skip=skip, limit=limit))


@router.get("/{user_id}/groups")
async def get_user_groups(
    user_id: str = Path(..., description="User ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get groups that a user belongs to."""
    groups = await _await_if_needed(controller.get_user_groups(user_id))
    if groups is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "groups": groups}
