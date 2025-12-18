"""
FastAPI Integration Example for MedhaOne Access Control

Demonstrates how to integrate the access control library with FastAPI.
"""

import os
import uvicorn
from contextlib import asynccontextmanager

from medha_one_access.api import create_app


def create_sample_app():
    """Create a sample FastAPI application with access control."""

    # Database URL (use SQLite for this example)
    database_url = os.getenv("DATABASE_URL", "sqlite:///fastapi_example.db")

    # Create the FastAPI app with access control
    app = create_app(
        database_url=database_url,
        title="Sample Access Control API",
        description="Example FastAPI application with MedhaOne Access Control",
        version="1.0.0",
        cors_origins=["http://localhost:3000", "http://localhost:8080"],
    )

    # Add custom routes
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "MedhaOne Access Control API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create the app instance
app = create_sample_app()


def main():
    """Run the FastAPI application."""
    print("Starting FastAPI application with MedhaOne Access Control...")
    print("API documentation available at: http://localhost:8000/docs")
    print("Health check available at: http://localhost:8000/health")
    print("")
    print("Available endpoints:")
    print("  GET  /api/v1/users           - List users")
    print("  POST /api/v1/users           - Create user")
    print("  GET  /api/v1/users/{id}      - Get user")
    print("  PUT  /api/v1/users/{id}      - Update user")
    print("  DELETE /api/v1/users/{id}    - Delete user")
    print("")
    print("  GET  /api/v1/artifacts       - List artifacts")
    print("  POST /api/v1/artifacts       - Create artifact")
    print("  GET  /api/v1/artifacts/{id}  - Get artifact")
    print("  PUT  /api/v1/artifacts/{id}  - Update artifact")
    print("  DELETE /api/v1/artifacts/{id} - Delete artifact")
    print("")
    print("  GET  /api/v1/access-rules    - List access rules")
    print("  POST /api/v1/access-rules    - Create access rule")
    print("  GET  /api/v1/access-rules/{id} - Get access rule")
    print("  PUT  /api/v1/access-rules/{id} - Update access rule")
    print("  DELETE /api/v1/access-rules/{id} - Delete access rule")
    print("")
    print("  GET  /api/v1/access/resolve/{user_id} - Resolve user access")
    print("  POST /api/v1/access/check    - Check specific permission")
    print(
        "  GET  /api/v1/access/check/{user_id}/{resource_id}/{permission} - Check permission (GET)"
    )
    print("  GET  /api/v1/access/summary/{user_id} - Get user access summary")
    print("")

    # Run the server
    uvicorn.run(
        "examples.fastapi_integration:app", host="0.0.0.0", port=8001, reload=True
    )


if __name__ == "__main__":
    main()
