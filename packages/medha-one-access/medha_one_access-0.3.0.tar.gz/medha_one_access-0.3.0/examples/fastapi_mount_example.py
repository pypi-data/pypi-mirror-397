"""
FastAPI Mount Integration Example

Demonstrates how to mount MedhaOne Access Control routes into an existing FastAPI app.
"""

from fastapi import FastAPI
from medha_one_access import LibraryConfig, mount_access_control_routes

# Create your existing FastAPI application
app = FastAPI(
    title="My Business Application",
    description="Example app with integrated access control",
    version="1.0.0",
)


# Your existing business routes
@app.get("/")
async def root():
    return {"message": "Welcome to My Business Application"}


@app.get("/api/business-data")
async def get_business_data():
    return {"data": "This is my business data"}


@app.get("/api/reports")
async def get_reports():
    return {"reports": ["Report 1", "Report 2"]}


# One-line integration with MedhaOne Access Control
# This adds ALL access control endpoints to your app!
try:
    controller = mount_access_control_routes(
        app,
        LibraryConfig(
            database_url="sqlite:///example_access_control.db",  # SQLite for demo
            secret_key="demo_secret_key_for_testing_only",
            api_prefix="/oneAccess",  # You can choose any prefix
        ),
    )

    print("✅ Successfully mounted access control routes!")
    print("📍 Available access control endpoints:")
    print("   GET  /oneAccess/users")
    print("   POST /oneAccess/users")
    print("   GET  /oneAccess/artifacts")
    print("   POST /oneAccess/artifacts")
    print("   GET  /oneAccess/access-rules")
    print("   POST /oneAccess/access-rules")
    print("   POST /oneAccess/access/check")
    print("   GET  /oneAccess/access/resolve/{user_id}")
    print("   GET  /oneAccess/access-summary")
    print("   GET  /oneAccess/reporting/structure/{user_id}")
    print("   POST /oneAccess/data-io/import")
    print("   POST /oneAccess/data-io/export")
    print("   GET  /oneAccess/health")
    print("")

except Exception as e:
    print(f"❌ Failed to mount access control routes: {str(e)}")
    controller = None


# Optional: Use the controller directly in your business logic
@app.get("/api/protected-resource/{resource_id}")
async def get_protected_resource(resource_id: str):
    """Example of using the access controller in your business logic"""
    if controller:
        # Example: Check if user has access (you'd get user_id from auth)
        user_id = "demo_user"  # In real app, get from JWT/session

        try:
            access_result = controller.check_access(user_id, resource_id, "READ")

            if access_result.get("hasAccess"):
                return {
                    "resource_id": resource_id,
                    "data": "Protected resource data",
                    "access_granted": True,
                }
            else:
                return {
                    "resource_id": resource_id,
                    "error": "Access denied",
                    "access_granted": False,
                }

        except Exception as e:
            return {
                "resource_id": resource_id,
                "error": f"Access check failed: {str(e)}",
                "access_granted": False,
            }
    else:
        return {
            "resource_id": resource_id,
            "data": "Resource data (access control not available)",
            "access_granted": True,
        }


# Add custom middleware or other integrations here
@app.middleware("http")
async def custom_middleware(request, call_next):
    """Your custom middleware"""
    print(f"🌐 Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting integrated FastAPI application...")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🏠 Home page: http://localhost:8000/")
    print("🔐 Access control: http://localhost:8000/oneAccess/")
    print("")

    uvicorn.run(
        "examples.fastapi_mount_example:app", host="0.0.0.0", port=8000, reload=True
    )
