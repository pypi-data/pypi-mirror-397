"""
Resource Groups API Routes

FastAPI routes for managing resource groups and their contents.
"""

from typing import Optional, List
import inspect

from fastapi import APIRouter, Query, Path, HTTPException, Depends

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import ArtifactInDB

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


@router.get("/{group_id}")
async def get_resourcegroup(
    group_id: str = Path(..., description="Resource Group ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get resource group details by ID."""
    group = await _await_if_needed(controller.get_artifact(group_id))
    if not group or group.type != "RESOURCEGROUP":
        raise HTTPException(status_code=404, detail="Resource group not found")
    return group


@router.get("/{group_id}/contents")
async def get_resourcegroup_contents(
    group_id: str = Path(..., description="Resource Group ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get contents of a resource group."""
    contents = await _await_if_needed(controller.get_resourcegroup_contents(group_id))
    if contents is None:
        raise HTTPException(status_code=404, detail="Resource group not found")
    return {"group_id": group_id, "contents": contents}
