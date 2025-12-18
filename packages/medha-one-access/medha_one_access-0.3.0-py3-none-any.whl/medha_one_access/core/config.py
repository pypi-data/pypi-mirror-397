"""
MedhaOne Access Control Library Configuration

Configuration management for the access control library.
Supports programmatic configuration, environment variables, and config files (YAML/JSON).

This library is designed to be fully configurable for ANY organization.
All settings can be customized via:
1. Constructor parameters (highest priority)
2. Environment variables (with configurable prefix)
3. Config files (YAML or JSON)
4. Default values (lowest priority)
"""

from typing import Optional, Dict, Any, Union
from pydantic import Field
from .compatibility import BaseSettings
from pydantic import PostgresDsn
import os
import json
from pathlib import Path


class AccessControlConfig(BaseSettings):
    """Pydantic-based configuration class for MedhaOne Access Control Library.

    This is the legacy configuration class. For new implementations,
    use LibraryConfig which provides more flexibility.
    """

    # Database configuration
    database_url: PostgresDsn = Field(..., description="PostgreSQL database URL")

    # Security configuration
    secret_key: str = Field(
        ..., description="Secret key for token encryption/decryption"
    )

    # API configuration (for FastAPI integration)
    api_prefix: str = Field("/access", description="API route prefix")

    # Application settings
    project_name: str = Field("Access Control Library", description="Project name")
    debug: bool = Field(False, description="Debug mode")

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "MEDHA_"


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        raise ImportError(
            "PyYAML is required to load YAML config files. "
            "Install it with: pip install medha-one-access[yaml] or pip install pyyaml"
        )


def _load_json(path: Path) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(path, 'r') as f:
        return json.load(f)


def load_config_file(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a YAML or JSON file.

    Args:
        path: Path to the configuration file (.yaml, .yml, or .json)

    Returns:
        Dictionary of configuration values

    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file does not exist
        ImportError: If PyYAML is not installed for YAML files
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    suffix = p.suffix.lower()
    if suffix in ('.yaml', '.yml'):
        return _load_yaml(p)
    elif suffix == '.json':
        return _load_json(p)
    else:
        raise ValueError(
            f"Unsupported config file format: {suffix}. "
            "Use .yaml, .yml, or .json"
        )


class LibraryConfig:
    """
    Comprehensive configuration class for the access control library.

    This class provides full configurability for ANY organization to use
    this library without modification. All hardcoded values have been
    exposed as configurable parameters.

    Configuration Methods:
        1. Programmatic: Pass values directly to constructor
        2. Environment Variables: Use from_env() with custom prefix
        3. Config Files: Use from_file() for YAML/JSON configuration
        4. Combined: Use from_env_or_file() for layered configuration

    Example:
        # Minimal configuration
        config = LibraryConfig(
            database_url="postgresql://user:pass@localhost/db",
            secret_key="your-secret-key"
        )

        # Custom organization configuration
        config = LibraryConfig(
            database_url="postgresql://...",
            secret_key="...",
            env_prefix="MYCOMPANY_",      # Your custom env prefix
            api_prefix="/my-access-api",   # Your API path
            project_name="MyCompany ACL",  # Your project name
        )

        # From environment variables with custom prefix
        config = LibraryConfig.from_env(env_prefix="MYCOMPANY_")
        # Reads: MYCOMPANY_DATABASE_URL, MYCOMPANY_SECRET_KEY, etc.

        # From config file
        config = LibraryConfig.from_file("config.yaml")
    """

    def __init__(
        self,
        # === REQUIRED PARAMETERS ===
        database_url: str,
        secret_key: str,

        # === NAMING & BRANDING (fully configurable for any organization) ===
        env_prefix: str = "MEDHA_",
        project_name: str = "Access Control Library",
        api_prefix: str = "/access",

        # === APPLICATION SETTINGS ===
        application_name: Optional[str] = None,
        debug: bool = False,

        # === CACHE CONFIGURATION ===
        # Global cache settings
        enable_caching: bool = True,
        cache_ttl: int = 300,  # General cache TTL (seconds)
        global_cache_max_size: int = 50000,
        global_cache_ttl: int = 600,
        # Expression cache settings
        expression_cache_max_size: int = 10000,
        expression_cache_ttl: int = 300,
        # User access cache settings
        user_access_cache_max_size: int = 10000,
        user_access_cache_ttl: int = 300,

        # === BACKGROUND TASK CONFIGURATION ===
        background_workers: int = 5,
        background_queue_size: int = 10000,
        background_shutdown_timeout: float = 30.0,
        background_worker_timeout: float = 1.0,
        task_cleanup_max_age_hours: int = 24,

        # === DATABASE POOL CONFIGURATION ===
        max_pool_size: int = 20,
        max_pool_overflow: int = 40,
        pool_recycle_time: int = 3600,
        pool_pre_ping: bool = True,
        db_jit_enabled: bool = False,  # PostgreSQL JIT compilation
        connection_timeout: int = 30,
        query_timeout: int = 60,

        # === API & PAGINATION CONFIGURATION ===
        default_page_size: int = 50,
        max_page_size: int = 1000,

        # === PERFORMANCE FLAGS ===
        enable_bulk_queries: bool = True,
        enable_audit_trail: bool = False,  # Disabled by default for performance

        # === AUTO-RECALCULATION SETTINGS ===
        enable_auto_recalculation: bool = True,
        auto_recalc_mode: str = "immediate",  # "immediate", "batched", or "disabled"
        auto_recalc_batch_size: int = 50,
        auto_recalc_batch_delay: int = 5,  # Seconds

        # === LOGGING CONFIGURATION ===
        log_level: str = "INFO",
        enable_query_logging: bool = False,

        # === EXTENSIBILITY ===
        **kwargs,
    ):
        """
        Initialize library configuration.

        Args:
            database_url: Database connection URL (PostgreSQL or SQLite)
            secret_key: Secret key for token encryption/decryption
            env_prefix: Prefix for environment variables (default: "MEDHA_")
            project_name: Project name for logs and errors
            api_prefix: Base path for API endpoints (default: "/access")
            application_name: Optional application context for multi-tenancy
            debug: Enable debug mode

            # Cache Configuration
            enable_caching: Enable/disable caching globally
            cache_ttl: General cache time-to-live in seconds
            global_cache_max_size: Maximum items in global cache
            global_cache_ttl: Global cache TTL in seconds
            expression_cache_max_size: Max items in expression parser cache
            expression_cache_ttl: Expression cache TTL in seconds
            user_access_cache_max_size: Max items in user access cache
            user_access_cache_ttl: User access cache TTL in seconds

            # Background Tasks
            background_workers: Number of background worker threads
            background_queue_size: Maximum queued background tasks
            background_shutdown_timeout: Graceful shutdown timeout in seconds
            background_worker_timeout: Worker poll timeout in seconds
            task_cleanup_max_age_hours: Task history retention in hours

            # Database Pool
            max_pool_size: Connection pool size
            max_pool_overflow: Maximum overflow connections
            pool_recycle_time: Connection recycle time in seconds
            pool_pre_ping: Validate connections before use
            db_jit_enabled: Enable PostgreSQL JIT compilation
            connection_timeout: Database connection timeout in seconds
            query_timeout: Query execution timeout in seconds

            # API Configuration
            default_page_size: Default items per page for pagination
            max_page_size: Maximum items per page

            # Performance Flags
            enable_bulk_queries: Enable bulk query optimizations
            enable_audit_trail: Enable audit trail logging

            # Auto-Recalculation
            enable_auto_recalculation: Auto-recalculate on data changes
            auto_recalc_mode: "immediate", "batched", or "disabled"
            auto_recalc_batch_size: Max users per batch
            auto_recalc_batch_delay: Batch processing delay in seconds

            # Logging
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            enable_query_logging: Log database queries

            **kwargs: Additional configuration for extensibility
        """
        # Required
        self.database_url = database_url
        self.secret_key = secret_key

        # Naming & Branding
        self.env_prefix = env_prefix
        self.project_name = project_name
        self.api_prefix = api_prefix

        # Application
        self.application_name = application_name
        self.debug = debug

        # Cache Configuration
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.global_cache_max_size = global_cache_max_size
        self.global_cache_ttl = global_cache_ttl
        self.expression_cache_max_size = expression_cache_max_size
        self.expression_cache_ttl = expression_cache_ttl
        self.user_access_cache_max_size = user_access_cache_max_size
        self.user_access_cache_ttl = user_access_cache_ttl

        # Background Tasks
        self.background_workers = background_workers
        self.background_queue_size = background_queue_size
        self.background_shutdown_timeout = background_shutdown_timeout
        self.background_worker_timeout = background_worker_timeout
        self.task_cleanup_max_age_hours = task_cleanup_max_age_hours

        # Database Pool
        self.max_pool_size = max_pool_size
        self.max_pool_overflow = max_pool_overflow
        self.pool_recycle_time = pool_recycle_time
        self.pool_pre_ping = pool_pre_ping
        self.db_jit_enabled = db_jit_enabled
        self.connection_timeout = connection_timeout
        self.query_timeout = query_timeout

        # API & Pagination
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size

        # Performance Flags
        self.enable_bulk_queries = enable_bulk_queries
        self.enable_audit_trail = enable_audit_trail

        # Auto-recalculation
        self.enable_auto_recalculation = enable_auto_recalculation
        self.auto_recalc_mode = auto_recalc_mode
        self.auto_recalc_batch_size = auto_recalc_batch_size
        self.auto_recalc_batch_delay = auto_recalc_batch_delay

        # Logging
        self.log_level = log_level
        self.enable_query_logging = enable_query_logging

        # Extra config for extensibility
        self.extra_config = kwargs

    @classmethod
    def from_env(cls, env_prefix: str = "MEDHA_") -> "LibraryConfig":
        """
        Create configuration from environment variables.

        The env_prefix allows any organization to use their own naming convention.

        Args:
            env_prefix: Prefix for environment variables (e.g., "MYCOMPANY_")

        Returns:
            LibraryConfig instance

        Raises:
            ValueError: If required environment variables are not set

        Example:
            # With default prefix (MEDHA_)
            config = LibraryConfig.from_env()
            # Reads: MEDHA_DATABASE_URL, MEDHA_SECRET_KEY, etc.

            # With custom prefix
            config = LibraryConfig.from_env(env_prefix="MYAPP_")
            # Reads: MYAPP_DATABASE_URL, MYAPP_SECRET_KEY, etc.
        """
        def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
            return os.getenv(f"{env_prefix}{key}", default)

        def get_env_bool(key: str, default: bool) -> bool:
            val = get_env(key)
            if val is None:
                return default
            return val.lower() in ('true', '1', 'yes', 'on')

        def get_env_int(key: str, default: int) -> int:
            val = get_env(key)
            if val is None:
                return default
            return int(val)

        def get_env_float(key: str, default: float) -> float:
            val = get_env(key)
            if val is None:
                return default
            return float(val)

        database_url = get_env("DATABASE_URL")
        secret_key = get_env("SECRET_KEY")

        if not database_url:
            raise ValueError(
                f"Environment variable {env_prefix}DATABASE_URL is required"
            )
        if not secret_key:
            raise ValueError(
                f"Environment variable {env_prefix}SECRET_KEY is required"
            )

        return cls(
            database_url=database_url,
            secret_key=secret_key,

            # Naming & Branding
            env_prefix=env_prefix,
            project_name=get_env("PROJECT_NAME", "Access Control Library"),
            api_prefix=get_env("API_PREFIX", "/access"),

            # Application
            application_name=get_env("APPLICATION_NAME"),
            debug=get_env_bool("DEBUG", False),

            # Cache Configuration
            enable_caching=get_env_bool("ENABLE_CACHING", True),
            cache_ttl=get_env_int("CACHE_TTL", 300),
            global_cache_max_size=get_env_int("GLOBAL_CACHE_MAX_SIZE", 50000),
            global_cache_ttl=get_env_int("GLOBAL_CACHE_TTL", 600),
            expression_cache_max_size=get_env_int("EXPRESSION_CACHE_MAX_SIZE", 10000),
            expression_cache_ttl=get_env_int("EXPRESSION_CACHE_TTL", 300),
            user_access_cache_max_size=get_env_int("USER_ACCESS_CACHE_MAX_SIZE", 10000),
            user_access_cache_ttl=get_env_int("USER_ACCESS_CACHE_TTL", 300),

            # Background Tasks
            background_workers=get_env_int("BACKGROUND_WORKERS", 5),
            background_queue_size=get_env_int("BACKGROUND_QUEUE_SIZE", 10000),
            background_shutdown_timeout=get_env_float("BACKGROUND_SHUTDOWN_TIMEOUT", 30.0),
            background_worker_timeout=get_env_float("BACKGROUND_WORKER_TIMEOUT", 1.0),
            task_cleanup_max_age_hours=get_env_int("TASK_CLEANUP_MAX_AGE_HOURS", 24),

            # Database Pool
            max_pool_size=get_env_int("MAX_POOL_SIZE", 20),
            max_pool_overflow=get_env_int("MAX_POOL_OVERFLOW", 40),
            pool_recycle_time=get_env_int("POOL_RECYCLE_TIME", 3600),
            pool_pre_ping=get_env_bool("POOL_PRE_PING", True),
            db_jit_enabled=get_env_bool("DB_JIT_ENABLED", False),
            connection_timeout=get_env_int("CONNECTION_TIMEOUT", 30),
            query_timeout=get_env_int("QUERY_TIMEOUT", 60),

            # API & Pagination
            default_page_size=get_env_int("DEFAULT_PAGE_SIZE", 50),
            max_page_size=get_env_int("MAX_PAGE_SIZE", 1000),

            # Performance Flags
            enable_bulk_queries=get_env_bool("ENABLE_BULK_QUERIES", True),
            enable_audit_trail=get_env_bool("ENABLE_AUDIT_TRAIL", False),

            # Auto-recalculation
            enable_auto_recalculation=get_env_bool("ENABLE_AUTO_RECALC", True),
            auto_recalc_mode=get_env("AUTO_RECALC_MODE", "immediate"),
            auto_recalc_batch_size=get_env_int("AUTO_RECALC_BATCH_SIZE", 50),
            auto_recalc_batch_delay=get_env_int("AUTO_RECALC_BATCH_DELAY", 5),

            # Logging
            log_level=get_env("LOG_LEVEL", "INFO"),
            enable_query_logging=get_env_bool("ENABLE_QUERY_LOGGING", False),
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "LibraryConfig":
        """
        Create configuration from a YAML or JSON file.

        Args:
            path: Path to configuration file (.yaml, .yml, or .json)

        Returns:
            LibraryConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If file format is not supported
            ImportError: If PyYAML is not installed for YAML files

        Example:
            config = LibraryConfig.from_file("config.yaml")

        Sample YAML config:
            database_url: "postgresql://user:pass@localhost/db"
            secret_key: "your-secret-key"
            env_prefix: "MYCOMPANY_"
            api_prefix: "/my-api"
            max_pool_size: 50
            enable_caching: true
        """
        config_dict = load_config_file(path)
        return cls(**config_dict)

    @classmethod
    def from_env_or_file(
        cls,
        env_prefix: str = "MEDHA_",
        config_file: Optional[Union[str, Path]] = None,
    ) -> "LibraryConfig":
        """
        Create configuration with layered sources.

        Priority (highest to lowest):
        1. Environment variables
        2. Config file values
        3. Default values

        Args:
            env_prefix: Prefix for environment variables
            config_file: Optional path to config file

        Returns:
            LibraryConfig instance

        Example:
            # Load from file, override with env vars
            config = LibraryConfig.from_env_or_file(
                env_prefix="MYAPP_",
                config_file="config.yaml"
            )
        """
        # Start with file config if provided
        base_config = {}
        if config_file:
            try:
                base_config = load_config_file(config_file)
            except FileNotFoundError:
                pass  # File is optional

        # Helper to get value with priority: env > file > default
        def get_value(key: str, env_key: str, default: Any) -> Any:
            env_val = os.getenv(f"{env_prefix}{env_key}")
            if env_val is not None:
                # Convert string to appropriate type
                if isinstance(default, bool):
                    return env_val.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default, int):
                    return int(env_val)
                elif isinstance(default, float):
                    return float(env_val)
                return env_val
            return base_config.get(key, default)

        database_url = get_value("database_url", "DATABASE_URL", None)
        secret_key = get_value("secret_key", "SECRET_KEY", None)

        if not database_url:
            raise ValueError(
                f"database_url is required. Set {env_prefix}DATABASE_URL or "
                "include 'database_url' in config file"
            )
        if not secret_key:
            raise ValueError(
                f"secret_key is required. Set {env_prefix}SECRET_KEY or "
                "include 'secret_key' in config file"
            )

        return cls(
            database_url=database_url,
            secret_key=secret_key,
            env_prefix=get_value("env_prefix", "ENV_PREFIX", env_prefix),
            project_name=get_value("project_name", "PROJECT_NAME", "Access Control Library"),
            api_prefix=get_value("api_prefix", "API_PREFIX", "/access"),
            application_name=get_value("application_name", "APPLICATION_NAME", None),
            debug=get_value("debug", "DEBUG", False),
            enable_caching=get_value("enable_caching", "ENABLE_CACHING", True),
            cache_ttl=get_value("cache_ttl", "CACHE_TTL", 300),
            global_cache_max_size=get_value("global_cache_max_size", "GLOBAL_CACHE_MAX_SIZE", 50000),
            global_cache_ttl=get_value("global_cache_ttl", "GLOBAL_CACHE_TTL", 600),
            expression_cache_max_size=get_value("expression_cache_max_size", "EXPRESSION_CACHE_MAX_SIZE", 10000),
            expression_cache_ttl=get_value("expression_cache_ttl", "EXPRESSION_CACHE_TTL", 300),
            user_access_cache_max_size=get_value("user_access_cache_max_size", "USER_ACCESS_CACHE_MAX_SIZE", 10000),
            user_access_cache_ttl=get_value("user_access_cache_ttl", "USER_ACCESS_CACHE_TTL", 300),
            background_workers=get_value("background_workers", "BACKGROUND_WORKERS", 5),
            background_queue_size=get_value("background_queue_size", "BACKGROUND_QUEUE_SIZE", 10000),
            background_shutdown_timeout=get_value("background_shutdown_timeout", "BACKGROUND_SHUTDOWN_TIMEOUT", 30.0),
            background_worker_timeout=get_value("background_worker_timeout", "BACKGROUND_WORKER_TIMEOUT", 1.0),
            task_cleanup_max_age_hours=get_value("task_cleanup_max_age_hours", "TASK_CLEANUP_MAX_AGE_HOURS", 24),
            max_pool_size=get_value("max_pool_size", "MAX_POOL_SIZE", 20),
            max_pool_overflow=get_value("max_pool_overflow", "MAX_POOL_OVERFLOW", 40),
            pool_recycle_time=get_value("pool_recycle_time", "POOL_RECYCLE_TIME", 3600),
            pool_pre_ping=get_value("pool_pre_ping", "POOL_PRE_PING", True),
            db_jit_enabled=get_value("db_jit_enabled", "DB_JIT_ENABLED", False),
            connection_timeout=get_value("connection_timeout", "CONNECTION_TIMEOUT", 30),
            query_timeout=get_value("query_timeout", "QUERY_TIMEOUT", 60),
            default_page_size=get_value("default_page_size", "DEFAULT_PAGE_SIZE", 50),
            max_page_size=get_value("max_page_size", "MAX_PAGE_SIZE", 1000),
            enable_bulk_queries=get_value("enable_bulk_queries", "ENABLE_BULK_QUERIES", True),
            enable_audit_trail=get_value("enable_audit_trail", "ENABLE_AUDIT_TRAIL", False),
            enable_auto_recalculation=get_value("enable_auto_recalculation", "ENABLE_AUTO_RECALC", True),
            auto_recalc_mode=get_value("auto_recalc_mode", "AUTO_RECALC_MODE", "immediate"),
            auto_recalc_batch_size=get_value("auto_recalc_batch_size", "AUTO_RECALC_BATCH_SIZE", 50),
            auto_recalc_batch_delay=get_value("auto_recalc_batch_delay", "AUTO_RECALC_BATCH_DELAY", 5),
            log_level=get_value("log_level", "LOG_LEVEL", "INFO"),
            enable_query_logging=get_value("enable_query_logging", "ENABLE_QUERY_LOGGING", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            # Required
            "database_url": self.database_url,
            "secret_key": self.secret_key,

            # Naming & Branding
            "env_prefix": self.env_prefix,
            "project_name": self.project_name,
            "api_prefix": self.api_prefix,

            # Application
            "application_name": self.application_name,
            "debug": self.debug,

            # Cache Configuration
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "global_cache_max_size": self.global_cache_max_size,
            "global_cache_ttl": self.global_cache_ttl,
            "expression_cache_max_size": self.expression_cache_max_size,
            "expression_cache_ttl": self.expression_cache_ttl,
            "user_access_cache_max_size": self.user_access_cache_max_size,
            "user_access_cache_ttl": self.user_access_cache_ttl,

            # Background Tasks
            "background_workers": self.background_workers,
            "background_queue_size": self.background_queue_size,
            "background_shutdown_timeout": self.background_shutdown_timeout,
            "background_worker_timeout": self.background_worker_timeout,
            "task_cleanup_max_age_hours": self.task_cleanup_max_age_hours,

            # Database Pool
            "max_pool_size": self.max_pool_size,
            "max_pool_overflow": self.max_pool_overflow,
            "pool_recycle_time": self.pool_recycle_time,
            "pool_pre_ping": self.pool_pre_ping,
            "db_jit_enabled": self.db_jit_enabled,
            "connection_timeout": self.connection_timeout,
            "query_timeout": self.query_timeout,

            # API & Pagination
            "default_page_size": self.default_page_size,
            "max_page_size": self.max_page_size,

            # Performance Flags
            "enable_bulk_queries": self.enable_bulk_queries,
            "enable_audit_trail": self.enable_audit_trail,

            # Auto-recalculation
            "enable_auto_recalculation": self.enable_auto_recalculation,
            "auto_recalc_mode": self.auto_recalc_mode,
            "auto_recalc_batch_size": self.auto_recalc_batch_size,
            "auto_recalc_batch_delay": self.auto_recalc_batch_delay,

            # Logging
            "log_level": self.log_level,
            "enable_query_logging": self.enable_query_logging,

            # Extra
            **self.extra_config,
        }

    def __repr__(self) -> str:
        """String representation of config (hides sensitive values)."""
        return (
            f"LibraryConfig("
            f"project_name='{self.project_name}', "
            f"api_prefix='{self.api_prefix}', "
            f"env_prefix='{self.env_prefix}', "
            f"debug={self.debug}"
            f")"
        )
