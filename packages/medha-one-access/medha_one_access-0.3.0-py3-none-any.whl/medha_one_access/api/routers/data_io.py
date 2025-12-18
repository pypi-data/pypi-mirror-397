"""
Data Import/Export API Routes

FastAPI routes for importing and exporting access control data.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from medha_one_access.api.dependencies import get_controller
from medha_one_access.core.controller import AccessController
from medha_one_access.core.schemas import (
    ImportData,
    ExportRequest,
    UserInDB,
    ArtifactInDB,
    AccessRuleInDB,
)
from medha_one_access.core.models import User, Artifact, AccessRule
from medha_one_access.core.exceptions import MedhaAccessError
from medha_one_access.core.compatibility import model_dump

router = APIRouter()


@router.post("/import")
async def import_data(import_file: UploadFile = File(...), controller: AccessController = Depends(get_controller)):
    """
    Import users, artifacts, and access rules from a JSON file
    """
    try:
        # Read and parse JSON file
        contents = await import_file.read()
        data = json.loads(contents)

        # Process the data
        import_data_obj = ImportData(**data)

        with controller.get_session() as session:
            # Statistics for response
            stats = {
                "users": {
                    "total": 0,
                    "created": 0,
                    "updated": 0,
                    "failed": 0,
                    "skipped": 0,
                },
                "artifacts": {
                    "total": 0,
                    "created": 0,
                    "updated": 0,
                    "failed": 0,
                    "skipped": 0,
                },
                "access_rules": {
                    "total": 0,
                    "created": 0,
                    "updated": 0,
                    "failed": 0,
                    "skipped": 0,
                },
            }

            # Import users if provided
            if import_data_obj.users:
                stats["users"]["total"] = len(import_data_obj.users)

                for user_data in import_data_obj.users:
                    try:
                        # Check if user already exists
                        existing_user = (
                            session.query(User).filter(User.id == user_data.id).first()
                        )

                        if existing_user:
                            # Update existing user with new data
                            for key, value in model_dump(
                                user_data, exclude_unset=True
                            ).items():
                                if value is not None:
                                    setattr(existing_user, key, value)
                            stats["users"]["updated"] += 1
                        else:
                            # Create new user
                            user_dict = model_dump(user_data)
                            db_user = User(**user_dict)
                            session.add(db_user)
                            stats["users"]["created"] += 1

                    except Exception as e:
                        stats["users"]["failed"] += 1

            # Import artifacts if provided
            if import_data_obj.artifacts:
                stats["artifacts"]["total"] = len(import_data_obj.artifacts)

                for artifact_data in import_data_obj.artifacts:
                    try:
                        # Check if artifact already exists
                        existing_artifact = (
                            session.query(Artifact)
                            .filter(Artifact.id == artifact_data.id)
                            .first()
                        )

                        if existing_artifact:
                            # Update existing artifact with new data
                            for key, value in model_dump(
                                artifact_data, exclude_unset=True
                            ).items():
                                if value is not None:
                                    setattr(existing_artifact, key, value)
                            stats["artifacts"]["updated"] += 1
                        else:
                            # Create new artifact
                            artifact_dict = model_dump(artifact_data)
                            db_artifact = Artifact(**artifact_dict)
                            session.add(db_artifact)
                            stats["artifacts"]["created"] += 1

                    except Exception as e:
                        stats["artifacts"]["failed"] += 1

            # Import access rules if provided
            if import_data_obj.access_rules:
                stats["access_rules"]["total"] = len(import_data_obj.access_rules)

                for rule_data in import_data_obj.access_rules:
                    try:
                        # Check if rule already exists
                        existing_rule = (
                            session.query(AccessRule)
                            .filter(AccessRule.id == rule_data.id)
                            .first()
                        )

                        if existing_rule:
                            # Update existing rule with new data
                            for key, value in model_dump(
                                rule_data, exclude_unset=True
                            ).items():
                                if value is not None:
                                    setattr(existing_rule, key, value)
                            stats["access_rules"]["updated"] += 1
                        else:
                            # Create new rule
                            rule_dict = model_dump(rule_data)
                            db_rule = AccessRule(**rule_dict)
                            session.add(db_rule)
                            stats["access_rules"]["created"] += 1

                    except Exception as e:
                        stats["access_rules"]["failed"] += 1

            # Commit all changes
            session.commit()

            # Return import statistics
            return {
                "status": "success",
                "message": "Data import completed",
                "statistics": stats,
            }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/export")
async def export_data(export_request: ExportRequest, controller: AccessController = Depends(get_controller)):
    """
    Export users, artifacts, and access rules as JSON
    """
    try:
        with controller.get_session() as session:
            result = {}

            # Export users if requested
            if export_request.include_users:
                user_query = session.query(User)

                # Filter by specific user IDs if provided
                if export_request.user_ids:
                    user_query = user_query.filter(User.id.in_(export_request.user_ids))

                users = user_query.all()
                result["users"] = [
                    {
                        "id": user.id,
                        "type": user.type,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "department": user.department,
                        "role": user.role,
                        "expression": user.expression,
                        "manager_id": user.manager_id,
                        "parent_group_id": user.parent_group_id,
                        "owner_id": user.owner_id,
                        "description": user.description,
                        "active": user.active,
                        "user_metadata": user.user_metadata,
                    }
                    for user in users
                ]

            # Export artifacts if requested
            if export_request.include_artifacts:
                artifact_query = session.query(Artifact)

                # Filter by specific artifact IDs if provided
                if export_request.artifact_ids:
                    artifact_query = artifact_query.filter(
                        Artifact.id.in_(export_request.artifact_ids)
                    )

                artifacts = artifact_query.all()
                result["artifacts"] = [
                    {
                        "id": artifact.id,
                        "type": artifact.type,
                        "name": artifact.name,
                        "description": artifact.description,
                        "application": artifact.application,  # Updated from category
                        "owner_id": artifact.owner_id,
                        "parent_group_id": artifact.parent_group_id,
                        "expression": artifact.expression,
                        "active": artifact.active,
                        "artifact_metadata": artifact.artifact_metadata,
                    }
                    for artifact in artifacts
                ]

            # Export access rules if requested
            if export_request.include_access_rules:
                rule_query = session.query(AccessRule)

                # Filter by specific rule IDs if provided
                if export_request.rule_ids:
                    rule_query = rule_query.filter(
                        AccessRule.id.in_(export_request.rule_ids)
                    )

                rules = rule_query.all()
                result["access_rules"] = [
                    {
                        "id": rule.id,
                        "name": rule.name,
                        "description": rule.description,
                        "user_expression": rule.user_expression,
                        "resource_expression": rule.resource_expression,
                        "permissions": rule.permissions,
                        "is_direct": rule.is_direct,
                        "parent_rule_id": rule.parent_rule_id,
                        "owner_id": rule.owner_id,
                        "time_constraints": rule.time_constraints,
                        "active": rule.active,
                        "rule_metadata": rule.rule_metadata,
                    }
                    for rule in rules
                ]

            # Add export metadata
            result["metadata"] = {
                "exportDate": datetime.now().isoformat(),
                "userCount": len(result.get("users", [])),
                "artifactCount": len(result.get("artifacts", [])),
                "ruleCount": len(result.get("access_rules", [])),
            }

            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/backup")
async def create_full_backup(controller: AccessController = Depends(get_controller)):
    """
    Create a complete backup of all data in the system
    """
    try:
        with controller.get_session() as session:
            backup_data = {}

            # Backup all users
            users = session.query(User).all()
            backup_data["users"] = [
                {
                    "id": user.id,
                    "type": user.type,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "department": user.department,
                    "role": user.role,
                    "expression": user.expression,
                    "manager_id": user.manager_id,
                    "parent_group_id": user.parent_group_id,
                    "owner_id": user.owner_id,
                    "description": user.description,
                    "active": user.active,
                    "user_metadata": user.user_metadata,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                    "updated_at": (
                        user.updated_at.isoformat() if user.updated_at else None
                    ),
                }
                for user in users
            ]

            # Backup all artifacts
            artifacts = session.query(Artifact).all()
            backup_data["artifacts"] = [
                {
                    "id": artifact.id,
                    "type": artifact.type,
                    "name": artifact.name,
                    "description": artifact.description,
                    "application": artifact.application,  # Updated from category
                    "owner_id": artifact.owner_id,
                    "parent_group_id": artifact.parent_group_id,
                    "expression": artifact.expression,
                    "active": artifact.active,
                    "artifact_metadata": artifact.artifact_metadata,
                    "created_at": (
                        artifact.created_at.isoformat() if artifact.created_at else None
                    ),
                    "updated_at": (
                        artifact.updated_at.isoformat() if artifact.updated_at else None
                    ),
                }
                for artifact in artifacts
            ]

            # Backup all access rules
            rules = session.query(AccessRule).all()
            backup_data["access_rules"] = [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "user_expression": rule.user_expression,
                    "resource_expression": rule.resource_expression,
                    "permissions": rule.permissions,
                    "is_direct": rule.is_direct,
                    "parent_rule_id": rule.parent_rule_id,
                    "owner_id": rule.owner_id,
                    "time_constraints": rule.time_constraints,
                    "active": rule.active,
                    "rule_metadata": rule.rule_metadata,
                    "created_at": (
                        rule.created_at.isoformat() if rule.created_at else None
                    ),
                    "updated_at": (
                        rule.updated_at.isoformat() if rule.updated_at else None
                    ),
                }
                for rule in rules
            ]

            # Add backup metadata
            backup_data["metadata"] = {
                "backupDate": datetime.now().isoformat(),
                "version": "1.0",
                "userCount": len(backup_data["users"]),
                "artifactCount": len(backup_data["artifacts"]),
                "ruleCount": len(backup_data["access_rules"]),
            }

            return JSONResponse(
                content=backup_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=medhaone_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                },
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/restore")
async def restore_from_backup(
    controller: AccessController = Depends(get_controller),
    backup_file: UploadFile = File(...),
    clear_existing: bool = Query(
        False, description="Clear all existing data before restore"
    ),
):
    """
    Restore data from a backup file
    """
    try:
        # Read and parse JSON file
        contents = await backup_file.read()
        backup_data = json.loads(contents)

        # Validate backup data
        if "metadata" not in backup_data or "version" not in backup_data["metadata"]:
            raise HTTPException(status_code=400, detail="Invalid backup file format")

        with controller.get_session() as session:
            # Clear existing data if requested
            if clear_existing:
                session.query(AccessRule).delete()
                session.query(Artifact).delete()
                session.query(User).delete()
                session.commit()

            restored_counts = {"users": 0, "artifacts": 0, "access_rules": 0}

            # Restore users
            if "users" in backup_data:
                for user_data in backup_data["users"]:
                    # Remove timestamps from data
                    user_data = {
                        k: v
                        for k, v in user_data.items()
                        if k not in ["created_at", "updated_at"]
                    }

                    # Check if user already exists
                    existing_user = (
                        session.query(User).filter(User.id == user_data["id"]).first()
                    )

                    if existing_user:
                        # Update existing user
                        for key, value in user_data.items():
                            if hasattr(existing_user, key):
                                setattr(existing_user, key, value)
                    else:
                        # Create new user
                        db_user = User(**user_data)
                        session.add(db_user)

                    restored_counts["users"] += 1

            # Restore artifacts
            if "artifacts" in backup_data:
                for artifact_data in backup_data["artifacts"]:
                    # Remove timestamps from data
                    artifact_data = {
                        k: v
                        for k, v in artifact_data.items()
                        if k not in ["created_at", "updated_at"]
                    }

                    # Check if artifact already exists
                    existing_artifact = (
                        session.query(Artifact)
                        .filter(Artifact.id == artifact_data["id"])
                        .first()
                    )

                    if existing_artifact:
                        # Update existing artifact
                        for key, value in artifact_data.items():
                            if hasattr(existing_artifact, key):
                                setattr(existing_artifact, key, value)
                    else:
                        # Create new artifact
                        db_artifact = Artifact(**artifact_data)
                        session.add(db_artifact)

                    restored_counts["artifacts"] += 1

            # Restore access rules
            if "access_rules" in backup_data:
                for rule_data in backup_data["access_rules"]:
                    # Remove timestamps from data
                    rule_data = {
                        k: v
                        for k, v in rule_data.items()
                        if k not in ["created_at", "updated_at"]
                    }

                    # Check if rule already exists
                    existing_rule = (
                        session.query(AccessRule)
                        .filter(AccessRule.id == rule_data["id"])
                        .first()
                    )

                    if existing_rule:
                        # Update existing rule
                        for key, value in rule_data.items():
                            if hasattr(existing_rule, key):
                                setattr(existing_rule, key, value)
                    else:
                        # Create new rule
                        db_rule = AccessRule(**rule_data)
                        session.add(db_rule)

                    restored_counts["access_rules"] += 1

            # Commit all changes
            session.commit()

            return {
                "status": "success",
                "message": "Data restored successfully",
                "statistics": restored_counts,
            }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.get("/validate")
async def validate_data_integrity(controller: AccessController = Depends(get_controller)):
    """
    Validate data integrity across the system
    """
    try:
        with controller.get_session() as session:
            issues = []

            # Check for orphaned users (users with invalid manager_id)
            orphaned_users = (
                session.query(User)
                .filter(
                    User.manager_id.isnot(None),
                    ~User.manager_id.in_(session.query(User.id)),
                )
                .all()
            )

            for user in orphaned_users:
                issues.append(
                    {
                        "type": "orphaned_user",
                        "entity_type": "User",
                        "entity_id": user.id,
                        "issue": f"User has invalid manager_id: {user.manager_id}",
                    }
                )

            # Check for orphaned artifacts (artifacts with invalid parent_group_id)
            orphaned_artifacts = (
                session.query(Artifact)
                .filter(
                    Artifact.parent_group_id.isnot(None),
                    ~Artifact.parent_group_id.in_(session.query(Artifact.id)),
                )
                .all()
            )

            for artifact in orphaned_artifacts:
                issues.append(
                    {
                        "type": "orphaned_artifact",
                        "entity_type": "Artifact",
                        "entity_id": artifact.id,
                        "issue": f"Artifact has invalid parent_group_id: {artifact.parent_group_id}",
                    }
                )

            # Check for invalid expressions
            users_with_expressions = (
                session.query(User)
                .filter(User.type == "USERGROUP", User.expression.isnot(None))
                .all()
            )

            artifacts_with_expressions = (
                session.query(Artifact)
                .filter(
                    Artifact.type == "RESOURCEGROUP", Artifact.expression.isnot(None)
                )
                .all()
            )

            # Validate user group expressions
            for user in users_with_expressions:
                try:
                    controller.validate_expression(user.expression, "user")
                except Exception as e:
                    issues.append(
                        {
                            "type": "invalid_expression",
                            "entity_type": "User",
                            "entity_id": user.id,
                            "issue": f"Invalid expression: {str(e)}",
                        }
                    )

            # Validate resource group expressions
            for artifact in artifacts_with_expressions:
                try:
                    controller.validate_expression(artifact.expression, "resource")
                except Exception as e:
                    issues.append(
                        {
                            "type": "invalid_expression",
                            "entity_type": "Artifact",
                            "entity_id": artifact.id,
                            "issue": f"Invalid expression: {str(e)}",
                        }
                    )

            return {
                "status": "success",
                "issues_found": len(issues),
                "issues": issues,
                "validation_date": datetime.now().isoformat(),
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
