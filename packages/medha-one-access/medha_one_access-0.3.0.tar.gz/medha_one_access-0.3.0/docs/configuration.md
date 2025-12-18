# Configuration Reference

This document provides a complete reference for all configurable parameters in the MedhaOne Access Control Library.

## Quick Start

```python
from medha_one_access import LibraryConfig

# Minimal configuration
config = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key"
)

# Full customization for your organization
config = LibraryConfig(
    database_url="postgresql://...",
    secret_key="...",
    env_prefix="MYCOMPANY_",      # Your custom env var prefix
    api_prefix="/my-access-api",   # Your API path
    project_name="MyCompany ACL",  # Your project name
)
```

## Configuration Methods

### Method 1: Programmatic Configuration

```python
from medha_one_access import LibraryConfig

config = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
    api_prefix="/my-api",
    max_pool_size=50,
    enable_caching=True,
)
```

### Method 2: Environment Variables

```python
from medha_one_access import LibraryConfig

# With default prefix (MEDHA_)
config = LibraryConfig.from_env()
# Reads: MEDHA_DATABASE_URL, MEDHA_SECRET_KEY, etc.

# With custom prefix
config = LibraryConfig.from_env(env_prefix="MYAPP_")
# Reads: MYAPP_DATABASE_URL, MYAPP_SECRET_KEY, etc.
```

### Method 3: Configuration File (YAML/JSON)

```python
from medha_one_access import LibraryConfig

# From YAML file
config = LibraryConfig.from_file("config.yaml")

# From JSON file
config = LibraryConfig.from_file("config.json")
```

**Sample YAML configuration:**

```yaml
# config.yaml
database_url: "postgresql://user:pass@localhost/db"
secret_key: "your-secret-key"
env_prefix: "MYCOMPANY_"
api_prefix: "/my-api"
project_name: "MyCompany Access Control"

# Cache settings
global_cache_max_size: 100000
global_cache_ttl: 1200

# Database pool
max_pool_size: 50
max_pool_overflow: 100

# Background tasks
background_workers: 10
```

### Method 4: Combined (File + Environment Variables)

```python
from medha_one_access import LibraryConfig

# Load from file, override with environment variables
config = LibraryConfig.from_env_or_file(
    env_prefix="MYAPP_",
    config_file="config.yaml"
)
```

**Priority (highest to lowest):**
1. Environment variables
2. Config file values
3. Default values

---

## All Configuration Options

### Required Parameters

| Parameter | Type | Env Var Suffix | Description |
|-----------|------|----------------|-------------|
| `database_url` | str | `DATABASE_URL` | PostgreSQL or SQLite connection URL |
| `secret_key` | str | `SECRET_KEY` | Encryption key for tokens |

### Naming & Branding

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `env_prefix` | str | `"MEDHA_"` | `ENV_PREFIX` | Prefix for environment variables |
| `project_name` | str | `"Access Control Library"` | `PROJECT_NAME` | Project name for logs/errors |
| `api_prefix` | str | `"/access"` | `API_PREFIX` | Base path for all API endpoints |

### Application Settings

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `application_name` | str | `None` | `APPLICATION_NAME` | Application context for multi-tenancy |
| `debug` | bool | `False` | `DEBUG` | Enable debug mode |

### Cache Configuration

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `enable_caching` | bool | `True` | `ENABLE_CACHING` | Enable/disable caching globally |
| `cache_ttl` | int | `300` | `CACHE_TTL` | General cache TTL (seconds) |
| `global_cache_max_size` | int | `50000` | `GLOBAL_CACHE_MAX_SIZE` | Maximum items in global cache |
| `global_cache_ttl` | int | `600` | `GLOBAL_CACHE_TTL` | Global cache TTL (seconds) |
| `expression_cache_max_size` | int | `10000` | `EXPRESSION_CACHE_MAX_SIZE` | Expression parser cache size |
| `expression_cache_ttl` | int | `300` | `EXPRESSION_CACHE_TTL` | Expression cache TTL (seconds) |
| `user_access_cache_max_size` | int | `10000` | `USER_ACCESS_CACHE_MAX_SIZE` | User access resolution cache size |
| `user_access_cache_ttl` | int | `300` | `USER_ACCESS_CACHE_TTL` | User access cache TTL (seconds) |

### Background Task Configuration

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `background_workers` | int | `5` | `BACKGROUND_WORKERS` | Number of worker threads |
| `background_queue_size` | int | `10000` | `BACKGROUND_QUEUE_SIZE` | Maximum queued tasks |
| `background_shutdown_timeout` | float | `30.0` | `BACKGROUND_SHUTDOWN_TIMEOUT` | Graceful shutdown timeout (seconds) |
| `background_worker_timeout` | float | `1.0` | `BACKGROUND_WORKER_TIMEOUT` | Worker poll timeout (seconds) |
| `task_cleanup_max_age_hours` | int | `24` | `TASK_CLEANUP_MAX_AGE_HOURS` | Task history retention (hours) |

### Database Pool Configuration

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `max_pool_size` | int | `20` | `MAX_POOL_SIZE` | Connection pool size |
| `max_pool_overflow` | int | `40` | `MAX_POOL_OVERFLOW` | Maximum overflow connections |
| `pool_recycle_time` | int | `3600` | `POOL_RECYCLE_TIME` | Connection recycle time (seconds) |
| `pool_pre_ping` | bool | `True` | `POOL_PRE_PING` | Validate connections before use |
| `db_jit_enabled` | bool | `False` | `DB_JIT_ENABLED` | Enable PostgreSQL JIT compilation |
| `connection_timeout` | int | `30` | `CONNECTION_TIMEOUT` | Database connection timeout (seconds) |
| `query_timeout` | int | `60` | `QUERY_TIMEOUT` | Query execution timeout (seconds) |

### API & Pagination Configuration

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `default_page_size` | int | `50` | `DEFAULT_PAGE_SIZE` | Default items per page |
| `max_page_size` | int | `1000` | `MAX_PAGE_SIZE` | Maximum items per page |

### Performance Flags

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `enable_bulk_queries` | bool | `True` | `ENABLE_BULK_QUERIES` | Enable bulk query optimizations |
| `enable_audit_trail` | bool | `False` | `ENABLE_AUDIT_TRAIL` | Enable audit trail logging |

### Auto-Recalculation Settings

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `enable_auto_recalculation` | bool | `True` | `ENABLE_AUTO_RECALC` | Auto-recalculate on data changes |
| `auto_recalc_mode` | str | `"immediate"` | `AUTO_RECALC_MODE` | Mode: "immediate", "batched", "disabled" |
| `auto_recalc_batch_size` | int | `50` | `AUTO_RECALC_BATCH_SIZE` | Maximum users per batch |
| `auto_recalc_batch_delay` | int | `5` | `AUTO_RECALC_BATCH_DELAY` | Batch processing delay (seconds) |

### Logging Configuration

| Parameter | Type | Default | Env Var Suffix | Description |
|-----------|------|---------|----------------|-------------|
| `log_level` | str | `"INFO"` | `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `enable_query_logging` | bool | `False` | `ENABLE_QUERY_LOGGING` | Log database queries |

---

## Environment Variable Mapping

Environment variables use the configured prefix (default: `MEDHA_`).

### With default prefix `MEDHA_`:

```bash
export MEDHA_DATABASE_URL="postgresql://user:pass@localhost/db"
export MEDHA_SECRET_KEY="your-secret-key"
export MEDHA_API_PREFIX="/access"
export MEDHA_MAX_POOL_SIZE="50"
export MEDHA_ENABLE_CACHING="true"
```

### With custom prefix `MYAPP_`:

```bash
export MYAPP_DATABASE_URL="postgresql://user:pass@localhost/db"
export MYAPP_SECRET_KEY="your-secret-key"
export MYAPP_API_PREFIX="/my-access-api"
export MYAPP_MAX_POOL_SIZE="50"
export MYAPP_ENABLE_CACHING="true"
```

---

## Example Configurations

### Development Environment

```python
config = LibraryConfig(
    database_url="sqlite+aiosqlite:///./dev.db",
    secret_key="dev-secret-not-for-production",
    debug=True,
    enable_query_logging=True,
    log_level="DEBUG",
    enable_audit_trail=False,
    max_pool_size=5,
)
```

### Production Environment

```python
import os

config = LibraryConfig(
    database_url=os.getenv("DATABASE_URL"),
    secret_key=os.getenv("SECRET_KEY"),
    debug=False,
    enable_audit_trail=True,
    max_pool_size=50,
    max_pool_overflow=100,
    global_cache_max_size=100000,
    global_cache_ttl=1200,
    pool_pre_ping=True,
)
```

### High-Load Environment

```python
config = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
    max_pool_size=100,
    max_pool_overflow=200,
    global_cache_max_size=500000,
    global_cache_ttl=1800,
    expression_cache_max_size=50000,
    user_access_cache_max_size=100000,
    background_workers=20,
    background_queue_size=50000,
)
```

### Multi-Tenant Environment

```python
# Tenant A
config_tenant_a = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
    application_name="tenant_a",
    env_prefix="TENANT_A_",
    api_prefix="/tenant-a/access",
)

# Tenant B
config_tenant_b = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
    application_name="tenant_b",
    env_prefix="TENANT_B_",
    api_prefix="/tenant-b/access",
)
```

---

## Exporting Configuration

```python
config = LibraryConfig(
    database_url="postgresql://user:pass@localhost/db",
    secret_key="your-secret-key",
)

# Export to dictionary
config_dict = config.to_dict()

# Export to JSON
import json
config_json = json.dumps(config.to_dict(), indent=2)
```

---

## Tips for Configuration

1. **Secret Management**: Never commit secrets to version control. Use environment variables or a secrets manager.

2. **Cache Tuning**: Start with default cache sizes and adjust based on memory usage and hit rates.

3. **Connection Pool Sizing**: Set `max_pool_size` based on expected concurrent connections. A good starting point is 2x the number of CPU cores.

4. **Background Workers**: For CPU-bound operations, set `background_workers` to match your CPU cores. For I/O-bound operations, you can use more workers.

5. **Timeout Values**: Set `connection_timeout` and `query_timeout` based on your network latency and expected query complexity.

6. **Audit Trail**: Enable `enable_audit_trail` for compliance-sensitive environments. Note that this may impact performance.

7. **JIT Compilation**: Keep `db_jit_enabled=False` (default) for most workloads. JIT can slow down short queries.
