"""
User Groups API Routes

FastAPI routes for managing user groups and their members.
"""

from typing import Optional, List
import inspect

from fastapi import APIRouter, Query, Path, HTTPException, Depends

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import UserInDB

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


@router.get("/{group_id}")
async def get_usergroup(
    group_id: str = Path(..., description="User Group ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get user group details by ID."""
    group = await _await_if_needed(controller.get_user(group_id))
    if not group or group.type != "USERGROUP":
        raise HTTPException(status_code=404, detail="User group not found")
    return group


@router.get("/{group_id}/members")
async def get_usergroup_members(
    group_id: str = Path(..., description="User Group ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get members of a user group."""
    members = await _await_if_needed(controller.get_usergroup_members(group_id))
    if members is None:
        raise HTTPException(status_code=404, detail="User group not found")
    return {"group_id": group_id, "members": members}
