"""
Access Control FastAPI Integration

Optional FastAPI integration for creating web APIs and mounting routes.
Gracefully handles cases where FastAPI dependencies are not installed.
"""

from ..core.compatibility import has_fastapi, require_optional_dependency

# Only define API functions if FastAPI is available
if has_fastapi():
    try:
        from .app import create_app
        from .mount import mount_access_control_routes, mount_async_access_control_routes, get_mounted_routers
        from .routers import users, artifacts, access_rules, access_check
        
        # Try to import optional routers
        _imports = {}
        for router_name in ['access_summary', 'reporting', 'data_io']:
            try:
                module = __import__(f'medha_one_access.api.routers.{router_name}', fromlist=[router_name])
                _imports[router_name] = getattr(module, router_name, None)
            except ImportError:
                pass
        
        # Build exports list
        __all__ = [
            "create_app",
            "mount_access_control_routes",
            "mount_async_access_control_routes",
            "get_mounted_routers",
            "users",
            "artifacts", 
            "access_rules",
            "access_check",
        ]
        
        # Add available optional routers
        __all__.extend(_imports.keys())
        
        # Make optional routers available in module namespace
        for name, router in _imports.items():
            if router:
                globals()[name] = router
                
    except ImportError as e:
        # FastAPI is available but there are other import issues
        def _create_error_func(error_msg):
            def error_func(*args, **kwargs):
                raise ImportError(f"FastAPI integration failed: {error_msg}")
            return error_func
        
        create_app = _create_error_func(str(e))
        mount_access_control_routes = _create_error_func(str(e))
        mount_async_access_control_routes = _create_error_func(str(e))
        get_mounted_routers = _create_error_func(str(e))
        
        __all__ = ['create_app', 'mount_access_control_routes', 'mount_async_access_control_routes', 'get_mounted_routers']
        
else:
    # FastAPI not available - provide helpful error messages
    def create_app(*args, **kwargs):
        require_optional_dependency('fastapi', 'API integration')
    
    def mount_access_control_routes(*args, **kwargs):
        require_optional_dependency('fastapi', 'API integration')
        
    def mount_async_access_control_routes(*args, **kwargs):
        require_optional_dependency('fastapi', 'API integration')
        
    def get_mounted_routers(*args, **kwargs):
        require_optional_dependency('fastapi', 'API integration')
        
    __all__ = ['create_app', 'mount_access_control_routes', 'mount_async_access_control_routes', 'get_mounted_routers']
