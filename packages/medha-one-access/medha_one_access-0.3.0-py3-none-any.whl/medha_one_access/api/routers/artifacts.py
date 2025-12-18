"""
Artifact Management API Routes

FastAPI routes for managing artifacts and resource groups.
"""

from typing import Optional, List
from datetime import datetime
import inspect

from fastapi import APIRouter, Query, Path, HTTPException, Depends

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import ArtifactCreate, ArtifactUpdate, ArtifactInDB
from medha_one_access.core.compatibility import model_dump

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


@router.post("/", response_model=ArtifactInDB)
async def create_artifact(artifact_data: ArtifactCreate, controller: AccessController = Depends(get_controller)):
    """Create a new artifact or resource group."""
    return await _await_if_needed(controller.create_artifact(model_dump(artifact_data)))


@router.get("/{artifact_id}", response_model=ArtifactInDB)
async def get_artifact(
    artifact_id: str = Path(..., description="Artifact ID"),
    controller: AccessController = Depends(get_controller)
):
    """Get artifact details by ID."""
    artifact = await _await_if_needed(controller.get_artifact(artifact_id))
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.put("/{artifact_id}", response_model=ArtifactInDB)
async def update_artifact(
    artifact_data: ArtifactUpdate,
    artifact_id: str = Path(..., description="Artifact ID"),
    controller: AccessController = Depends(get_controller)
):
    """Update artifact details."""
    updated_artifact = await _await_if_needed(controller.update_artifact(
        artifact_id, model_dump(artifact_data, exclude_unset=True)
    ))
    if not updated_artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return updated_artifact


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: str = Path(..., description="Artifact ID"),
    controller: AccessController = Depends(get_controller)
):
    """Delete an artifact."""
    success = await _await_if_needed(controller.delete_artifact(artifact_id))
    if not success:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {"message": "Artifact deleted successfully"}


@router.get("/", response_model=List[ArtifactInDB])
async def list_artifacts(
    controller: AccessController = Depends(get_controller),
    skip: int = Query(0, ge=0, description="Number of artifacts to skip"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Number of artifacts to return"),
    artifact_type: Optional[str] = Query(None, description="Filter by artifact type (RESOURCE/RESOURCEGROUP)"),
    application_name: Optional[str] = Query(None, description="Filter by application name"),
    application: Optional[str] = Query(None, description="Filter by application (alias for application_name)"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """List artifacts with filtering and pagination."""
    # Use application_name if provided, otherwise use application
    app_filter = application_name if application_name is not None else application

    return await _await_if_needed(controller.list_artifacts(
        skip=skip,
        limit=limit,
        artifact_type=artifact_type,
        application=app_filter,
        active=active
    ))


@router.get("/{artifact_id}/groups")
async def get_artifact_groups(
    artifact_id: str = Path(..., description="Artifact ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get resource groups that an artifact belongs to."""
    groups = await _await_if_needed(controller.get_artifact_groups(artifact_id))
    if groups is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {"artifact_id": artifact_id, "groups": groups}
