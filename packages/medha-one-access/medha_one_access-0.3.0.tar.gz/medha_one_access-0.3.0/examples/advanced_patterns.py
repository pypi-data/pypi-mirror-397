"""
Advanced Usage Patterns for MedhaOne Access Control

Demonstrates complex access patterns, time constraints, and BODMAS resolution.
"""

from datetime import datetime, timedelta
from medha_one_access import AccessController


def main():
    """Demonstrate advanced access control patterns."""

    database_url = "sqlite:///advanced_example.db"

    print("🚀 MedhaOne Access Control - Advanced Patterns Example\n")

    with AccessController(database_url) as controller:

        # Initialize database
        controller.init_database()
        print("✅ Database initialized\n")

        # Create complex organizational structure
        print("🏢 Creating organizational structure...")

        # Individual users
        ceo = controller.create_user(
            user_id="ceo",
            type="USER",
            first_name="Sarah",
            last_name="CEO",
            email="ceo@company.com",
            role="Chief Executive Officer",
        )

        manager1 = controller.create_user(
            user_id="manager1",
            type="USER",
            first_name="Mike",
            last_name="Manager",
            email="mike.manager@company.com",
            role="Department Manager",
            manager_id="ceo",
        )

        manager2 = controller.create_user(
            user_id="manager2",
            type="USER",
            first_name="Lisa",
            last_name="Manager",
            email="lisa.manager@company.com",
            role="Department Manager",
            manager_id="ceo",
        )

        dev1 = controller.create_user(
            user_id="dev1",
            type="USER",
            first_name="John",
            last_name="Developer",
            email="john.dev@company.com",
            role="Senior Developer",
            manager_id="manager1",
        )

        dev2 = controller.create_user(
            user_id="dev2",
            type="USER",
            first_name="Jane",
            last_name="Developer",
            email="jane.dev@company.com",
            role="Junior Developer",
            manager_id="manager1",
        )

        analyst = controller.create_user(
            user_id="analyst",
            type="USER",
            first_name="Bob",
            last_name="Analyst",
            email="bob.analyst@company.com",
            role="Business Analyst",
            manager_id="manager2",
        )

        # Complex user groups with expressions
        all_managers = controller.create_user(
            user_id="all_managers",
            type="USERGROUP",
            expression="manager1 + manager2",  # Include both managers
            description="All department managers",
        )

        dev_team = controller.create_user(
            user_id="dev_team",
            type="USERGROUP",
            expression="dev1 + dev2",  # All developers
            description="Development team",
        )

        senior_staff = controller.create_user(
            user_id="senior_staff",
            type="USERGROUP",
            expression="ceo + all_managers + dev1",  # CEO, managers, and senior dev
            description="Senior staff members",
        )

        # Resources with complex grouping
        print("\n📦 Creating resource hierarchy...")

        # Individual resources
        prod_db = controller.create_artifact(
            artifact_id="prod-database",
            type="RESOURCE",
            name="Production Database",
            description="Main production database",
            application="Database",
        )

        staging_db = controller.create_artifact(
            artifact_id="staging-database",
            type="RESOURCE",
            name="Staging Database",
            description="Staging environment database",
            application="Database",
        )

        dev_db = controller.create_artifact(
            artifact_id="dev-database",
            type="RESOURCE",
            name="Development Database",
            description="Development environment database",
            application="Database",
        )

        admin_panel = controller.create_artifact(
            artifact_id="admin-panel",
            type="RESOURCE",
            name="Admin Panel",
            description="Administrative interface",
            application="Admin",
        )

        reports = controller.create_artifact(
            artifact_id="reports-system",
            type="RESOURCE",
            name="Reports System",
            description="Business reporting system",
            application="Reports",
        )

        # Resource groups
        all_databases = controller.create_artifact(
            artifact_id="all_databases",
            type="RESOURCEGROUP",
            name="All Databases",
            expression="prod-database + staging-database + dev-database",
            description="All database environments",
        )

        non_prod_resources = controller.create_artifact(
            artifact_id="non_prod",
            type="RESOURCEGROUP",
            name="Non-Production Resources",
            expression="staging-database + dev-database",
            description="Staging and development resources",
        )

        business_systems = controller.create_artifact(
            artifact_id="business_systems",
            type="RESOURCEGROUP",
            name="Business Systems",
            expression="admin-panel + reports-system",
            description="Business management systems",
        )

        # Complex access rules demonstrating BODMAS
        print("\n🔐 Creating complex access rules...")

        # Rule 1: Senior staff gets read access to all databases
        rule1 = controller.create_access_rule(
            rule_id="senior-db-read",
            user_expression="senior_staff",
            resource_expression="all_databases",
            permissions=["read"],
            name="Senior Staff Database Read",
            description="Senior staff can read all databases",
        )

        # Rule 2: Dev team gets full access to non-prod, but exclude prod
        rule2 = controller.create_access_rule(
            rule_id="dev-nonprod-access",
            user_expression="dev_team",
            resource_expression="non_prod",
            permissions=["read", "write", "delete"],
            name="Dev Team Non-Prod Access",
            description="Developers have full access to non-production resources",
        )

        # Rule 3: Only CEO gets admin access to production
        rule3 = controller.create_access_rule(
            rule_id="ceo-prod-admin",
            user_expression="ceo",
            resource_expression="prod-database",
            permissions=["read", "write", "admin"],
            name="CEO Production Admin",
            description="CEO has full admin access to production database",
        )

        # Rule 4: Managers get business systems access
        rule4 = controller.create_access_rule(
            rule_id="managers-business-access",
            user_expression="all_managers",
            resource_expression="business_systems",
            permissions=["read", "write"],
            name="Managers Business Systems",
            description="Managers can access business systems",
        )

        # Rule 5: Time-based rule - Dev access only during business hours
        now = datetime.now()
        rule5 = controller.create_access_rule(
            rule_id="dev-business-hours",
            user_expression="dev_team",
            resource_expression="staging-database",
            permissions=["read", "write"],
            time_constraints={
                "dateRanges": [
                    {
                        "startDate": now.strftime("%Y-%m-%d"),
                        "endDate": (now + timedelta(days=365)).strftime("%Y-%m-%d"),
                    }
                ],
                "timeWindows": [{"startTime": "08:00", "endTime": "18:00"}],
                "daysOfWeek": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
            },
            name="Dev Business Hours Access",
            description="Developers can access staging during business hours only",
        )

        # Rule 6: Emergency access - analyst gets read-only during weekends
        rule6 = controller.create_access_rule(
            rule_id="analyst-weekend-emergency",
            user_expression="analyst",
            resource_expression="reports-system",
            permissions=["read"],
            time_constraints={"daysOfWeek": ["SATURDAY", "SUNDAY"]},
            name="Analyst Weekend Emergency Access",
            description="Analyst can read reports during weekends for emergencies",
        )

        # Demonstrate BODMAS resolution
        print("\n🧮 Demonstrating BODMAS access resolution...")

        # Test different users' access
        test_users = ["ceo", "manager1", "dev1", "dev2", "analyst"]

        for user_id in test_users:
            print(f"\n👤 Resolving access for {user_id}:")

            try:
                result = controller.resolve_user_access(
                    user_id=user_id, include_audit=True
                )

                print(f"  Total accessible resources: {len(result.resolved_access)}")

                for resource_id, permissions in result.resolved_access.items():
                    print(f"    {resource_id}: {permissions}")

                # Show BODMAS steps
                print(f"  BODMAS resolution steps: {len(result.audit_trail)}")
                for i, step in enumerate(result.audit_trail, 1):
                    step_name = step.get("step", f"Step {i}")
                    applied_rules = len(step.get("appliedRules", []))
                    result_count = len(step.get("result", {}))
                    print(
                        f"    {step_name}: {applied_rules} rules → {result_count} resources"
                    )

            except Exception as e:
                print(f"  Error: {e}")

        # Test specific access checks
        print("\n🔍 Testing specific access scenarios...")

        test_cases = [
            ("dev1", "prod-database", "read", "Should be allowed (senior staff rule)"),
            ("dev1", "prod-database", "admin", "Should be denied (CEO only)"),
            ("dev2", "dev-database", "write", "Should be allowed (dev team rule)"),
            ("manager1", "admin-panel", "write", "Should be allowed (managers rule)"),
            (
                "analyst",
                "staging-database",
                "read",
                "Should be denied (not in any relevant rule)",
            ),
            ("ceo", "prod-database", "admin", "Should be allowed (CEO admin rule)"),
        ]

        for user_id, resource_id, permission, expected in test_cases:
            result = controller.check_access(user_id, resource_id, permission)

            status = "✅" if result.allowed else "❌"
            print(f"{status} {user_id} → {resource_id}:{permission}")
            print(f"    Result: {result.allowed} ({result.reason})")
            print(f"    Expected: {expected}")

        # Show access summaries
        print("\n📊 Access summaries:")

        for user_id in ["ceo", "manager1", "dev1"]:
            try:
                summary = controller.get_access_summary(user_id)
                if summary:
                    print(
                        f"  {user_id}: {summary.total_accessible_resources} resources, "
                        f"{summary.direct_permissions} direct + {summary.inherited_permissions} inherited"
                    )
            except:
                print(f"  {user_id}: No summary available")

        print("\n✅ Advanced patterns example completed successfully!")


if __name__ == "__main__":
    main()
