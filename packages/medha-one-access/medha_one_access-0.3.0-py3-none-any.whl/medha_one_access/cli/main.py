"""
MedhaOne Access Control CLI Main Module

Command line interface for database management and access control operations.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import click
from sqlalchemy.exc import OperationalError

from medha_one_access.core.database import DatabaseManager, DatabaseConfig
from medha_one_access.core.controller import AccessController
from medha_one_access.core.compatibility import model_dump
from medha_one_access.core.exceptions import (
    MedhaAccessError,
    DatabaseConnectionError,
    ConfigurationError,
)


# CLI context class
class CLIContext:
    """CLI context for sharing state between commands."""

    def __init__(self):
        self.database_url: Optional[str] = None
        self.controller: Optional[AccessController] = None


# Pass context between commands
pass_context = click.make_pass_decorator(CLIContext, ensure=True)


@click.group()
@click.option(
    "--database-url", "-d", envvar="DATABASE_URL", help="Database connection URL"
)
@click.option(
    "--config-file", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@pass_context
def app(
    ctx: CLIContext,
    database_url: Optional[str],
    config_file: Optional[str],
    verbose: bool,
):
    """MedhaOne Access Control CLI - Database and access management tools."""

    # Set up logging level
    if verbose:
        import logging

        logging.basicConfig(level=logging.INFO)

    # Load configuration
    if config_file:
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                database_url = database_url or config.get("database_url")
        except Exception as e:
            click.echo(f"Error loading config file: {e}", err=True)
            sys.exit(1)

    # Set database URL
    if database_url:
        ctx.database_url = database_url
    else:
        try:
            ctx.database_url = DatabaseConfig.from_env()
        except ConfigurationError as e:
            click.echo(f"Database configuration error: {e.message}", err=True)
            click.echo(
                "Set DATABASE_URL environment variable or use --database-url option",
                err=True,
            )
            sys.exit(1)


@app.command()
@pass_context
def init_db(ctx: CLIContext):
    """Initialize the database schema."""
    click.echo("Initializing database schema...")

    try:
        db_manager = DatabaseManager(ctx.database_url)
        db_manager.create_all()
        click.echo("✅ Database schema initialized successfully")

        # Show database info
        info = db_manager.get_database_info()
        click.echo(f"Database: {info['database_url']}")

        db_manager.close()

    except DatabaseConnectionError as e:
        click.echo(f"❌ Database connection error: {e.message}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error initializing database: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@pass_context
def status(ctx: CLIContext):
    """Show database and system status."""
    click.echo("Checking system status...")

    try:
        db_manager = DatabaseManager(ctx.database_url)
        info = db_manager.get_database_info()

        click.echo("\n🔍 System Status:")
        click.echo(f"Database URL: {info['database_url']}")
        click.echo(f"Engine: {info['engine']}")
        click.echo(f"Tables exist: {'✅' if info['tables_exist'] else '❌'}")

        if info.get("table_counts"):
            click.echo("\n📊 Table Counts:")
            for table, count in info["table_counts"].items():
                click.echo(f"  {table}: {count}")

        if info.get("error"):
            click.echo(f"\n❌ Error: {info['error']}")

        db_manager.close()

    except Exception as e:
        click.echo(f"❌ Error checking status: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@click.argument("revision", default="head")
@pass_context
def migrate(ctx: CLIContext, revision: str):
    """Run database migrations."""
    click.echo(f"Running migrations to {revision}...")

    try:
        # Use Alembic programmatically
        from alembic.config import Config
        from alembic import command

        # Find alembic.ini file in the package
        package_dir = Path(__file__).parent.parent
        alembic_cfg_path = package_dir / "migrations" / "alembic.ini"

        if not alembic_cfg_path.exists():
            click.echo("❌ Alembic configuration not found", err=True)
            sys.exit(1)

        # Set up Alembic config
        alembic_cfg = Config(str(alembic_cfg_path))
        alembic_cfg.set_main_option("sqlalchemy.url", ctx.database_url)

        # Run migration
        command.upgrade(alembic_cfg, revision)
        click.echo("✅ Migrations completed successfully")

    except Exception as e:
        click.echo(f"❌ Migration error: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@click.argument("message")
@pass_context
def create_migration(ctx: CLIContext, message: str):
    """Create a new migration file."""
    click.echo(f"Creating migration: {message}")

    try:
        from alembic.config import Config
        from alembic import command

        # Find alembic.ini file
        package_dir = Path(__file__).parent.parent
        alembic_cfg_path = package_dir / "migrations" / "alembic.ini"

        # Set up Alembic config
        alembic_cfg = Config(str(alembic_cfg_path))
        alembic_cfg.set_main_option("sqlalchemy.url", ctx.database_url)

        # Create revision
        command.revision(alembic_cfg, message=message, autogenerate=True)
        click.echo("✅ Migration file created successfully")

    except Exception as e:
        click.echo(f"❌ Error creating migration: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@click.argument("file_path", type=click.Path(exists=True))
@pass_context
def import_data(ctx: CLIContext, file_path: str):
    """Import users, artifacts, and access rules from JSON file."""
    click.echo(f"Importing data from {file_path}...")

    try:
        # Load JSON data
        with open(file_path, "r") as f:
            data = json.load(f)

        # Create controller
        controller = AccessController(ctx.database_url)
        stats = {"users": 0, "artifacts": 0, "access_rules": 0, "errors": 0}

        # Import users
        if "users" in data:
            click.echo(f"Importing {len(data['users'])} users...")
            for user_data in data["users"]:
                try:
                    controller.create_user(**user_data)
                    stats["users"] += 1
                except MedhaAccessError as e:
                    click.echo(f"Warning: {e.message}", err=True)
                    stats["errors"] += 1

        # Import artifacts
        if "artifacts" in data:
            click.echo(f"Importing {len(data['artifacts'])} artifacts...")
            for artifact_data in data["artifacts"]:
                try:
                    controller.create_artifact(**artifact_data)
                    stats["artifacts"] += 1
                except MedhaAccessError as e:
                    click.echo(f"Warning: {e.message}", err=True)
                    stats["errors"] += 1

        # Import access rules
        if "access_rules" in data:
            click.echo(f"Importing {len(data['access_rules'])} access rules...")
            for rule_data in data["access_rules"]:
                try:
                    controller.create_access_rule(**rule_data)
                    stats["access_rules"] += 1
                except MedhaAccessError as e:
                    click.echo(f"Warning: {e.message}", err=True)
                    stats["errors"] += 1

        click.echo("\n✅ Import completed:")
        click.echo(f"  Users: {stats['users']}")
        click.echo(f"  Artifacts: {stats['artifacts']}")
        click.echo(f"  Access Rules: {stats['access_rules']}")
        if stats["errors"] > 0:
            click.echo(f"  Errors: {stats['errors']}")

    except Exception as e:
        click.echo(f"❌ Import error: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@click.argument("file_path", type=click.Path())
@click.option(
    "--include-users", is_flag=True, default=True, help="Include users in export"
)
@click.option(
    "--include-artifacts",
    is_flag=True,
    default=True,
    help="Include artifacts in export",
)
@click.option(
    "--include-rules", is_flag=True, default=True, help="Include access rules in export"
)
@pass_context
def export_data(
    ctx: CLIContext,
    file_path: str,
    include_users: bool,
    include_artifacts: bool,
    include_rules: bool,
):
    """Export users, artifacts, and access rules to JSON file."""
    click.echo(f"Exporting data to {file_path}...")

    try:
        controller = AccessController(ctx.database_url)
        export_data = {}

        # Export users
        if include_users:
            users = controller.list_users(limit=10000)
            export_data["users"] = [model_dump(user) for user in users]
            click.echo(f"Exported {len(users)} users")

        # Export artifacts
        if include_artifacts:
            artifacts = controller.list_artifacts(limit=10000)
            export_data["artifacts"] = [
                model_dump(artifact) for artifact in artifacts
            ]
            click.echo(f"Exported {len(artifacts)} artifacts")

        # Export access rules
        if include_rules:
            rules = controller.list_access_rules(limit=10000)
            export_data["access_rules"] = [model_dump(rule) for rule in rules]
            click.echo(f"Exported {len(rules)} access rules")

        # Add metadata
        export_data["metadata"] = {
            "export_date": str(datetime.now()),
            "version": "0.1.0",
            "total_users": len(export_data.get("users", [])),
            "total_artifacts": len(export_data.get("artifacts", [])),
            "total_rules": len(export_data.get("access_rules", [])),
        }

        # Write to file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        click.echo(f"✅ Data exported successfully to {file_path}")

    except Exception as e:
        click.echo(f"❌ Export error: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@click.argument("user_id")
@click.option("--include-audit", is_flag=True, help="Include audit trail in output")
@pass_context
def check_user_access(ctx: CLIContext, user_id: str, include_audit: bool):
    """Check what resources a user can access."""
    click.echo(f"Checking access for user: {user_id}")

    try:
        controller = AccessController(ctx.database_url)
        result = controller.resolve_user_access(
            user_id, include_audit=include_audit
        )

        click.echo(f"\n👤 User: {result['user_id']}")
        click.echo(f"🕒 Evaluation Time: {result['evaluation_time']}")
        click.echo(f"📊 Total Resources: {len(result['resolved_access'])}")

        if result['resolved_access']:
            click.echo("\n🔓 Accessible Resources:")
            for resource_id, permissions in result['resolved_access'].items():
                click.echo(f"  {resource_id}: {', '.join(permissions)}")
        else:
            click.echo("\n❌ No accessible resources found")

        if include_audit and result.get('audit_trail'):
            click.echo("\n📋 Audit Trail:")
            for step in result['audit_trail']:
                click.echo(f"  Step: {step['step']}")
                click.echo(f"    Applied Rules: {len(step['appliedRules'])}")
                click.echo(f"    Resources: {len(step['result'])}")

    except MedhaAccessError as e:
        click.echo(f"❌ Error: {e.message}", err=True)
        sys.exit(1)


@app.command()
@click.argument("expression")
@click.argument("expression_type", type=click.Choice(["USER", "RESOURCE"]))
@pass_context
def validate_expression(ctx: CLIContext, expression: str, expression_type: str):
    """Validate an expression and show resolved entities."""
    click.echo(f"Validating {expression_type} expression: {expression}")

    try:
        with AccessController(ctx.database_url) as controller:
            result = controller.validate_expression(expression, expression_type)

            if result["valid"]:
                click.echo("✅ Expression is valid")
                click.echo(f"📊 Resolved Entities ({len(result['resolvedEntities'])}):")
                for entity in result["resolvedEntities"]:
                    click.echo(f"  {entity}")
            else:
                click.echo("❌ Expression is invalid")
                click.echo("Errors:")
                for error in result["errors"]:
                    click.echo(f"  {error}")

    except MedhaAccessError as e:
        click.echo(f"❌ Error: {e.message}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
