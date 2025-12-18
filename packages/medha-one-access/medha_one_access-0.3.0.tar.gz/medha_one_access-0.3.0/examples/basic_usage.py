"""
Basic Usage Example for MedhaOne Access Control

Demonstrates basic CRUD operations and access checking.
"""

import os
from datetime import datetime, timedelta
from medha_one_access import AccessController


def main():
    """Demonstrate basic usage of the access control library."""

    # Database URL (use SQLite for this example)
    database_url = "sqlite:///example_access_control.db"

    print("🚀 MedhaOne Access Control - Basic Usage Example\n")

    # Create and configure the access controller
    with AccessController(database_url) as controller:

        # Initialize database (create tables)
        print("📊 Initializing database...")
        controller.init_database()
        print("✅ Database initialized\n")

        # 1. Create users
        print("👥 Creating users...")

        # Individual users
        john = controller.create_user(
            user_id="john_doe",
            type="USER",
            first_name="John",
            last_name="Doe",
            email="john.doe@company.com",
            department="Engineering",
            role="Senior Developer",
        )
        print(f"Created user: {john.id}")

        jane = controller.create_user(
            user_id="jane_smith",
            type="USER",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@company.com",
            department="Engineering",
            role="Team Lead",
        )
        print(f"Created user: {jane.id}")

        # User groups
        dev_group = controller.create_user(
            user_id="developers",
            type="USERGROUP",
            expression="john_doe + jane_smith",  # Include these users
            description="All developers in the engineering team",
        )
        print(f"Created user group: {dev_group.id}")

        # 2. Create resources/artifacts
        print("\n📦 Creating resources...")

        # Individual resources
        user_service = controller.create_artifact(
            artifact_id="user-service-api",
            type="RESOURCE",
            name="User Service API",
            description="REST API for user management",
            application="UserService",
        )
        print(f"Created resource: {user_service.id}")

        admin_panel = controller.create_artifact(
            artifact_id="admin-panel",
            type="RESOURCE",
            name="Admin Panel",
            description="Web-based administration interface",
            application="AdminApp",
        )
        print(f"Created resource: {admin_panel.id}")

        # Resource groups
        apis = controller.create_artifact(
            artifact_id="all-apis",
            type="RESOURCEGROUP",
            name="All APIs",
            expression="user-service-api",  # Include specific APIs
            description="All company APIs",
        )
        print(f"Created resource group: {apis.id}")

        # 3. Create access rules
        print("\n🔐 Creating access rules...")

        # Give developers read access to APIs
        dev_api_rule = controller.create_access_rule(
            rule_id="dev-api-access",
            user_expression="developers",
            resource_expression="all-apis",
            permissions=["read", "test"],
            name="Developer API Access",
            description="Developers can read and test APIs",
        )
        print(f"Created access rule: {dev_api_rule.id}")

        # Give Jane admin access (as team lead)
        jane_admin_rule = controller.create_access_rule(
            rule_id="jane-admin-access",
            user_expression="jane_smith",
            resource_expression="admin-panel",
            permissions=["read", "write", "admin"],
            name="Jane Admin Access",
            description="Jane has full admin access",
        )
        print(f"Created access rule: {jane_admin_rule.id}")

        # Time-based rule (office hours only)
        office_hours_rule = controller.create_access_rule(
            rule_id="office-hours-access",
            user_expression="developers",
            resource_expression="admin-panel",
            permissions=["read"],
            time_constraints={
                "timeWindows": [{"startTime": "09:00", "endTime": "17:00"}],
                "daysOfWeek": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
            },
            name="Office Hours Access",
            description="Developers can access admin panel during office hours",
        )
        print(f"Created time-based rule: {office_hours_rule.id}")

        # 4. Check access permissions
        print("\n🔍 Checking access permissions...")

        # Check John's access to user service API
        john_api_access = controller.check_access(
            user_id="john_doe", resource_id="user-service-api", permission="read"
        )
        print(f"John can read user-service-api: {john_api_access.allowed}")
        print(f"  Reason: {john_api_access.reason}")

        # Check Jane's access to admin panel
        jane_admin_access = controller.check_access(
            user_id="jane_smith", resource_id="admin-panel", permission="admin"
        )
        print(f"Jane has admin access to admin-panel: {jane_admin_access.allowed}")
        print(f"  Reason: {jane_admin_access.reason}")

        # Check John's access to admin panel (should fail)
        john_admin_access = controller.check_access(
            user_id="john_doe", resource_id="admin-panel", permission="admin"
        )
        print(f"John has admin access to admin-panel: {john_admin_access.allowed}")
        print(f"  Reason: {john_admin_access.reason}")

        # 5. Resolve all user access
        print("\n📋 Resolving complete user access...")

        # Get all of Jane's access permissions
        jane_access = controller.resolve_user_access(
            user_id="jane_smith", include_audit=True
        )
        print(f"Jane has access to {len(jane_access.resolved_access)} resources:")
        for resource_id, permissions in jane_access.resolved_access.items():
            print(f"  {resource_id}: {permissions}")

        print(f"\nAudit trail has {len(jane_access.audit_trail)} steps")

        # 6. List all entities
        print("\n📊 Listing all entities...")

        users = controller.list_users(limit=10)
        print(f"Total users: {len(users)}")

        artifacts = controller.list_artifacts(limit=10)
        print(f"Total artifacts: {len(artifacts)}")

        rules = controller.list_access_rules(limit=10)
        print(f"Total access rules: {len(rules)}")

        print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main()
