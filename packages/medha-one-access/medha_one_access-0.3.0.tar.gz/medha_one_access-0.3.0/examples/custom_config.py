"""
Custom Configuration Examples for MedhaOne Access Control

This example demonstrates how to configure the library for different
environments and use cases with custom branding, API prefixes, and
performance settings.
"""

import os
import asyncio


def example_programmatic_config():
    """
    Example 1: Programmatic Configuration

    Configure directly in code with full control over all parameters.
    """
    from medha_one_access import LibraryConfig, AccessController

    # Full customization for your organization
    config = LibraryConfig(
        # Required parameters
        database_url="postgresql://user:pass@localhost/db",
        secret_key="your-secret-key-min-32-chars-long",

        # Custom branding - use your organization's prefix
        env_prefix="MYCOMPANY_",           # Environment variable prefix
        api_prefix="/api/v1/access",       # API endpoint prefix
        project_name="MyCompany ACL",      # Project name for logs

        # Application isolation (multi-tenancy)
        application_name="my-app",

        # Cache configuration for high performance
        enable_caching=True,
        global_cache_max_size=100000,
        global_cache_ttl=1200,             # 20 minutes
        expression_cache_max_size=20000,
        user_access_cache_max_size=50000,

        # Database pool configuration
        max_pool_size=50,
        max_pool_overflow=100,
        pool_pre_ping=True,
        connection_timeout=30,
        query_timeout=60,

        # Background task configuration
        background_workers=10,
        background_queue_size=50000,

        # Auto-recalculation settings
        enable_auto_recalculation=True,
        auto_recalc_mode="batched",        # "immediate" or "batched"
        auto_recalc_batch_size=100,

        # Logging
        log_level="INFO",
        debug=False,
    )

    # Create controller with this config
    controller = AccessController(config)

    print("Controller initialized with custom config:")
    print(f"  API Prefix: {config.api_prefix}")
    print(f"  Env Prefix: {config.env_prefix}")
    print(f"  Pool Size: {config.max_pool_size}")

    return controller


def example_environment_config():
    """
    Example 2: Environment Variable Configuration

    Load configuration from environment variables with custom prefix.
    """
    from medha_one_access import LibraryConfig, AccessController

    # Set up environment variables (normally done in shell/docker/k8s)
    os.environ["ACME_DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    os.environ["ACME_SECRET_KEY"] = "env-secret-key-min-32-chars"
    os.environ["ACME_API_PREFIX"] = "/acme/access"
    os.environ["ACME_MAX_POOL_SIZE"] = "30"
    os.environ["ACME_ENABLE_CACHING"] = "true"
    os.environ["ACME_GLOBAL_CACHE_TTL"] = "900"
    os.environ["ACME_BACKGROUND_WORKERS"] = "8"
    os.environ["ACME_DEBUG"] = "false"

    # Load from environment with custom prefix
    config = LibraryConfig.from_env(env_prefix="ACME_")

    print("Config loaded from environment:")
    print(f"  Database URL: {config.database_url}")
    print(f"  API Prefix: {config.api_prefix}")
    print(f"  Pool Size: {config.max_pool_size}")
    print(f"  Cache TTL: {config.global_cache_ttl}")

    controller = AccessController(config)
    return controller


def example_yaml_config():
    """
    Example 3: YAML File Configuration

    Load configuration from a YAML file.
    Requires: pip install medha-one-access[yaml]
    """
    from medha_one_access import LibraryConfig

    # Create a sample YAML config file
    yaml_content = """
# config.yaml - MedhaOne Access Control Configuration

# Required settings
database_url: "postgresql://user:pass@localhost/db"
secret_key: "yaml-secret-key-minimum-32-characters"

# Branding
env_prefix: "MYORG_"
api_prefix: "/myorg/access"
project_name: "MyOrg Access Control"

# Application
application_name: "production"
debug: false

# Cache settings
enable_caching: true
global_cache_max_size: 100000
global_cache_ttl: 600
expression_cache_max_size: 10000
user_access_cache_max_size: 20000

# Database pool
max_pool_size: 40
max_pool_overflow: 80
pool_pre_ping: true
connection_timeout: 30
query_timeout: 60

# Background tasks
background_workers: 5
background_queue_size: 10000

# Auto-recalculation
enable_auto_recalculation: true
auto_recalc_mode: "immediate"
auto_recalc_batch_size: 50

# Logging
log_level: "INFO"
enable_query_logging: false
"""

    # Write sample config file
    config_path = "/tmp/medha_config.yaml"
    with open(config_path, "w") as f:
        f.write(yaml_content)

    # Load from YAML file
    try:
        config = LibraryConfig.from_file(config_path)
        print("Config loaded from YAML:")
        print(f"  Project Name: {config.project_name}")
        print(f"  API Prefix: {config.api_prefix}")
        print(f"  Pool Size: {config.max_pool_size}")
        return config
    except ImportError:
        print("YAML support requires: pip install medha-one-access[yaml]")
        return None


def example_combined_config():
    """
    Example 4: Combined Configuration (File + Environment Override)

    Load base config from file, override with environment variables.
    """
    from medha_one_access import LibraryConfig

    # Base config in file, overrides in environment
    # Environment variables take precedence over file values

    # Set environment override
    os.environ["PROD_MAX_POOL_SIZE"] = "100"  # Override file value
    os.environ["PROD_DEBUG"] = "false"

    # Create base YAML config
    yaml_content = """
database_url: "postgresql://user:pass@localhost/db"
secret_key: "combined-secret-key-min-32-chars"
max_pool_size: 20
debug: true
"""
    config_path = "/tmp/base_config.yaml"
    with open(config_path, "w") as f:
        f.write(yaml_content)

    try:
        # Load with environment overrides
        config = LibraryConfig.from_env_or_file(
            env_prefix="PROD_",
            config_file=config_path
        )

        print("Combined config (file + env overrides):")
        print(f"  Pool Size: {config.max_pool_size}")  # Should be 100 (from env)
        print(f"  Debug: {config.debug}")              # Should be False (from env)
        return config
    except ImportError:
        print("YAML support requires: pip install medha-one-access[yaml]")
        return None


def example_development_config():
    """
    Example 5: Development Configuration

    Optimized settings for local development.
    """
    from medha_one_access import LibraryConfig, AccessController

    config = LibraryConfig(
        # Use SQLite for local development
        database_url="sqlite+aiosqlite:///./dev_access.db",
        secret_key="dev-only-secret-not-for-production",

        # Development settings
        debug=True,
        enable_query_logging=True,
        log_level="DEBUG",

        # Smaller resource footprint
        max_pool_size=5,
        global_cache_max_size=1000,
        background_workers=2,

        # Shorter cache for faster iteration
        global_cache_ttl=60,

        # Disable audit for speed
        enable_audit_trail=False,
    )

    print("Development config created:")
    print(f"  Debug: {config.debug}")
    print(f"  Log Level: {config.log_level}")

    return AccessController(config)


def example_production_config():
    """
    Example 6: Production Configuration

    High-performance settings for production deployment.
    """
    from medha_one_access import LibraryConfig, AccessController

    config = LibraryConfig(
        # Production database (from environment in real deployment)
        database_url=os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/prod"),
        secret_key=os.getenv("SECRET_KEY", "must-set-in-production"),

        # Production settings
        debug=False,
        enable_query_logging=False,
        log_level="WARNING",

        # High-performance settings
        max_pool_size=100,
        max_pool_overflow=200,
        pool_pre_ping=True,
        connection_timeout=30,
        query_timeout=120,

        # Large caches
        global_cache_max_size=500000,
        global_cache_ttl=1800,  # 30 minutes
        expression_cache_max_size=50000,
        user_access_cache_max_size=100000,

        # Many background workers
        background_workers=20,
        background_queue_size=100000,

        # Enable audit for compliance
        enable_audit_trail=True,

        # Batched recalculation for better throughput
        auto_recalc_mode="batched",
        auto_recalc_batch_size=200,
    )

    print("Production config created:")
    print(f"  Pool Size: {config.max_pool_size}")
    print(f"  Workers: {config.background_workers}")
    print(f"  Audit: {config.enable_audit_trail}")

    return AccessController(config)


async def example_fastapi_integration():
    """
    Example 7: FastAPI Integration with Custom Config

    Mount access control routes with custom API prefix.
    """
    try:
        from fastapi import FastAPI
        from medha_one_access import LibraryConfig, mount_access_control_routes
    except ImportError:
        print("FastAPI integration requires: pip install medha-one-access[api]")
        return

    app = FastAPI(title="My API with Access Control")

    config = LibraryConfig(
        database_url="sqlite+aiosqlite:///./api_example.db",
        secret_key="api-secret-key-minimum-32-chars",
        # Custom API prefix - all routes will be under this path
        api_prefix="/api/v2/permissions",
        project_name="My API Access Control",
    )

    # Mount routes with custom prefix
    controller = mount_access_control_routes(app, config)

    print("FastAPI routes mounted:")
    print(f"  Users: {config.api_prefix}/users")
    print(f"  Artifacts: {config.api_prefix}/artifacts")
    print(f"  Access Rules: {config.api_prefix}/access-rules")
    print(f"  Access Check: {config.api_prefix}/access/check")
    print(f"  Health: {config.api_prefix}/health")

    return app, controller


def example_multi_tenant_config():
    """
    Example 8: Multi-Tenant Configuration

    Separate configurations for different tenants sharing the same database.
    """
    from medha_one_access import LibraryConfig, AccessController

    # Shared database URL
    shared_db = "postgresql://user:pass@localhost/shared_db"
    shared_secret = "shared-secret-key-minimum-32-chars"

    # Tenant A configuration
    tenant_a_config = LibraryConfig(
        database_url=shared_db,
        secret_key=shared_secret,
        application_name="tenant_a",       # Isolates data by tenant
        env_prefix="TENANT_A_",
        api_prefix="/tenant-a/access",
        project_name="Tenant A Access Control",
    )

    # Tenant B configuration
    tenant_b_config = LibraryConfig(
        database_url=shared_db,
        secret_key=shared_secret,
        application_name="tenant_b",       # Isolates data by tenant
        env_prefix="TENANT_B_",
        api_prefix="/tenant-b/access",
        project_name="Tenant B Access Control",
    )

    print("Multi-tenant configs created:")
    print(f"  Tenant A: app={tenant_a_config.application_name}, api={tenant_a_config.api_prefix}")
    print(f"  Tenant B: app={tenant_b_config.application_name}, api={tenant_b_config.api_prefix}")

    # Each controller only sees its own tenant's data
    controller_a = AccessController(tenant_a_config)
    controller_b = AccessController(tenant_b_config)

    return controller_a, controller_b


if __name__ == "__main__":
    print("=" * 60)
    print("MedhaOne Access Control - Custom Configuration Examples")
    print("=" * 60)

    print("\n1. Programmatic Configuration:")
    print("-" * 40)
    example_programmatic_config()

    print("\n2. Environment Variable Configuration:")
    print("-" * 40)
    example_environment_config()

    print("\n3. YAML File Configuration:")
    print("-" * 40)
    example_yaml_config()

    print("\n4. Combined Configuration:")
    print("-" * 40)
    example_combined_config()

    print("\n5. Development Configuration:")
    print("-" * 40)
    example_development_config()

    print("\n6. Production Configuration:")
    print("-" * 40)
    example_production_config()

    print("\n7. FastAPI Integration:")
    print("-" * 40)
    asyncio.run(example_fastapi_integration())

    print("\n8. Multi-Tenant Configuration:")
    print("-" * 40)
    example_multi_tenant_config()

    print("\n" + "=" * 60)
    print("Examples completed!")
