"""
FastAPI Application Factory for MedhaOne Access Control

Creates and configures a FastAPI application with all routes and middleware.
"""

from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from medha_one_access.core.controller import AccessController
from medha_one_access.core.exceptions import MedhaAccessError
from medha_one_access.api.routers import users, artifacts, access_rules, access_check
from medha_one_access.api.dependencies import get_controller


# Global controller instance
_controller: Optional[AccessController] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _controller

    # Startup
    database_url = app.state.database_url
    _controller = AccessController(database_url)

    yield

    # Shutdown
    if _controller:
        _controller.close()
        _controller = None


def get_global_controller() -> AccessController:
    """Get the global controller instance."""
    if not _controller:
        raise RuntimeError("Controller not initialized. Call create_app() first.")
    return _controller


def create_app(
    database_url: str,
    title: str = "MedhaOne Access Control API",
    description: str = "BODMAS-based access control system",
    version: str = "0.1.0",
    cors_origins: Optional[list] = None,
    **kwargs,
) -> FastAPI:
    """
    Create and configure a FastAPI application.

    Args:
        database_url: Database connection URL
        title: API title
        description: API description
        version: API version
        cors_origins: CORS allowed origins
        **kwargs: Additional FastAPI configuration

    Returns:
        Configured FastAPI application
    """

    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=lifespan,
        **kwargs,
    )

    # Store database URL in app state
    app.state.database_url = database_url

    # Add CORS middleware
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Exception handlers
    @app.exception_handler(MedhaAccessError)
    async def medha_access_exception_handler(request: Request, exc: MedhaAccessError):
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.error_type,
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            controller = get_global_controller()
            # Simple database connectivity check
            with controller._session_manager.get_session() as session:
                session.execute("SELECT 1")
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return JSONResponse(
                status_code=503, content={"status": "unhealthy", "error": str(e)}
            )

    # Include routers
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(artifacts.router, prefix="/api/v1/artifacts", tags=["Artifacts"])
    app.include_router(
        access_rules.router, prefix="/api/v1/access-rules", tags=["Access Rules"]
    )
    app.include_router(
        access_check.router, prefix="/api/v1/access", tags=["Access Control"]
    )

    return app


# Convenience function for getting controller in route handlers
def get_controller_dependency():
    """Dependency for getting the controller in route handlers."""
    return get_global_controller()
