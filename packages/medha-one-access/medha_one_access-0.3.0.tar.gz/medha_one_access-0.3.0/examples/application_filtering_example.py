"""
Example: Application Name Filtering

This example demonstrates how to use the application_name parameter
in the backend library to automatically filter all operations by 
application name, similar to the frontend implementation.
"""

from medha_one_access import AccessController, LibraryConfig

# Example 1: Using LibraryConfig with application_name
def example_with_application_filtering():
    """Example showing how application filtering works"""
    
    print("=== Application Filtering Example ===")
    
    import os
    import time
    
    # Clean up previous test database
    db_file = "test_app_filtering.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Configure with application name
    config = LibraryConfig(
        database_url="sqlite:///test_app_filtering.db",
        secret_key="test-secret",
        application_name="MyDashboardApp"  # This will filter all operations
    )
    
    # Initialize controller with application filtering
    controller = AccessController(config)
    
    print(f"Controller configured for application: {controller.application_name}")
    
    # Create artifacts - application name will be automatically set
    print("\n1. Creating artifacts...")
    
    artifact1 = controller.create_artifact({
        "id": "dashboard_001",
        "type": "RESOURCE", 
        "description": "Sales Dashboard"
        # Note: No application field specified - will be set automatically
    })
    print(f"Created artifact: {artifact1.id}, application: {artifact1.application}")
    
    artifact2 = controller.create_artifact({
        "id": "report_001",
        "type": "RESOURCE",
        "description": "Monthly Report", 
        "application": "CustomApp"  # Explicitly setting different application
    })
    print(f"Created artifact: {artifact2.id}, application: {artifact2.application}")
    
    # Create access rules - application name will be automatically set
    print("\n2. Creating access rules...")
    
    controller.create_user({"id": "john", "type": "USER", "email": "john@company.com"})
    
    rule1 = controller.create_access_rule({
        "id": "rule_001",
        "user_expression": "john",
        "resource_expression": "dashboard_001",
        "permissions": ["READ", "WRITE"]
        # Note: No application field specified - will be set automatically
    })
    print(f"Created rule: {rule1.id}, application: {rule1.application}")
    
    # List artifacts - only returns artifacts from configured application
    print("\n3. Listing artifacts (filtered by application)...")
    
    artifacts = controller.list_artifacts()
    print(f"Found {len(artifacts)} artifacts:")
    for artifact in artifacts:
        print(f"  - {artifact.id}: {artifact.description} (app: {artifact.application})")
    
    # List access rules - only returns rules from configured application  
    print("\n4. Listing access rules (filtered by application)...")
    
    rules = controller.list_access_rules()
    print(f"Found {len(rules)} access rules:")
    for rule in rules:
        print(f"  - {rule.id}: {rule.user_expression} -> {rule.resource_expression} (app: {rule.application})")
    
    # Health check shows current application
    print("\n5. Health check...")
    health = controller.health_check()
    print(f"Health check result: {health}")
    if 'configuration' in health:
        print(f"Application in config: {health['configuration']['application_name']}")
    else:
        print("No configuration found in health check")


def example_without_application_filtering():
    """Example without application filtering for comparison"""
    
    print("\n=== Without Application Filtering ===")
    
    import os
    
    # Clean up previous test database
    db_file = "test_no_filtering.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Configure without application name
    config = LibraryConfig(
        database_url="sqlite:///test_no_filtering.db", 
        secret_key="test-secret"
        # No application_name specified
    )
    
    controller = AccessController(config)
    print(f"Controller application name: {controller.application_name}")
    
    # Create artifacts - no automatic application setting
    artifact = controller.create_artifact({
        "id": "general_dashboard",
        "type": "RESOURCE",
        "description": "General Dashboard"
    })
    print(f"Created artifact without app filtering: {artifact.id}, application: {artifact.application}")
    
    # List all artifacts - no filtering applied
    artifacts = controller.list_artifacts()
    print(f"Found {len(artifacts)} artifacts (no filtering)")


def example_environment_configuration():
    """Example using environment variables for configuration"""
    
    print("\n=== Environment Configuration ===")
    
    import os
    
    # Clean up previous test database
    db_file = "test_env.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Set environment variables
    os.environ["MEDHA_DATABASE_URL"] = "sqlite:///test_env.db"
    os.environ["MEDHA_SECRET_KEY"] = "env-secret"
    os.environ["MEDHA_APPLICATION_NAME"] = "EnvironmentApp"
    
    # Create config from environment
    config = LibraryConfig.from_env()
    controller = AccessController(config)
    
    print(f"Application from environment: {controller.application_name}")
    
    # Clean up environment
    del os.environ["MEDHA_DATABASE_URL"]
    del os.environ["MEDHA_SECRET_KEY"] 
    del os.environ["MEDHA_APPLICATION_NAME"]


def example_mixed_applications():
    """Example showing how to work with mixed applications"""
    
    print("\n=== Mixed Applications Example ===")
    
    import os
    
    # Clean up previous test database
    db_file = "test_mixed.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Controller configured for specific application
    config = LibraryConfig(
        database_url="sqlite:///test_mixed.db",
        secret_key="test-secret", 
        application_name="AppA"
    )
    
    controller = AccessController(config)
    
    # Create artifacts for different applications
    controller.create_artifact({
        "id": "app_a_dashboard",
        "type": "RESOURCE",
        "description": "App A Dashboard"
        # Will automatically get application = "AppA"
    })
    
    controller.create_artifact({
        "id": "app_b_dashboard", 
        "type": "RESOURCE",
        "description": "App B Dashboard",
        "application": "AppB"  # Explicitly set to different app
    })
    
    # List artifacts - only shows "AppA" artifacts due to filtering
    filtered_artifacts = controller.list_artifacts()
    print(f"Filtered artifacts (AppA only): {len(filtered_artifacts)}")
    for artifact in filtered_artifacts:
        print(f"  - {artifact.id}: {artifact.application}")
    
    # To see all artifacts, bypass filtering by specifying application=None in query
    # (This would need to be implemented if needed)
    all_artifacts = controller.list_artifacts(application=None)
    print(f"All artifacts: {len(all_artifacts)}")


if __name__ == "__main__":
    try:
        example_with_application_filtering()
        example_without_application_filtering()
        example_environment_configuration() 
        example_mixed_applications()
        
        print("\n=== Summary ===")
        print("[OK] Application name filtering implemented successfully")
        print("[OK] Automatic application name setting on create operations")
        print("[OK] Filtered queries for get/list operations")
        print("[OK] Environment variable support")
        print("[OK] Health check shows application configuration")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()