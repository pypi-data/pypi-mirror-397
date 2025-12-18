"""
CLI Usage Example for MedhaOne Access Control

Demonstrates command-line interface usage with sample data.
"""

import os
import json
import subprocess
from pathlib import Path


def create_sample_data():
    """Create sample data file for importing."""

    sample_data = {
        "users": [
            {
                "user_id": "alice",
                "type": "USER",
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@example.com",
                "department": "Marketing",
                "role": "Marketing Manager",
            },
            {
                "user_id": "bob",
                "type": "USER",
                "first_name": "Bob",
                "last_name": "Wilson",
                "email": "bob.wilson@example.com",
                "department": "Sales",
                "role": "Sales Representative",
            },
            {
                "user_id": "marketing_team",
                "type": "USERGROUP",
                "expression": "alice",
                "description": "Marketing team members",
            },
        ],
        "artifacts": [
            {
                "artifact_id": "crm-system",
                "type": "RESOURCE",
                "name": "CRM System",
                "description": "Customer Relationship Management System",
                "application": "CRM",
            },
            {
                "artifact_id": "analytics-dashboard",
                "type": "RESOURCE",
                "name": "Analytics Dashboard",
                "description": "Business analytics and reporting dashboard",
                "application": "Analytics",
            },
            {
                "artifact_id": "business_tools",
                "type": "RESOURCEGROUP",
                "name": "Business Tools",
                "expression": "crm-system + analytics-dashboard",
                "description": "All business productivity tools",
            },
        ],
        "access_rules": [
            {
                "rule_id": "marketing-crm-access",
                "user_expression": "marketing_team",
                "resource_expression": "crm-system",
                "permissions": ["read", "write"],
                "name": "Marketing CRM Access",
                "description": "Marketing team can access CRM system",
            },
            {
                "rule_id": "alice-analytics-access",
                "user_expression": "alice",
                "resource_expression": "analytics-dashboard",
                "permissions": ["read", "admin"],
                "name": "Alice Analytics Access",
                "description": "Alice has admin access to analytics dashboard",
            },
        ],
    }

    # Write sample data to file
    data_file = Path("sample_data.json")
    with open(data_file, "w") as f:
        json.dump(sample_data, f, indent=2)

    return data_file


def run_cli_command(command, database_url="sqlite:///cli_example.db"):
    """Run a CLI command and return the output."""

    env = os.environ.copy()
    env["DATABASE_URL"] = database_url

    try:
        result = subprocess.run(
            ["python", "-m", "medha_one_access.cli"] + command,
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return None


def main():
    """Demonstrate CLI usage."""

    print("🚀 MedhaOne Access Control - CLI Usage Example\n")

    database_url = "sqlite:///cli_example.db"

    # 1. Initialize database
    print("📊 Initializing database...")
    output = run_cli_command(["init-db"], database_url)
    if output:
        print(output)

    # 2. Check status
    print("🔍 Checking system status...")
    output = run_cli_command(["status"], database_url)
    if output:
        print(output)

    # 3. Create sample data file
    print("📝 Creating sample data file...")
    data_file = create_sample_data()
    print(f"Created: {data_file}")

    # 4. Import data
    print("📥 Importing sample data...")
    output = run_cli_command(["import-data", str(data_file)], database_url)
    if output:
        print(output)

    # 5. Check user access
    print("🔐 Checking Alice's access...")
    output = run_cli_command(
        ["check-user-access", "alice", "--include-audit"], database_url
    )
    if output:
        print(output)

    # 6. Validate expressions
    print("✅ Validating user expression...")
    output = run_cli_command(
        ["validate-expression", "marketing_team", "USER"], database_url
    )
    if output:
        print(output)

    print("✅ Validating resource expression...")
    output = run_cli_command(
        ["validate-expression", "business_tools", "RESOURCE"], database_url
    )
    if output:
        print(output)

    # 7. Export data
    print("📤 Exporting data...")
    export_file = "exported_data.json"
    output = run_cli_command(["export-data", export_file], database_url)
    if output:
        print(output)

    # 8. Show final status
    print("📊 Final system status...")
    output = run_cli_command(["status"], database_url)
    if output:
        print(output)

    # Clean up
    try:
        os.remove(data_file)
        os.remove(export_file)
    except OSError:
        pass

    print("\n✅ CLI example completed successfully!")
    print(f"\nTo try the CLI yourself, run:")
    print(f"  export DATABASE_URL='{database_url}'")
    print(f"  python -m medha_one_access.cli --help")


if __name__ == "__main__":
    main()
