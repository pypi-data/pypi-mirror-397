# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the MedhaOne Access Control Library.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Database Connection Issues](#database-connection-issues)
- [Configuration Issues](#configuration-issues)
- [Expression Errors](#expression-errors)
- [Performance Issues](#performance-issues)
- [API Issues](#api-issues)
- [Common Error Messages](#common-error-messages)

---

## Installation Issues

### ImportError: No module named 'medha_one_access'

**Problem**: Package not installed or not in Python path.

**Solution**:
```bash
# Install the package
pip install medha-one-access

# Verify installation
pip show medha-one-access

# Check if it's importable
python -c "import medha_one_access; print(medha_one_access.__version__)"
```

### Missing Optional Dependencies

**Problem**: Features like YAML config or FastAPI integration not working.

**Solution**:
```bash
# Install with all optional dependencies
pip install medha-one-access[all]

# Or install specific extras
pip install medha-one-access[api]    # FastAPI integration
pip install medha-one-access[yaml]   # YAML config support
pip install medha-one-access[cli]    # CLI tools
```

### asyncpg Installation Fails

**Problem**: `asyncpg` compilation errors on some systems.

**Solution**:
```bash
# On macOS
brew install postgresql

# On Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# On Windows - use pre-built wheel
pip install asyncpg --only-binary :all:
```

---

## Database Connection Issues

### DatabaseConnectionError: Failed to initialize database

**Problem**: Cannot connect to the database.

**Diagnosis**:
```python
from medha_one_access import LibraryConfig

config = LibraryConfig(
    database_url="postgresql://user:pass@localhost:5432/db",
    secret_key="test",
    debug=True,  # Enable debug logging
)

# Check the URL format
print(f"Database URL: {config.database_url}")
```

**Common causes and solutions**:

1. **Wrong URL format**:
   ```python
   # PostgreSQL
   "postgresql://user:password@host:5432/database"

   # SQLite
   "sqlite+aiosqlite:///./local.db"
   ```

2. **Database not running**:
   ```bash
   # Check PostgreSQL status
   pg_isready -h localhost -p 5432

   # Start PostgreSQL (macOS)
   brew services start postgresql
   ```

3. **Wrong credentials**:
   ```bash
   # Test connection manually
   psql -h localhost -U user -d database
   ```

4. **Firewall blocking connection**:
   ```bash
   # Check if port is accessible
   nc -zv localhost 5432
   ```

### Connection Pool Exhausted

**Problem**: "QueuePool limit of size X overflow Y reached"

**Solution**:
```python
config = LibraryConfig(
    database_url="...",
    secret_key="...",
    # Increase pool size
    max_pool_size=50,        # Default: 20
    max_pool_overflow=100,   # Default: 40
    # Recycle connections more frequently
    pool_recycle_time=1800,  # 30 minutes
)
```

### Connection Timeout

**Problem**: Operations timing out during database operations.

**Solution**:
```python
config = LibraryConfig(
    database_url="...",
    secret_key="...",
    connection_timeout=60,  # Increase from 30s default
    query_timeout=120,      # Increase from 60s default
)
```

---

## Configuration Issues

### ConfigurationError: Missing required configuration

**Problem**: Required configuration parameters not provided.

**Solution**:
```python
# Both database_url and secret_key are required
config = LibraryConfig(
    database_url="postgresql://...",  # Required
    secret_key="your-secret-key",     # Required
)

# Or use environment variables
# Set: MEDHA_DATABASE_URL and MEDHA_SECRET_KEY
config = LibraryConfig.from_env()
```

### Environment Variables Not Loading

**Problem**: Configuration from environment not working.

**Diagnosis**:
```python
import os

# Check if variables are set
print(os.getenv("MEDHA_DATABASE_URL"))
print(os.getenv("MEDHA_SECRET_KEY"))

# Try with explicit prefix
config = LibraryConfig.from_env(env_prefix="MEDHA_")
```

**Solution**:
```bash
# Make sure variables are exported
export MEDHA_DATABASE_URL="postgresql://..."
export MEDHA_SECRET_KEY="..."

# Verify they're in the environment
env | grep MEDHA_
```

### YAML Config File Not Found

**Problem**: `FileNotFoundError` when loading YAML config.

**Solution**:
```python
from pathlib import Path

# Check if file exists
config_path = Path("config.yaml")
print(f"File exists: {config_path.exists()}")
print(f"Absolute path: {config_path.absolute()}")

# Use absolute path
config = LibraryConfig.from_file("/full/path/to/config.yaml")
```

### Custom Prefix Not Working

**Problem**: Custom environment prefix not being recognized.

**Solution**:
```python
# When using custom prefix, ALL variables must use that prefix
# Example with MYAPP_ prefix:

# Environment variables should be:
# MYAPP_DATABASE_URL (not MEDHA_DATABASE_URL)
# MYAPP_SECRET_KEY (not MEDHA_SECRET_KEY)

config = LibraryConfig.from_env(env_prefix="MYAPP_")
```

---

## Expression Errors

### ExpressionValidationError: Invalid expression syntax

**Problem**: Expression syntax is incorrect.

**Common mistakes and fixes**:

```python
# Wrong: Using = instead of ==
"USER.department = 'engineering'"    # BAD
"USER.department == 'engineering'"   # GOOD

# Wrong: Missing quotes around strings
"USER.department == engineering"     # BAD
"USER.department == 'engineering'"   # GOOD

# Wrong: Invalid operator
"USER.level && USER.active"          # BAD
"USER.level AND USER.active"         # GOOD

# Wrong: Unbalanced parentheses
"(USER.a == 'x' AND USER.b == 'y'"   # BAD
"(USER.a == 'x' AND USER.b == 'y')"  # GOOD
```

### Expression References Non-Existent Entity

**Problem**: Expression references a user or resource that doesn't exist.

**Solution**:
```python
# Validate that referenced entities exist before creating expressions
async with controller.get_session() as session:
    # Check if user exists
    user = await controller.get_user("user-to-reference")
    if not user:
        print("User doesn't exist - expression will fail")
```

### Circular Expression Reference

**Problem**: User group expressions reference each other.

**Detection**:
```python
# Group A references Group B
# Group B references Group A
# This creates infinite recursion

# The library detects this and raises an error
# Fix by breaking the circular reference
```

---

## Performance Issues

### Slow Access Checks

**Problem**: `check_access()` calls taking too long.

**Solutions**:

1. **Enable caching**:
   ```python
   config = LibraryConfig(
       database_url="...",
       secret_key="...",
       enable_caching=True,
       global_cache_ttl=600,           # 10 minutes
       user_access_cache_ttl=300,      # 5 minutes
       expression_cache_ttl=300,       # 5 minutes
   )
   ```

2. **Increase cache size**:
   ```python
   config = LibraryConfig(
       database_url="...",
       secret_key="...",
       global_cache_max_size=100000,      # Default: 50000
       user_access_cache_max_size=50000,  # Default: 10000
   )
   ```

3. **Use batched recalculation**:
   ```python
   config = LibraryConfig(
       database_url="...",
       secret_key="...",
       auto_recalc_mode="batched",
       auto_recalc_batch_size=100,
   )
   ```

### High Memory Usage

**Problem**: Application using too much memory.

**Solutions**:

1. **Reduce cache sizes**:
   ```python
   config = LibraryConfig(
       database_url="...",
       secret_key="...",
       global_cache_max_size=10000,    # Reduce from 50000
       expression_cache_max_size=5000, # Reduce from 10000
   )
   ```

2. **Reduce cache TTL** (items expire faster):
   ```python
   config = LibraryConfig(
       database_url="...",
       secret_key="...",
       global_cache_ttl=300,  # 5 minutes instead of 10
   )
   ```

### Background Tasks Backing Up

**Problem**: Recalculation tasks not completing fast enough.

**Solution**:
```python
config = LibraryConfig(
    database_url="...",
    secret_key="...",
    # Increase workers
    background_workers=10,           # Default: 5
    background_queue_size=50000,     # Default: 10000
    # Adjust batch processing
    auto_recalc_batch_size=100,      # Default: 50
)
```

---

## API Issues

### 404 Not Found on API Endpoints

**Problem**: API endpoints returning 404.

**Diagnosis**:
```python
from medha_one_access import get_mounted_routers

# Check what routes are mounted
routers = get_mounted_routers(config)
print("Mounted routes:")
for name, path in routers.items():
    print(f"  {name}: {path}")
```

**Common causes**:

1. **Routes not mounted**:
   ```python
   # Make sure to call mount function
   from medha_one_access import mount_access_control_routes

   controller = mount_access_control_routes(app, config)
   ```

2. **Wrong API prefix**:
   ```python
   # Check your api_prefix
   print(f"API Prefix: {config.api_prefix}")
   # Requests should go to: {api_prefix}/users, {api_prefix}/artifacts, etc.
   ```

### 500 Internal Server Error

**Problem**: API returning 500 errors.

**Diagnosis**:
```python
# Enable debug mode
config = LibraryConfig(
    database_url="...",
    secret_key="...",
    debug=True,
    enable_query_logging=True,
    log_level="DEBUG",
)
```

### CORS Errors

**Problem**: Browser showing CORS errors.

**Solution**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Common Error Messages

### "MedhaAccessError: User with ID xxx already exists"

**Cause**: Trying to create a user that already exists.

**Solution**:
```python
# Use upsert to update if exists
await controller.create_user(user_data, upsert=True)

# Or check first
existing = await controller.get_user(user_id)
if existing:
    await controller.update_user(user_id, user_data)
else:
    await controller.create_user(user_data)
```

### "MedhaAccessError: Failed to create user: ..."

**Cause**: Various issues during user creation.

**Diagnosis**:
```python
import traceback

try:
    await controller.create_user(user_data)
except MedhaAccessError as e:
    print(f"Error: {e}")
    traceback.print_exc()
```

### "DatabaseConnectionError: Async database connection test failed"

**Cause**: Database connection issues during async initialization.

**Solution**:
```python
# Test database connection first
import asyncpg

try:
    conn = await asyncpg.connect(
        "postgresql://user:pass@host/db"
    )
    await conn.close()
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

---

## Getting Help

If you're still experiencing issues:

1. **Check the documentation**: [docs/](docs/)
2. **Search existing issues**: [GitHub Issues](https://github.com/medhaone-analytics/medha-one-access/issues)
3. **Create a new issue** with:
   - Python version
   - Package version (`pip show medha-one-access`)
   - Full error traceback
   - Minimal reproducible example
