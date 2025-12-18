"""
Expression Validation API Routes

FastAPI routes for validating and parsing expressions.
"""

import inspect

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController

router = APIRouter()


async def _await_if_needed(result):
    """Helper to await result if it's a coroutine (async), otherwise return it directly."""
    if inspect.iscoroutine(result):
        return await result
    return result


class ExpressionValidateRequest(BaseModel):
    """Request model for expression validation."""
    expression: str
    expression_type: str  # "USER" or "RESOURCE"


@router.post("/validate")
async def validate_expression(
    request: ExpressionValidateRequest,
    controller: AccessController = Depends(get_controller),
):
    """Validate an expression and return validation results."""
    return await _await_if_needed(controller.validate_expression(request.expression, request.expression_type))
