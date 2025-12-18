"""
Access Summary API Routes

FastAPI routes for managing and calculating access summaries.
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import (
    AccessSummaryCreate,
    AccessSummaryUpdate,
    AccessSummaryInDB,
)
from medha_one_access.core.models import User, Artifact, AccessRule, AccessSummary
from medha_one_access.core.exceptions import MedhaAccessError
from medha_one_access.core.compatibility import model_dump

router = APIRouter()


@router.post("/", response_model=AccessSummaryInDB)
async def create_access_summary(
    summary: AccessSummaryCreate, controller: AccessController = Depends(get_controller)
):
    """Create a new access summary for a user"""
    try:
        from sqlalchemy import select
        async with controller.get_session() as session:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.id == summary.user_id, User.active == True)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check if summary already exists
            result = await session.execute(
                select(AccessSummary).where(AccessSummary.user_id == summary.user_id)
            )
            existing_summary = result.scalar_one_or_none()
            if existing_summary:
                raise HTTPException(
                    status_code=400,
                    detail="Access summary already exists for this user",
                )

            # Create new summary
            db_summary = AccessSummary(
                id=f"summary_{summary.user_id}",
                user_id=summary.user_id,
                total_accessible_resources=summary.total_accessible_resources,
                total_groups=summary.total_groups,
                direct_permissions=summary.direct_permissions,
                inherited_permissions=summary.inherited_permissions,
                summary_data=summary.summary_data,
                last_calculated=datetime.now(),
            )

            # Add to database
            session.add(db_summary)
            await session.commit()
            await session.refresh(db_summary)

            return AccessSummaryInDB.from_orm(db_summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create access summary: {str(e)}"
        )


@router.get("/", response_model=List[AccessSummaryInDB])
async def list_access_summaries(
    controller: AccessController = Depends(get_controller),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=10000),
):
    """List all access summaries"""
    try:
        from sqlalchemy import select
        async with controller.get_session() as session:
            query = select(AccessSummary).offset(skip)
            if limit is not None:
                query = query.limit(limit)
            result = await session.execute(query)
            summaries = result.scalars().all()
            return [AccessSummaryInDB.from_orm(summary) for summary in summaries]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list access summaries: {str(e)}"
        )


@router.get("/{user_id}", response_model=AccessSummaryInDB)
async def get_access_summary(user_id: str, controller: AccessController = Depends(get_controller)):
    """Get access summary for a user"""
    try:
        from sqlalchemy import select
        async with controller.get_session() as session:
            # Get application name from controller
            application_name = controller.application_name or "default"
            
            result = await session.execute(
                select(AccessSummary).where(
                    AccessSummary.user_id == user_id,
                    AccessSummary.application == application_name
                )
            )
            summary = result.scalar_one_or_none()
            if not summary:
                raise HTTPException(status_code=404, detail="Access summary not found")

            return AccessSummaryInDB.from_orm(summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get access summary: {str(e)}"
        )


@router.put("/{user_id}", response_model=AccessSummaryInDB)
async def update_access_summary(
    summary_update: AccessSummaryUpdate, user_id: str, controller: AccessController = Depends(get_controller)
):
    """Update access summary for a user"""
    try:
        from sqlalchemy import select
        async with controller.get_session() as session:
            # Get application name from controller
            application_name = controller.application_name or "default"
            
            # Get existing summary (application-scoped)
            result = await session.execute(
                select(AccessSummary).where(
                    AccessSummary.user_id == user_id,
                    AccessSummary.application == application_name
                )
            )
            db_summary = result.scalar_one_or_none()
            if not db_summary:
                raise HTTPException(status_code=404, detail="Access summary not found")

            # Update fields if provided
            update_data = model_dump(summary_update, exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_summary, field, value)

            # Update last calculated timestamp
            db_summary.last_calculated = datetime.now()

            # Commit changes
            await session.commit()
            await session.refresh(db_summary)

            return AccessSummaryInDB.from_orm(db_summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update access summary: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_access_summary(user_id: str, controller: AccessController = Depends(get_controller)):
    """Delete access summary for a user"""
    try:
        from sqlalchemy import select
        async with controller.get_session() as session:
            # Get application name from controller
            application_name = controller.application_name or "default"
            
            # Get existing summary (application-scoped)
            result = await session.execute(
                select(AccessSummary).where(
                    AccessSummary.user_id == user_id,
                    AccessSummary.application == application_name
                )
            )
            db_summary = result.scalar_one_or_none()
            if not db_summary:
                raise HTTPException(status_code=404, detail="Access summary not found")

            # Delete summary
            await session.delete(db_summary)
            await session.commit()

            return {
                "status": "success",
                "message": f"Access summary for user {user_id} deleted",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete access summary: {str(e)}"
        )


@router.post("/calculate/{user_id}", response_model=AccessSummaryInDB)
async def calculate_access_summary(user_id: str, controller: AccessController = Depends(get_controller)):
    """Calculate access summary for a user based on current access rules"""
    try:
        # Use the controller's resolve_user_access method instead of direct database access
        user_access = controller.resolve_user_access(user_id, include_audit=True)
        
        # Extract data from the resolved access
        resolved_access = user_access.get("resolved_access", {})
        total_accessible_resources = len(resolved_access)
        
        # Get user groups that this user belongs to
        user_groups_result = controller.get_user_groups(user_id)
        user_groups = [group.id for group in user_groups_result] if user_groups_result else []
        
        # Simplified permission counts (from resolved access)
        permission_counts = {}
        for permission_type in ["READ", "WRITE", "EXPORT"]:
            permission_counts[permission_type.lower()] = sum(
                1 for res, perms in resolved_access.items() if permission_type in perms
            )
        
        # Create enhanced summary data
        summary_data = {
            "resolved_access": resolved_access,
            "resolved_access_detailed": user_access.get("resolved_access_detailed", {}),
            "accessibleResourceIds": list(resolved_access.keys()),
            "groupMemberships": user_groups,
            "permissionCounts": permission_counts,
            "calculationDetails": {
                "auditTrail": user_access.get("audit_trail", []),
                "calculatedAt": datetime.now().isoformat(),
            },
        }

        # Get application name from controller
        application_name = controller.application_name or "default"
        
        # Use the controller's session for database operations
        with controller.get_session() as session:
            # Get or create access summary (application-scoped)
            db_summary = (
                session.query(AccessSummary)
                .filter(
                    AccessSummary.user_id == user_id,
                    AccessSummary.application == application_name
                )
                .first()
            )

            if db_summary:
                # Update existing summary
                db_summary.total_accessible_resources = total_accessible_resources
                db_summary.total_groups = len(user_groups)
                db_summary.direct_permissions = 0  # Simplified for this endpoint
                db_summary.inherited_permissions = 0  # Simplified for this endpoint
                db_summary.summary_data = summary_data
                db_summary.last_calculated = datetime.now()
                db_summary.is_stale = False  # Mark as fresh
            else:
                # Create new summary
                db_summary = AccessSummary(
                    id=f"summary_{user_id}_{application_name}",
                    user_id=user_id,
                    application=application_name,
                    total_accessible_resources=total_accessible_resources,
                    total_groups=len(user_groups),
                    direct_permissions=0,  # Simplified for this endpoint
                    inherited_permissions=0,  # Simplified for this endpoint
                    summary_data=summary_data,
                    last_calculated=datetime.now(),
                    is_stale=False,
                )
                session.add(db_summary)

            # Commit changes
            session.commit()
            session.refresh(db_summary)

            return AccessSummaryInDB.from_orm(db_summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate access summary: {str(e)}"
        )


@router.get("/stats/overview")
async def get_access_stats_overview(controller: AccessController = Depends(get_controller)):
    """Get overview statistics for access across the system"""
    try:
        # Use the controller's health_check method which already provides good statistics
        health_result = controller.health_check()
        
        if health_result.get("status") != "healthy":
            raise HTTPException(status_code=503, detail="System not healthy")
            
        # Extract stats from health check
        stats = health_result.get("statistics", {})
        cache_stats = stats.get("cache_summaries", {})
        
        # Get simplified resource list using controller methods
        most_accessed_resources = []
        try:
            # Get a sample of artifacts to demonstrate access patterns
            artifacts = controller.list_artifacts(limit=5, artifact_type="RESOURCE")
            for artifact in artifacts:
                try:
                    # Use resolve_resource_access to get user count
                    resource_access = controller.resolve_resource_access(artifact.id, include_audit=False)
                    access_count = len(resource_access.get("users_with_access", {}))
                    most_accessed_resources.append({
                        "id": artifact.id,
                        "name": artifact.name or artifact.id,
                        "description": artifact.description,
                        "accessCount": access_count,
                    })
                except Exception:
                    # Skip resources with calculation errors
                    continue
        except Exception:
            # If we can't get resources, provide empty list
            pass

        # Sort by access count
        most_accessed_resources.sort(key=lambda x: x["accessCount"], reverse=True)

        return {
            "overview": {
                "totalUsers": stats.get("users", 0),
                "totalGroups": 0,  # Would need separate query to distinguish user groups
                "totalResources": stats.get("artifacts", 0),
                "totalResourceGroups": 0,  # Would need separate query to distinguish resource groups
                "totalRules": stats.get("access_rules", 0),
            },
            "cacheStatistics": cache_stats,
            "mostAccessedResources": most_accessed_resources[:5],  # Top 5 most accessed
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get access stats: {str(e)}"
        )
