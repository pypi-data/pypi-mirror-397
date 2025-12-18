# Security Guide

This guide covers security best practices when using the MedhaOne Access Control Library.

## Table of Contents

- [Secret Key Management](#secret-key-management)
- [Database Security](#database-security)
- [Expression Security](#expression-security)
- [API Security](#api-security)
- [Audit Trail](#audit-trail)
- [Environment Variables](#environment-variables)
- [Production Checklist](#production-checklist)

---

## Secret Key Management

The `secret_key` configuration parameter is used for encryption operations. Proper management is critical.

### Generating a Strong Secret Key

```python
# Using cryptography library
from cryptography.fernet import Fernet
secret_key = Fernet.generate_key().decode()
print(secret_key)  # Use this value

# Using Python secrets module
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

### Best Practices

1. **Never hardcode secrets in source code**
   ```python
   # BAD - Never do this
   config = LibraryConfig(
       database_url="...",
       secret_key="my-secret-key-in-code"  # WRONG!
   )

   # GOOD - Use environment variables
   import os
   config = LibraryConfig(
       database_url=os.getenv("DATABASE_URL"),
       secret_key=os.getenv("SECRET_KEY")
   )
   ```

2. **Use a secrets manager in production**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Google Secret Manager

3. **Rotate secrets periodically**
   - Establish a rotation schedule (e.g., every 90 days)
   - Have a process for emergency rotation

---

## Database Security

### Connection Security

Always use SSL/TLS for database connections in production:

```python
# PostgreSQL with SSL
config = LibraryConfig(
    database_url="postgresql://user:pass@host/db?sslmode=require",
    secret_key=os.getenv("SECRET_KEY"),
)

# With full SSL verification
config = LibraryConfig(
    database_url="postgresql://user:pass@host/db?sslmode=verify-full&sslrootcert=/path/to/ca.crt",
    secret_key=os.getenv("SECRET_KEY"),
)
```

### Database User Permissions

Create a dedicated database user with minimal required permissions:

```sql
-- Create dedicated user
CREATE USER medha_access WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE your_db TO medha_access;
GRANT USAGE ON SCHEMA public TO medha_access;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO medha_access;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO medha_access;

-- Revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM medha_access;
```

### Connection Pool Security

Configure connection pooling for security and reliability:

```python
config = LibraryConfig(
    database_url="postgresql://...",
    secret_key="...",
    # Pool settings
    max_pool_size=20,           # Limit connections
    pool_pre_ping=True,         # Validate connections
    connection_timeout=30,       # Prevent hanging
    query_timeout=60,           # Prevent runaway queries
)
```

---

## Expression Security

The BODMAS expression engine is designed with security in mind.

### Expression Parsing (Not Execution)

Expressions are **parsed and evaluated**, not executed as code:

```python
# Safe - expressions are parsed, not executed
expression = "USER.department == 'engineering' AND USER.level >= 3"

# The expression parser:
# 1. Tokenizes the expression
# 2. Validates syntax
# 3. Evaluates against known attributes
# 4. NO arbitrary code execution
```

### Input Sanitization

User input is automatically sanitized before expression evaluation:

```python
# User group expressions are validated before storage
user_data = UserCreate(
    id="user-group-1",
    name="Engineering Team",
    type="USERGROUP",
    expression="USER.department == 'engineering'"  # Validated
)

# Invalid expressions are rejected
try:
    user_data = UserCreate(
        id="bad-group",
        name="Bad Group",
        type="USERGROUP",
        expression="__import__('os').system('rm -rf /')"  # Rejected!
    )
except ExpressionValidationError:
    print("Invalid expression rejected")
```

### Allowed Expression Operators

Only safe operators are allowed:

| Operator | Description |
|----------|-------------|
| `AND`, `OR`, `NOT` | Logical operators |
| `==`, `!=` | Equality comparison |
| `<`, `>`, `<=`, `>=` | Numeric comparison |
| `IN`, `NOT IN` | Set membership |
| `(`, `)` | Grouping |

Dangerous operations like function calls, imports, and system access are not supported.

---

## API Security

When using the FastAPI integration, implement these security measures:

### Authentication Middleware

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Implement your token verification logic
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# Mount routes with authentication
from medha_one_access import mount_access_control_routes

controller = mount_access_control_routes(app, config)

# Protect all access control endpoints
@app.middleware("http")
async def auth_middleware(request, call_next):
    if request.url.path.startswith(config.api_prefix):
        # Verify authentication for access control endpoints
        auth_header = request.headers.get("Authorization")
        if not auth_header or not verify_auth(auth_header):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Apply rate limits to sensitive endpoints
@app.get(f"{config.api_prefix}/access/check")
@limiter.limit("100/minute")
async def check_access(request: Request):
    # ...
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## Audit Trail

Enable audit trail for compliance and forensics:

```python
config = LibraryConfig(
    database_url="...",
    secret_key="...",
    enable_audit_trail=True,  # Enable logging
)
```

### What's Logged

When audit trail is enabled, the following events are logged:

- User creation, update, deletion
- Artifact creation, update, deletion
- Access rule changes
- Access check requests and results
- Permission denials

### Log Format

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "event_type": "access_check",
    "user_id": "user123",
    "artifact_id": "report-dashboard",
    "permission": "VIEW",
    "result": "granted",
    "resolved_via": "rule-45",
    "ip_address": "192.168.1.100"
}
```

### Performance Consideration

Audit trail adds overhead. For high-throughput systems, consider:

```python
# Batch audit logging
config = LibraryConfig(
    enable_audit_trail=True,
    # Use batched recalculation mode for better performance
    auto_recalc_mode="batched",
    auto_recalc_batch_size=100,
)
```

---

## Environment Variables

### Secure Environment Variable Handling

```bash
# Production environment setup
export MYAPP_DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
export MYAPP_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export MYAPP_DEBUG="false"
export MYAPP_ENABLE_AUDIT_TRAIL="true"
```

### Using Custom Prefix

Use a custom prefix to avoid conflicts:

```python
# With custom prefix
config = LibraryConfig.from_env(env_prefix="MYAPP_")
# Reads: MYAPP_DATABASE_URL, MYAPP_SECRET_KEY, etc.
```

### Sensitive Variables

These environment variables contain sensitive data:

| Variable | Sensitivity | Handling |
|----------|-------------|----------|
| `*_DATABASE_URL` | High | Contains credentials |
| `*_SECRET_KEY` | Critical | Encryption key |
| `*_API_KEY` | High | API authentication |

---

## Production Checklist

### Before Deployment

- [ ] **Secrets**
  - [ ] Generate strong `secret_key` (32+ characters)
  - [ ] Store secrets in environment variables or secrets manager
  - [ ] Never commit secrets to version control
  - [ ] Set up secret rotation policy

- [ ] **Database**
  - [ ] Enable SSL/TLS for database connections
  - [ ] Create dedicated database user with minimal permissions
  - [ ] Configure connection pool limits
  - [ ] Set appropriate timeouts

- [ ] **API Security**
  - [ ] Implement authentication middleware
  - [ ] Configure rate limiting
  - [ ] Set up CORS with specific origins
  - [ ] Enable HTTPS only

- [ ] **Logging & Monitoring**
  - [ ] Enable audit trail if required
  - [ ] Set up log aggregation
  - [ ] Configure alerting for security events

- [ ] **Configuration**
  - [ ] Set `debug=False`
  - [ ] Disable `enable_query_logging` in production
  - [ ] Review all configuration parameters

### Example Production Configuration

```python
import os

config = LibraryConfig(
    # Required
    database_url=os.environ["DATABASE_URL"],
    secret_key=os.environ["SECRET_KEY"],

    # Security
    debug=False,
    enable_audit_trail=True,
    enable_query_logging=False,

    # Performance with security
    max_pool_size=50,
    max_pool_overflow=100,
    pool_pre_ping=True,
    connection_timeout=30,
    query_timeout=60,

    # Caching
    enable_caching=True,
    global_cache_ttl=600,

    # Custom branding
    env_prefix="PROD_",
    api_prefix="/api/v1/access",
    project_name="Production Access Control",
)
```

---

## Security Updates

Subscribe to security updates:

1. Watch the GitHub repository for releases
2. Check the CHANGELOG for security-related changes
3. Keep dependencies updated

```bash
# Update to latest version
pip install --upgrade medha-one-access
```
