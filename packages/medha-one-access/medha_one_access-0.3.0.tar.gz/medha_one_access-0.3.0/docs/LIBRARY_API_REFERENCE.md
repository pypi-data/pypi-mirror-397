# MedhaOne Access Library API Reference

## Table of Contents

1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Performance Configuration](#performance-configuration)
4. [User Management](#user-management)
5. [Artifact Management](#artifact-management)
6. [Access Rules Management](#access-rules-management)
7. [Access Resolution](#access-resolution)
8. [Utility Methods](#utility-methods)
9. [Exception Handling](#exception-handling)

## Overview

The MedhaOne Access library provides a complete `AccessController` class for managing users, artifacts, access rules, and performing access resolution. This reference documents all available methods and their usage.

## Configuration

### LibraryConfig

```python
from medha_one_access import LibraryConfig

config = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
    api_prefix="/oneAccess",           # Optional: default "/oneAccess"
    application_name="MyApp",          # Optional: filters all operations
    debug=False,                       # Optional: default False
    # 🚀 Performance optimization settings
    enable_caching=True,               # Optional: enable caching (default: True)
    cache_ttl=300,                    # Optional: cache TTL seconds (default: 300)
    enable_bulk_queries=True,          # Optional: enable bulk operations (default: True)
    enable_audit_trail=False,          # Optional: enable audit trail (default: False)
    max_pool_size=20,                 # Optional: connection pool size (default: 20)
    pool_recycle_time=3600,           # Optional: pool recycle seconds (default: 3600)
)
```

#### Parameters

**Core Settings:**
- `database_url` (str): Database connection URL (required)
- `secret_key` (str): Secret key for encryption (required)
- `api_prefix` (str, optional): API prefix for FastAPI integration (default: "/oneAccess")
- `application_name` (str, optional): Application name for filtering operations
- `debug` (bool, optional): Enable debug mode (default: False)

**🚀 Performance Settings:**
- `enable_caching` (bool, optional): Enable multi-level caching system (default: True)
- `cache_ttl` (int, optional): Cache time-to-live in seconds (default: 300)
- `enable_bulk_queries` (bool, optional): Enable bulk database operations (default: True)
- `enable_audit_trail` (bool, optional): Enable detailed audit trails (default: False for performance)
- `max_pool_size` (int, optional): Database connection pool size (default: 20)
- `pool_recycle_time` (int, optional): Connection recycle time in seconds (default: 3600)

#### Environment Configuration

```python
# Set environment variables:
# Core settings
# MEDHA_DATABASE_URL=postgresql://user:pass@localhost/db
# MEDHA_SECRET_KEY=your-secret-key
# MEDHA_APPLICATION_NAME=MyApp
# MEDHA_API_PREFIX=/oneAccess
# MEDHA_DEBUG=false

# 🚀 Performance settings
# MEDHA_ENABLE_CACHING=true
# MEDHA_CACHE_TTL=300
# MEDHA_ENABLE_BULK_QUERIES=true
# MEDHA_ENABLE_AUDIT_TRAIL=false
# MEDHA_MAX_POOL_SIZE=20
# MEDHA_POOL_RECYCLE_TIME=3600

config = LibraryConfig.from_env()
```

### AccessController

```python
from medha_one_access import AccessController

controller = AccessController(config)
```

## Performance Configuration

The library includes advanced performance optimizations for high-throughput production environments.

### Performance Features

#### Multi-Level Caching System
- **Expression Parsing Cache**: Caches 1000 parsed expressions using LRU
- **Expression Validation Cache**: Caches 500 validation results
- **Session-Level Caching**: Eliminates repeated database queries within operations
- **Global Performance Cache**: 10,000+ items with configurable TTL

#### Database Optimizations
- **Strategic Indexes**: Automatically created on all critical columns
- **Connection Pooling**: Optimized pool sizes with overflow and recycling
- **Bulk Operations**: New methods to reduce N+1 query problems
- **Smart Pre-filtering**: Only processes relevant access rules

#### Algorithm Improvements
- **Rule Pre-filtering**: Filters rules by user/application before BODMAS processing
- **Optional Audit Trail**: Can be disabled for 2-3x performance improvement
- **Memoized Resolution**: Caches expression resolution results across sessions

### High-Performance Configuration

```python
from medha_one_access import LibraryConfig, AccessController

# Production-optimized configuration
config = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
    application_name="MyApp",
    
    # Performance settings for high-load scenarios
    enable_caching=True,        # Enable all caching layers
    cache_ttl=600,             # Cache for 10 minutes (adjust based on data change frequency)
    enable_bulk_queries=True,   # Use bulk operations
    enable_audit_trail=False,   # Disable for maximum speed
    max_pool_size=50,          # High connection pool for concurrency
    pool_recycle_time=1800,    # Recycle connections every 30 minutes
)

controller = AccessController(config)
```

### Performance Benchmarks

| Operation | Before Optimization | After Optimization | Improvement |
|-----------|-------------------|-------------------|-------------|
| Simple access check | ~5ms | ~0.5ms | **10x faster** |
| Complex group resolution | ~500ms | ~50ms | **10x faster** |
| High-load throughput | 100 req/s | 1000+ req/s | **10x improvement** |
| Database queries per operation | 100+ queries | 5-10 queries | **90% reduction** |

### Bulk Operations API

New high-performance bulk methods for processing multiple entities:

```python
# Bulk user retrieval (single query instead of N queries)
user_ids = ["user1", "user2", "user3", ...]
users_dict = controller.get_users_bulk(user_ids)  # Returns {id: UserInDB}

# Bulk artifact retrieval  
artifact_ids = ["res1", "res2", "res3", ...]
artifacts_dict = controller.get_artifacts_bulk(artifact_ids)  # Returns {id: ArtifactInDB}

# Bulk access rule retrieval
rule_ids = ["rule1", "rule2", "rule3", ...]
rules_dict = controller.get_access_rules_bulk(rule_ids)  # Returns {id: AccessRuleInDB}
```

### Cache Management

```python
from medha_one_access.core.cache import get_cache_stats, clear_all_caches, invalidate_user_cache

# Get cache performance statistics
stats = get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
print(f"Cache size: {stats['size']}/{stats['max_size']}")

# Invalidate specific user's cached data (after updates)
invalidated_count = invalidate_user_cache("user@example.com")
print(f"Invalidated {invalidated_count} cache entries")

# Clear all caches (useful for testing)
clear_all_caches()
```

### Performance Tuning Guidelines

#### For Maximum Speed (Production)
```python
config = LibraryConfig(
    database_url="postgresql://...",
    secret_key="...",
    enable_caching=True,          # Enable all caching
    cache_ttl=600,               # Longer cache for stable data
    enable_audit_trail=False,     # Disable audit for speed
    max_pool_size=50,            # High concurrency support
)

# Fast access checks (no audit overhead)
access = controller.resolve_user_access("user@example.com")
has_permission = controller.check_access("user@example.com", "resource1", "READ")
```

#### For Development/Debugging
```python
config = LibraryConfig(
    database_url="postgresql://...",
    secret_key="...",
    enable_caching=False,        # Disable caching for testing
    enable_audit_trail=True,     # Enable detailed audit
    debug=True,                 # Enable SQL query logging
)

# Get detailed audit trail
access = controller.resolve_user_access("user@example.com", include_audit=True)
print("Resolution steps:", access['audit_trail'])
```

## User Management

### create_user(user_data, upsert=False)

Create a new user or user group.

**Parameters:**
- `user_data` (Union[UserCreate, Dict]): User data
- `upsert` (bool): If True, update existing user instead of raising error

**Returns:** `UserInDB` - Created user object

**Example:**
```python
# Individual user
user = controller.create_user({
    "id": "john.doe",
    "type": "USER",
    "email": "john.doe@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering",
    "role": "Senior Developer",
    "active": True
})

# User group
group = controller.create_user({
    "id": "senior_developers",
    "type": "USERGROUP",
    "name": "Senior Developers",
    "expression": "john.doe+jane.smith+alice.wilson",
    "description": "Senior development team",
    "active": True
})

# Upsert (create or update)
user = controller.create_user(user_data, upsert=True)
```

### get_user(user_id)

Retrieve a user by ID.

**Parameters:**
- `user_id` (str): User ID

**Returns:** `Optional[UserInDB]` - User object or None if not found

**Example:**
```python
user = controller.get_user("john.doe")
if user:
    print(f"Found: {user.first_name} {user.last_name}")
```

### update_user(user_id, user_data)

Update an existing user.

**Parameters:**
- `user_id` (str): User ID
- `user_data` (Union[UserUpdate, Dict]): Update data

**Returns:** `Optional[UserInDB]` - Updated user object or None if not found

**Example:**
```python
updated_user = controller.update_user("john.doe", {
    "role": "Lead Developer",
    "department": "Platform Engineering",
    "active": True
})
```

### delete_user(user_id)

Delete a user.

**Parameters:**
- `user_id` (str): User ID

**Returns:** `bool` - True if deleted, False if not found

**Example:**
```python
success = controller.delete_user("john.doe")
print(f"User deleted: {success}")
```

### list_users(skip=0, limit=100, user_type=None)

List users with optional filtering and pagination.

**Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Maximum records to return
- `user_type` (str, optional): Filter by "USER" or "USERGROUP"

**Returns:** `List[UserInDB]` - List of user objects

**Example:**
```python
all_users = controller.list_users()
users_only = controller.list_users(user_type="USER")
groups_only = controller.list_users(user_type="USERGROUP")
paginated = controller.list_users(skip=20, limit=10)
```

## Artifact Management

### create_artifact(artifact_data)

Create a new artifact (resource or resource group).

**Parameters:**
- `artifact_data` (Union[ArtifactCreate, Dict]): Artifact data

**Returns:** `ArtifactInDB` - Created artifact object

**Example:**
```python
# Individual resource
artifact = controller.create_artifact({
    "id": "sales_dashboard",
    "type": "RESOURCE",
    "name": "Sales Analytics Dashboard",
    "description": "Real-time sales performance dashboard",
    "application": "Analytics",
    "active": True
})

# Resource group
group = controller.create_artifact({
    "id": "analytics_suite",
    "type": "RESOURCEGROUP",
    "name": "Analytics Suite",
    "expression": "sales_dashboard+marketing_dashboard+financial_reports",
    "description": "Complete analytics platform",
    "active": True
})
```

### get_artifact(artifact_id)

Retrieve an artifact by ID.

**Parameters:**
- `artifact_id` (str): Artifact ID

**Returns:** `Optional[ArtifactInDB]` - Artifact object or None if not found

**Example:**
```python
artifact = controller.get_artifact("sales_dashboard")
if artifact:
    print(f"Found: {artifact.name}")
```

### update_artifact(artifact_id, artifact_data)

Update an existing artifact.

**Parameters:**
- `artifact_id` (str): Artifact ID
- `artifact_data` (Dict[str, Any]): Update data

**Returns:** `ArtifactInDB` - Updated artifact object

**Example:**
```python
updated_artifact = controller.update_artifact("sales_dashboard", {
    "name": "Enhanced Sales Dashboard",
    "description": "Advanced analytics with ML insights",
    "active": True
})
```

### delete_artifact(artifact_id)

Delete an artifact.

**Parameters:**
- `artifact_id` (str): Artifact ID

**Returns:** `bool` - True if deleted, False if not found

**Example:**
```python
success = controller.delete_artifact("sales_dashboard")
print(f"Artifact deleted: {success}")
```

### list_artifacts(skip=0, limit=100, artifact_type=None, application=None, active=None)

List artifacts with filtering and pagination.

**Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Maximum records to return
- `artifact_type` (str, optional): Filter by "RESOURCE" or "RESOURCEGROUP"
- `application` (str, optional): Filter by application name
- `active` (bool, optional): Filter by active status

**Returns:** `List[ArtifactInDB]` - List of artifact objects

**Example:**
```python
all_artifacts = controller.list_artifacts()
resources_only = controller.list_artifacts(artifact_type="RESOURCE")
groups_only = controller.list_artifacts(artifact_type="RESOURCEGROUP")
app_artifacts = controller.list_artifacts(application="Analytics")
active_only = controller.list_artifacts(active=True)
paginated = controller.list_artifacts(skip=0, limit=50)
```

## Access Rules Management

### create_access_rule(rule_data)

Create a new access rule.

**Parameters:**
- `rule_data` (Union[AccessRuleCreate, Dict]): Rule data

**Returns:** `AccessRuleInDB` - Created rule object

**Example:**
```python
rule = controller.create_access_rule({
    "id": "analytics_access",
    "name": "Analytics Team Access",
    "user_expression": "data_analysts+senior_developers",
    "resource_expression": "analytics_suite-sensitive_financial_data",
    "permissions": ["READ", "WRITE", "EXPORT"],
    "application": "Analytics",
    "active": True,
    "time_constraints": {
        "startTime": "08:00",
        "endTime": "18:00",
        "daysOfWeek": [1, 2, 3, 4, 5],  # Monday-Friday
        "startDate": "2024-01-01",
        "endDate": "2024-12-31"
    }
})
```

### get_access_rule(rule_id)

Retrieve an access rule by ID.

**Parameters:**
- `rule_id` (str): Rule ID

**Returns:** `Optional[AccessRuleInDB]` - Rule object or None if not found

**Example:**
```python
rule = controller.get_access_rule("analytics_access")
if rule:
    print(f"Found rule: {rule.name}")
```

### update_access_rule(rule_id, rule_data)

Update an existing access rule.

**Parameters:**
- `rule_id` (str): Rule ID
- `rule_data` (Dict[str, Any]): Update data

**Returns:** `AccessRuleInDB` - Updated rule object

**Example:**
```python
updated_rule = controller.update_access_rule("analytics_access", {
    "permissions": ["READ", "WRITE", "EXPORT", "ADMIN"],
    "user_expression": "data_analysts+senior_developers+team_leads",
    "active": True
})
```

### delete_access_rule(rule_id)

Delete an access rule.

**Parameters:**
- `rule_id` (str): Rule ID

**Returns:** `bool` - True if deleted, False if not found

**Example:**
```python
success = controller.delete_access_rule("analytics_access")
print(f"Rule deleted: {success}")
```

### list_access_rules(user_expression=None, resource_expression=None, application=None, active=None, skip=0, limit=100)

List access rules with filtering and pagination.

**Parameters:**
- `user_expression` (str, optional): Filter by user expression substring
- `resource_expression` (str, optional): Filter by resource expression substring
- `application` (str, optional): Filter by application name
- `active` (bool, optional): Filter by active status
- `skip` (int): Number of records to skip
- `limit` (int): Maximum records to return

**Returns:** `List[AccessRuleInDB]` - List of rule objects

**Example:**
```python
all_rules = controller.list_access_rules()
filtered_rules = controller.list_access_rules(
    user_expression="developers",
    resource_expression="dashboards",
    application="Analytics",
    active=True
)
paginated_rules = controller.list_access_rules(skip=0, limit=25)
```

## Access Resolution

### check_access(user_id, resource_id, permission, evaluation_time=None)

Check if a user has specific permission on a resource.

**Parameters:**
- `user_id` (str): User ID
- `resource_id` (str): Resource ID
- `permission` (str): Permission to check
- `evaluation_time` (datetime, optional): Time for evaluation (default: now)

**Returns:** `bool` - True if access is granted

**Example:**
```python
has_read = controller.check_access("john.doe", "sales_dashboard", "READ")
has_write = controller.check_access("john.doe", "sales_dashboard", "WRITE")
print(f"John can read: {has_read}, write: {has_write}")
```

### resolve_user_access(user_id, include_audit=False, evaluation_time=None)

Get complete access resolution for a user.

**Parameters:**
- `user_id` (str): User ID
- `include_audit` (bool): Include audit trail
- `evaluation_time` (datetime, optional): Time for evaluation

**Returns:** `Dict[str, Any]` - Complete access resolution

**Example:**
```python
user_access = controller.resolve_user_access("john.doe", include_audit=True)
print(f"User has access to: {list(user_access['resolvedAccess'].keys())}")
print(f"Audit entries: {len(user_access.get('auditTrail', []))}")
```

### get_access_summary(user_id)

Get access summary for a user.

**Parameters:**
- `user_id` (str): User ID

**Returns:** `Optional[Dict[str, Any]]` - Access summary or None

**Example:**
```python
summary = controller.get_access_summary("john.doe")
if summary:
    print(f"Total resources: {summary['total_accessible_resources']}")
    print(f"Direct permissions: {summary['direct_permissions']}")
    print(f"Inherited permissions: {summary['inherited_permissions']}")
```

## Utility Methods

### health_check()

Perform system health check.

**Returns:** `Dict[str, Any]` - Health check results

**Example:**
```python
health = controller.health_check()
print(f"Status: {health['status']}")
print(f"Database: {health['database']}")
print(f"User count: {health['statistics']['users']}")
print(f"Application: {health['configuration']['application_name']}")
```

### get_session()

Get a database session for advanced operations.

**Returns:** `Session` - SQLAlchemy session

**Example:**
```python
with controller.get_session() as session:
    # Perform custom database operations
    users = session.query(User).filter(User.active == True).all()
```

## Exception Handling

### Exception Types

```python
from medha_one_access.core.exceptions import (
    MedhaAccessError,           # Base exception
    DatabaseConnectionError,    # Database issues
    ExpressionValidationError,  # Invalid expressions
    PermissionDeniedError,      # Permission issues
    ConfigurationError          # Configuration issues
)
```

### Error Handling Pattern

```python
try:
    user = controller.create_user({
        "id": "test_user",
        "type": "USER",
        "email": "test@company.com"
    })
except MedhaAccessError as e:
    print(f"Access error: {e}")
except DatabaseConnectionError as e:
    print(f"Database error: {e}")
except ExpressionValidationError as e:
    print(f"Invalid expression '{e.expression}': {e.reason}")
except PermissionDeniedError as e:
    print(f"Permission denied: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Application Filtering

When `application_name` is set in `LibraryConfig`, all operations are automatically filtered by application:

### Automatic Filtering Behavior

- **Create Operations**: Automatically set `application` field if not provided
- **Read Operations**: Only return entities from the configured application
- **List Operations**: Only return entities from the configured application
- **Update/Delete Operations**: Only affect entities from the configured application

### Example with Application Filtering

```python
# Configure with application filtering
config = LibraryConfig(
    database_url="postgresql://...",
    secret_key="...",
    application_name="CRM"
)
controller = AccessController(config)

# All operations now automatically filter by "CRM" application
crm_users = controller.list_users()        # Only CRM users
crm_artifacts = controller.list_artifacts()  # Only CRM artifacts
crm_rules = controller.list_access_rules()   # Only CRM rules

# Create operations automatically set application="CRM"
artifact = controller.create_artifact({
    "id": "customer_dashboard",
    "type": "RESOURCE",
    "name": "Customer Dashboard"
    # application="CRM" is automatically set
})
```

### Bypassing Application Filtering

To work with multiple applications or bypass filtering, create separate controllers:

```python
# CRM controller
crm_config = LibraryConfig(database_url="...", secret_key="...", application_name="CRM")
crm_controller = AccessController(crm_config)

# Analytics controller  
analytics_config = LibraryConfig(database_url="...", secret_key="...", application_name="Analytics")
analytics_controller = AccessController(analytics_config)

# Global controller (no application filtering)
global_config = LibraryConfig(database_url="...", secret_key="...")
global_controller = AccessController(global_config)

# Use appropriate controller based on context
crm_users = crm_controller.list_users()
analytics_artifacts = analytics_controller.list_artifacts()
all_rules = global_controller.list_access_rules()
```