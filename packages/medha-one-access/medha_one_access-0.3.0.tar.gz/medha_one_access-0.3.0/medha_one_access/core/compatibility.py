"""
Compatibility layer for handling different package versions

This module ensures the library works with any version of dependencies 
already installed in the host environment without forcing upgrades/downgrades.
"""
import sys
import warnings
from typing import Any, Dict, Optional, Type

# Pydantic version compatibility
PYDANTIC_V2 = False
PYDANTIC_VERSION = None

try:
    import pydantic
    PYDANTIC_VERSION = getattr(pydantic, '__version__', 'unknown')
    
    # Try to detect Pydantic v2
    if hasattr(pydantic, 'BaseModel') and hasattr(pydantic.BaseModel, 'model_validate'):
        PYDANTIC_V2 = True
    
    # Try different import patterns for BaseSettings
    try:
        from pydantic.v1 import BaseSettings as V1BaseSettings
        from pydantic import BaseSettings as V2BaseSettings
    except ImportError:
        try:
            from pydantic import BaseSettings as V1BaseSettings
            V2BaseSettings = None
        except ImportError:
            V1BaseSettings = None
            V2BaseSettings = None
            
except ImportError:
    V1BaseSettings = None
    V2BaseSettings = None

# Try to import pydantic-settings (may or may not be installed)
SettingsBaseSettings = None
HAS_PYDANTIC_SETTINGS = False

try:
    from pydantic_settings import BaseSettings as SettingsBaseSettings
    HAS_PYDANTIC_SETTINGS = True
except ImportError:
    pass

# Determine which BaseSettings to use - try all possibilities
BaseSettings = None

if HAS_PYDANTIC_SETTINGS:
    BaseSettings = SettingsBaseSettings
elif PYDANTIC_V2 and V2BaseSettings:
    BaseSettings = V2BaseSettings
elif V1BaseSettings:
    BaseSettings = V1BaseSettings
else:
    # Ultimate fallback - create a basic settings class that works anywhere
    class FallbackBaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
                
        class Config:
            env_file = ".env"
            case_sensitive = False
            
    BaseSettings = FallbackBaseSettings

# SQLAlchemy version compatibility
try:
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import MetaData
    
    # SQLAlchemy 2.x style
    def get_base_class():
        return declarative_base()
        
    SQLALCHEMY_2X = True
except ImportError:
    try:
        from sqlalchemy.ext.declarative import declarative_base
        
        # SQLAlchemy 1.x style
        def get_base_class():
            return declarative_base()
            
        SQLALCHEMY_2X = False
    except ImportError:
        # Very old versions
        def get_base_class():
            from sqlalchemy.ext.declarative import declarative_base
            return declarative_base()
        SQLALCHEMY_2X = False

# FastAPI version compatibility
def get_fastapi_dependency_params():
    """Get the correct parameter order for FastAPI dependencies based on version"""
    try:
        import fastapi
        version = getattr(fastapi, '__version__', '0.0.0')
        major, minor = version.split('.')[:2]
        
        # FastAPI 0.100+ uses different parameter ordering
        if int(major) > 0 or (int(major) == 0 and int(minor) >= 100):
            return 'new'  # Dependencies first
        else:
            return 'old'  # Path parameters first
    except:
        return 'old'  # Default to old style for safety

# Version information helper
def get_package_versions() -> Dict[str, Optional[str]]:
    """Get versions of key packages for debugging"""
    versions = {}
    
    packages = [
        'pydantic', 
        'pydantic_settings', 
        'sqlalchemy', 
        'fastapi', 
        'uvicorn',
        'alembic'
    ]
    
    for package in packages:
        try:
            module = __import__(package)
            versions[package] = getattr(module, '__version__', 'unknown')
        except ImportError:
            versions[package] = None
            
    return versions

# Optional dependency handling
def safe_import(module_name: str, fallback=None):
    """Safely import a module, return fallback if not available"""
    try:
        return __import__(module_name)
    except ImportError:
        return fallback

def require_optional_dependency(module_name: str, feature_name: str):
    """Raise helpful error if optional dependency is missing"""
    try:
        return __import__(module_name)
    except ImportError:
        raise ImportError(
            f"The '{module_name}' package is required for {feature_name}. "
            f"Install it with: pip install {module_name}"
        )

# Feature availability checks
def has_fastapi() -> bool:
    """Check if FastAPI is available"""
    return safe_import('fastapi') is not None

def has_cli_support() -> bool:
    """Check if CLI dependencies are available"""
    return all([
        safe_import('click') is not None,
        safe_import('rich') is not None,
        safe_import('typer') is not None
    ])

def check_environment_compatibility():
    """Check compatibility with current environment and warn if needed"""
    versions = get_package_versions()
    
    # Only warn, don't fail - library should work with any versions
    missing_deps = [name for name, version in versions.items() if version is None]
    
    if missing_deps:
        warnings.warn(
            f"Some optional dependencies are not installed: {', '.join(missing_deps)}. "
            f"Some features may not be available.",
            UserWarning
        )

# Pydantic model conversion helper
def from_orm(model_class, orm_obj):
    """Convert ORM object to Pydantic model, handling v1/v2 differences"""
    if PYDANTIC_V2:
        # Pydantic v2 uses model_validate
        if hasattr(model_class, 'model_validate'):
            return model_class.model_validate(orm_obj)
    # Pydantic v1 uses from_orm
    if hasattr(model_class, 'from_orm'):
        return model_class.from_orm(orm_obj)
    # Fallback - try to instantiate directly
    return model_class(**orm_obj.__dict__)

def model_dump(pydantic_obj, **kwargs):
    """Convert Pydantic model to dict, handling v1/v2 differences"""
    if hasattr(pydantic_obj, 'model_dump'):
        # Pydantic v2
        return pydantic_obj.model_dump(**kwargs)
    else:
        # Pydantic v1 - convert kwargs if needed
        v1_kwargs = {}
        if 'exclude_unset' in kwargs:
            v1_kwargs['exclude_unset'] = kwargs['exclude_unset']
        return pydantic_obj.dict(**v1_kwargs)

# Export compatibility information
__all__ = [
    'BaseSettings',
    'PYDANTIC_V2', 
    'HAS_PYDANTIC_SETTINGS',
    'SQLALCHEMY_2X',
    'get_base_class',
    'get_fastapi_dependency_params',
    'get_package_versions',
    'warn_compatibility_issues',
    'from_orm',
    'model_dump'
]