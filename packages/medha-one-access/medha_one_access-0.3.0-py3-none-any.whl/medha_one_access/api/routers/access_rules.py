"""
Access Rules Management API Routes

FastAPI routes for managing access rules and permissions.
"""

from typing import Optional, List
from datetime import datetime
import inspect

from fastapi import APIRouter, Query, Path, HTTPException, Depends

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import (
    AccessRuleCreate,
    AccessRuleUpdate,
    AccessRuleInDB,
)
from medha_one_access.core.compatibility import model_dump

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


@router.post("/", response_model=AccessRuleInDB)
async def create_access_rule(
    rule_data: AccessRuleCreate, controller: AccessController = Depends(get_controller)
):
    """Create a new access rule."""
    return await _await_if_needed(controller.create_access_rule(rule_data))


@router.get("/{rule_id}", response_model=AccessRuleInDB)
async def get_access_rule(
    rule_id: str = Path(..., description="Access rule ID"),
    controller: AccessController = Depends(get_controller),
):
    """Get access rule details by ID."""
    rule = await _await_if_needed(controller.get_access_rule(rule_id))
    if not rule:
        raise HTTPException(status_code=404, detail="Access rule not found")
    return rule


@router.put("/{rule_id}", response_model=AccessRuleInDB)
async def update_access_rule(
    rule_data: AccessRuleUpdate,
    rule_id: str = Path(..., description="Access rule ID"),
    controller: AccessController = Depends(get_controller),
):
    """Update access rule details."""
    return await _await_if_needed(controller.update_access_rule(
        rule_id, model_dump(rule_data, exclude_unset=True)
    ))


@router.delete("/{rule_id}")
async def delete_access_rule(
    rule_id: str = Path(..., description="Access rule ID"),
    controller: AccessController = Depends(get_controller),
):
    """Delete an access rule."""
    await _await_if_needed(controller.delete_access_rule(rule_id))
    return {"message": "Access rule deleted successfully"}


@router.get("/", response_model=List[AccessRuleInDB])
async def list_access_rules(
    user_expression: Optional[str] = Query(
        None, description="Filter by user expression"
    ),
    resource_expression: Optional[str] = Query(
        None, description="Filter by resource expression"
    ),
    application: Optional[str] = Query(None, description="Filter by application"),
    application_name: Optional[str] = Query(None, description="Filter by application name (alias for application)"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of rules to skip"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Number of rules to return"),
    controller: AccessController = Depends(get_controller),
):
    """List access rules with filtering and pagination."""
    # Use application_name if provided, otherwise use application
    app_filter = application_name if application_name is not None else application

    return await _await_if_needed(controller.list_access_rules(
        user_expression=user_expression,
        resource_expression=resource_expression,
        application=app_filter,
        active=active,
        skip=skip,
        limit=limit,
    ))


@router.post("/validate-expression")
async def validate_expression(
    expression: str = Query(..., description="Expression to validate"),
    expression_type: str = Query(..., description="Expression type (USER/RESOURCE)"),
    controller: AccessController = Depends(get_controller),
):
    """Validate an expression and return resolved entities."""
    return await _await_if_needed(controller.validate_expression(expression, expression_type))
