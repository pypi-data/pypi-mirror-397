"""
Reporting API Routes

FastAPI routes for organizational reporting and hierarchy management.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.models import User
from medha_one_access.core.exceptions import MedhaAccessError

router = APIRouter()


def _build_hierarchy(
    user_id: str, session, levels_deep: int = 1, current_level: int = 0
) -> Optional[Dict]:
    """Recursively build the reporting hierarchy for a user"""
    user = session.query(User).filter(User.id == user_id, User.active == True).first()
    if not user:
        return None

    # Create base hierarchy for this user
    hierarchy = {
        "id": user.id,
        "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.id,
        "email": user.email,
        "department": user.department,
        "role": user.role,
        "reports": [],
    }

    # Add manager info if available
    if user.manager_id:
        manager = (
            session.query(User)
            .filter(User.id == user.manager_id, User.active == True)
            .first()
        )
        if manager:
            hierarchy["manager"] = {
                "id": manager.id,
                "name": f"{manager.first_name or ''} {manager.last_name or ''}".strip()
                or manager.id,
            }

    # If we haven't reached the max depth, add direct reports
    if current_level < levels_deep:
        direct_reports = (
            session.query(User)
            .filter(User.manager_id == user.id, User.active == True)
            .all()
        )

        for report in direct_reports:
            report_hierarchy = _build_hierarchy(
                report.id, session, levels_deep, current_level + 1
            )
            if report_hierarchy:
                hierarchy["reports"].append(report_hierarchy)

    return hierarchy


@router.get("/structure/{user_id}")
async def get_reporting_structure(
    user_id: str,
    levels_down: int = Query(
        1, description="Number of levels down to include", ge=0, le=10
    ),
    levels_up: int = Query(
        1, description="Number of levels up to include", ge=0, le=10
    ),
    controller: AccessController = Depends(get_controller),
):
    """
    Get the reporting structure for a user, including managers above
    and direct reports below.
    """
    try:
        with controller.get_session() as session:
            # Check if user exists
            user = (
                session.query(User)
                .filter(User.id == user_id, User.active == True)
                .first()
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Build hierarchy upward (managers)
            managers_chain = []
            current_user = user
            managers_levels = 0

            while current_user.manager_id and managers_levels < levels_up:
                manager = (
                    session.query(User)
                    .filter(User.id == current_user.manager_id, User.active == True)
                    .first()
                )

                if not manager:
                    break

                managers_chain.append(
                    {
                        "id": manager.id,
                        "name": f"{manager.first_name or ''} {manager.last_name or ''}".strip()
                        or manager.id,
                        "email": manager.email,
                        "department": manager.department,
                        "role": manager.role,
                    }
                )

                current_user = manager
                managers_levels += 1

            # Build hierarchy downward (direct reports)
            downward_hierarchy = _build_hierarchy(user_id, session, levels_down)

            # Combine the results
            result = {
                "user": {
                    "id": user.id,
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip()
                    or user.id,
                    "email": user.email,
                    "department": user.department,
                    "role": user.role,
                },
                "managers": managers_chain,
                "reports": (
                    downward_hierarchy.get("reports", []) if downward_hierarchy else []
                ),
            }

            return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get reporting structure: {str(e)}"
        )


@router.get("/manager/{manager_id}/reports")
async def get_direct_reports(manager_id: str, controller: AccessController = Depends(get_controller)):
    """Get all direct reports for a manager"""
    try:
        with controller.get_session() as session:
            # Check if manager exists
            manager = (
                session.query(User)
                .filter(User.id == manager_id, User.active == True)
                .first()
            )
            if not manager:
                raise HTTPException(status_code=404, detail="Manager not found")

            # Get direct reports
            direct_reports = (
                session.query(User)
                .filter(User.manager_id == manager_id, User.active == True)
                .all()
            )

            # Format the response
            result = {
                "manager": {
                    "id": manager.id,
                    "name": f"{manager.first_name or ''} {manager.last_name or ''}".strip()
                    or manager.id,
                    "email": manager.email,
                    "department": manager.department,
                    "role": manager.role,
                },
                "reports": [],
            }

            for report in direct_reports:
                result["reports"].append(
                    {
                        "id": report.id,
                        "name": f"{report.first_name or ''} {report.last_name or ''}".strip()
                        or report.id,
                        "email": report.email,
                        "department": report.department,
                        "role": report.role,
                    }
                )

            return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get direct reports: {str(e)}"
        )


@router.get("/organization-chart")
async def get_organization_chart(
    top_level_only: bool = Query(False, description="Return only top-level managers"),
    controller: AccessController = Depends(get_controller),
):
    """
    Get the full organization chart, optionally with only the top level managers.
    """
    try:
        with controller.get_session() as session:
            # Find top-level managers (users with no manager)
            if top_level_only:
                top_managers = (
                    session.query(User)
                    .filter(
                        User.type == "USER",
                        User.manager_id == None,
                        User.active == True,
                    )
                    .all()
                )

                result = {"topManagers": []}

                for manager in top_managers:
                    direct_report_count = (
                        session.query(User)
                        .filter(User.manager_id == manager.id, User.active == True)
                        .count()
                    )

                    result["topManagers"].append(
                        {
                            "id": manager.id,
                            "name": f"{manager.first_name or ''} {manager.last_name or ''}".strip()
                            or manager.id,
                            "email": manager.email,
                            "department": manager.department,
                            "role": manager.role,
                            "directReportCount": direct_report_count,
                        }
                    )

                return result

            # Build full org chart
            top_managers = (
                session.query(User)
                .filter(
                    User.type == "USER", User.manager_id == None, User.active == True
                )
                .all()
            )

            org_chart = []
            for manager in top_managers:
                hierarchy = _build_hierarchy(
                    manager.id, session, 999
                )  # Unlimited depth
                if hierarchy:
                    org_chart.append(hierarchy)

            return {"organizationChart": org_chart}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get organization chart: {str(e)}"
        )


@router.post("/assign-manager")
async def assign_manager(
    user_id: str = Query(..., description="ID of the user to update"),
    manager_id: str = Query(..., description="ID of the manager to assign"),
    controller: AccessController = Depends(get_controller),
):
    """Assign a manager to a user"""
    try:
        with controller.get_session() as session:
            # Check if user exists
            user = (
                session.query(User)
                .filter(User.id == user_id, User.active == True)
                .first()
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check if manager exists
            manager = (
                session.query(User)
                .filter(User.id == manager_id, User.type == "USER", User.active == True)
                .first()
            )
            if not manager:
                raise HTTPException(status_code=404, detail="Manager not found")

            # Check for circular reference
            current_manager = manager
            while current_manager:
                if current_manager.id == user_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Circular reference: A user cannot be a manager of their own manager",
                    )
                current_manager = (
                    session.query(User)
                    .filter(User.id == current_manager.manager_id)
                    .first()
                )

            # Assign manager
            user.manager_id = manager_id
            session.commit()

            return {
                "status": "success",
                "message": f"Manager {manager_id} assigned to user {user_id}",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to assign manager: {str(e)}"
        )


@router.delete("/remove-manager/{user_id}")
async def remove_manager(user_id: str, controller: AccessController = Depends(get_controller)):
    """Remove the manager from a user"""
    try:
        with controller.get_session() as session:
            # Check if user exists
            user = (
                session.query(User)
                .filter(User.id == user_id, User.active == True)
                .first()
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Remove manager
            user.manager_id = None
            session.commit()

            return {
                "status": "success",
                "message": f"Manager removed from user {user_id}",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to remove manager: {str(e)}"
        )


@router.get("/department-summary")
async def get_department_summary(controller: AccessController = Depends(get_controller)):
    """Get summary of users by department"""
    try:
        with controller.get_session() as session:
            from sqlalchemy import func

            # Get department counts
            department_counts = (
                session.query(User.department, func.count(User.id).label("count"))
                .filter(
                    User.type == "USER",
                    User.active == True,
                    User.department.isnot(None),
                )
                .group_by(User.department)
                .all()
            )

            departments = []
            for dept, count in department_counts:
                # Get managers in this department
                managers = (
                    session.query(User)
                    .filter(
                        User.department == dept,
                        User.type == "USER",
                        User.active == True,
                        User.manager_id == None,
                    )
                    .all()
                )

                departments.append(
                    {
                        "department": dept,
                        "totalUsers": count,
                        "topManagers": [
                            {
                                "id": mgr.id,
                                "name": f"{mgr.first_name or ''} {mgr.last_name or ''}".strip()
                                or mgr.id,
                                "email": mgr.email,
                                "role": mgr.role,
                            }
                            for mgr in managers
                        ],
                    }
                )

            return {"departments": departments}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get department summary: {str(e)}"
        )
